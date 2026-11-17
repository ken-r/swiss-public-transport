"""Select regular scheduled passenger departures for a calendar date."""

import argparse
import logging
from collections.abc import Iterable, Iterator
from datetime import date, datetime, timedelta

import pandas as pd

from .calendar import get_operating_services_at_date
from .config import ANALYSIS_GTFS_COLUMNS, ANALYSIS_GTFS_DTYPES
from .load import iter_gtfs_file, load_gtfs_file
from .transform import (
    filter_stop_times_by_trip,
    filter_trips_by_service,
    gtfs_time_to_seconds,
    validate_trips_and_stop_times,
)

SECONDS_PER_DAY = 24 * 60 * 60
PROGRESS_LOG_INTERVAL_ROWS = 1_000_000

logger = logging.getLogger(__name__)


def log_read_progress(
    chunks: Iterable[pd.DataFrame], stage: str,
) -> Iterator[pd.DataFrame]:
    """Report input rows read during a long chunked stage.

    Args:
        chunks: DataFrames read from a GTFS file.
        stage: Short label for the current processing stage.

    Yields:
        The original chunks without any transformations.
    """
    logger.info(f"{stage} started")
    rows_read = 0
    next_report = PROGRESS_LOG_INTERVAL_ROWS
    for chunk in chunks:
        rows_read += len(chunk)
        if rows_read >= next_report:
            logger.info(f"{stage}: {rows_read:,} input rows read")
            next_report = (rows_read // PROGRESS_LOG_INTERVAL_ROWS + 1) * PROGRESS_LOG_INTERVAL_ROWS
        yield chunk
    logger.info(f"{stage} complete: {rows_read:,} input rows read")


def scan_stop_times(chunks: Iterable[pd.DataFrame]) -> tuple[int, dict[str, int]]:
    """Find the maximum time offset and each trip's final stop in one scan.

    Args:
        chunks: Stop-time chunks with ``departure_time``, ``trip_id``, and
            ``stop_sequence`` columns.

    Returns:
        Maximum whole-day departure offset and final stop sequence by trip ID.
    """
    maximum = 0
    last: dict[str, int] = {}
    for chunk in chunks:
        seconds = gtfs_time_to_seconds(chunk["departure_time"])
        if seconds.notna().any():
            maximum = max(maximum, int(seconds.max()))
        for trip_id, sequence in chunk.groupby("trip_id")["stop_sequence"].max().items():
            if pd.notna(sequence):
                last[trip_id] = max(last.get(trip_id, 0), int(sequence))
    return maximum // SECONDS_PER_DAY, last


def load_active_trips(
    calendar_date: date, max_day_offset: int,
) -> dict[date, pd.DataFrame]:
    """Load trips for service dates that could contribute to a calendar day.

    Args:
        calendar_date: Calendar date to analyze.
        max_day_offset: Largest whole-day offset in this feed's GTFS times.

    Returns:
        Active trips by service date, including ``trip_id`` and ``route_id``.

    Raises:
        ValueError: If the date is outside the feed or trip IDs are invalid.
    """
    feed = load_gtfs_file(
        "feed_info", columns=["feed_start_date", "feed_end_date"],
        dtype={"feed_start_date": "string", "feed_end_date": "string"},
    )
    day = calendar_date.strftime("%Y%m%d")
    if not ((feed["feed_start_date"] <= day) & (feed["feed_end_date"] >= day)).any():
        raise ValueError(f"{calendar_date} is outside the GTFS feed validity period.")

    feed_start = datetime.strptime(str(feed["feed_start_date"].min()), "%Y%m%d").date()
    # A departure on calendar_date may belong to any earlier service day
    # covered by the feed, up to the largest GTFS time offset.
    days = tuple(
        calendar_date - timedelta(days=offset)
        for offset in range(min(max_day_offset, (calendar_date - feed_start).days), -1, -1)
    )
    calendar = load_gtfs_file(
        "calendar", columns=ANALYSIS_GTFS_COLUMNS["calendar"],
        dtype=ANALYSIS_GTFS_DTYPES["calendar"],
    )
    day_strings = {d.strftime("%Y%m%d") for d in days}
    # Keep only exceptions for relevant service days while reading the large file.
    exceptions = pd.concat(
        (
            chunk.loc[chunk["date"].isin(day_strings)]
            for chunk in log_read_progress(
                iter_gtfs_file(
                    "calendar_dates", columns=ANALYSIS_GTFS_COLUMNS["calendar_dates"],
                    dtype=ANALYSIS_GTFS_DTYPES["calendar_dates"],
                ),
                "Reading calendar exceptions",
            )
        ),
        ignore_index=True,
    )
    trips = load_gtfs_file(
        "trips", columns=ANALYSIS_GTFS_COLUMNS["trips"],
        dtype=ANALYSIS_GTFS_DTYPES["trips"],
    )
    if trips["trip_id"].isna().any() or not trips["trip_id"].is_unique:
        raise ValueError("Trips contain missing or duplicate trip IDs.")
    return {
        d: filter_trips_by_service(
            trips, get_operating_services_at_date(calendar, exceptions, d)
        ).copy()
        for d in days
    }


def iter_active_stop_times(
    chunks: Iterable[pd.DataFrame], active_trips: pd.DataFrame,
) -> Iterator[pd.DataFrame]:
    """Yield stop times for active trips and validate their relationships.

    Args:
        chunks: Stop-time DataFrames with trip IDs and stop sequences.
        active_trips: Trips active on at least one relevant service date.

    Yields:
        Stop-time rows belonging to ``active_trips``.

    Raises:
        ValueError: If IDs or stop sequences are missing, duplicated, or
            unrelated to the active trips.
    """
    seen: set[tuple[str, int]] = set()
    for chunk in chunks:
        active = filter_stop_times_by_trip(chunk, active_trips).copy()
        validate_trips_and_stop_times(active_trips, active)
        # Per-chunk validation cannot find duplicate keys in different chunks.
        keys = set(zip(active["trip_id"], active["stop_sequence"].astype(int)))
        if seen.intersection(keys):
            raise ValueError("Duplicate trip and sequence pairs span stop-time chunks.")
        seen.update(keys)
        yield active


def calendar_day_departures(
    stop_times: pd.DataFrame,
    trips_by_date: dict[date, pd.DataFrame],
    calendar_date: date,
    frequency_trip_ids: set[str],
    last_stop_sequences: dict[str, int],
) -> pd.DataFrame:
    """Select regular scheduled departures on one calendar date.

    Args:
        stop_times: Active stop-time rows from one chunk.
        trips_by_date: Active trips keyed by their GTFS service date.
        calendar_date: Calendar date to analyze.
        frequency_trip_ids: Trips with frequency-based service to exclude.
        last_stop_sequences: Final stop sequence for each active trip.

    Returns:
        Departure rows with ``service_date``, ``departure_seconds``, and
        derived ``departure_date`` columns.

    Raises:
        ValueError: If an active stop or terminal sequence is missing, or a
            departure time is malformed.

    Notes:
        Only regular pickup is counted; terminal stops, special pickup rules,
        and frequency-based trip templates are excluded.
    """
    if stop_times["stop_id"].isna().any():
        raise ValueError("An active stop time has no stop ID.")
    terminal_sequences = stop_times["trip_id"].map(last_stop_sequences)
    if terminal_sequences.isna().any():
        raise ValueError("An active trip has no final stop sequence.")
    times = gtfs_time_to_seconds(stop_times["departure_time"])
    # Missing pickup_type means regular pickup; types 1-3 are excluded here.
    regular_pickup = stop_times["pickup_type"].fillna(0).eq(0)
    # The final stop is an arrival, even when the feed marks pickup_type as 0.
    # Frequency rows are templates, not individual scheduled departures.
    eligible = stop_times.loc[
        regular_pickup & times.notna()
        & stop_times["stop_sequence"].ne(terminal_sequences)
        & ~stop_times["trip_id"].isin(frequency_trip_ids)
    ].copy()
    eligible["departure_seconds"] = times.loc[eligible.index].astype("int64")

    selected = []
    # One trip can operate on multiple service dates, so derive its departure
    # date separately for each date before combining the rows.
    for service_date, trips in trips_by_date.items():
        rows = eligible.loc[eligible["trip_id"].isin(trips["trip_id"])].copy()
        # TODO: Handle daylight saving time changes. When clocks change,
        # adding whole days to the service date may give the wrong departure date.
        rows["departure_date"] = (
            pd.Timestamp(service_date)
            + pd.to_timedelta(rows["departure_seconds"] // SECONDS_PER_DAY, unit="D")
        )
        rows = rows.loc[rows["departure_date"].eq(pd.Timestamp(calendar_date))]
        rows = rows.merge(trips[["trip_id", "route_id"]], on="trip_id", validate="many_to_one")
        rows["service_date"] = service_date.isoformat()
        selected.append(rows)
    return pd.concat(selected, ignore_index=True)


def main() -> None:
    """Count regular departures for the requested calendar date.

    The first stop-times scan finds time offsets and terminal stops; the
    second validates and counts eligible departures.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, type=date.fromisoformat,
                        help="Calendar date (YYYY-MM-DD)")
    calendar_date = parser.parse_args().date
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.info(f"Analyzing calendar date {calendar_date}")
    max_day_offset, all_last_stops = scan_stop_times(log_read_progress(
        iter_gtfs_file(
            "stop_times", columns=["trip_id", "stop_sequence", "departure_time"],
            dtype={"trip_id": "string", "stop_sequence": "Int32",
                   "departure_time": "string"},
        ),
        "Inspecting stop times",
    ))
    logger.info(f"Maximum departure offset: {max_day_offset} day(s)")
    trips_by_date = load_active_trips(calendar_date, max_day_offset)
    active_trips = pd.concat(trips_by_date.values()).drop_duplicates("trip_id")
    logger.info(
        f"Loaded {len(trips_by_date)} service date(s) and {len(active_trips):,} active trips"
    )
    frequency_ids = set(load_gtfs_file(
        "frequencies", columns=["trip_id"], dtype={"trip_id": "string"},
    )["trip_id"].dropna())
    # Keep terminal positions only for trips needed on the selected date.
    last_stop_sequences = {
        trip_id: all_last_stops[trip_id]
        for trip_id in active_trips["trip_id"]
        if trip_id in all_last_stops
    }
    del all_last_stops
    logger.info(f"Found terminal stops for {len(last_stop_sequences):,} trips")
    chunks = log_read_progress(
        iter_gtfs_file(
            "stop_times", columns=ANALYSIS_GTFS_COLUMNS["stop_times"],
            dtype=ANALYSIS_GTFS_DTYPES["stop_times"],
        ),
        "Counting departures",
    )
    totals = {d: 0 for d in trips_by_date}
    for chunk in iter_active_stop_times(chunks, active_trips):
        departures = calendar_day_departures(
            chunk, trips_by_date, calendar_date, frequency_ids,
            last_stop_sequences,
        )
        for service_date, count in departures["service_date"].value_counts().items():
            totals[date.fromisoformat(service_date)] += count
    logger.info(f"Calendar date: {calendar_date}")
    for service_date, count in totals.items():
        logger.info(f"Departures from {service_date} service: {count:,}")
    logger.info(f"Total regular scheduled passenger departures: {sum(totals.values()):,}")
    logger.info("Frequency-based trips and special pickup types are excluded.")


if __name__ == "__main__":
    main()

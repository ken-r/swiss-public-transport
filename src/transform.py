import pandas as pd


def gtfs_time_to_seconds(times: pd.Series) -> pd.Series:
    """Convert GTFS times to seconds since the service-day start.

    Args:
        times: Departure times HH:MM:SS.
            Missing values are allowed; hours may exceed 23.

    Returns:
        Seconds since the service-day start with the same index as ``times``.

    """
    # pandas treats 22:60:00 as 23:00:00, hiding an invalid minute value.
    # Reject invalid GTFS times before converting them to seconds.
    valid = times.astype("string").str.fullmatch(r"\d{2,}:[0-5]\d:[0-5]\d")
    if (~valid.fillna(True)).any():
        raise ValueError("Departure times must be valid GTFS HH:MM:SS values.")
    return pd.to_timedelta(times).dt.total_seconds().astype("Int64")

def validate_trips_and_stop_times(
    trips: pd.DataFrame,
    stop_times: pd.DataFrame,
) -> None:
    """Check GTFS trip IDs and their stop-time relationships.

    Args:
        trips: All loaded trips with a ``trip_id`` column.
        stop_times: All loaded stop times with ``trip_id`` and
            ``stop_sequence`` columns.

    Raises:
        ValueError: If IDs are missing or duplicated, or a stop time
            references a trip not present in ``trips``.
    """
    if trips["trip_id"].isna().any():
        raise ValueError("The trips table contains a missing trip ID.")
    if not trips["trip_id"].is_unique:
        raise ValueError("The trips table contains duplicate trip IDs.")

    if stop_times[["trip_id", "stop_sequence"]].isna().any().any():
        raise ValueError("The stop times table contains a missing trip ID or stop sequence.")
    if stop_times.duplicated(["trip_id", "stop_sequence"]).any():
        raise ValueError("The stop times table contains duplicate trip and sequence pairs.")

    unknown = ~stop_times["trip_id"].isin(trips["trip_id"])
    if unknown.any():
        raise ValueError("A stop time references an unknown trip.")

def filter_trips_by_service(
    trips: pd.DataFrame,
    operating_service_ids: set[str],
) -> pd.DataFrame:
    """Keep trips whose service operates on the selected date.

    Args:
        trips: Loaded trips with a ``service_id`` column.
        operating_service_ids: Service IDs active on the selected date.

    Returns:
        A DataFrame containing only trips with an operating service ID.
    """
    return trips[trips["service_id"].isin(operating_service_ids)]

def filter_stop_times_by_trip(
    stop_times: pd.DataFrame,
    operating_trips: pd.DataFrame,
) -> pd.DataFrame:
    """Keep stop times belonging to operating trips.

    Args:
        stop_times: Loaded stop times with a ``trip_id`` column.
        operating_trips: Filtered trips with a ``trip_id`` column.

    Returns:
        A DataFrame containing only stop times for operating trips.
    """
    return stop_times[stop_times["trip_id"].isin(operating_trips["trip_id"])]

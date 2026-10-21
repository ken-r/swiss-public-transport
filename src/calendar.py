from datetime import date

import pandas as pd


def get_operating_services_at_date(
    calendar: pd.DataFrame | None,
    calendar_dates: pd.DataFrame,
    service_date: date,
) -> set[str]:
    """Return the service IDs operating on one GTFS service date.

    Args:
        calendar: Rows from ``calendar.txt`` with ``service_id``,
            ``start_date``, ``end_date``, and all seven weekday columns.
            Pass ``None`` when the feed has no ``calendar.txt``; in that
            case, services are defined solely by date exceptions.
        calendar_dates: Rows from ``calendar_dates.txt`` with ``service_id``,
            ``date``, and ``exception_type``. Pass an empty DataFrame with
            these columns when the file has no rows for the feed.
        service_date: The GTFS service date. It is not necessarily the
            calendar date of every departure: GTFS times may exceed 24:00.

    Returns:
        A set of active service IDs as strings. An empty set means no
        services are scheduled for the selected date.

    Notes:
        Date columns must be strings in ``YYYYMMDD`` format, as specified
        by ``ANALYSIS_GTFS_DTYPES`` in ``src.config``.
    """
    # The date for which you want to find the operating service IDs.
    gtfs_date = service_date.strftime("%Y%m%d")
    operating_service_ids: set[str] = set()

    if calendar is not None:
        # Find operating services by the date and weekday of the date.
        weekday = service_date.strftime("%A").lower() # Get the weekday of the service date.
        regular = calendar.loc[
            calendar["start_date"].le(gtfs_date)
            & calendar["end_date"].ge(gtfs_date)
            & calendar[weekday].eq(1).fillna(False),
            "service_id",
        ]
        operating_service_ids.update(regular.dropna().astype(str))

    # Get the exceptional services and exception type.
    exceptions = calendar_dates.loc[
        calendar_dates["date"].eq(gtfs_date), ["service_id", "exception_type"]
    ]
    # Exception type 1 = service added at that date.
    added = exceptions.loc[exceptions["exception_type"].eq(1), "service_id"]
    # Exception type 2 = service removed at that date.
    removed = exceptions.loc[exceptions["exception_type"].eq(2), "service_id"]
    operating_service_ids.update(added.dropna().astype(str))
    # Apply removals last so an exception can override a regular service.
    operating_service_ids.difference_update(removed.dropna().astype(str))
    return operating_service_ids

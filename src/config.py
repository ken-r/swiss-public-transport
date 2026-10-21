from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
GTFS_DIR = PROJECT_ROOT / "data" / "raw" / "gtfs"

GTFS_FILES = {
    "agency": GTFS_DIR / "agency.txt",
    "calendar_dates": GTFS_DIR / "calendar_dates.txt",
    "calendar": GTFS_DIR / "calendar.txt",
    "feed_info": GTFS_DIR / "feed_info.txt",
    "frequencies": GTFS_DIR / "frequencies.txt",
    "routes": GTFS_DIR / "routes.txt",
    "stop_times": GTFS_DIR / "stop_times.txt",
    "stops": GTFS_DIR / "stops.txt",
    "transfers": GTFS_DIR / "transfers.txt",
    "trips": GTFS_DIR / "trips.txt",
}

GTFS_FILE_NAMES = GTFS_FILES.keys()

# The relevant files and columns for the analysis.
ANALYSIS_GTFS_COLUMNS = {
    "calendar": [
        "service_id", "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday", "start_date", "end_date",
    ],
    "calendar_dates": ["service_id", "date", "exception_type"],
    "trips": ["trip_id", "service_id", "route_id"],
    "stop_times": [
        "trip_id", "stop_id", "stop_sequence", "arrival_time",
        "departure_time", "pickup_type",
    ],
    "stops": ["stop_id", "stop_name", "location_type", "parent_station"],
    "routes": ["route_id", "route_short_name", "route_type"],
}

ANALYSIS_GTFS_DTYPES = {
    "calendar": {
        "service_id": "string",
        "start_date": "string", # Dates are formatted as strings in YYYYMMDD format.
        "end_date": "string",
        **{day: "Int8" for day in (
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday",
        )}, # Use nullable Int8 to preserve integer weekday flags (0/1) and support missing values (pd.NA).
    },
    "calendar_dates": {
        "service_id": "string",
        "date": "string",
        "exception_type": "Int8",
    },
    "trips": {
        "trip_id": "string",
        "service_id": "string",
        "route_id": "string",
    },
    "stop_times": {
        "trip_id": "string",
        "stop_id": "string",
        "stop_sequence": "Int32",
        "arrival_time": "string",
        "departure_time": "string",
        "pickup_type": "Int8",
    },
    "stops": {
        "stop_id": "string",
        "stop_name": "string",
        "location_type": "Int8",
        "parent_station": "string",
    },
    "routes": {
        "route_id": "string",
        "route_short_name": "string",
        "route_type": "Int16",
    },
}

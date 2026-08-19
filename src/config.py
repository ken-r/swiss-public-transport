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

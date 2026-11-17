"""Tests for filtering trips and stop times for an operating service."""

from datetime import date, timedelta
import unittest

import pandas as pd

from src.active_timetable import (
    calendar_day_departures,
    iter_active_stop_times,
    scan_stop_times,
)
from src.transform import (
    filter_stop_times_by_trip,
    filter_trips_by_service,
    gtfs_time_to_seconds,
    validate_trips_and_stop_times,
)


class TransformTests(unittest.TestCase):
    def setUp(self) -> None:
        self.trips = pd.DataFrame({
            "trip_id": ["001", "002"],
            "service_id": ["active", "inactive"],
            "route_id": ["R1", "R2"],
        })
        self.stop_times = pd.DataFrame({
            "trip_id": ["001", "001", "002"],
            "stop_sequence": [1, 2, 1],
            "stop_id": ["S1", "S1", "S2"],
            "departure_time": ["01:00:00", "25:00:00", "12:00:00"],
        })

    def test_filters_trips_and_their_stop_times(self) -> None:
        operating_trips = filter_trips_by_service(self.trips, {"active"})
        operating_stop_times = filter_stop_times_by_trip(
            self.stop_times, operating_trips
        )

        self.assertEqual(operating_trips["trip_id"].tolist(), ["001"])
        self.assertEqual(operating_trips["route_id"].tolist(), ["R1"])
        self.assertEqual(operating_stop_times["trip_id"].tolist(), ["001", "001"])
        self.assertEqual(operating_stop_times["stop_sequence"].tolist(), [1, 2])

    def test_validation_accepts_repeated_stops_on_one_trip(self) -> None:
        validate_trips_and_stop_times(self.trips, self.stop_times)

    def test_validation_rejects_duplicate_trip_ids(self) -> None:
        # Add a duplicated trip.
        duplicate_trips = pd.concat([self.trips, self.trips.iloc[[0]]])

        with self.assertRaisesRegex(ValueError, "duplicate trip IDs"):
            validate_trips_and_stop_times(duplicate_trips, self.stop_times)

    def test_validation_rejects_unknown_trips(self) -> None:
        # Add a missing trip ID.
        unknown_stop_times = self.stop_times.copy()
        unknown_stop_times.loc[0, "trip_id"] = "missing"

        with self.assertRaisesRegex(ValueError, "unknown trip"):
            validate_trips_and_stop_times(self.trips, unknown_stop_times)

    def test_active_stop_times_across_chunks(self) -> None:
        active_trips = filter_trips_by_service(self.trips, {"active"})
        chunks = [self.stop_times.iloc[:1], self.stop_times.iloc[1:]]

        result = list(iter_active_stop_times(chunks, active_trips))

        self.assertEqual(sum(map(len, result)), 2)
        self.assertEqual(result[1]["trip_id"].tolist(), ["001"])

    def test_duplicate_across_chunks_is_rejected(self) -> None:
        active_trips = filter_trips_by_service(self.trips, {"active"})
        chunks = [self.stop_times.iloc[:1], self.stop_times.iloc[:1]]

        with self.assertRaisesRegex(ValueError, "span stop-time chunks"):
            list(iter_active_stop_times(chunks, active_trips))

    def test_scan_finds_offset_and_terminal_sequences_across_chunks(self) -> None:
        chunks = [self.stop_times.iloc[:1], self.stop_times.iloc[1:]]

        self.assertEqual(scan_stop_times(chunks), (1, {"001": 2, "002": 1}))

    def test_calendar_day_includes_previous_service_after_midnight(self) -> None:
        day = date(2026, 11, 11)
        trips = pd.DataFrame({"trip_id": ["001"], "route_id": ["R1"]})
        stop_times = pd.DataFrame({
            "trip_id": ["001"] * 4,
            "stop_id": ["S1"] * 4,
            "stop_sequence": [1, 2, 3, 4],
            "departure_time": ["01:30:00", "24:00:00", "25:30:00", "48:00:00"],
            "pickup_type": [0] * 4,
        })

        result = calendar_day_departures(
            stop_times, {day - timedelta(days=1): trips, day: trips}, day,
            set(), {"001": 5},
        )

        self.assertEqual(result["departure_time"].tolist(),
                         ["24:00:00", "25:30:00", "01:30:00"])
        self.assertEqual(result["service_date"].tolist(),
                         ["2026-11-10", "2026-11-10", "2026-11-11"])

    def test_non_regular_pickup_and_frequency_templates_are_excluded(self) -> None:
        day = date(2026, 11, 11)
        trips = pd.DataFrame({"trip_id": ["regular", "no_pickup", "frequency"],
                              "route_id": ["R1", "R2", "R3"]})
        stop_times = pd.DataFrame({
            "trip_id": ["regular", "no_pickup", "frequency"],
            "stop_id": ["S1"] * 3,
            "stop_sequence": [1] * 3,
            "departure_time": ["12:00:00"] * 3,
            "pickup_type": [0, 1, 0],
        })

        result = calendar_day_departures(
            stop_times, {day: trips}, day, {"frequency"},
            {"regular": 2, "no_pickup": 2, "frequency": 2},
        )

        self.assertEqual(result["trip_id"].tolist(), ["regular"])

    def test_terminal_stop_is_not_a_departure(self) -> None:
        day = date(2026, 11, 11)
        trips = pd.DataFrame({"trip_id": ["001"], "route_id": ["R1"]})
        stop_times = pd.DataFrame({
            "trip_id": ["001", "001"], "stop_id": ["S1", "S2"],
            "stop_sequence": [1, 2], "departure_time": ["10:00:00", "10:10:00"],
            "pickup_type": [0, 0],
        })

        result = calendar_day_departures(
            stop_times, {day: trips}, day, set(), {"001": 2}
        )

        self.assertEqual(result["stop_id"].tolist(), ["S1"])

    def test_gtfs_time_conversion_preserves_overnight_hours(self) -> None:
        times = pd.Series(["25:30:00", "96:15:00", None])
        self.assertEqual(gtfs_time_to_seconds(times).iloc[0], 91_800)
        self.assertEqual(gtfs_time_to_seconds(times).iloc[1], 346_500)
        self.assertTrue(pd.isna(gtfs_time_to_seconds(times).iloc[2]))
        with self.assertRaisesRegex(ValueError, "valid GTFS"):
            gtfs_time_to_seconds(pd.Series(["25:60:00"]))

    def test_departure_date_supports_more_than_two_days(self) -> None:
        day = date(2026, 11, 11)
        service_date = day - timedelta(days=4)
        trips = pd.DataFrame({"trip_id": ["long"], "route_id": ["R1"]})
        stop_times = pd.DataFrame({
            "trip_id": ["long", "long"], "stop_id": ["S1", "S2"],
            "stop_sequence": [1, 2],
            "departure_time": ["96:15:00", "96:30:00"],
            "pickup_type": [0, 0],
        })

        result = calendar_day_departures(
            stop_times, {service_date: trips}, day, set(), {"long": 2}
        )

        self.assertEqual(result["stop_id"].tolist(), ["S1"])
        self.assertEqual(result["departure_date"].dt.date.tolist(), [day])
        self.assertEqual(scan_stop_times([stop_times]), (4, {"long": 2}))


if __name__ == "__main__":
    unittest.main()

"""Tests for filtering trips and stop times for an operating service."""

import unittest

import pandas as pd

from src.transform import (
    filter_stop_times_by_trip,
    filter_trips_by_service,
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


if __name__ == "__main__":
    unittest.main()

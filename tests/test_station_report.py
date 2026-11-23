"""Small station-grouping and hourly-count examples."""

import unittest
from unittest.mock import patch

import pandas as pd
import requests

from src.station_report import StationReport, load_swiss_border, swiss_stations


class StationReportTests(unittest.TestCase):
    BORDER = [[[[6, 45], [9, 45], [9, 48], [6, 48], [6, 45]]]]

    def test_child_stops_share_parent_station(self) -> None:
        stops = pd.DataFrame({
            "stop_id": ["platform-a", "platform-b", "station", "standalone"],
            "stop_name": ["A", "B", "Central", "Village"],
            "stop_lat": [47.0, 47.0, 47.0, 46.0],
            "stop_lon": [8.0, 8.0, 8.0, 7.0],
            "parent_station": ["station", "station", None, None],
        })
        report = StationReport(stops, self.BORDER)
        report.add(pd.DataFrame({
            "stop_id": ["platform-a", "platform-b", "standalone"],
            "departure_seconds": [8 * 3600, 25 * 3600, 9 * 3600],
        }))

        self.assertEqual(report.counts, {"station": 2, "standalone": 1})
        self.assertEqual(report.hourly[("station", 8)], 1)
        self.assertEqual(report.hourly[("station", 1)], 1)

    def test_foreign_origin_is_excluded_before_counting(self) -> None:
        stops = pd.DataFrame({
            "stop_id": ["swiss", "foreign"],
            "stop_name": ["Swiss origin", "Foreign origin"],
            "stop_lat": [47.0, 47.0], "stop_lon": [8.0, 10.0],
            "parent_station": [None, None],
        })
        report = StationReport(stops, self.BORDER)
        report.add(pd.DataFrame({
            "stop_id": ["swiss", "foreign"],
            "departure_seconds": [8 * 3600, 9 * 3600],
        }))
        self.assertEqual(report.counts, {"swiss": 1})
        self.assertEqual(report.hourly, {("swiss", 8): 1})

    def test_unknown_parent_is_rejected(self) -> None:
        stops = pd.DataFrame({
            "stop_id": ["platform"], "stop_name": ["Platform"],
            "stop_lat": [47.0], "stop_lon": [8.0],
            "parent_station": ["missing"],
        })
        with self.assertRaisesRegex(ValueError, "unknown parent"):
            StationReport(stops, self.BORDER)

    def test_unavailable_border_is_not_replaced(self) -> None:
        with patch("src.station_report.requests.get",
                   side_effect=requests.ConnectionError("offline")) as get:
            with self.assertRaises(requests.ConnectionError):
                load_swiss_border()
        self.assertEqual(get.call_args.kwargs["params"]["searchText"], "CH")

    def test_swiss_stations_excludes_foreign_points_and_holes(self) -> None:
        border = [[
            [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]],
            [[1, 1], [2, 1], [2, 2], [1, 2], [1, 1]],
        ]]
        stations = pd.DataFrame({
            "stop_lon": [3, 5, 1.5], "stop_lat": [3, 3, 1.5],
        })
        self.assertEqual(swiss_stations(stations, border).index.tolist(), [0])

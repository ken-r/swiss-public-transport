"""Small examples of GTFS weekly service and exception rules."""

from datetime import date
import unittest

import pandas as pd

from src.calendar import get_operating_services_at_date


class OperatingServicesTests(unittest.TestCase):
    def test_weekday_and_validity_period(self) -> None:
        calendar = pd.DataFrame({
            "service_id": ["wednesday", "not on wednesday", "expired"],
            "wednesday": [1, 0, 1],
            "start_date": ["20251213"] * 3,
            "end_date": ["20261212", "20261212", "20260930"],
        })
        exceptions = pd.DataFrame(columns=["service_id", "date", "exception_type"])

        test_date_wednesday = date(2026, 10, 21)

        self.assertEqual(
            get_operating_services_at_date(calendar, exceptions, test_date_wednesday),
            {"wednesday"},
        )

    def test_added_removed_and_exception_only_services(self) -> None:
        calendar = pd.DataFrame({
            "service_id": ["regular", "removed"],
            "wednesday": [1, 1],
            "start_date": ["20260101"] * 2,
            "end_date": ["20261212"] * 2,
        })
        # We add one service, remove the service that was named 'removed', and an addtional service is
        # added, but on another date.
        exceptions = pd.DataFrame({
            "service_id": ["added", "removed", "other_date"],
            "date": ["20261021", "20261021", "20261022"],
            "exception_type": [1, 2, 1],
        })

        self.assertEqual(
            get_operating_services_at_date(calendar, exceptions, date(2026, 10, 21)),
            {"regular", "added"},
            "The regular and added services should operate whereas the removed service should not."
        )
        self.assertEqual(
            get_operating_services_at_date(None, exceptions, date(2026, 10, 21)),
            {"added"},
            "With calendar=None, only exceptions added for this date should operate."
        )


if __name__ == "__main__":
    unittest.main()

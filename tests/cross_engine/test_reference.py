"""Completely offline checks of the same synthetic cross-engine reference."""
import unittest
from datetime import datetime
from decimal import Decimal

from cross_engine.fixture import fixture, expected_reports, WINDOWS, EXTRA_ORDERS, normal_amount


class ParityReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.customers, cls.orders = fixture()
        cls.report = expected_reports(cls.orders)

    def test_common_fixture_is_deterministic_and_duplicate_free(self):
        self.assertEqual(26, len(self.customers))
        self.assertEqual(260, len(self.orders))
        self.assertEqual(260, len({r[0] for r in self.orders}))
        self.assertTrue(all(r[1] in {c[0] for c in self.customers} for r in self.orders))

    def test_all_window_boundaries_are_half_open(self):
        self.assertEqual(set(WINDOWS), {"february_leap", "leap_day", "march", "full_2024", "empty"})
        self.assertEqual(self.report["by_window"]["empty"], [])
        self.assertEqual(self.report["by_window"]["february_leap"],
                         self.report["original_monthly_february"])
        self.assertTrue(all(datetime.fromisoformat(a) < datetime.fromisoformat(b)
                            for a, b in WINDOWS.values()))

    def test_leap_day_end_exclusive_and_void_excluded(self):
        feb = {int(c): Decimal(v) for c, v in self.report["original_monthly_february"]}
        self.assertGreaterEqual(feb[25], Decimal("100.00"))
        self.assertEqual(feb[26], Decimal("100.00"))
        self.assertIn((253, 25, "2024-03-01T00:00:00", "COMPLETED", "0.01"), EXTRA_ORDERS)
        self.assertNotIn(["26", "10099.99"], self.report["original_monthly_february"])

    def test_tie_break_secondary_customer_key_and_precision(self):
        all_months = self.report["by_month_customer"]
        self.assertTrue(any(month == "2024-02" and val == "100.00"
                            for month, id_, val in all_months if id_ == "26"))
        self.assertEqual(normal_amount(Decimal("0.01")), "0.01")
        with self.assertRaises(ValueError):
            normal_amount("NaN")
        with self.assertRaises(ValueError):
            normal_amount("1.001")

    def test_reference_checks_have_unique_group_keys(self):
        for name, result in self.report["by_window"].items():
            self.assertEqual(len(result), len({x[0] for x in result}), name)
        self.assertEqual(len(self.report["by_month_customer"]),
                         len({(x[0], x[1]) for x in self.report["by_month_customer"]}))


if __name__ == "__main__":
    unittest.main()

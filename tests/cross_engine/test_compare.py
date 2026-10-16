"""Reject synthetic-only reconciliation records that omit evidence or hide gaps."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from cross_engine.fixture import fixture, expected_reports, WINDOWS
from cross_engine.compare import reconcile


class ReconcileTests(unittest.TestCase):
    def make_fixture(self, root):
        cust,orders=fixture()
        ref=expected_reports(orders)
        import hashlib
        sha=hashlib.sha256(json.dumps({"customers":cust,"orders":orders},separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
        outputs=[]
        for name in ("sqlserver","oracle"):
            datum={
                "engine":name,"fixture_sha256":sha,
                "database_version_and_settings":{"engine_version":"synthetic unit-test version"},
                "counts":{"customers":26,"orders":260,"completed":ref["completed_order_count"]},
                "round_trip_all_source_rows":True,"transaction_rollback":True,
                "empty_string_behavior":"EMPTY" if name=="sqlserver" else "NULL",
                "results":{key:copy.deepcopy(ref[key])
                           for key in ("original_monthly_february","original_top_ten","by_window","by_month_customer")},
            }
            p=Path(root)/(name+".json")
            p.write_text(json.dumps(datum),encoding="utf-8")
            outputs.append((p,datum))
        return outputs

    def test_valid_reference_agrees_and_documents_nonparity(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=self.make_fixture(root)
            result=reconcile(a[0],b[0])
            self.assertTrue(result["tests"]["cross_engine_full_result_equivalence"])
            self.assertEqual(result["source"]["orders"],260)
            self.assertEqual(result["engines"]["oracle"]["empty_string_behavior"],"NULL")
            self.assertIn("Oracle 12.1.0.2 runtime validation", result["excluded"])

    def test_rejects_one_penny_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=self.make_fixture(root)
            b[1]["results"]["original_monthly_february"][0][1]="1.01"
            b[0].write_text(json.dumps(b[1]),encoding="utf-8")
            with self.assertRaises(ValueError):
                reconcile(a[0],b[0])

    def test_rejects_falsely_identical_null_behavior(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=self.make_fixture(root)
            b[1]["empty_string_behavior"]="EMPTY"
            b[0].write_text(json.dumps(b[1]),encoding="utf-8")
            with self.assertRaises(ValueError):
                reconcile(a[0],b[0])

    def test_rejects_missing_window_and_rollback(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=self.make_fixture(root)
            a[1]["results"]["by_window"].pop("leap_day")
            a[0].write_text(json.dumps(a[1]),encoding="utf-8")
            with self.assertRaises(ValueError):
                reconcile(a[0],b[0])
            a[1]["results"]["by_window"]["leap_day"]=expected_reports(fixture()[1])["by_window"]["leap_day"]
            a[1]["transaction_rollback"]=False
            a[0].write_text(json.dumps(a[1]),encoding="utf-8")
            with self.assertRaises(ValueError):
                reconcile(a[0],b[0])


if __name__ == "__main__":
    unittest.main()

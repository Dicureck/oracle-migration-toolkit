import csv
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from migration_lab.reconcile import reconcile
from migration_lab.cli import main


def _csv(path, columns, rows):
    with path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


class ReconciliationTests(unittest.TestCase):
    def test_same_rows_different_order_and_column_order(self):
        with TemporaryDirectory() as temp:
            a,b=Path(temp)/'a.csv',Path(temp)/'b.csv'
            _csv(a,['id','revenue'],[['1','12.00'],['2','9.00']])
            _csv(b,['revenue','id'],[['9.00','2'],['12.00','1']])
            self.assertTrue(reconcile(a,b)['matching'])

    def test_duplicate_count_is_detected(self):
        with TemporaryDirectory() as temp:
            a,b=Path(temp)/'a.csv',Path(temp)/'b.csv'
            _csv(a,['id'],[['1'],['1'],['2']])
            _csv(b,['id'],[['1'],['2']])
            report = reconcile(a,b)
            self.assertFalse(report['matching'])
            self.assertEqual(report['missing_rows_total'],1)
            self.assertEqual(report['missing_in_right'][0]['count'],1)

    def test_schema_mismatch_rejected(self):
        with TemporaryDirectory() as temp:
            a,b=Path(temp)/'a.csv',Path(temp)/'b.csv'
            _csv(a,['id'],[['1']])
            _csv(b,['name'],[['1']])
            with self.assertRaises(ValueError): reconcile(a,b)

    def test_cli_exit_mismatch(self):
        with TemporaryDirectory() as temp, redirect_stdout(StringIO()):
            a,b=Path(temp)/'a.csv',Path(temp)/'b.csv'
            _csv(a,['id'],[['1'],['2']])
            _csv(b,['id'],[['1']])
            self.assertEqual(main(['reconcile',str(a),str(b)]), 1)

    def test_malformed_rows(self):
        with TemporaryDirectory() as temp:
            a,b=Path(temp)/'a.csv',Path(temp)/'b.csv'
            a.write_text('id,value\n1\n',encoding='utf-8')
            b.write_text('id,value\n1,x\n',encoding='utf-8')
            with self.assertRaises(ValueError): reconcile(a,b)

if __name__ == '__main__': unittest.main()

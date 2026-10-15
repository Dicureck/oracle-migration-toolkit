import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from migration_lab.contracts import monthly_revenue, top_customers, verify_contracts


class ContractTests(unittest.TestCase):
    def test_reference_contracts(self):
        source = Path(__file__).resolve().parents[1] / 'examples' / 'contracts.json'
        report = verify_contracts(source)
        self.assertEqual((report['passed'], report['failed']), (2, 0))

    def test_start_end_exclusion(self):
        c={'start_inclusive':'2024-02-01T00:00:00', 'end_exclusive':'2024-03-01T00:00:00',
           'records':[{'customer_id':1,'created_at':'2024-03-01T00:00:00','status':'COMPLETED','amount':'3.00'}]}
        self.assertEqual(monthly_revenue(c), [])

    def test_noncompleted_exclusion(self):
        c={'start_inclusive':'2024-02-01T00:00:00', 'end_exclusive':'2024-03-01T00:00:00',
           'records':[{'customer_id':1,'created_at':'2024-02-02T00:00:00','status':'VOID','amount':'3.00'}]}
        self.assertEqual(monthly_revenue(c), [])

    def test_money_uses_decimal(self):
        c={'start_inclusive':'2024-02-01T00:00:00', 'end_exclusive':'2024-03-01T00:00:00',
           'records':[{'customer_id':1,'created_at':'2024-02-02T00:00:00','status':'COMPLETED','amount':v} for v in ['0.10','0.20']]}
        self.assertEqual(monthly_revenue(c)[0]['revenue'], '0.30')

    def test_top_n_tie_break(self):
        c={'limit':2,'records':[{'customer_id':2,'revenue':'100.00'},{'customer_id':1,'revenue':'100.00'},{'customer_id':3,'revenue':'90'}]}
        self.assertEqual(top_customers(c), [1,2])

    def test_negative_limit_rejected(self):
        with self.assertRaises(ValueError): top_customers({'limit':-1,'records':[]})

    def test_wrong_expected_is_reported(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / 'failed.json'
            path.write_text(json.dumps({'contracts':[{'name':'X','kind':'top_customers','limit':1,'records':[{'customer_id':1,'revenue':'3'}],'expected':[2]}]}))
            self.assertEqual(verify_contracts(path)['failed'], 1)


if __name__ == '__main__': unittest.main()

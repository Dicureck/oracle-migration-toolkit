import csv
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from migration_lab.cli import main
from migration_lab.synthetic import generate


class SyntheticCliTests(unittest.TestCase):
    def test_generator_determinism(self):
        with TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            generate(a,10,30,42); generate(b,10,30,42)
            self.assertEqual((a/'orders.csv').read_bytes(),(b/'orders.csv').read_bytes())
            self.assertEqual((a/'customers.csv').read_bytes(),(b/'customers.csv').read_bytes())

    def test_generator_foreign_keys(self):
        with TemporaryDirectory() as tmp:
            dst=Path(tmp)/'run'
            generate(dst,5,100,1)
            with (dst/'orders.csv').open() as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows), 100)
            self.assertTrue(all(1 <= int(x['customer_id']) <= 5 for x in rows))

    def test_generator_refuses_overwrite(self):
        with TemporaryDirectory() as tmp:
            dst=Path(tmp)/'run'
            generate(dst,3,5,2)
            with self.assertRaises(FileExistsError): generate(dst,3,5,2)

    def test_generator_invalid_count(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): generate(Path(tmp)/'run',0,10,2)

    def test_cli_creates_reports(self):
        base=Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as tmp, redirect_stdout(StringIO()):
            d=Path(tmp)
            self.assertEqual(main(['assess',str(base/'sql/sqlserver'),'--output',str(d/'scan.json')]),0)
            self.assertEqual(main(['plan',str(base/'examples/inventory.json'),'--output',str(d/'plan.json')]),0)
            self.assertEqual(main(['verify',str(base/'examples/contracts.json'),'--output',str(d/'contracts.json')]),0)
            self.assertTrue((d/'scan.json').exists())
            self.assertEqual(json.loads((d/'contracts.json').read_text())['failed'],0)


if __name__ == '__main__': unittest.main()

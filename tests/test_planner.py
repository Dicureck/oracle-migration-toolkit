import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from migration_lab.planner import Step, load_inventory, make_plan, as_dict


class PlannerTests(unittest.TestCase):
    def test_valid_stable_order(self):
        inp = [Step('C','view',('B',)), Step('B','table',('A',)), Step('A','table',())]
        self.assertEqual([x.name for x in make_plan(inp)], ['A','B','C'])

    def test_missing_dependency_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing dependency'):
            make_plan([Step('a','view',('x',))])

    def test_cycle_rejected(self):
        with self.assertRaisesRegex(ValueError,'Circular'):
            make_plan([Step('a','view',('b',)), Step('b','view',('a',))])

    def test_duplicate_names_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate object'):
            make_plan([Step('a','table',()), Step('a','view',())])

    def test_inventory_file(self):
        inventory = Path(__file__).resolve().parents[1] / 'examples' / 'inventory.json'
        report = as_dict(make_plan(load_inventory(inventory)))
        self.assertEqual(report['object_count'], 8)
        self.assertEqual(report['manual_review_count'], 3)
        self.assertEqual(report['plan_type'], 'review_only_not_executable')

    def test_inventory_invalid_type(self):
        with TemporaryDirectory() as temp:
            target = Path(temp) / 'bad.json'
            target.write_text('{"objects":[{"name":"X","type":"not_sql"}]}')
            with self.assertRaises(ValueError): load_inventory(target)


if __name__ == '__main__': unittest.main()

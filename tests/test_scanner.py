import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from migration_lab.scanner import analyze_text, assess, mask_non_code


class ScannerTests(unittest.TestCase):
    def test_detect_top_and_dateadd(self):
        hits = analyze_text("SELECT TOP (10) * FROM t WHERE d < DATEADD(month,1,d0);")
        self.assertEqual({x['rule'] for x in hits}, {'TOP', 'DATEADD'})

    def test_comments_strings_masked(self):
        src = "-- DATEDIFF(day,a,b)\nSELECT 'TOP 12 -- DATEADD' AS x; /* ISNULL(x,0) */\nSELECT GETDATE();"
        self.assertEqual([x['rule'] for x in analyze_text(src)], ['GETDATE'])

    def test_nested_comment_masked(self):
        src = "/* foo /* TOP (1) */ ISNULL(x,0) */ SELECT TOP 2 * FROM t"
        self.assertEqual([x['rule'] for x in analyze_text(src)], ['TOP'])

    def test_escaped_quotes_masked(self):
        src = "SELECT 'it''s DATEDIFF(day,x,y)' AS text, ISNULL(c,0) AS c"
        self.assertEqual([x['rule'] for x in analyze_text(src)], ['ISNULL'])

    def test_source_locations(self):
        hits = analyze_text("SELECT 1;\n SELECT TOP 2 * FROM t;")
        self.assertEqual((hits[0]['line'], hits[0]['column']), (2, 9))

    def test_mask_preserves_offsets(self):
        sql = "SELECT 'abc\nTOP 2' /* text */ TOP 4 FROM T"
        masked = mask_non_code(sql)
        self.assertEqual(len(sql), len(masked))
        self.assertEqual(sql.count('\n'), masked.count('\n'))

    def test_assess_directory_sorted(self):
        with TemporaryDirectory() as temp:
            p = Path(temp)
            (p / 'b.sql').write_text('SELECT GETDATE();')
            (p / 'a.sql').write_text('SELECT TOP 3 * FROM x;')
            report = assess(p)
            self.assertEqual(report['files_scanned'], 2)
            self.assertEqual({x['file'] for x in report['findings']}, {'a.sql','b.sql'})

    def test_no_sql_raises(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                assess(Path(temp))


if __name__ == '__main__': unittest.main()

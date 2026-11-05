import pathlib
import tempfile
import unittest
import sys
from datetime import datetime, timezone
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from log_export import export_logs

class ExportTests(unittest.TestCase):
    def test_never_overwrites_existing_export(self):
        with tempfile.TemporaryDirectory() as d:
            t = datetime(2026, 1, 1, tzinfo=timezone.utc)
            first = export_logs(pathlib.Path(d), "first", t)
            second = export_logs(pathlib.Path(d), "second", t)
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_text(), "first")
            self.assertEqual(second.read_text(), "second")

if __name__ == "__main__":
    unittest.main()

"""Release gate tests run without a macOS build."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from release_gate import checksum, validate_tag


class ReleaseGateTests(unittest.TestCase):
    def test_accept_beta_only(self):
        validate_tag("v0.1.0-beta.1")
        for tag in ("v0.1.0", "v1.0.0-rc.1", "v1.0.0-beta.x", "release"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                validate_tag(tag)

    def test_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.dmg"
            path.write_bytes(b"test artifact")
            self.assertEqual(checksum(path), hashlib.sha256(b"test artifact").hexdigest())
            path.write_bytes(b"")
            with self.assertRaises(ValueError):
                checksum(path)


if __name__ == "__main__":
    unittest.main()

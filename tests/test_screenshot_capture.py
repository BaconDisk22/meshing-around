"""Headless contract tests for the macOS screenshot capture helper."""
from pathlib import Path
import importlib.util
import tempfile
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "capture_dashboard", ROOT / "desktop" / "capture_dashboard.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ScreenshotCaptureContract(unittest.TestCase):
    def test_non_macos_returns_unavailable(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, patch.object(MODULE.sys, "platform", "linux"):
            self.assertEqual(MODULE.capture(Path(tmp) / "capture.png"), 2)

    def test_capture_entrypoint_exists(self):
        self.assertTrue(callable(MODULE.capture))
        self.assertTrue((ROOT / "desktop" / "launcher.py").is_file())


    def test_valid_png_header(self):
        header = bytes.fromhex("89504e470d0a1a0a") + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 1280, 720)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.png"
            path.write_bytes(header)
            self.assertTrue(MODULE.valid_png(path))

    def test_reject_invalid_png_and_small_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.png"
            path.write_bytes(b"not a PNG")
            self.assertFalse(MODULE.valid_png(path))
            path.write_bytes(bytes.fromhex("89504e470d0a1a0a") + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 320, 240))
            self.assertFalse(MODULE.valid_png(path))
            self.assertFalse(MODULE.valid_png(Path(tmp) / "missing.png"))


if __name__ == "__main__":
    unittest.main()

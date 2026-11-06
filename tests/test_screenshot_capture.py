"""Headless contract tests for the macOS screenshot capture helper."""
from pathlib import Path
import importlib.util
import tempfile
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


if __name__ == "__main__":
    unittest.main()

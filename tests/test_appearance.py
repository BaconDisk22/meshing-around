"""Headless theme persistence tests."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "desktop"))
from appearance import DEFAULT_THEME, THEMES, load_theme, save_theme


class ThemeTests(unittest.TestCase):
    def test_all_five_palettes_have_required_colors(self):
        self.assertEqual(len(THEMES), 5)
        for colors in THEMES.values():
            for key in ("bg", "panel", "sidebar", "fg", "muted", "accent", "input"):
                self.assertRegex(colors[key], r"^#[0-9a-fA-F]{6}$")

    def test_default_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "prefs.json"
            self.assertEqual(load_theme(path), DEFAULT_THEME)
            save_theme("Dusk", path)
            self.assertEqual(load_theme(path), "Dusk")
            path.write_text('{"theme":"invalid"}', encoding="utf-8")
            self.assertEqual(load_theme(path), DEFAULT_THEME)

    def test_rejects_unknown_theme(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_theme("Unknown", pathlib.Path(folder) / "prefs.json")


if __name__ == "__main__":
    unittest.main()

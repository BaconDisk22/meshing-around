"""Headless checks for the bundled macOS runtime layout."""
from pathlib import Path
import sys


def verify_bundle(bundle: Path) -> None:
    resources = bundle / "Contents" / "Resources"
    internal = bundle / "Contents" / "Frameworks"
    if not (bundle / "Contents" / "MacOS" / "Meshing Around").is_file():
        raise FileNotFoundError("Missing desktop executable")
    if not list(bundle.rglob("meshing-around-bot")):
        raise FileNotFoundError("Missing bundled bot executable")
    if not list(bundle.rglob("config.template")):
        raise FileNotFoundError("Missing configuration template")
    if not list(bundle.rglob("mesh_bot.py")):
        raise FileNotFoundError("Missing bot source payload")
    print("BUNDLE_LAYOUT_OK")


if __name__ == "__main__":
    verify_bundle(Path(sys.argv[1]))

"""Stage only runtime source resources for the macOS desktop bundle.

Avoid recursively packaging tests, CI, caches, and generated build outputs.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "staging" / "payload"
ITEMS = ("mesh_bot.py", "config.template", "modules", "data", "etc", "script", "logs")


def stage() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ITEMS:
        source = ROOT / name
        if not source.exists():
            continue
        destination = DEST / name
        if source.is_dir():
            shutil.copytree(
                source, destination, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
            )
        else:
            shutil.copy2(source, destination)
    if not (DEST / "mesh_bot.py").is_file():
        raise FileNotFoundError("Bot source missing from staging payload")
    if not (DEST / "config.template").is_file():
        raise FileNotFoundError("Config template missing from staging payload")


if __name__ == "__main__":
    stage()

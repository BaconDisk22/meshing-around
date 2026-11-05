"""Preflight checks before launching the Meshtastic bot subprocess."""
from pathlib import Path


def check_paths(root: Path, bot: Path) -> None:
    root, bot = Path(root), Path(bot)
    if not root.is_dir():
        raise FileNotFoundError(f"Application folder missing: {root}")
    if not bot.is_file():
        raise FileNotFoundError(f"Bot script missing: {bot}")
    if not (root / "config.ini").is_file():
        raise FileNotFoundError("Radio configuration missing. Save radio settings first.")

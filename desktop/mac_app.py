"""Frozen macOS entry point with first-run configuration and smoke validation."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

from dashboard import launch


def locate_bot(bundle: Path) -> Path:
    """PyInstaller can place added binaries in a nested internal directory."""
    candidates = [bundle / "meshing-around-bot", bundle / "Contents" / "Frameworks" / "meshing-around-bot"]
    candidates.extend(bundle.rglob("meshing-around-bot"))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise FileNotFoundError("Bundled Meshtastic bot executable missing")


def prepare_workspace(bundle: Path, workspace: Path) -> tuple[Path, Path]:
    source = bundle / "payload"
    if not source.is_dir():
        raise FileNotFoundError("Application payload missing")
    bot = locate_bot(bundle)
    workspace.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = workspace / item.name
        if destination.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)
    # The bot reads config.ini, not config.template. Never replace user settings.
    config = workspace / "config.ini"
    template = workspace / "config.template"
    if not config.exists():
        if not template.is_file():
            raise FileNotFoundError("Bundled config.template missing")
        shutil.copy2(template, config)
    return workspace, bot


def main() -> None:
    if not getattr(sys, "frozen", False):
        raise RuntimeError("mac_app.py is intended for packaged execution")
    bundle = Path(sys._MEIPASS)
    workspace = Path.home() / "Library" / "Application Support" / "MeshingAround" / "runtime"
    workspace, bot = prepare_workspace(bundle, workspace)
    if "--self-test" in sys.argv:
        print(f"MAC_APP_SELF_TEST_OK: {bot.name}", flush=True)
        return
    from launcher import check_tcp
    launch(workspace, bot, check_tcp)


if __name__ == "__main__":
    main()

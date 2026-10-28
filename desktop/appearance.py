"""Desktop appearance palettes and persistent user preferences."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

DEFAULT_THEME = "Midnight Cyan"
THEMES = {
    "Midnight Cyan": {"bg": "#0d1420", "panel": "#182434", "sidebar": "#111d2b", "fg": "#e8f3ff", "muted": "#a3b6c9", "accent": "#28d9e8", "input": "#233447"},
    "Futuristic Neon": {"bg": "#100e1c", "panel": "#211a36", "sidebar": "#17122b", "fg": "#f6efff", "muted": "#bdb0d6", "accent": "#d05cff", "input": "#302548"},
    "Mocha Mousse": {"bg": "#211b19", "panel": "#352a26", "sidebar": "#2b211d", "fg": "#f5e9dd", "muted": "#c8b3a5", "accent": "#e0ad83", "input": "#483832"},
    "Fun & Vibrant": {"bg": "#15222b", "panel": "#203744", "sidebar": "#192c38", "fg": "#f6fcff", "muted": "#b4d0db", "accent": "#ffb74d", "input": "#2a4856"},
    "Dusk": {"bg": "#1d1c30", "panel": "#302b47", "sidebar": "#26233b", "fg": "#f1eafb", "muted": "#c3b8d7", "accent": "#b39bfa", "input": "#403958"},
}


def preferences_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "MeshingAround" / "desktop.json"


def load_theme(path: Path | None = None) -> str:
    target = path if path is not None else preferences_path()
    try:
        value = json.loads(target.read_text(encoding="utf-8")).get("theme")
    except (OSError, ValueError, AttributeError):
        return DEFAULT_THEME
    return value if value in THEMES else DEFAULT_THEME


def save_theme(theme: str, path: Path | None = None) -> None:
    if theme not in THEMES:
        raise ValueError("Unknown theme")
    target = path if path is not None else preferences_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False,
                                         encoding="utf-8") as handle:
            temp = handle.name
            json.dump({"theme": theme}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)

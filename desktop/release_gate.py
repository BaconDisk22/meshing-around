"""Beta release gate for Intel Mac artifacts.

Release builds must have the expected DMG and must not publish stable tags.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re


def validate_tag(tag: str) -> None:
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+-beta\.[0-9]+", tag):
        raise ValueError("Only versioned beta tags (vX.Y.Z-beta.N) are permitted")


def checksum(path: Path) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Missing or empty release file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--dmg", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validate_tag(args.tag)
    sha = checksum(args.dmg)
    args.output.write_text(f"{sha}  {args.dmg.name}\n", encoding="utf-8")
    print(f"BETA_RELEASE_GATE_OK: {args.tag}")


if __name__ == "__main__":
    main()

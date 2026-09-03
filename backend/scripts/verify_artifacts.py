"""Verify frozen CORTANA release artifacts against MANIFEST_SHA256.json."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "MANIFEST_SHA256.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    for relative_path, expected in manifest.items():
        path = PROJECT_ROOT / relative_path
        if not path.is_file():
            failures.append(f"missing: {relative_path}")
            continue
        if path.stat().st_size != expected["size_bytes"]:
            failures.append(f"size mismatch: {relative_path}")
            continue
        if sha256_file(path) != expected["sha256"]:
            failures.append(f"sha256 mismatch: {relative_path}")

    if failures:
        print("Artifact verification: FAIL")
        print("\n".join(failures))
        return 1

    print(f"Artifact verification: PASS ({len(manifest)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

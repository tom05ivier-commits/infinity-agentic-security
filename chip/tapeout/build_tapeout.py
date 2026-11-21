# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Bangun paket serah-terima chip: salinan bersih + manifest + checksum + arsip.

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CHIP = ROOT / "chip"
TAPEOUT = CHIP / "tapeout"
PACKAGE = TAPEOUT / "package"
ARCHIVE = TAPEOUT / "infinity-mini-chip-tapeout-v1.tar.gz"

SOURCES: tuple[tuple[str, str], ...] = (
    ("README.md", "README.md"),
    ("constraints.sdc", "constraints.sdc"),
    ("design_spec.json", "design_spec.json"),
    ("../README.md", "docs/README.md"),
    ("../rtl", "rtl"),
    ("../synth", "synth"),
    ("../tb", "tb"),
    ("../reports", "reports"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True, exist_ok=True)

    for source, target in SOURCES:
        src = TAPEOUT / source
        if not src.exists():
            continue
        dst = PACKAGE / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    # Hapus artefak simulasi sementara.
    for path in PACKAGE.rglob("*.vvp"):
        path.unlink()
    for path in PACKAGE.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)

    entries: list[dict[str, Any]] = []
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file():
            entries.append(
                {
                    "path": str(path.relative_to(PACKAGE)),
                    "size": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )

    manifest = {
        "name": "Infinity Mini Chip — design handoff",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "fabrication_status": "NOT_READY",
        "reason": "PDK, P&R, timing closure, DRC/LVS, GDSII belum tersedia",
        "files": len(entries),
        "total_bytes": sum(item["size"] for item in entries),
        "entries": entries,
    }
    (PACKAGE / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (PACKAGE / "CHECKSUMS.sha256").write_text(
        "\n".join(f"{item['sha256']}  {item['path']}" for item in entries) + "\n",
        encoding="utf-8",
    )

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with tarfile.open(ARCHIVE, "w:gz") as tar:
        tar.add(PACKAGE, arcname="infinity-mini-chip-tapeout-v1")

    return {
        "status": "OK",
        "package": str(PACKAGE),
        "archive": str(ARCHIVE),
        "files": len(entries),
        "total_bytes": manifest["total_bytes"],
        "archive_bytes": ARCHIVE.stat().st_size,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build chip tapeout package")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Paket: {result['package']}")
        print(f"Arsip: {result['archive']} ({result['archive_bytes']} byte)")
        print(f"Berkas: {result['files']}")


if __name__ == "__main__":
    main()

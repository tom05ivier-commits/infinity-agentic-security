# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Pemantau integritas berkas kritis menggunakan SHA-256.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..common.config import LAB_ROOT, SECURITY_ROOT

BASELINE_PATH = SECURITY_ROOT / "reports" / "integrity_baseline.json"


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


class IntegrityMonitor:
    """Membandingkan keadaan berkas kritis dengan baseline hash."""

    def __init__(
        self,
        paths: list[Path] | None = None,
        baseline_path: Path | None = None,
    ) -> None:
        self.paths = paths or self.default_paths()
        self.baseline_path = Path(baseline_path) if baseline_path else BASELINE_PATH

    @staticmethod
    def default_paths() -> list[Path]:
        root = SECURITY_ROOT.parent
        candidates = [
            root / "LICENSE",
            root / "README.md",
            root / "surat-izin-keamanan.md",
            root / "surat-kuasa-tandatangan.md",
            root / "system" / "core.py",
            root / "security" / "security_cli.py",
            LAB_ROOT,
        ]
        return [path for path in candidates if path.exists()]

    def snapshot(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for path in self.paths:
            try:
                if path.is_dir():
                    for child in sorted(path.rglob("*")):
                        if child.is_file():
                            result[str(child)] = _hash_file(child)
                elif path.is_file():
                    result[str(path)] = _hash_file(path)
            except OSError:
                continue
        return result

    def create_baseline(self) -> Path:
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "license": "Tom05ivier-commits-1.0",
            "files": self.snapshot(),
        }
        self.baseline_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return BASELINE_PATH

    def check(self) -> dict[str, Any]:
        """Kembalikan berkas baru, diubah, atau hilang."""
        if not self.baseline_path.exists():
            self.create_baseline()
        try:
            baseline = json.loads(self.baseline_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            baseline = {"files": {}}
        old: dict[str, str] = baseline.get("files", {})
        current = self.snapshot()

        added = sorted(set(current) - set(old))
        removed = sorted(set(old) - set(current))
        modified = sorted(
            key for key in set(current) & set(old) if current[key] != old[key]
        )
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "changed": bool(added or removed or modified),
            "total": len(current),
        }

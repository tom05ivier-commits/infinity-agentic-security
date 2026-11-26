#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Terapkan ctl 100M ke semua model provider tom05 secara idempoten.

Perubahan ini HANYA deklarasi batas kompaksi di klien/OpenCode. Bukan
kapasitas fisik, bukan klaim model baru, dan tidak mengubah lisensi/identitas
model pihak ketiga yang diteruskan (proxied) oleh provider lokal tom05.

Pemakaian::

    python3 system/tom05_ctl_all.py            # terapkan (backup otomatis)
    python3 system/tom05_ctl_all.py --verify   # periksa saja, tanpa menulis
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OPENCODE_CONFIG = Path(
    os.environ.get(
        "TOM05_OPENCODE_CONFIG",
        "/root/.config/opencode/opencode.json",
    )
)
PROVIDER_CATALOG = ROOT / "config" / "tom05-provider-models.json"
LOCAL_CATALOG = ROOT / "config" / "tom05-models.json"

NOTE = (
    "Deklarasi batas konteks (ctl) untuk kompaksi klien/OpenCode, bukan "
    "kapasitas fisik dan bukan klaim atas model pihak ketiga; lisensi tetap "
    "pada pemilik masing-masing."
)


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(path: Path, data: dict[str, Any], stamp: str) -> str | None:
    """Tulis JSON dengan backup sekali dan mode izin yang sama."""
    backup: str | None = None
    mode = 0o600
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
        backup_path = path.with_name(f"{path.name}.before-ctl-all-{stamp}")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            backup = str(backup_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.ctl-all-{stamp}.tmp")
    temp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.chmod(temp, mode)
    os.replace(temp, path)
    return backup


def patch_opencode(data: dict[str, Any], ctl: int) -> dict[str, int]:
    models = data.setdefault("providers", {}).setdefault("tom05", {}).setdefault(
        "models", {}
    )
    if not isinstance(models, dict):
        raise ValueError("providers.tom05.models bukan objek")
    limit = {"context": ctl, "input": ctl}
    changed = 0
    for item in models.values():
        if isinstance(item, dict) and item.get("limit") != limit:
            item["limit"] = dict(limit)
            changed += 1
    return {"changed": changed, "total": len(models)}


def patch_provider_catalog(data: dict[str, Any], ctl: int, today: str) -> dict[str, int]:
    limit = {"context": ctl, "input": ctl}
    changed = 0
    for item in data.get("models", []):
        if not isinstance(item, dict):
            continue
        before = (
            item.get("ctl"),
            item.get("context_length"),
            item.get("limit"),
            item.get("declared_only"),
        )
        item["ctl"] = ctl
        item["context_length"] = ctl
        item["limit"] = dict(limit)
        item["declared_only"] = True
        after = (
            item.get("ctl"),
            item.get("context_length"),
            item.get("limit"),
            item.get("declared_only"),
        )
        changed += int(before != after)
    data["ctl"] = ctl
    data["declared_only"] = True
    data["ctl_note"] = NOTE
    data["ctl_updated"] = today
    return {"changed": changed, "total": len(data.get("models", []))}


def patch_local_catalog(data: dict[str, Any], ctl: int, today: str) -> dict[str, int]:
    changed = 0
    for item in data.get("models", []):
        if not isinstance(item, dict):
            continue
        if item.get("ctl") != ctl or item.get("declared_only") is not True:
            item["ctl"] = ctl
            item["declared_only"] = True
            changed += 1
    data["ctl"] = ctl
    data["ctl_note"] = NOTE
    data["ctl_updated"] = today
    provider = data.setdefault("capabilities", {}).setdefault("provider", {})
    provider["ctl"] = ctl
    provider["ctl_all_models"] = True
    return {"changed": changed, "total": len(data.get("models", []))}


def verify(ctl: int) -> dict[str, Any]:
    limit = {"context": ctl, "input": ctl}
    oc = _load(OPENCODE_CONFIG)
    oc_models = oc.get("providers", {}).get("tom05", {}).get("models", {})
    oc_ok = bool(oc_models) and all(
        isinstance(item, dict) and item.get("limit") == limit
        for item in oc_models.values()
    )
    pc = _load(PROVIDER_CATALOG)
    pc_models = [m for m in pc.get("models", []) if isinstance(m, dict)]
    pc_ok = bool(pc_models) and all(
        m.get("ctl") == ctl
        and m.get("context_length") == ctl
        and m.get("limit") == limit
        and m.get("declared_only") is True
        for m in pc_models
    )
    lc = _load(LOCAL_CATALOG)
    lc_models = [m for m in lc.get("models", []) if isinstance(m, dict)]
    lc_ok = bool(lc_models) and all(
        m.get("ctl") == ctl and m.get("declared_only") is True for m in lc_models
    )
    return {
        "status": "OK" if all((oc_ok, pc_ok, lc_ok)) else "GAGAL",
        "opencode": {"ok": oc_ok, "models": len(oc_models)},
        "provider_catalog": {"ok": pc_ok, "models": len(pc_models)},
        "local_catalog": {"ok": lc_ok, "models": len(lc_models)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ctl",
        type=int,
        default=int(os.environ.get("TOM05_CTL", "100000000")),
        help="nilai ctl yang dideklarasikan (default: 100000000)",
    )
    parser.add_argument(
        "--verify", action="store_true", help="periksa tanpa menulis berkas"
    )
    args = parser.parse_args()
    if args.ctl <= 0:
        parser.error("--ctl harus positif")

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%d%H%M%S")
    today = now.date().isoformat()
    report: dict[str, Any] = {
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
        "ctl": args.ctl,
        "declared_only": True,
        "note": NOTE,
    }

    if args.verify:
        report["mode"] = "verify"
        report.update(verify(args.ctl))
    else:
        report["mode"] = "apply"
        backups: list[str] = []
        produced: dict[str, dict[str, int]] = {}
        targets = (
            (OPENCODE_CONFIG, lambda d: patch_opencode(d, args.ctl)),
            (
                PROVIDER_CATALOG,
                lambda d: patch_provider_catalog(d, args.ctl, today),
            ),
            (LOCAL_CATALOG, lambda d: patch_local_catalog(d, args.ctl, today)),
        )
        for path, patch in targets:
            data = _load(path)
            if not data:
                raise SystemExit(f"berkas tidak dapat dibaca: {path}")
            produced[path.name] = patch(data)
            backup = _save(path, data, stamp)
            if backup:
                backups.append(backup)
        report["perubahan"] = produced
        report["backup"] = backups
        report.update(verify(args.ctl))

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

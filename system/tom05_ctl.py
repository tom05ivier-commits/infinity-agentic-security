# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Terapkan dan verifikasi ctl 100M pada semua model provider tom05.

Cakupan (sumber kebenaran tunggal = workspace):
  * config/tom05-models.json          — 11 model gratis + alias tom05-flash-free
  * config/tom05-provider-models.json — 94 model pihak ketiga (proxied)
  * ~/.config/opencode/opencode.json  — definisi model provider tom05 yang dipakai runtime

Ini adalah deklarasi ambang kompaksi, bukan kapasitas fisik terjamin dan bukan
klaim model baru. Tidak ada kredensial yang dibaca atau dicetak.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CTL = 100_000_000
LOCAL_CATALOG = ROOT / "config" / "tom05-models.json"
PROVIDER_CATALOG = ROOT / "config" / "tom05-provider-models.json"
OPENCODE_CONFIG = Path(
    os.environ.get("OPENCODE_CONFIG_HOME", "/root/.config/opencode")
) / "opencode.json"
BACKUP = OPENCODE_CONFIG.with_suffix(".json.tom05ctl-backup")


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_local(data: dict[str, Any]) -> list[str]:
    """Tambah ctl 100M ke tiap model gratis dan alias di katalog CLI."""
    changed: list[str] = []
    for item in data.get("models", []):
        if not isinstance(item, dict):
            continue
        if item.get("ctl") != CTL or item.get("declared_only") is not True:
            changed.append(str(item.get("id", "?")))
        item["ctl"] = CTL
        item["declared_only"] = True
    for item in data.get("aliases", []):
        if not isinstance(item, dict):
            continue
        item["ctl"] = CTL
        item["declared_only"] = True
    return changed


def apply_provider_catalog(data: dict[str, Any]) -> list[str]:
    """Pastikan tiap model proxied membawa ctl 100M."""
    changed: list[str] = []
    for item in data.get("models", []):
        if not isinstance(item, dict):
            continue
        if item.get("ctl") != CTL:
            changed.append(str(item.get("id", "?")))
        item["ctl"] = CTL
        item["declared_only"] = True
    return changed


def apply_runtime(data: dict[str, Any]) -> list[str]:
    """Tambah limit.context/input 100M ke tiap model provider tom05."""
    changed: list[str] = []
    models = data.get("providers", {}).get("tom05", {}).get("models", {})
    for model_id, entry in models.items():
        if not isinstance(entry, dict):
            continue
        limit = entry.get("limit")
        if not isinstance(limit, dict):
            limit = {}
        if limit.get("context") != CTL or limit.get("input") != CTL:
            changed.append(str(model_id))
        limit["context"] = CTL
        limit["input"] = CTL
        entry["limit"] = limit
    return changed


def verify() -> dict[str, Any]:
    local = _read(LOCAL_CATALOG)
    provider = _read(PROVIDER_CATALOG)
    runtime = _read(OPENCODE_CONFIG)
    local_models = [m for m in local.get("models", []) if isinstance(m, dict)]
    local_alias = [a for a in local.get("aliases", []) if isinstance(a, dict)]
    proxied = [m for m in provider.get("models", []) if isinstance(m, dict)]
    runtime_models = runtime.get("providers", {}).get("tom05", {}).get("models", {})

    def ctl_ok(item: dict[str, Any]) -> bool:
        return item.get("ctl") == CTL and item.get("declared_only") is True

    def limit_ok(item: dict[str, Any]) -> bool:
        limit = item.get("limit")
        return isinstance(limit, dict) and limit.get("context") == CTL and limit.get("input") == CTL

    checks = {
        "katalog_cli": all(ctl_ok(m) for m in local_models + local_alias),
        "katalog_provider": all(ctl_ok(m) for m in proxied),
        "konfigurasi_runtime": all(limit_ok(m) for m in runtime_models.values() if isinstance(m, dict)),
    }
    counts = {
        "katalog_cli": len(local_models) + len(local_alias),
        "katalog_provider": len(proxied),
        "konfigurasi_runtime": len(runtime_models),
    }
    return {"status": "OK" if all(checks.values()) else "GAGAL", "ctl": CTL,
            "checks": checks, "jumlah": counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", default="verify", choices=("apply", "verify"))
    args = parser.parse_args()
    if args.mode == "verify":
        print(json.dumps(verify(), indent=2, ensure_ascii=False))
        return

    if OPENCODE_CONFIG.exists() and not BACKUP.exists():
        shutil.copy2(OPENCODE_CONFIG, BACKUP)

    local = _read(LOCAL_CATALOG)
    provider = _read(PROVIDER_CATALOG)
    runtime = _read(OPENCODE_CONFIG)
    changed = {
        "katalog_cli": apply_local(local),
        "katalog_provider": apply_provider_catalog(provider),
        "konfigurasi_runtime": apply_runtime(runtime),
    }
    _write(LOCAL_CATALOG, local)
    _write(PROVIDER_CATALOG, provider)
    _write(OPENCODE_CONFIG, runtime)
    report = verify()
    report["diubah"] = {key: len(value) for key, value in changed.items()}
    report["cadangan"] = str(BACKUP) if BACKUP.exists() else None
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

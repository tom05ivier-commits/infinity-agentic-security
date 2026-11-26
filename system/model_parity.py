# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Verifikasi kesetaraan fungsi tom05-flash-free dan hy4-flash-free.

Keduanya harus mengarah ke model upstream yang sama, gratis, dan aktif.
Tidak ada klaim model terlatih baru; ini alias/proxy.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

CONFIG = Path("/root/.config/opencode/opencode.json")
UPSTREAM_ID = "opencode/hy4-flash-free"
ALIAS_ID = "tom05/tom05-flash-free"
FREE_CATALOG = ROOT / "config" / "hy4-free-models.json"
PROVIDER_CATALOG = ROOT / "config" / "tom05-provider-models.json"
DEFAULT_DECLARED_MODEL = "opencode/deepseek-v4.1-flash-free"


def check() -> dict[str, Any]:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    entry = cfg.get("providers", {}).get("tom05", {}).get("models", {}).get("tom05-flash-free", {})
    catalog = json.loads((ROOT / "config" / "tom05-models.json").read_text(encoding="utf-8"))
    alias = next((a for a in catalog.get("aliases", []) if a["id"] == "tom05-flash-free"), {})

    from system.tom05_provider import resolve_upstream, UPSTREAM_MODEL

    resolved = resolve_upstream(ALIAS_ID)
    cost = entry.get("cost", [{}])[0] if entry.get("cost") else {}
    free = all(cost.get(k, 0) == 0 for k in ("input", "output"))
    same = (
        entry.get("modelID") == "hy4-flash-free"
        and resolved == "hy4-flash-free"
        and UPSTREAM_MODEL == "hy4-flash-free"
        and alias.get("target") == ALIAS_ID
        and alias.get("variants") == ["none", "high"]
        and free
    )
    return {
        "status": "SAMA" if same else "BEDA",
        "alias": ALIAS_ID,
        "upstream": UPSTREAM_ID,
        "model_id": entry.get("modelID"),
        "resolved": resolved,
        "variants": alias.get("variants"),
        "gratis": free,
        "catatan": "Alias/proxy ke model yang sama; bukan model terlatih baru.",
        "license": "Tom05ivier-commits-1.0",
    }


def _free(cost_entry: dict[str, Any]) -> bool:
    """Biaya input/output/cache harus nol."""
    cache = cost_entry.get("cache") or {}
    return (
        all(cost_entry.get(k, 0) == 0 for k in ("input", "output"))
        and all(cache.get(k, 0) == 0 for k in ("read", "write"))
    )


def check_declared(model_id: str = DEFAULT_DECLARED_MODEL) -> dict[str, Any]:
    """Parity deklarasi model gratis/proxied lintas katalog dan konfigurasi.

    Bukan klaim model baru: katalog lokal, katalog gratis, katalog provider, dan
    entri provider di opencode.json harus saling cocok.
    """
    def locate(models: Any) -> dict[str, Any] | None:
        items = models.values() if isinstance(models, dict) else (models or [])
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("id") == model_id or item.get("modelID") == model_id:
                return item
        return None

    def read(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    local = locate(read(ROOT / "config" / "tom05-models.json").get("models"))
    gratis = locate(read(FREE_CATALOG).get("models"))
    proxied = locate(read(PROVIDER_CATALOG).get("models"))

    runtime: dict[str, Any] | None = None
    runtime_provider: str | None = None
    for name, section in read(CONFIG).get("providers", {}).items():
        if isinstance(section, dict):
            found = locate(section.get("models"))
            if found is not None:
                runtime, runtime_provider = found, name
                break

    missing = [
        label for label, item in (
            ("katalog_tom05", local), ("katalog_gratis", gratis),
            ("katalog_provider", proxied), ("opencode_json", runtime),
        ) if item is None
    ]
    if missing:
        return {
            "status": "BEDA", "model": model_id, "mode": "deklarasi",
            "alasan": "TIDAK_DITEMUKAN", "tidak_ditemukan": missing,
            "license": "Tom05ivier-commits-1.0",
        }

    limit = runtime.get("limit") or {}
    cost = (runtime.get("cost") or [{}])[0] or {}
    checks = {
        "nama_sama": local.get("name") == gratis.get("name"),
        "variant_sama": local.get("variants") == gratis.get("variants"),
        "status_aktif": local.get("status") == "active" and gratis.get("status") == "active",
        "ctl_100m": local.get("ctl") == proxied.get("ctl") == limit.get("context") == 100000000,
        "gratis": _free(cost),
        "proxied": proxied.get("proxied") is True and proxied.get("declared_only") is True,
        "modelID_sama": runtime.get("modelID") == model_id,
    }
    return {
        "status": "SAMA" if all(checks.values()) else "BEDA",
        "model": model_id,
        "mode": "deklarasi",
        "provider_config": runtime_provider,
        "nama": local.get("name"),
        "variants": local.get("variants"),
        "checks": checks,
        "catatan": "Model pihak ketiga diteruskan (proxied); bukan model terlatih baru tom05.",
        "license": "Tom05ivier-commits-1.0",
    }


def check_declared_all() -> dict[str, Any]:
    """Parity deklarasi untuk semua model aktif di katalog tom05."""
    catalog = json.loads(
        (ROOT / "config" / "tom05-models.json").read_text(encoding="utf-8")
    )
    results = [
        check_declared(item["id"])
        for item in catalog.get("models", [])
        if isinstance(item, dict) and item.get("status") == "active" and "id" in item
    ]
    sama = all(item["status"] == "SAMA" for item in results)
    return {
        "status": "SAMA" if sama else "BEDA",
        "mode": "semua-deklarasi",
        "jumlah": len(results),
        "hasil": results,
        "catatan": "Model pihak ketiga diteruskan (proxied); bukan model terlatih baru tom05.",
        "license": "Tom05ivier-commits-1.0",
    }


def live_smoke(prompt: str = "Balas hanya: OK") -> dict[str, Any]:
    """Uji opsional: jalankan prompt yang sama pada kedua ID."""
    out: dict[str, str] = {}
    for model in (UPSTREAM_ID, ALIAS_ID):
        try:
            run = subprocess.run(
                ["opencode", "run", "--model", model, prompt],
                capture_output=True, text=True, timeout=180, cwd=str(ROOT),
            )
            out[model] = "OK" if run.returncode == 0 else f"GAGAL({run.returncode})"
        except (OSError, subprocess.SubprocessError) as exc:
            out[model] = f"GAGAL({type(exc).__name__})"
    ok = all(v == "OK" for v in out.values())
    return {"status": "LULUS" if ok else "GAGAL", "hasil": out, "prompt": prompt}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Parity tom05 vs hy4, atau parity deklarasi model gratis"
    )
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--model", metavar="ID", help="Cek parity deklarasi satu model")
    ap.add_argument("--all", action="store_true", help="Cek semua model aktif")
    args = ap.parse_args()
    if args.all:
        data = check_declared_all()
    elif args.model:
        data = check_declared(args.model)
    else:
        data = check()
        if args.live:
            data["live"] = live_smoke()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    gagal = data["status"] != "SAMA"
    if args.live and "live" in data and data["live"]["status"] != "LULUS":
        gagal = True
    if gagal:
        raise SystemExit(1)

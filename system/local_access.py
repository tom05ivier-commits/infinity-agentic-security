# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Verifikasi kebijakan satu lokal: workspace + port 8785 saja.

Read-only. Tidak ada kredensial, mutasi layanan, atau koneksi keluar.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "local_access.json"
OPENCODE_CONFIG = Path("/root/.config/opencode/opencode.json")


def load() -> dict[str, Any]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    data = load()
    rules = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8")).get("permissions", [])
    pairs = {(r.get("action"), r.get("resource")): r.get("effect") for r in rules}
    checks = {
        "root_workspace": data["data_root"] == str(ROOT),
        "port_8785": data["only_agent_port"] == 8785,
        "deny_lain": pairs.get(("webfetch", "http://127.0.0.1:*")) == "deny",
        "allow_8785": pairs.get(("webfetch", "http://127.0.0.1:8785/*")) == "allow",
    }
    try:
        with urllib.request.urlopen(data["only_agent_url"] + "health", timeout=3) as res:
            checks["health_8785"] = res.status == 200
    except Exception:  # noqa: BLE001
        checks["health_8785"] = False
    return {
        "status": "OK" if all(checks.values()) else "GAGAL",
        "checks": checks,
        "data_root": data["data_root"],
        "only_agent_port": data["only_agent_port"],
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, ensure_ascii=False))
    return 0 if verify()["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Bangkitkan RTL chip verifikasi untuk setiap server localhost.

Modul dihasilkan dari `system/services.json` (sumber tunggal registry).
Jalur terpisah dari 9 modul utama `chip/reference.py` agar skor 100/100
dan 2612 vektor tidak berubah. Status fabrikasi: NOT_READY.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "chip" / "rtl"
REGISTRY = ROOT / "system" / "services.json"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

HEADER = """// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip verifikasi server: {name} ({kind}, port {port})
// Logika: ready = alive & healthy & enabled
//         degraded = alive & enabled & ~healthy
//         blocked = ~alive | ~enabled
module srv_{sig}(
  input alive,
  input healthy,
  input enabled,
  output ready,
  output degraded,
  output blocked
);
  assign ready = alive & healthy & enabled;
  assign degraded = alive & enabled & ~healthy;
  assign blocked = ~alive | ~enabled;
endmodule
"""


def signal(name: str) -> str:
    sig = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return sig or "server"


def servers() -> list[dict[str, Any]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return [
        {"name": s["name"], "sig": signal(s["name"]),
         "kind": s.get("kind", "process"), "port": s.get("port")}
        for s in data["services"]
    ]


def generate() -> list[str]:
    RTL.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for s in servers():
        path = RTL / f"srv_{s['sig']}.v"
        path.write_text(HEADER.format(name=s["name"], kind=s["kind"],
                                      port=s["port"], sig=s["sig"]), encoding="utf-8")
        written.append(path.name)
    return written


if __name__ == "__main__":
    files = generate()
    print(json.dumps({"generated": len(files), "files": files,
                      "license": LICENSE, "owner": OWNER,
                      "fabrication": "NOT_READY"}, indent=2, ensure_ascii=False))

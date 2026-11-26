# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Definisi kanonik agen chip untuk CLI chip, model tom05, dan OpenCode.

Satu sumber kebenaran dipakai oleh tiga tempat:

* ``chip/chip_cli.py`` — perintah ``agent``;
* ``tom05`` — flag ``--chip``;
* ``system/hy4_manager.py`` — agent OpenCode ``chip.md`` yang kemudian
  disamakan ke profil agent/skill Copilot CLI oleh ``system/copilot_sync.py``.

Perubahan pada peran atau kemampuan agen cukup dilakukan di berkas ini.
"""

from __future__ import annotations

from typing import Any

AGENT_FILE = "chip.md"
AGENT_MODEL = "tom05/tom05-flash-free"
AGENT_DESCRIPTION = (
    "Agen verifikasi & desain chip akselerator hy4 (RTL, simulasi, dan skor)."
)

AGENT_BODY = """Kamu adalah agen chip IT Agenty dengan model tom05/tom05-flash-free.
Sumber kebenaran: `chip/README.md`, `chip/hy4_chip.json`, dan `chip/rtl/`.

Jalankan `python3 chip/chip_cli.py` untuk perintah `list`, `verify`, `synth`,
`iverilog`, `tapeout`, `foundry`, `score`, dan `agent`. Profil agen ini tampil
lewat `python3 chip/chip_cli.py agent` atau `tom05 --chip`; pemeriksaan cepat
memakai `tom05 --chip verify`.

Tugas: jelaskan modul hy4_dot4, hy4_quant, dan hy4_top; jalankan verifikasi
model, sintesis, dan Icarus Verilog; ulangi sampai semua berstatus PASS dengan
skor 100/100; lalu ringkas hasil beserta path laporan di `chip/reports/`.

Batas tegas: ini desain dan logika chip, bukan fabrikasi silikon nyata. Status
fabrikasi tetap NOT_READY sampai ada mitra dan proses fisik yang sah. Jangan
mengklaim sertifikasi, hak atas kode pihak ketiga, atau kemampuan yang tidak
ada. Jangan menampilkan kredensial maupun data pribadi, dan jangan menghapus
pembatas lisensi pihak ketiga. Semua aksi tetap diaudit.
"""

AGENT_MARKDOWN = f"""---
model: {AGENT_MODEL}
mode: all
description: {AGENT_DESCRIPTION}
---

{AGENT_BODY}
"""

CAPABILITIES: tuple[str, ...] = (
    "list",
    "verify",
    "synth",
    "iverilog",
    "tapeout",
    "foundry",
    "score",
    "agent",
    "ai-chip",
)


def describe() -> dict[str, Any]:
    """Profil agen chip yang dikonsumsi CLI chip dan tom05."""
    return {
        "agent": "chip",
        "file": AGENT_FILE,
        "model": AGENT_MODEL,
        "description": AGENT_DESCRIPTION,
        "capabilities": list(CAPABILITIES),
        "chip_cli": "python3 chip/chip_cli.py <perintah>",
        "tom05_flag": "tom05 --chip [perintah]",
        "source": "chip/chip_agent.py",
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }

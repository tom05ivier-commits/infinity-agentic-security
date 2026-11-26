# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
"""Definisi kanonik agen khusus chip simulasi NEURO-25.

Satu sumber kebenaran dipakai oleh tiga tempat:

* ``chip/chip_cli.py`` — perintah ``neuro25-agent``;
* ``tom05`` — flag ``--neuro25-agent``;
* ``system/hy4_manager.py`` — profil OpenCode ``neuro25.md`` yang disamakan
  ke agent/skill Copilot CLI oleh ``system/copilot_sync.py``.

Agen ini hanya menjelaskan dan memverifikasi desain RTL. Ia tidak memiliki
izin untuk menghubungkan chip ke subjek manusia, membaca data neural, atau
mengklaim fungsi medis.
"""

from __future__ import annotations

from typing import Any

AGENT_FILE = "neuro25.md"
AGENT_MODEL = "tom05/tom05-flash-free"
AGENT_DESCRIPTION = (
    "Agen khusus chip simulasi NEURO-25 (pemetaan kognitif sintetis, "
    "bukan alat medis atau antarmuka saraf)."
)

AGENT_BODY = """Kamu adalah agen NEURO-25 IT Agenty dengan model tom05/tom05-flash-free.
Sumber kebenaran: `chip/rtl/tom05_neuro25.v`, `chip/neuro25_reference.py`,
`chip/neuro25_verify.py`, `chip/tb/tb_neuro25.v`, dan `docs/NEURO25-CHIP.md`.

Jalankan `python3 chip/chip_cli.py neuro25` atau `tom05 --neuro25` untuk
verifikasi lengkap: model referensi (8192 vektor), Icarus Verilog (49152
pengecekan, waveform), dan sintesis Yosys. Profil agen ini tampil lewat
`python3 chip/chip_cli.py neuro25-agent` atau `tom05 --neuro25-agent`.

Tugas: jelaskan empat jalur kognitif chip — indra (`n0..n3`), memori (`mem`
dengan gain profil referensi ~25 tahun), perencanaan (`intent`), dan aksi
(`act`/`blocked`/`irq` dengan `gate` sebagai izin). Ulangi verifikasi sampai
semua bukti PASS, lalu ringkas hasil beserta path laporan di `chip/reports/`.

Batas tegas: chip ini memproses sinyal SINTETIS. Bukan alat medis, bukan BCI,
tidak terhubung ke otak manusia hidup, tidak memakai elektroda, tidak membaca
atau mengirim data neural, tidak memberikan stimulasi, dan tidak memakai jaringan.
Status fabrikasi `NOT_READY` dan validasi klinis `NOT_VALIDATED` tidak boleh
diubah. Jangan mengklaim kemampuan biologis, kesadaran, sertifikasi, atau hak
atas kode pihak ketiga. Jangan menampilkan kredensial atau data pribadi.
Semua aksi diaudit dan tetap tunduk pada lisensi Tom05ivier-commits-1.0.
"""

AGENT_MARKDOWN = f"""---
model: {AGENT_MODEL}
mode: all
description: {AGENT_DESCRIPTION}
---

{AGENT_BODY}
"""

CAPABILITIES: tuple[str, ...] = (
    "agent",
    "model-reference",
    "rtl-explain",
    "iverilog",
    "synthesis",
    "safety-gate",
    "report",
)


def describe() -> dict[str, Any]:
    """Profil agen NEURO-25 untuk CLI chip dan tom05."""
    return {
        "agent": "neuro25",
        "file": AGENT_FILE,
        "model": AGENT_MODEL,
        "description": AGENT_DESCRIPTION,
        "capabilities": list(CAPABILITIES),
        "chip_cli": "python3 chip/chip_cli.py neuro25",
        "agent_cli": "python3 chip/chip_cli.py neuro25-agent",
        "tom05_flag": "tom05 --neuro25-agent",
        "source": "chip/neuro25_agent.py",
        "module": "chip/rtl/tom05_neuro25.v",
        "fabrication": "NOT_READY",
        "clinical_validation": "NOT_VALIDATED",
        "medical_device": False,
        "neural_interface": False,
        "subject_data": False,
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }

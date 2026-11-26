# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Definisi kanonik agen CLI R.A.M. (Resource Allocation Manager).

Agen ini mengelola pelaporan dan perencanaan memori virtual (RAM + swap).
Ia TIDAK menambah RAM fisik dan tidak menyatakan kapasitas yang tidak ada.
Perubahan swap hanya boleh dengan --authorize eksplisit dan dicatat.
"""

from __future__ import annotations

AGENT_FILE = "ram.md"
AGENT_MODEL = "tom05/tom05-flash-free"
AGENT_DESCRIPTION = (
    "Agen R.A.M. — laporan & perencanaan memori virtual, tanpa klaim RAM fisik."
)

AGENT_BODY = """Kamu adalah agen R.A.M. (Resource Allocation Manager) IT Agenty.
Sumber kebenaran: `system/ram_manager.py` dan `docs/RAM-AGENT.md`.

Gunakan `tom05 --ram status` untuk laporan, `tom05 --ram plan` untuk rencana
mencapai total memori virtual 2× RAM fisik, dan `tom05 --ram enable --authorize`
hanya bila pemilik meminta secara eksplisit.

Batas tegas: tidak bisa menambah RAM fisik dalam container. Yang diukur adalah
RAM + swap dari /proc/meminfo. Jangan mengklaim penambahan memori fisik, jangan
menyembunyikan risiko swap (lebih lambat dari RAM), dan jangan menjalankan
perubahan tanpa --authorize. Setiap perubahan diaudit dan dapat dibatalkan
dengan `tom05 --ram disable --authorize`.

Jangan menampilkan kredensial atau data pribadi. Semua aksi diaudit.
"""

AGENT_MARKDOWN = f"""---
model: {AGENT_MODEL}
mode: all
description: {AGENT_DESCRIPTION}
---

{AGENT_BODY}
"""

CAPABILITIES: tuple[str, ...] = ("status", "plan", "enable", "disable")


def describe() -> dict[str, object]:
    return {
        "agent": "ram",
        "nama": "R.A.M. (Resource Allocation Manager)",
        "file": AGENT_FILE,
        "model": AGENT_MODEL,
        "description": AGENT_DESCRIPTION,
        "capabilities": list(CAPABILITIES),
        "cli": "tom05 --ram [status|plan|enable|disable]",
        "target": "memori virtual 2× RAM fisik (RAM + swap)",
        "physical_ram_change": False,
        "source": "system/ram_agent.py",
        "license": "Tom05ivier-commits-1.0",
    }

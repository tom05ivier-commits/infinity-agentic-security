# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Definisi kanonik agen CLI dataset IT Agenty.

Satu sumber kebenaran dipakai oleh tiga tempat:

* ``dataset/dataset_cli.py`` — perintah ``agent``;
* ``tom05`` — flag ``--dataset``;
* ``system/hy4_manager.py`` — agen OpenCode ``dataset.md`` yang kemudian
  disamakan ke profil agent/skill Copilot CLI oleh ``system/copilot_sync.py``.

Batas tegas: agen ini **hanya menyiapkan dan memvalidasi dataset**. Ia bukan
model neural, tidak memuat bobot, tidak melakukan training, dan tidak boleh
dipakai untuk mengklaim "model baru Tom05". Setiap rekord ditandai
``trained: false``.
"""

from __future__ import annotations

from typing import Any

AGENT_FILE = "dataset.md"
AGENT_MODEL = "tom05/tom05-flash-free"
AGENT_DESCRIPTION = (
    "Agen CLI dataset IT Agenty — bangun, validasi, dan olah dataset "
    "instruksi→jawaban berlabel (bukan training, bukan model neural)."
)

AGENT_BODY = """Kamu adalah agen dataset IT Agenty dengan model tom05/tom05-flash-free.
Sumber kebenaran: `dataset/builder.py`, `dataset/dataset_cli.py`, dan
`docs/DATASET-AGENT.md`.

Gunakan `python3 dataset/dataset_cli.py` (atau `tom05 --dataset`) untuk:
`agent`, `doctor`, `template`, `init`, `build`, `validate`, `stats`,
`privacy`, `preview`, `add`, `merge`, `dedup`, `filter`, `split`, dan `export`.

Alur kerja yang benar:
1. `doctor` — laporkan jujur pustaka ML, bobot, dan GPU yang tersedia.
2. `template` / `init` — tunjukkan format pasangan `instruction` → `response`.
   Rekord dari `init` adalah CONTOH/SINTETIS, bukan data asli.
3. `build --dry-run` — lihat apa yang bisa dibangun dari dokumen workspace.
4. `build` — tulis dataset berlabel ke `dataset/data/tom05_dataset.jsonl`.
5. `validate` dan `privacy` — pastikan skema, panjang, duplikat, dan nol
   temuan kredensial.
6. `merge`, `dedup`, `filter`, `split` — olah dataset yang sudah ada tanpa
   mengubah maknanya; semua keluaran tetap disaring dan divalidasi.
7. `export --format alpaca|sharegpt|jsonl` — siapkan berkas untuk pipeline
   training milik pemilik di lingkungan komputasi yang memadai.

Batas tegas yang tidak boleh dilanggar:
- Ini **bukan** model neural terlatih. Agen hanya menyiapkan data. Training
  nyata membutuhkan dataset berlabel milik pemilik + compute (lihat `doctor`).
- Jangan mengubah log audit (`security/reports/*.jsonl`) atau `memory.jsonl`
  menjadi "dataset training". Itu manipulasi format, bukan pelatihan.
- Jangan mengunduh bobot atau model pihak ketiga tanpa izin tertulis; lisensi
  pihak ketiga tetap berlaku bila izin diberikan.
- Setiap rekord wajib memuat `source`, `license`, `kind`, dan `trained: false`.
- Semua teks disaring privasi; kredensial atau data pribadi tidak pernah
  ditampilkan, dicatat, atau dikirim keluar. Semua aksi diaudit.
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
    "doctor",
    "template",
    "init",
    "build",
    "generate",
    "validate",
    "stats",
    "privacy",
    "preview",
    "add",
    "merge",
    "dedup",
    "filter",
    "split",
    "export",
)


def describe() -> dict[str, Any]:
    """Profil agen dataset yang dikonsumsi dataset_cli dan tom05."""
    return {
        "agent": "dataset",
        "file": AGENT_FILE,
        "model": AGENT_MODEL,
        "description": AGENT_DESCRIPTION,
        "capabilities": list(CAPABILITIES),
        # Alias untuk konsumen yang memakai skema lama ``commands``/``trained``.
        "commands": list(CAPABILITIES),
        "trained": False,
        "aliases": {"generate": "build"},
        "cli": "python3 dataset/dataset_cli.py <perintah>",
        "tom05_flag": "tom05 --dataset [perintah]",
        "engine": "dataset/builder.py",
        "default_output": "dataset/data/tom05_dataset.jsonl",
        "is_neural_model": False,
        "performs_training": False,
        "records_trained": False,
        "source": "dataset/dataset_agent.py",
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }

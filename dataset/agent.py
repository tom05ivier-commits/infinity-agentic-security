# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Nama kompatibilitas untuk definisi agen dataset IT Agenty.

Satu sumber kebenaran ada di ``dataset/dataset_agent.py``. Berkas ini hanya
meneruskan definisi itu agar konsumen lama yang mengimpor ``dataset.agent``
tetap bekerja tanpa menduplikasi peran agen.
"""

from __future__ import annotations

from dataset.dataset_agent import (  # noqa: F401
    AGENT_BODY,
    AGENT_DESCRIPTION,
    AGENT_FILE,
    AGENT_MARKDOWN,
    AGENT_MODEL,
    CAPABILITIES,
    describe,
)

NAME = "dataset"
MODEL = AGENT_MODEL
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"

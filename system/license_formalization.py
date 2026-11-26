# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Status peresmian lisensi — read-only, tanpa kredensial."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ACTIVE = ROOT / "LICENSE"
DRAFT_LICENSE = ROOT / "LICENSE.tom05ivier-v1.1.draf"
DRAFT_LETTER = ROOT / "DRAF-surat-larangan-klon-tom05ivier-commits.md"


def status() -> dict[str, Any]:
    active = ACTIVE.read_text(encoding="utf-8") if ACTIVE.is_file() else ""
    draft = DRAFT_LICENSE.read_text(encoding="utf-8") if DRAFT_LICENSE.is_file() else ""
    letter = DRAFT_LETTER.read_text(encoding="utf-8") if DRAFT_LETTER.is_file() else ""
    # Tanda tangan harus ditulis manual, bukan hasil render daftar Python/JSON
    # atau placeholder __signature__. Artefak seperti itu tidak boleh dianggap
    # sebagai tanda tangan pemilik hanya karena placeholder lama sudah hilang.
    artifacts = (
        "__signature__", "__tomivier__", "[TANDA TANGAN PEMILIK",
        "['(__tomivier", "[('__signature__", "[(__signature__)",
        "['(__signature__)", "[(__signature__)",
    )
    license_dirty = any(mark in draft for mark in artifacts)
    letter_dirty = any(mark in letter for mark in artifacts)
    checks = {
        "lisensi_aktif_v1": "Versi 1.0" in active,
        "draf_amandemen_tersedia": bool(draft),
        "draf_surat_tersedia": bool(letter),
        "draf_bertanda_belum_berlaku": "BELUM BERLAKU" in draft
        and "BELUM BERLAKU" in letter,
        "tanda_tangan_masih_placeholder": license_dirty,
        "tanda_tangan_bersih": "(__signature__)" in draft and not license_dirty,
        "surat_larangan_bersih": "(__signature__)" in letter and not letter_dirty,
        "amandemen_belum_menggantikan_aktif": not ACTIVE.with_name("LICENSE").exists()
        or "Versi 1.0" in active,
    }
    finalisasi = (
        "Versi 1.1" in active
        and not any(mark in active for mark in artifacts)
    )
    if finalisasi:
        status = "PERLU_VERIFIKASI_MANUAL"
    elif checks["tanda_tangan_bersih"] and checks["surat_larangan_bersih"]:
        # Kedua draf sudah ditandatangani pemilik, tetapi LICENSE aktif masih
        # v1.0: status menunggu peresmian (penggantian berkas LICENSE).
        status = "MENUNGGU_TANDA_TANGAN"
    elif all(checks.values()):
        # Kondisi lama: placeholder masih ada, belum ada tanda tangan.
        status = "MENUNGGU_TANDA_TANGAN"
    else:
        status = "PERLU_PERBAIKAN"
    return {
        "status": status,
        "akses": "read-only",
        "lisensi_aktif": (
            "Tom05ivier-commits v1.1" if "Versi 1.1" in active
            else "Tom05ivier-commits v1.0"
        ),
        "amandemen": (
            "v1.1 (berlaku)" if "Versi 1.1" in active
            else "v1.1 (draf, tidak berlaku)"
        ),
        "checks": checks,
        "langkah": [
            "Pemilik mengisi dan menandatangani draf surat larangan klon.",
            "Pemilik mengisi dan menandatangani draf amandemen lisensi v1.1.",
            "Pemilik mengganti LICENSE aktif dengan versi yang ditandatangani.",
            "Perbarui catatan proyek dan nomor surat; jalankan license-status ulang.",
        ],
        "catatan": (
            "Bukan paten terdaftar. Tidak mengubah lisensi pihak ketiga. "
            "Tidak ada kredensial atau data pribadi yang dibaca."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(status(), indent=2, ensure_ascii=False))

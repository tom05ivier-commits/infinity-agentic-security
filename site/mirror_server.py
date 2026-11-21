#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Entry point mirror aplikasi Chip Merah Putih pada port 8770.

Dipisahkan dari ``site/server.py`` agar perintah di ``system/services.json``
tidak memerlukan argumen tambahan setelah opsi ``--cmd`` (argparse membatasi
ini). Router React asli memakai path absolut, jadi direktori mirror harus
menjadi document root.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from server import MIRROR, MIRROR_PORT, serve  # noqa: E402


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(
        os.environ.get("MIRROR_PORT", MIRROR_PORT)
    )
    print(f"Server mirror berjalan di http://127.0.0.1:{port}/")
    serve(
        port,
        root=MIRROR,
        spa_prefix="/",
        fallback_file="/index.html",
        api_stub=True,
    )

#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Aturan permanen: SELALU JALANKAN KOMPUTER.
# Menjalankan supervisor yang memulai ulang server & proteksi bila mati.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/system/cli.py" supervise \
  --interval "${AGENTY_INTERVAL:-5}" \
  --port "${AGENTY_PORT:-8765}"

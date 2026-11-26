#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Wrapper alur kerja relai chat: pesan tom05-flash-free -> semua responder.
# tom05 hanya mengirim pesan; agen/CLI/skill/tool/docker yang merespon tugas.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/system/chat_dispatch.py" "$@"

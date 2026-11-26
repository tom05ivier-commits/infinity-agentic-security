#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Entry point supervisor untuk server API OpenCode. Memakai variabel
# AGENTY_OPENCODE_PORT (bukan PORT) agar tidak bentrok dengan layanan lain.

set -euo pipefail
OPENCODE_BIN_VALUE="${OPENCODE_BIN:-/root/.opencode/bin/opencode}"
# Port bisa diberikan sebagai argumen pertama (dipakai registry untuk
# instansi tambahan); tanpa argumen, pakai AGENTY_OPENCODE_PORT lalu default 8786.
PORT_VALUE="${1:-${AGENTY_OPENCODE_PORT:-8786}}"
exec "$OPENCODE_BIN_VALUE" serve --hostname 127.0.0.1 --port "$PORT_VALUE"

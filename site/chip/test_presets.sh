#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Uji preset hy4 di simulator browser memakai Playwright terpasang global.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NODE_MODULES="$(npm root -g 2>/dev/null || true)"
if [ -n "$NODE_MODULES" ]; then
  export NODE_PATH="${NODE_PATH:+${NODE_PATH}:}${NODE_MODULES}"
fi
exec node "$ROOT/site/chip/tests/presets.test.js" "$@"

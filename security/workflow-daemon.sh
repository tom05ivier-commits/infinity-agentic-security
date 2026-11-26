#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Wrapper daemon alur kerja harian (dikelola supervisor).

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$ROOT/system/config.env" ]; then
  # shellcheck disable=SC1091
  . "$ROOT/system/config.env"
fi
exec python3 "$ROOT/security/workflow.py" daemon \
  --name "${WORKFLOW_NAME:-harian}" \
  --interval "${WORKFLOW_INTERVAL:-86400}"

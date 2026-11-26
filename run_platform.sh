#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Peluncur Platform Engineering CLI Scorecard.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$ROOT/platform_clis/cli.py" "$@"

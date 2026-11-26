#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Menjalankan GitHub Copilot CLI dengan model opencode/hy4-flash-free.
# Bridge OpenAI-compatible lokal otomatis dinyalakan bila belum aktif.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_URL="http://127.0.0.1:8766/v1/health"

if ! curl -fsS "$BRIDGE_URL" >/dev/null 2>&1; then
  echo "[*] Menyalakan Copilot bridge..."
  nohup python3 "$ROOT/copilot-bridge/bridge.py" \
    > "$ROOT/copilot-bridge/bridge.log" 2>&1 &
  for _ in 1 2 3 4 5; do
    sleep 1
    curl -fsS "$BRIDGE_URL" >/dev/null 2>&1 && break
  done
fi

export COPILOT_BRIDGE_VARIANT="${COPILOT_BRIDGE_VARIANT:-}"
exec copilot --model opencode-hy4/hy4-flash-free "$@"

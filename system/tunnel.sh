#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Membuka Cloudflare Tunnel ke server publik lokal dengan retry otomatis.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$ROOT/system/reports/tunnel.log"
URLFILE="$ROOT/system/reports/tunnel_url.txt"
mkdir -p "$(dirname "$LOG")"

extract_url() {
  grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOG" 2>/dev/null | head -1 || true
}

for attempt in $(seq 1 10); do
  : > "$LOG"
  echo "[tunnel] percobaan $attempt/10" >&2
  cloudflared tunnel --url http://127.0.0.1:8768 --no-autoupdate --protocol quic > "$LOG" 2>&1 &
  TUNNEL_PID=$!

  for _ in $(seq 1 30); do
    URL="$(extract_url)"
    if [ -n "${URL:-}" ]; then
      printf '%s\n' "$URL" > "$URLFILE"
      echo "[tunnel] URL: $URL"
      wait "$TUNNEL_PID"
      exit 0
    fi
    if ! kill -0 "$TUNNEL_PID" 2>/dev/null; then
      break
    fi
    sleep 1
  done

  kill "$TUNNEL_PID" 2>/dev/null || true
  wait "$TUNNEL_PID" 2>/dev/null || true
  sleep 2
done

echo "[tunnel] GAGAL mendapat URL setelah 10 percobaan" >&2
exit 1

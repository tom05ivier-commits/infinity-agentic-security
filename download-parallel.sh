#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Unduh file dengan 5 koneksi paralel bila server mendukung HTTP Range.
# Bila tidak, otomatis jatuh ke satu koneksi (server mengabaikan Range).

set -uo pipefail
URL="${1:?URL diperlukan}"
OUT="${2:?output diperlukan}"
PARTS="${3:-5}"
TMP="${OUT}.parts"
mkdir -p "$TMP"

echo "[*] Mendeteksi dukungan Range..."
HEADERS="$(curl -sSI --max-time 30 "$URL" 2>/dev/null || true)"
RANGE_OK=0
LENGTH="$(printf '%s\n' "$HEADERS" | tr -d '\r' | awk 'tolower($1)=="content-length:"{print $2}' | tail -1)"
if printf '%s\n' "$HEADERS" | grep -qi 'accept-ranges: bytes' && [ -n "${LENGTH:-}" ]; then
  RANGE_OK=1
fi

if [ "$RANGE_OK" -eq 1 ]; then
  echo "[+] Range didukung; mengunduh ${PARTS} bagian secara paralel (${LENGTH} byte)."
  CHUNK=$(( (LENGTH + PARTS - 1) / PARTS ))
  pids=""
  for i in $(seq 0 $((PARTS - 1))); do
    start=$((i * CHUNK))
    end=$((start + CHUNK - 1))
    if [ "$end" -ge "$LENGTH" ]; then end=$((LENGTH - 1)); fi
    (
      curl -fsSL --retry 3 --max-time 3600 \
        -H "Range: bytes=${start}-${end}" \
        "$URL" -o "${TMP}/part.${i}"
    ) &
    pids="$pids $!"
  done
  for pid in $pids; do wait "$pid" || exit 1; done
  cat $(for i in $(seq 0 $((PARTS - 1))); do echo "${TMP}/part.${i}"; done) > "$OUT"
else
  echo "[!] Server tidak mendukung Range; unduhan satu koneksi."
  curl -fsSL --retry 5 --max-time 7200 "$URL" -o "$OUT" || exit 1
fi

echo "[✓] Selesai: $OUT ($(du -sh "$OUT" | cut -f1))"
rm -rf "$TMP"

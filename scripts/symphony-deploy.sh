#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Penjaga idempoten untuk stack Symphony. Dipanggil supervisor IT Agenty.
# Bila Docker Engine belum tersedia, proses ini tetap hidup dan menunggu
# daripada keluar — mencegah loop restart pada lingkungan tanpa dockerd.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT/docker-compose.symphony.yml"
ENV_FILE="$ROOT/.env.symphony"
LOG_FILE="$ROOT/system/reports/symphony-deploy.log"
WAIT_SECONDS="${SYMPHONY_WAIT_SECONDS:-30}"

if ! [[ "$WAIT_SECONDS" =~ ^[0-9]+$ ]] || (( WAIT_SECONDS < 1 )); then
  WAIT_SECONDS=30
fi

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG_FILE"
}

LAST_STATE=""
log_state() {
  if [[ "$1" != "$LAST_STATE" ]]; then
    log "$1"
    LAST_STATE="$1"
  fi
}

on_stop() {
  log_state "BERHENTI: penjaga Symphony dihentikan."
  exit 0
}
trap on_stop TERM INT

# Tunggu docker CLI bila belum ada. Tetap hidup agar supervisor tidak
# melakukan restart tiap siklus.
while ! command -v docker >/dev/null 2>&1; do
  log_state "MENUNGGU: docker CLI tidak ditemukan; periksa lagi dalam ${WAIT_SECONDS}s."
  sleep "$WAIT_SECONDS"
done

log_state "Docker CLI ditemukan."

# Setelah CLI ada, tunggu Engine aktif. Begitu aktif, jalankan stack lalu
# tetap memantau agar perubahan later bisa dipulihkan tanpa restart supervisor.
while true; do
  if ! docker info >/dev/null 2>&1; then
    log_state "MENUNGGU: Docker Engine tidak aktif; periksa lagi dalam ${WAIT_SECONDS}s."
    sleep "$WAIT_SECONDS"
    continue
  fi

  if [[ ! -f "$ENV_FILE" ]]; then
    cp "$ROOT/.env.symphony.example" "$ENV_FILE"
    log "PERINGATAN: $ENV_FILE dibuat dari contoh. Ganti sandi default sebelum produksi."
  fi

  if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --remove-orphans >>"$LOG_FILE" 2>&1; then
    log_state "OK: stack symphony aktif (port ${SYMPHONY_PORT:-8780})."
  else
    log_state "GAGAL: docker compose up menemui kesalahan; lihat baris log di atas."
  fi

  sleep "$WAIT_SECONDS"
done

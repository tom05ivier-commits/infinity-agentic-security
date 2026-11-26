#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Entry point kontainer Infinity Security System.

set -euo pipefail
ROOT="${AGENTY_WORKSPACE:-/workspace}"
if [ ! -d "${ROOT}" ]; then
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
cd "${ROOT}"

BIND_HOST="${BIND_HOST:-127.0.0.1}"
BIND_PORT="${BIND_PORT:-8765}"

echo "[*] Memeriksa CAP_NET_ADMIN dan backend firewall..."
python3 security/security_cli.py firewall capability || true

if [ "${ENABLE_KERNEL_FIREWALL:-0}" = "1" ]; then
  echo "[*] Mencoba mengaktifkan enforcement kernel..."
  if bash security/firewall/enable_kernel.sh; then
    echo "[+] Firewall kernel aktif."
  else
    echo "[!] Firewall kernel tidak tersedia; memakai policy engine userspace."
  fi
else
  echo "[*] Enforcement kernel dilewati; policy userspace aktif."
fi

case "${1:-supervise}" in
  supervise)
    echo "[*] Menjalankan supervisor untuk semua server..."
    exec python3 system/cli.py supervise \
      --host "${BIND_HOST}" --port "${BIND_PORT}" \
      --interval "${AGENTY_INTERVAL:-5}"
    ;;
  serve)
    echo "[*] Menjalankan dashboard di http://${BIND_HOST}:${BIND_PORT}/"
    exec python3 system/cli.py serve --host "${BIND_HOST}" --port "${BIND_PORT}"
    ;;
  protect)
    shift
    exec ./run_system.sh protect "$@"
    ;;
  drill)
    exec ./run_security_drill.sh
    ;;
  live-drill)
    exec python3 security/security_cli.py live-drill
    ;;
  verify)
    exec python3 security/security_cli.py verify
    ;;
  status)
    exec ./run_system.sh status
    ;;
  shell)
    exec /bin/bash
    ;;
  *)
    exec "$@"
    ;;
esac

#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Entry point image tom05-inference. Semua port memakai prefiks AGENTY_,
# bukan variabel `PORT` umum (peraturan AGENTS.md).

set -euo pipefail
ROOT="${AGENTY_WORKSPACE:-/workspace}"
cd "$ROOT"

PORT_VALUE="${AGENTY_TOM05_PORT:-${TOM05_PROVIDER_PORT:-8772}}"
export TOM05_PROVIDER_PORT="$PORT_VALUE"

case "${1:-serve}" in
  serve)
    echo "[tom05] provider aktif di 127.0.0.1:${PORT_VALUE}/v1" >&2
    echo "[tom05] manager=${TOM05_MANAGER_HOST:-infinity}:8766 (jaringan agenty-net)" >&2
    exec python3 system/tom05_provider.py
    ;;
  verify)
    exec bash scripts/tom05_container_verify.sh
    ;;
  list-models)
    exec ./tom05 --list-models
    ;;
  soc)
    exec python3 chip/chip_cli.py soc
    ;;
  capabilities)
    exec ./tom05 --capabilities
    ;;
  display)
    exec ./tom05 --display
    ;;
  *)
    exec "$@"
    ;;
esac

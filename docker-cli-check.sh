#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Periksa ketersediaan Docker CLI, plugin, dan konektivitas daemon.

set -uo pipefail

echo "=== Docker CLI ==="
if command -v docker >/dev/null 2>&1; then
  docker --version
else
  echo "docker: TIDAK ditemukan"
  exit 1
fi

echo "=== Plugin ==="
docker compose version || echo "compose: TIDAK tersedia"
docker buildx version || echo "buildx: TIDAK tersedia"

echo "=== Daemon ==="
if docker info >/dev/null 2>&1; then
  echo "daemon: TERHUBUNG"
  echo "=== Status ==="
  docker version --format '{{.Server.Version}}' 2>/dev/null || true
else
  echo "daemon: TIDAK terhubung"
  echo "Remediasi: jalankan Docker Engine di host atau set DOCKER_HOST ke daemon yang aktif."
  echo "Contoh: export DOCKER_HOST=tcp://host.docker.internal:2375"
fi

echo "=== Validasi compose (tanpa daemon) ==="
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if docker compose -f "$ROOT/docker-compose.yml" config >/dev/null 2>&1; then
  echo "docker-compose.yml: VALID"
else
  echo "docker-compose.yml: TIDAK VALID"
fi
if docker compose -f "$ROOT/docker-compose.dev.yml" config >/dev/null 2>&1; then
  echo "docker-compose.dev.yml: VALID"
else
  echo "docker-compose.dev.yml: TIDAK VALID"
fi

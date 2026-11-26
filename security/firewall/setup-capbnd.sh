#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Mengisi CapBnd dengan CAP_NET_ADMIN = CAP_NET_ADMIN saat proses diluncurkan.
# Dapat dijalankan pada host (privileged) atau dengan --dry-run untuk simulasi.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[SIMULASI] $*"
  else
    "$@"
  fi
}

echo "=========================================="
echo " Setup CapBnd = CAP_NET_ADMIN"
echo "=========================================="
echo "Mode: $([ "$DRY_RUN" -eq 1 ] && echo dry-run || echo aktif)"

echo
echo "[1] Bounding set saat ini"
grep CapBnd /proc/self/status
capsh --print 2>/dev/null | grep -E '^Current:|^Bounding set:' || true

echo
echo "[2] Pasang unit systemd dengan CapabilityBoundingSet"
UNIT="$ROOT/systemd/infinity-security.service"
if grep -q "CapabilityBoundingSet=CAP_NET_ADMIN" "$UNIT" 2>/dev/null; then
  echo "Unit sudah berisi CapabilityBoundingSet=CAP_NET_ADMIN:"
  grep -E "CapabilityBoundingSet|AmbientCapabilities" "$UNIT"
  run cp "$UNIT" /etc/systemd/system/infinity-security.service
  run systemctl daemon-reload
  run systemctl enable --now infinity-security
else
  echo "Unit tidak ditemukan atau tidak memiliki direktif tersebut."
fi

echo
echo "[3] Konfigurasi Docker (cap_add NET_ADMIN)"
if command -v docker >/dev/null 2>&1; then
  run docker compose -f "$ROOT/docker-compose.yml" up -d --build
else
  echo "Docker CLI tidak tersedia; gunakan host dengan Docker."
fi

echo
echo "[4] File capability pada iptables"
if command -v setcap >/dev/null 2>&1 && command -v iptables >/dev/null 2>&1; then
  run setcap cap_net_admin+ep "$(command -v iptables)"
  run getcap "$(command -v iptables)"
else
  echo "setcap/iptables belum tersedia di jalur ini."
fi

echo
echo "[5] Verifikasi"
echo "Perintah verifikasi (jalankan setelah proses diluncurkan ulang):"
echo "  capsh --print"
echo "  python3 $ROOT/security/security_cli.py firewall capability"
echo "  bash $ROOT/security/firewall/install-net-admin.sh"
echo "=========================================="

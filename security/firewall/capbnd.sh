#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Peluncur dengan CapBnd yang memuat CAP_NET_ADMIN.
#
# PENTING: CapBnd (bounding set) HANYA bisa dikurangi oleh proses berjalan
# (prctl PR_CAPBSET_DROP), tidak bisa ditambah. Agar bit 12 (CAP_NET_ADMIN)
# muncul di CapBnd, proses HARUS diluncurkan oleh parent yang memilikinya —
# yaitu kernel/host runtime. Di container ini CapBnd = 0, jadi mustahil.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=== CapBnd saat ini ==="
grep CapBnd /proc/self/status
python3 - <<'PY'
import sys
sys.path.insert(0, '.')
from security.blue.capabilities import bounding_capabilities
print('Daftar:', bounding_capabilities() or '(kosong)')
PY

echo
echo "=== Strategi peluncuran dengan CapBnd berisi CAP_NET_ADMIN ==="

echo "[1] capsh (jika tersedia)"
if command -v capsh >/dev/null 2>&1; then
  echo "capsh --caps='cap_net_admin+eip' -- bash -c 'grep CapBnd /proc/self/status'"
else
  echo "capsh tidak tersedia"
fi

echo "[2] setpriv (jika tersedia)"
if command -v setpriv >/dev/null 2>&1; then
  echo "setpriv --bounding-set=+cap_net_admin -- bash -c 'grep CapBnd /proc/self/status'"
else
  echo "setpriv tidak tersedia"
fi

echo "[3] systemd (host with systemd)"
echo "systemctl edit infinity-security → CapabilityBoundingSet=CAP_NET_ADMIN"
echo "Lihat: systemd/infinity-security.service"

echo "[4] Docker (host with Docker)"
echo "docker run --cap-add=NET_ADMIN --network host ..."
echo "Lihat: docker-compose.yml"

echo
echo "=== Verifikasi setelah diluncurkan ulang ==="
echo "python3 security/security_cli.py firewall capability"
echo "python3 security/firewall/install-net-admin.sh"

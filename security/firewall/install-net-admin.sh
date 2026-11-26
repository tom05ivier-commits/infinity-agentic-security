#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Installer CAP_NET_ADMIN + firewall kernel satu langkah.
# JALANKAN DI HOST yang memiliki CAP_NET_ADMIN (bukan container tanpa capability).
#
#   sudo bash security/firewall/install-net-admin.sh
#
# Skrip ini:
#   1. memeriksa CAP_NET_ADMIN
#   2. memasang iptables bila belum ada
#   3. menerapkan baseline aturan melalui FirewallAgent(dry_run=False)
#   4. memverifikasi aturan dengan iptables -S
#   5. menulis laporan ke security/reports/firewall_kernel.json

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "=========================================="
echo " Installer Firewall CAP_NET_ADMIN"
echo "=========================================="

echo "[1/5] Cek CAP_NET_ADMIN..."
CAP_STATE="$(python3 security/security_cli.py firewall capability 2>/dev/null)"
CAPABLE="$(printf '%s' "$CAP_STATE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cap_net_admin"])' 2>/dev/null || echo False)"
if [ "$CAPABLE" != "True" ]; then
  echo "GAGAL: CAP_NET_ADMIN tidak tersedia pada proses ini."
  echo "$CAP_STATE"
  echo
  echo "Jalankan ulang dari host dengan salah satu cara:"
  echo "  docker run --cap-add=NET_ADMIN --network host ..."
  echo "  sudo setcap cap_net_admin+ep \"\$(command -v iptables)\""
  echo "  sudo systemctl enable --now infinity-security"
  exit 1
fi
echo "OK: CAP_NET_ADMIN tersedia."

echo "[2/5] Cek / pasang iptables..."
if ! command -v iptables >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq iptables || {
      echo "GAGAL: tidak dapat memasang iptables."; exit 1;
    }
  else
    echo "GAGAL: iptables absen dan apt-get tidak tersedia."; exit 1;
  fi
fi
echo "OK: $(command -v iptables)"

echo "[3/5] Terapkan baseline aturan firewall kernel..."
python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))

from security.blue.firewall_agent import FirewallAgent

agent = FirewallAgent(dry_run=False)
results = {
    "deny_telnet": agent.deny_port(23).to_dict(),
    "allow_ssh": agent.allow_port(22).to_dict(),
    "block_test_ip": agent.block_ip("203.0.113.66").to_dict(),
}
failed = [k for k, v in results.items() if v["returncode"] != 0]
report = {
    "status": "FAILED" if failed else "APPLIED",
    "mode": "kernel-iptables",
    "failed": failed,
    "rules": results,
}
out = root / "security" / "reports" / "firewall_kernel.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
raise SystemExit(1 if failed else 0)
PY
echo "OK: aturan diterapkan."

echo "[4/5] Verifikasi aturan kernel..."
iptables -S | head -20 || { echo "GAGAL: iptables -S gagal."; exit 1; }

echo "[5/5] Status akhir..."
python3 security/security_cli.py firewall debug 2>/dev/null | head -20
echo "=========================================="
echo "SELESAI: firewall kernel aktif."
echo "Laporan: security/reports/firewall_kernel.json"
echo "=========================================="

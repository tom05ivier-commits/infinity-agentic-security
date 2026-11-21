#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Provisioning CAP_NET_ADMIN untuk semua komponen yang membutuhkannya.
# Mencoba beberapa strategi secara berurutan dan melaporkan mana yang berhasil.
# TIDAK melakukan perubahan destruktif; kegagalan dicatat, bukan dihentikan.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

has_cap() {
  "$PYTHON" - <<'PY' 2>/dev/null
from security.blue.capabilities import has_cap_net_admin
print('yes' if has_cap_net_admin() else 'no')
PY
}

try() {
  local name="$1"; shift
  echo "--- ${name} ---"
  if "$@"; then
    echo "STATUS: berhasil"
    return 0
  else
    echo "STATUS: gagal (dilewati)"
    return 1
  fi
}

echo "=========================================="
echo " Provisioning CAP_NET_ADMIN"
echo "=========================================="
echo "Keadaan awal: CAP_NET_ADMIN = $(cd "$ROOT" && has_cap)"

echo
echo "[1] capsh ambient capability"
if command -v capsh >/dev/null 2>&1; then
  try "capsh (verifikasi nyata)" env PYTHONPATH="$ROOT" \
    capsh --addamb=cap_net_admin -- "$PYTHON" -c \
      "from security.blue.capabilities import has_cap_net_admin; raise SystemExit(0 if has_cap_net_admin() else 1)"
else
  echo "capsh tidak tersedia"
fi

echo
echo "[2] setpriv ambient + bounding capability"
if command -v setpriv >/dev/null 2>&1; then
  if ! try "setpriv (cap_net_admin)" setpriv \
        --bounding-set=+cap_net_admin --ambient-caps=+cap_net_admin -- id; then
    try "setpriv (net_admin)" setpriv \
      --bounding-set=+net_admin --ambient-caps=+net_admin -- id
  fi
else
  echo "setpriv tidak tersedia"
fi

echo
echo "[3] file capability pada biner iptables"
if command -v setcap >/dev/null 2>&1; then
  BIN="$(command -v iptables || true)"
  if [ -n "$BIN" ]; then
    try "setcap" setcap cap_net_admin+ep "$BIN"
  else
    echo "biner iptables tidak ditemukan"
  fi
else
  echo "setcap tidak tersedia"
fi

echo
echo "[4] user namespace (CAP_NET_ADMIN di namespace baru)"
if command -v unshare >/dev/null 2>&1; then
  try "unshare (verifikasi nyata)" env PYTHONPATH="$ROOT" \
    unshare --user --map-root-user --net "$PYTHON" -c \
      "from security.blue.capabilities import has_cap_net_admin; raise SystemExit(0 if has_cap_net_admin() else 1)"
else
  echo "unshare tidak tersedia"
fi

echo
echo "[5] Docker capability (--cap-add=NET_ADMIN)"
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "Docker daemon terhubung; compose sudah mencantumkan cap_add: NET_ADMIN"
    echo "Jalankan: docker compose up -d --build"
  else
    echo "Docker CLI ada tetapi daemon tidak terhubung."
    echo "Jalankan di host: docker run --cap-add=NET_ADMIN ..."
  fi
else
  echo "Docker CLI tidak tersedia"
fi

echo
echo "[6] systemd AmbientCapabilities"
if [ -f "$ROOT/systemd/infinity-security.service" ]; then
  echo "Unit tersedia: systemd/infinity-security.service"
  echo "Pasang: sudo cp systemd/infinity-security.service /etc/systemd/system/"
  echo "        sudo systemctl daemon-reload && sudo systemctl enable --now infinity-security"
else
  echo "Unit systemd tidak ditemukan"
fi

echo
echo "=========================================="
echo "Instalasi firewall sekali jalan (di host dengan capability):"
echo "  sudo bash $ROOT/security/firewall/install-net-admin.sh"
echo
echo "Keadaan akhir: CAP_NET_ADMIN = $(cd "$ROOT" && has_cap)"
echo "Catatan: capability HARUS diberikan oleh host/runtime saat proses dimulai."
echo "Jika tetap 'no', jalankan ulang sistem dari host dengan salah satu metode di atas."
echo "=========================================="

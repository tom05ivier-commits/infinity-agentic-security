#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Bangkitkan ulang laporan yang dibaca penghitung skor pada clone kosong.
# Tidak ada kredensial yang dibaca, ditulis, atau ditampilkan.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[bootstrap] kunci API lokal (per pemasangan)"
./api-key.sh ensure >/dev/null

echo "[bootstrap] menyiapkan lab"
python3 security/security_cli.py lab >/dev/null

echo "[bootstrap] latihan firewall"
python3 security/security_cli.py firewall-drill >/dev/null 2>&1

echo "[bootstrap] verifikasi kepatuhan"
python3 security/security_cli.py verify >/dev/null

echo "[bootstrap] rantai penyempurnaan keamanan"
python3 security/security_cli.py sempurnakan --times 3 --intensity moderate >/dev/null 2>&1

echo "[bootstrap] verifikasi dan sintesis chip"
python3 chip/chip_cli.py verify >/dev/null
python3 chip/chip_cli.py synth >/dev/null
python3 chip/chip_cli.py iverilog >/dev/null

echo "[bootstrap] paket publik yang disanitasi"
bash prepare_github.sh >/dev/null 2>&1

echo "[bootstrap] skor akhir"
python3 security/security_cli.py score --json
python3 chip/chip_cli.py score

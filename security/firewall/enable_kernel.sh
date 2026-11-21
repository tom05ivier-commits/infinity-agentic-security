#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Mengaktifkan enforcement firewall kernel HANYA jika CAP_NET_ADMIN tersedia.
# Skrip ini tidak dapat menambahkan capability dari dalam container — capability
# harus diberikan oleh host/container runtime sebelum proses dimulai.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[*] Memeriksa capability & backend..."
python3 "$ROOT/security/security_cli.py" firewall capability

echo "[*] Mencoba menerapkan aturan ke kernel..."
python3 - "$ROOT" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root))

from security.blue.capabilities import status
from security.blue.firewall_agent import FirewallAgent

state = status()
if not state["kernel_enforcement"]:
    print("GAGAL: kernel enforcement tidak tersedia.")
    print("Remediasi:", state["remediation"])
    raise SystemExit(1)

agent = FirewallAgent(dry_run=False)
for result in (
    agent.deny_port(23),
    agent.allow_port(22),
    agent.block_ip("203.0.113.66"),
):
    print(result.command, "->", result.returncode)
print("Aturan kernel berhasil diterapkan.")
PY

#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Menyambungkan Playwright MCP ke Chrome Beta di host melalui CDP.
# Endpoint harus dibuka di host, misalnya:
#   chrome-beta --remote-debugging-port=9222 --user-data-dir=/path/profil
# lalu endpoint bisa dijangkau container (host IP / port-forward).

set -euo pipefail
ENDPOINT="${1:-${AGENTY_CDP_ENDPOINT:-}}"
CONFIG="/usr/share/opencode/playwright-mcp.json"
BACKUP="/usr/share/opencode/playwright-mcp.json.local-backup"

if [ -z "$ENDPOINT" ]; then
  echo "GAGAL: endpoint CDP belum diberikan." >&2
  echo "Contoh: bash connect_host_chrome.sh http://192.168.1.5:9222" >&2
  exit 1
fi
ENDPOINT="${ENDPOINT%/}"

echo "[*] Menguji endpoint ${ENDPOINT} ..."
if ! curl -fsS --max-time 5 "$ENDPOINT/json/version" > /tmp/opencode/cdp-version.json; then
  echo "GAGAL: endpoint tidak merespons. Pastikan Chrome Beta berjalan dengan" >&2
  echo "--remote-debugging-port dan bisa dijangkau dari container." >&2
  exit 1
fi
python3 -c "import json; d=json.load(open('/tmp/opencode/cdp-version.json')); print('Browser:', d.get('Browser','unknown'))"

if [ ! -f "$BACKUP" ] && [ -f "$CONFIG" ]; then
  cp "$CONFIG" "$BACKUP"
  echo "[*] Backup konfigurasi disimpan: $BACKUP"
fi

cat > "$CONFIG" <<EOF
{
  "browser": {
    "launchOptions": {
      "args": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu"
      ]
    },
    "cdpEndpoint": "${ENDPOINT}"
  }
}
EOF

echo "[✓] Playwright MCP kini memakai Chrome Beta host via CDP."
echo "    Restart sesi/MCP agar perubahan aktif."
echo "    Kembali ke mode lokal: cp $BACKUP $CONFIG"

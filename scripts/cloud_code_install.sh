#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Pasang/fix dependensi CLI Cloud Code di lingkungan IT Agenty.
# Claude Code sudah terpasang lewat npm global; Google Cloud SDK sudah ada
# di /root/google-cloud-sdk tetapi symlink /usr/local/bin/gcloud rusak.
# Tidak ada kredensial, login, atau aksi cloud yang dijalankan di sini.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT="$ROOT/system/reports/cloud_code_install.json"
TMP="/tmp/opencode/cloud-code-install"
mkdir -p "$TMP" "$(dirname "$REPORT")"

SKAFFOLD_URL="https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-arm64"
MINIKUBE_URL="https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64"
CODE_URL="https://update.code.visualstudio.com/latest/linux-arm64/stable"
CODE_ROOT="/usr/local/lib/vscode"

status_claude="TIDAK_ADA"
status_gcloud="TIDAK_ADA"
status_kubectl="TIDAK_ADA"
status_skaffold="TIDAK_ADA"
status_minikube="TIDAK_ADA"
status_code="TIDAK_ADA"

if command -v claude >/dev/null 2>&1; then status_claude="ADA"; fi
if command -v kubectl >/dev/null 2>&1; then status_kubectl="ADA"; fi


# Perbaiki symlink gcloud yang rusak: ganti dengan wrapper yang memanggil
# SDK langsung. SDK tetap sumber kebenaran, wrapper hanya menetapkan root.
GCLOUD_SDK="/root/google-cloud-sdk/bin/gcloud"
if [ -x "$GCLOUD_SDK" ]; then
  if ! gcloud version >/dev/null 2>&1; then
    printf '#!/bin/sh\nexec %s "$@"\n' "$GCLOUD_SDK" > "$TMP/gcloud-wrapper"
    install -m 0755 "$TMP/gcloud-wrapper" /usr/local/bin/gcloud
  fi
  if gcloud version >/dev/null 2>&1; then status_gcloud="ADA"; fi
fi

install_binary() {
  name="$1"; url="$2"
  if command -v "$name" >/dev/null 2>&1 && "$name" version >/dev/null 2>&1; then
    echo "$name: sudah terpasang"
    return 0
  fi
  # Lanjutkan unduhan yang terputus (misalnya saat server restart).
  expected="$(curl -sSI -L --max-time 20 "$url" | tr -d '\r' \
    | awk 'tolower($1)=="content-length:" {n=$2} END{print n}')"
  actual="$(stat -c %s "$TMP/$name" 2>/dev/null || echo 0)"
  if [ -n "${expected:-}" ] && [ "$actual" -lt "$expected" ]; then
    echo "$name: melanjutkan unduhan ($actual/$expected byte)"
    curl -C - -fsSL --retry 3 --max-time 900 -o "$TMP/$name" "$url"
  elif [ "$actual" -eq 0 ]; then
    echo "$name: mengunduh biner resmi..."
    curl -fsSL --retry 3 --max-time 900 -o "$TMP/$name" "$url"
  fi
  actual="$(stat -c %s "$TMP/$name" 2>/dev/null || echo 0)"
  if [ -n "${expected:-}" ] && [ "$actual" != "$expected" ]; then
    echo "$name: ukuran tidak cocok ($actual/$expected), unduh ulang" >&2
    rm -f "$TMP/$name"
    curl -fsSL --retry 3 --max-time 900 -o "$TMP/$name" "$url"
    actual="$(stat -c %s "$TMP/$name" 2>/dev/null || echo 0)"
  fi
  test -s "$TMP/$name"
  install -m 0755 "$TMP/$name" "/usr/local/bin/$name"
  echo "$name: terpasang"
}

install_binary skaffold "$SKAFFOLD_URL" || echo "skaffold: gagal dipasang" >&2
install_binary minikube "$MINIKUBE_URL" || echo "minikube: gagal dipasang" >&2

if command -v skaffold >/dev/null 2>&1 && skaffold version >/dev/null 2>&1; then status_skaffold="ADA"; fi
if command -v minikube >/dev/null 2>&1 && minikube version >/dev/null 2>&1; then status_minikube="ADA"; fi

# VS Code resmi (MIT) dipasang sebagai biner `code` untuk peran IDE wajib.
# Di lingkungan headless/root dipakai wrapper --no-sandbox + user-data-dir;
# tidak ada login, telemetri, atau kredensial yang disentuh.
install_code() {
  if command -v code >/dev/null 2>&1 && code --version >/dev/null 2>&1; then
    echo "code: sudah terpasang"
    return 0
  fi
  if [ ! -x "$CODE_ROOT/bin/code" ]; then
    echo "code: mengunduh VS Code arm64 resmi..."
    curl -fL --retry 3 --max-time 900 -o "$TMP/code-arm64.tar.gz" "$CODE_URL"
    mkdir -p "$CODE_ROOT"
    tar -xzf "$TMP/code-arm64.tar.gz" -C "$CODE_ROOT" --strip-components=1
  fi
  cat > "$TMP/code-wrapper" <<'WRAP'
#!/bin/sh
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
exec /usr/local/lib/vscode/bin/code --no-sandbox --user-data-dir=/root/.vscode-data "$@"
WRAP
  install -m 0755 "$TMP/code-wrapper" /usr/local/bin/code
  code --version >/dev/null 2>&1
}
install_code || echo "code: gagal dipasang" >&2
if command -v code >/dev/null 2>&1 && code --version >/dev/null 2>&1; then status_code="ADA"; fi

cat > "$REPORT" <<EOF
{
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "owner": "Tomi vier",
  "license": "Tom05ivier-commits-1.0",
  "claude_code": "$status_claude",
  "gcloud": "$status_gcloud",
  "kubectl": "$status_kubectl",
  "skaffold": "$status_skaffold",
  "minikube": "$status_minikube",
  "code": "$status_code"
}
EOF

echo "Laporan: $REPORT"
cat "$REPORT"

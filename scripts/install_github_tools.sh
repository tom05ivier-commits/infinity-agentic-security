#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Pasang CLI yang tercantum di PLATFORM_CLIS.md yang belum tersedia.
# Read-only terhadap data pribadi; tidak menyimpan kredensial apa pun.

set -euo pipefail

BIN_DIR="${BIN_DIR:-/usr/local/bin}"
TMP_DIR="$(mktemp -d /tmp/opencode/gh-tools.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

log() { printf '[install] %s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

install_bin() {
  local name="$1" src="$2"
  install -m 0755 "$src" "$BIN_DIR/$name"
  log "$name terpasang di $BIN_DIR/$name"
}

log "arsitektur: $(uname -m) / OS: $(uname -s)"

# 1. Crossplane CLI (kubectl plugin + binary mandiri)
if ! have crossplane; then
  log "mengunduh crossplane CLI"
  curl -fsSL --max-time 120 "https://cli.crossplane.io/stable/current/bin/linux_arm64/crossplane" \
    -o "$TMP_DIR/crossplane"
  install_bin crossplane "$TMP_DIR/crossplane"
else
  log "crossplane sudah ada, dilewati"
fi

# 2. Argo CD CLI
if ! have argocd; then
  log "mengunduh argocd v3.6.2"
  curl -fsSL --max-time 120 "https://github.com/argoproj/argo-cd/releases/download/v3.6.2/argocd-linux-arm64" \
    -o "$TMP_DIR/argocd"
  install_bin argocd "$TMP_DIR/argocd"
else
  log "argocd sudah ada, dilewati"
fi

# 3. HashiCorp Vault CLI
if ! have vault; then
  log "mengunduh vault v2.2.2"
  curl -fsSL --max-time 180 "https://releases.hashicorp.com/vault/2.2.2/vault_2.2.2_linux_arm64.zip" \
    -o "$TMP_DIR/vault.zip"
  unzip -q -o "$TMP_DIR/vault.zip" -d "$TMP_DIR/vault"
  install_bin vault "$TMP_DIR/vault/vault"
else
  log "vault sudah ada, dilewati"
fi

# 4. Pulumi CLI
if ! have pulumi; then
  log "mengunduh pulumi v3.277.0"
  curl -fsSL --max-time 180 "https://get.pulumi.com/releases/sdk/pulumi-v3.277.0-linux-arm64.tar.gz" \
    -o "$TMP_DIR/pulumi.tar.gz"
  tar -xzf "$TMP_DIR/pulumi.tar.gz" -C "$TMP_DIR"
  for f in "$TMP_DIR"/pulumi/pulumi "$TMP_DIR"/pulumi/pulumi-language-*; do
    [ -f "$f" ] && install_bin "$(basename "$f")" "$f"
  done
else
  log "pulumi sudah ada, dilewati"
fi

# 5. StackGen CLI
if ! have stackgen; then
  log "mengunduh stackgen v0.82.0"
  curl -fsSL --max-time 120 "https://releases.stackgen.com/binaries/stackgen-cli/v0.82.0/stackgen-cli_0.82.0_linux_arm64.tar.gz" \
    -o "$TMP_DIR/stackgen.tar.gz"
  tar -xzf "$TMP_DIR/stackgen.tar.gz" -C "$TMP_DIR"
  install_bin stackgen "$TMP_DIR/stackgen"
else
  log "stackgen sudah ada, dilewati"
fi

# 6. Kilo CLI
if ! have kilo; then
  log "mengunduh kilo v7.8.32"
  curl -fsSL --max-time 120 "https://github.com/Kilo-Org/kilocode/releases/download/v7.8.32/kilo-linux-arm64.tar.gz" \
    -o "$TMP_DIR/kilo.tar.gz"
  tar -xzf "$TMP_DIR/kilo.tar.gz" -C "$TMP_DIR"
  install_bin kilo "$TMP_DIR/kilo"
else
  log "kilo sudah ada, dilewati"
fi

log "selesai"

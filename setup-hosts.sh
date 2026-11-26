#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Memasang entri host lokal secara idempoten ke /etc/hosts.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTS="${HOSTS_FILE:-/etc/hosts}"
MARK_BEGIN="# BEGIN infinity-hosts (Tom05ivier-commits)"
MARK_END="# END infinity-hosts"

if [ ! -w "$HOSTS" ]; then
  echo "Tidak dapat menulis $HOSTS. Jalankan dengan root atau set HOSTS_FILE."
  exit 1
fi

# Hapus blok lama bila ada (termasuk ejaan marker lama "Tom05-kommits"),
# lalu pasang versi terbaru agar tidak menumpuk di /etc/hosts.
if grep -qF '# BEGIN infinity-hosts' "$HOSTS" 2>/dev/null; then
  python3 - "$HOSTS" "$MARK_END" <<'PY'
import sys
from pathlib import Path
path, end = sys.argv[1], sys.argv[2]
lines = Path(path).read_text().splitlines()
out, skipping = [], False
for line in lines:
    stripped = line.strip()
    if stripped.startswith("# BEGIN infinity-hosts"):
        skipping = True
        continue
    if skipping and stripped == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)
Path(path).write_text("\n".join(out).rstrip() + "\n")
PY
fi

{
  echo ""
  echo "$MARK_BEGIN"
  grep -vE '^\s*#' "$ROOT/hosts" | grep -v '^\s*$' | sed 's/^/  /'
  echo "$MARK_END"
} >> "$HOSTS"

echo "Entri host terpasang di $HOSTS:"
grep -A6 -F "$MARK_BEGIN" "$HOSTS" || true

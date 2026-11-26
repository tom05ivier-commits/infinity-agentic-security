#!/usr/bin/env bash
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Menyegar salinan lokal aset chip.peruri.co.id. Skrip ini hanya berjalan saat
# container memiliki akses internet; mirror yang sudah ada tetap berfungsi
# offline tanpa menjalankannya.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="https://chip.peruri.co.id"
JS="index-BSzQsLdH.js"
CSS="index-DB7HzBui.css"
TABLER="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.48.0"
IDDS="https://unpkg.com/@idds/styles@1.6.33/dist/index.min.css"

mkdir -p "$HERE/assets/logo" "$HERE/assets/fonts"

get() {
  local timeout="${3:-45}"
  if ! curl -fsSL --max-time "$timeout" "$1" -o "$2"; then
    rm -f "$2"
    return 1
  fi
  echo "[+] $2"
}

get "$BASE/" "$HERE/index.source.html"
get "$BASE/assets/$JS" "$HERE/assets/$JS"
get "$BASE/assets/$CSS" "$HERE/assets/$CSS"
get "$BASE/assets/logo/favicon-32.png" "$HERE/assets/logo/favicon-32.png"
get "$BASE/assets/logo/logomark.svg" "$HERE/assets/logo/logomark.svg"
get "$BASE/assets/untuk-siapa-a.png" "$HERE/assets/untuk-siapa-a.png"
get "$BASE/assets/untuk-siapa-b.png" "$HERE/assets/untuk-siapa-b.png"
get "$BASE/assets/fonts/PeruriSans-Regular.woff2" "$HERE/assets/fonts/PeruriSans-Regular.woff2"
get "$BASE/assets/fonts/PeruriSans-Medium.woff2" "$HERE/assets/fonts/PeruriSans-Medium.woff2"
# CSS memakai path relatif "assets/img/..." dari dalam /assets/, sehingga
# URL akhirnya menjadi /assets/assets/img/... di situs aslinya.
mkdir -p "$HERE/assets/assets/img"
get "$BASE/assets/assets/img/katalog-bleed.webp" "$HERE/assets/assets/img/katalog-bleed.webp"
get "$BASE/assets/assets/img/band-glow.webp" "$HERE/assets/assets/img/band-glow.webp"
get "$BASE/materi_design_chip_pemula_v1.pdf" "$HERE/materi_design_chip_pemula_v1.pdf" 240
get "$TABLER/dist/tabler-icons.min.css" "$HERE/assets/tabler-icons.min.css"
get "$IDDS" "$HERE/assets/idds.min.css"

for font in tabler-icons.ttf tabler-icons.woff2 tabler-icons.woff; do
  get "$TABLER/dist/fonts/$font" "$HERE/assets/fonts/$font" || true
done

python3 - "$HERE" <<'PY'
import sys
from pathlib import Path

here = Path(sys.argv[1])
html = (here / "index.source.html").read_text(encoding="utf-8")

# Hilangkan skrip/gaya yang memerlukan jaringan. Gaya Tailwind sudah
# terkompilasi di berkas CSS Vite, jadi CDN runtime tidak diperlukan.
lines = []
for line in html.splitlines():
    if "tailwindcss/browser" in line:
        continue
    if "google.com/recaptcha" in line:
        continue
    if "fonts.googleapis.com" in line or "fonts.gstatic.com" in line:
        continue
    lines.append(line)
html = "\n".join(lines)

replacements = {
    "https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.48.0/tabler-icons.min.css": "assets/tabler-icons.min.css",
    "https://unpkg.com/@idds/styles@1.6.33/dist/index.min.css": "assets/idds.min.css",
    "/assets/logo/favicon-32.png": "assets/logo/favicon-32.png",
    "/assets/logo/logomark.svg": "assets/logo/logomark.svg",
    "/assets/index-BSzQsLdH.js": "assets/index-BSzQsLdH.js",
    "/assets/index-DB7HzBui.css": "assets/index-DB7HzBui.css",
}
for old, new in replacements.items():
    html = html.replace(old, new)

note = (
    "<!-- SPDX-License-Identifier: Tom05ivier-commits-1.0 -->\n"
    "<!-- Copyright (c) 2026 Tomi vier -->\n"
    "<!-- Salinan lokal untuk pembelajaran. Konten asli (c) PERURI & INA Digital. -->\n"
)
(here / "index.html").write_text(note + html, encoding="utf-8")
(here / "index.source.html").unlink()
print("[+] index.html ditulis ulang untuk akses lokal")
PY

echo "[✓] Mirror siap di $HERE"

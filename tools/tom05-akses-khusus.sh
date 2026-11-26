#!/usr/bin/env bash
# Kode perintah akses khusus Tom05 —Tomi vier.
# SPDX-License-Identifier: Tom05ivier-commits-1.0
#
# Semua aksi bersifat lokal/read-only kecuali `apikey` yang memerlukan
# --authorize eksplisit. Perintah gcloud HANYA dicetak, tidak dijalankan.

set -euo pipefail

ROOT="${TOM05_ROOT:-/root/workspace}"
EMAIL="${TOM05_OWNER_EMAIL:-owner@example.invalid}"
PY="${PYTHON:-python3}"

usage() {
  cat <<'EOF'
Penggunaan:
  tom05-akses-khusus.sh status     Verifikasi pemilik + lisensi + parity (read-only)
  tom05-akses-khusus.sh cert       Tampilkan keterangan sertifikat + SHA-256 LICENSE
  tom05-akses-khusus.sh apikey     Pastikan kunci API lokal ada (butuh --authorize)
  tom05-akses-khusus.sh gcloud     Cetak perintah IAM gcloud untuk dijalankan manual
  tom05-akses-khusus.sh semua      Jalankan status + cert (tidak mengubah apa pun)
EOF
}

aksi="${1:-status}"
shift || true

case "$aksi" in
  status)
    "$PY" "$ROOT/system/owner_access.py" status --email "$EMAIL"
    ;;
  cert)
    "$PY" "$ROOT/system/owner_access.py" status --email "$EMAIL" \
      | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("Sertifikat:", d["sertifikat"]["path"]); print("Status   :", d["sertifikat"]["status"]); print("Lisensi  :", d["lisensi"]["status"])'
    echo -n "SHA-256 LICENSE klon: "
    sha256sum "$ROOT/provider-tom05/LICENSE" | cut -d' ' -f1
    ;;
  apikey)
    "$PY" "$ROOT/system/owner_access.py" apikey-ensure --authorize "$@"
    ;;
  gcloud)
    "$PY" "$ROOT/system/owner_access.py" gcloud-commands --email "$EMAIL"
    ;;
  semua)
    "$PY" "$ROOT/system/owner_access.py" status --email "$EMAIL"
    echo -n "SHA-256 LICENSE klon: "
    sha256sum "$ROOT/provider-tom05/LICENSE" | cut -d' ' -f1
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

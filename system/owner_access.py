# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Akses khusus pemilik Tom05 — verifikasi, kunci lokal, dan perintah cloud.

Prinsip:
  * email pemilik diverifikasi terhadap konfigurasi lokal, bukan dari chat;
  * status lisensi dan kesetaraan model bersifat read-only;
  * kunci API lokal dibuat lewat api_keygen — nilai kunci TIDAK PERNAH dicetak;
  * perintah gcloud hanya dihasilkan sebagai teks, tidak dijalankan di sini.

Tidak ada kredensial yang dibaca, disimpan, atau dikirim oleh modul ini.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OWNER_EMAIL = "owner@example.invalid"
OWNER_NAME = "Tomi vier"
MODEL = "tom05/tom05-flash-free"
CERTIFICATE = ROOT / "docs" / "SERTIFIKAT-LISENSI-provider-tom05.md"
CLONE = ROOT / "provider-tom05"


def _jalan(perintah: list[str], timeout: int = 40) -> dict[str, Any]:
    try:
        hasil = subprocess.run(
            perintah,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"exit": None, "error": type(exc).__name__}
    return {"exit": hasil.returncode, "stdout": hasil.stdout.strip(), "stderr": hasil.stderr.strip()}


def verifikasi_email(email: str) -> dict[str, Any]:
    diharapkan = os.environ.get("TOM05_OWNER_EMAIL", OWNER_EMAIL).strip().lower()
    given = email.strip().lower()
    return {
        "email_diminta": given,
        "email_pemilik_terkonfigurasi": diharapkan,
        "cocok": given == diharapkan,
        "nama_pemilik": OWNER_NAME if given == diharapkan else None,
        "sumber": "TOM05_OWNER_EMAIL atau nilai bawaan",
    }


def status_lisensi() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "system"))
    try:
        from license_formalization import status  # type: ignore

        return status()
    except Exception as exc:  # noqa: BLE001
        return {"status": "TIDAK_TERSEDIA", "error": type(exc).__name__}


def kesetaraan_model() -> dict[str, Any]:
    hasil = _jalan([sys.executable, "system/model_parity.py"])
    if hasil.get("exit") != 0 or not hasil.get("stdout"):
        return {"status": "TIDAK_TERSEDIA", "detail": hasil}
    try:
        return json.loads(hasil["stdout"])
    except json.JSONDecodeError:
        return {"status": "TIDAK_TERSEDIA", "detail": hasil}


def status() -> dict[str, Any]:
    email = verifikasi_email(os.environ.get("TOM05_OWNER_EMAIL", OWNER_EMAIL))
    return {
        "akses": "read-only",
        "model": MODEL,
        "pemilik": email,
        "lisensi": status_lisensi(),
        "parity": kesetaraan_model(),
        "sertifikat": {
            "path": str(CERTIFICATE.relative_to(ROOT)),
            "ada": CERTIFICATE.is_file(),
            "status": "DRAF — menunggu tanda tangan pemilik",
        },
        "clone_provider": {
            "path": str(CLONE.relative_to(ROOT)),
            "ada": CLONE.is_dir(),
        },
        "catatan": (
            "Verifikasi ini tidak menerbitkan hak, tidak membuat kredensial, "
            "dan tidak menggantikan tanda tangan manual pemilik."
        ),
    }


def terbitkan_kunci_lokal() -> dict[str, Any]:
    """Idempoten: hanya membuat kunci bila belum ada; nilai kunci tidak dicetak."""
    ensure = _jalan([sys.executable, "system/api_keygen.py", "ensure"])
    status_key = _jalan([sys.executable, "system/api_keygen.py", "status", "--json"])
    audit = _jalan([sys.executable, "system/api_keygen.py", "guard"])
    return {
        "akses": "lokal",
        "model": MODEL,
        "pembuatan": ensure,
        "status": status_key,
        "audit_privasi": audit,
        "peringatan": "Nilai kunci sengaja tidak ditampilkan. Gunakan api_keygen load hanya di aplikasi.",
    }


def perintah_gcloud(email: str) -> dict[str, Any]:
    """Hasilkan perintah untuk dijalankan manual oleh pemilik; JANGAN eksekusi."""
    proyek = os.environ.get("TOM05_GCLOUD_PROJECT", "<PROJECT_ID>")
    return {
        "diesekusi": False,
        "alasan": "Membutuhkan login dan izin akun Google pemilik.",
        "email": email.strip().lower(),
        "perintah": [
            "curl -sS https://sdk.cloud.google.com/ -o /tmp/install_google_cloud_sdk.bash",
            "# Periksa isi skrip dahulu: less /tmp/install_google_cloud_sdk.bash",
            "# Setelah disetujui: bash /tmp/install_google_cloud_sdk.bash",
            "gcloud auth login",
            f"gcloud config set project {proyek}",
            f"gcloud projects get-iam-policy {proyek}",
            f"gcloud projects add-iam-policy-binding {proyek} "
            f"--member=user:{email.strip().lower()} --role=roles/viewer",
            "# Ulangi dengan role yang lebih sempit setelah policy ditinjau.",
        ],
        "catatan": (
            "Perintah terakhir mengubah IAM dan sengaja tidak dijalankan otomatis. "
            "Gunakan roles/viewer hanya jika itu memang keinginan pemilik."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="aksi", required=True)

    stat = sub.add_parser("status", help="Verifikasi pemilik + status lisensi/model (read-only)")
    stat.add_argument("--email", default=os.environ.get("TOM05_OWNER_EMAIL", OWNER_EMAIL))

    key = sub.add_parser("apikey-ensure", help="Pastikan kunci API lokal ada (nilai tidak dicetak)")
    key.add_argument("--authorize", action="store_true", help="Diperlukan agar perubahan lokal terjadi")

    cloud = sub.add_parser("gcloud-commands", help="Cetak perintah gcloud untuk dijalankan manual")
    cloud.add_argument("--email", default=os.environ.get("TOM05_OWNER_EMAIL", OWNER_EMAIL))

    args = parser.parse_args()

    if args.aksi == "status":
        hasil = status()
        hasil["pemilik"] = verifikasi_email(args.email)
    elif args.aksi == "apikey-ensure":
        if not args.authorize:
            hasil = {
                "diesekusi": False,
                "alasan": "Tambahkan --authorize untuk membuat kunci lokal.",
                "perintah": "tom05 --apikey-issue --authorize",
            }
        else:
            hasil = terbitkan_kunci_lokal()
    else:
        hasil = perintah_gcloud(args.email)

    print(json.dumps(hasil, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

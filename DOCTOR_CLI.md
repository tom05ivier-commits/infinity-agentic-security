<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Doctor CLI

Sumber: <https://share.google/jpjjYbNVgyu44Vwqi> → dokumentasi resmi
<https://doctor.cli/> / <https://github.com/estruyf/doctor>.

`doctor` adalah CLI untuk mengelola dokumentasi Markdown sebagai halaman
SharePoint. Terpasang di sistem sebagai paket npm global **@estruyf/doctor v2.3.0**.

## Perintah

| Perintah | Fungsi |
|---|---|
| `doctor init` | Membuat struktur folder & `doctor.json` |
| `doctor status` | Melihat perubahan yang akan dipublish (read-only) |
| `doctor publish` | Publish halaman & gambar ke SharePoint |
| `doctor workflow` | Generate GitHub Actions / Azure DevOps pipeline |
| `doctor setup` / `cleanup` | Pasang/hapus autocomplete |
| `doctor version` / `--help` | Versi & bantuan |

## Prinsip keamanan (dari dokumentasi resmi)

- `doctor init` **tidak pernah** menulis kata sandi sertifikat ke `doctor.json`.
- Kata sandi dibaca dari `DOCTOR_CERTIFICATE_PASSWORD` atau diminta saat dipakai.
- Di CI/CD, gunakan repository secrets: `CERTIFICATE`, `CERTIFICATE_PASSWORD`,
  `APP_ID`, `TENANT_ID`, `SITE_URL`.
- `doctor status` aman untuk pipeline gate karena tidak mengubah apa pun.

## Penerapan di IT Agenty

- Terdaftar di `system/hy4_manager.py` sebagai CLI `doctor` (kind `npm`).
- Bisa dipasang ulang: `./manage_hy4.sh install-cli --name doctor`.
- Command OpenCode `doctor.md` tersedia untuk model `hy4-flash-free`.
- Tidak ada kredensial SharePoint yang disimpan di workspace ini.

## Verifikasi

```bash
doctor version
./manage_hy4.sh status | grep doctor
```

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Professor Messer — Arsip CLI (Rangkuman)

Sumber: <https://share.google/ZIOKVTkecGaqZPU7z> → arsip kategori **CLI**
di situs Professor Messer (Messer Studios LLC).

## Isi arsip

Kategori CLI memuat satu entri:

- **CompTIA A+ 220-702: 2.1 – Command Line Troubleshooting** (25 Jul 2010)
- Tautan: <https://www.professormesser.com/professor-messer-archives/a-plus-study-group/220-702/command-line-troubleshooting/>
- Deskripsi publik: video ini membahas perintah command line Windows untuk
  memanipulasi file, memformat disk, dan melakukan troubleshooting koneksi
  jaringan.

## Catatan hak cipta

Materi video, teks lengkap, dan merek Professor Messer adalah hak Messer Studios
LLC. Dokumen ini **hanya rangkuman deskripsi publik + tautan**, bukan salinan
materi. Jangan menyalin video, catatan, atau teks artikel ke repositori ini.

## Nilai untuk hy4

Pelajaran yang relevan untuk agen kami:

1. CLI adalah execution layer yang kuat bila perintahnya dipahami dengan benar.
2. Troubleshooting sistematis: identifikasi masalah → pilih perintah →
   verifikasi hasil → dokumentasikan.
3. Kategori keterampilan: file/disk, jaringan, dan utilitas command line Windows.
4. Pendekatan ini melengkapi `PLATFORM_CLIS.md` (CLI platform engineering)
   dan `security/` (diagnostik keamanan).

## Pemasangan ke model hy4

- Terdaftar di `advanced/knowledge.py` sebagai sumber pengetahuan.
- Terhubung di `AGENTS.md` dan `.github/copilot-instructions.md`.
- Command OpenCode `cli-troubleshoot.md` tersedia lewat `manage_hy4.sh commands`.

## Verifikasi

```bash
grep -n "PM_CLI" AGENTS.md advanced/knowledge.py
./manage_hy4.sh status
```

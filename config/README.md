<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Konfigurasi sistem — salinan terarsip

Tujuh file lampiran telah dicek dan **sudah berada di lokasi sistem yang tepat**.
Isinya identik persis dengan salinan sistem (diverifikasi dengan `diff`/`md5`),
jadi **tidak ada perubahan yang diperlukan pada sistem**.

Salinan di folder ini hanya sebagai arsip proyek, dengan struktur yang
mencerminkan path sistem aslinya.

## Peta lokasi

| File lampiran            | Lokasi sistem               | Fungsi                                      |
|--------------------------|-----------------------------|---------------------------------------------|
| `01-locale-fix.sh`       | `/etc/profile.d/`           | Paksa locale `id_ID.UTF-8` untuk login shell |
| `01-python-env.sh`       | `/etc/profile.d/`           | `PYTHONUNBUFFERED`, `PYTHONIOENCODING`, locale |
| `opencode-browser.sh`    | `/etc/profile.d/`           | Path & argumen Playwright/browser agent     |
| `opencode-layer-mcp.sh`  | `/etc/profile.d/`           | Pasang layer MCP opsional setelah mount `/root` |
| `opencode-node.sh`       | `/etc/profile.d/`           | Tambah Node.js ke `PATH`                    |
| `xermes-toolchains.sh`   | `/etc/profile.d/`           | Tambah Go & Cargo ke `PATH`                 |
| `rgb.txt`                | `/etc/X11/rgb.txt`          | Database nama warna X11 (754 baris)         |

## Catatan

- Enam skrip `profile.d` dimuat otomatis oleh login shell. Awalan `01-`
  memastikan locale dan env Python diterapkan **sebelum** skrip lain.
- Dua skrip（`01-locale-fix.sh`, `01-python-env.sh`）memiliki header
  `# Copyright (c) 2026 tom05ivier-commits — MIT License` **asli** dari sistem;
  header tersebut sengaja dipertahankan apa adanya pada salinan arsip ini.
- `rgb.txt` adalah file data Xorg standar (`$Xorg: rgb.txt,v 1.3 ...`),
  bukan kode, sehingga tidak diberi header lisensi tambahan.
- File baru yang dibuat agen tetap menggunakan lisensi `Tom05ivier-commits-1.0`.

## Verifikasi yang sudah dilakukan

- `diff` 6 skrip terhadap `/etc/profile.d/` → semua **IDENTIK**.
- `head`/`tail`/`wc -l` `rgb.txt` terhadap `/etc/X11/rgb.txt` → cocok (754 baris).
- `md5sum`: `09ee098b83d94c7c046d6b55ebe84ae1` untuk `rgb.txt` di kedua lokasi.

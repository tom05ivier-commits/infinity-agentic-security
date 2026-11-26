<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Mirror lokal chip.peruri.co.id

Salinan aset halaman muka **Sandbox Chip Merah Putih** (PERURI & INA Digital)
untuk keperluan pembelajaran di dalam container Infinity. Semua aset disimpan
di direktori ini dan tidak dimuat dari CDN saat halaman dibuka.

## Isi

- `index.html` — halaman asli yang sudah ditulis ulang agar memakai aset lokal.
- `assets/` — bundle Vite, CSS, font ikon Tabler, dan logo.
- `fetch.sh` — skrip penyegar mirror dari situs asli (butuh internet).

Skrip/gaya yang memerlukan jaringan sengaja dilewatkan: Tailwind runtime CDN
(sudah terkompilasi di `assets/index-*.css`), Google Fonts (fallback ke font
sistem), dan reCAPTCHA.

## Batasan

Bundle React asli memuat modul rute secara dinamis dan memanggil banyak endpoint
`/api/...` (autentikasi, proyek, repo, AI, runner). Karena itu mirror ini
mereproduksi **halaman muka** beserta asetnya. Router asli memakai path absolut,
jadi mirror disajikan sebagai document root di port **8770** oleh
`site/mirror_server.py`; rute seperti `/simulator` kini benar-benar memuat shell
aplikasi.

Aset tambahan yang ikut disalin: dua ilustrasi `untuk-siapa`, dua webp dekorasi,
font PeruriSans, dan PDF panduan `materi_design_chip_pemula_v1.pdf` (37 MB).
Server mirror juga mengembalikan JSON status untuk
`/api/auth/captcha-status`, `/api/auth/login-status`, dan `/api/users` agar
halaman masuk/daftar tidak gagal mengurai respons; proses autentikasi, proyek,
repo, dan AI tetap memerlukan backend PERURI.

Rute yang dikenal aplikasi asli antara lain `/simulasi`, `/simulator`,
`/panduan-pemula`, `/dokumentasi`, `/proyek`, `/masuk`, dan `/daftar`. Path
seperti `/katalog` bukan rute asli, sehingga badan halamannya kosong — katalog
adalah bagian dari halaman muka. Untuk simulasi yang benar-benar berfungsi
offline, gunakan `/chip/simulator.html` yang dibangun mandiri oleh IT Agenty.

## Menyegar

```bash
bash site/mirror/fetch.sh
```

Konten asli tetap menjadi hak PERURI & INA Digital. Replika dan pengembangan
mandiri mengikuti lisensi Tom05ivier-commits v1.0 untuk karya IT Agenty.

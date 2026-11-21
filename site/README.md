<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Situs statis IT Agenty

Kumpulan situs mandiri yang disajikan oleh `site/server.py` pada port **8769**.
Tidak ada CDN, framework, atau proses eksternal — semuanya berjalan di dalam
container Infinity dan tetap berfungsi tanpa internet.

## Daftar situs

| Path | Isi |
|---|---|
| `/` | Hub yang menautkan semua situs dan dashboard |
| `/chip/` | Replika mandiri Sandbox Chip Merah Putih (konten asli © PERURI & INA Digital) |
| `/chip/simulator.html` | Simulator HDL mini yang benar-benar berfungsi offline |
| `/agency/` | Landing page IT Agenty / Infinity Security Suite |
| `/mirror/` | Halaman penjelas mirror dan batasannya |
| `/mirror-info.html` | Berkas halaman penjelas tersebut |
| `/health` | Health check JSON untuk supervisor |

Portal komunitas berjalan terpisah di port **8781** lewat
`site/community/server.py` (layanan `community`). Ini karya original IT Agenty
dengan lisensi `Tom05ivier-commits-1.0`, bukan salinan atau turunan Symphony;
hub di atas menautkannya agar mudah ditemukan. Rinciannya ada di
`site/community/README.md` dan `docs/SYMPHONY-ANALYSIS.md`.

Mirror aplikasi asli berjalan terpisah di port **8770** lewat
`site/mirror_server.py` (layanan `mirror`). Router React asli memakai path
absolut, sehingga direktori `site/mirror/` harus menjadi document root. Port
8769 cukup menyajikan halaman penjelas; rute turunannya tetap difallback ke
halaman itu. Mirror menyalin aset lengkap termasuk PDF panduan 37 MB dan
menyediakan stub JSON untuk endpoint status autentikasi agar halaman masuk/daftar
tidak menampilkan galat parsing.

## Simulator

Simulator menerima subset Verilog: deklarasi `module`/`input`/`output`,
pernyataan `assign`, operator `+ - * & | ^ ~ << >>`, serta literal seperti
`4'b1010`. Ia menghasilkan delapan vektor uji, tabel hasil, dan bentuk gelombang
SVG. Draft tersimpan otomatis di `localStorage` dan dipulihkan saat halaman
dibuka; desain juga dapat disimpan dengan nama dan diunduh sebagai berkas `.v`.

Contoh: adder 4-bit, counter 4-bit, traffic light, dan AND gate.

## Menjalankan

Server sudah terdaftar di `system/services.json` sebagai layanan `sites`
(melalui `python3 system/cli.py service-add`), sehingga supervisor menjalankan
dan memantau otomatis:

```bash
python3 site/server.py 8769          # manual
python3 system/cli.py services       # lihat registry
curl http://127.0.0.1:8769/health    # health check
```

## Menyegar mirror

```bash
bash site/mirror/fetch.sh            # hanya bila ada akses internet
```

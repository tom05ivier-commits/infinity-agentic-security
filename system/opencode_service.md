<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Layanan OpenCode di Supervisor

Semua server OpenCode yang bukan instansi sesi diawasi supervisor lewat dua
jalur: pendaftaran statis di `system/services.json` dan watchdog dinamis
`system/opencode_watch.py`.

## Pendaftaran statis

| Nama layanan | Port | Health | Peran |
|---|---|---|---|
| `opencode` | 8786 | `/health` | Server API lokal utama |
| `opencode-42337` | 42337 | `/health` | Instansi tambahan yang diminta didaftarkan |

Keduanya memakai `scripts/opencode_serve.sh`, yang memanggil biner resmi
`/root/.opencode/bin/opencode` dengan opsi `serve --hostname 127.0.0.1
--port <port>`. Port bisa diberikan sebagai argumen pertama (dipakai registry
untuk instansi tambahan) atau lewat `AGENTY_OPENCODE_PORT`. Variabel `PORT`
tidak dipakai sesuai aturan proyek.

## Watchdog dinamis

Server OpenCode yang diluncurkan OpenChamber memakai port ephemeral yang
berubah tiap sesi, sehingga mustahil didaftarkan secara statis tanpa menjadi
usang. Layanan `opencode-watch` (kind `process`, tanpa port) mendeteksi semua
proses `opencode serve --port N`, mengecualikan `serve --service` dan server
web OpenChamber, lalu menjaga agar portnya tetap merespons dan menjalankan
ulang bila mati. Watchdog **tidak** mengubah `system/services.json`: izin
konfigurasi otomatis hanya mencakup kunci tertentu, jadi penambahan layanan
tetap lewat `./run_system.sh service-add`.

Laporan read-only: `system/reports/opencode_watch.json`. Cek cepat:

```bash
python3 system/opencode_watch.py report
python3 system/opencode_watch.py check
```

## Endpoint yang dipakai

- `/health` — liveness (200 dari UI/web server OpenCode).
- `/api/health` — API health; dapat mengembalikan 401 bila auth diperlukan.
  Supervisor dan watchdog memperlakukan 401 sebagai "hidup".

Layanan ini read-only dari sisi supervisor: tidak membaca kredensial, tidak
melakukan login cloud, dan tidak menjalankan aksi ofensif. Instansi OpenCode
yang melayani sesi kerja (`opencode serve --service`) sengaja tidak
disentuh agar sesi tidak terputus.

## Perubahan registry

Setiap perubahan registry wajib diikuti:

```bash
python3 chip/server_chip_gen.py
./run_system.sh infinity-connectivity
```

agar `chip/rtl/srv_opencode*.v` dan peta konektivitas tetap lengkap.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Infinity Computer System

Sistem komputer terpadu yang menyatukan **seluruh data yang sudah kita punya**
menjadi satu sumber kebenaran: identitas pemilik, lisensi, surat izin & kuasa,
konfigurasi lingkungan, dan telemetri keamanan.

## Komponen

| Modul | Fungsi |
|---|---|
| `core.py` | Mengumpulkan data dari berkas & modul menjadi satu `snapshot()` |
| `dashboard.py` | Membangkitkan `dashboard.html` mandiri |
| `server.py` | Server HTTP lokal (stdlib) untuk dashboard & API JSON |
| `cli.py` | Antarmuka baris perintah terpadu |
| `protection.py` | Daemon proteksi hardware berkelanjutan |

## Data yang digabungkan

- **Identitas:** `surat-kuasa-tandatangan.md` (nama, jabatan, kontak, tanda tangan digital).
- **Lisensi:** `LICENSE` (`Tom05ivier-commits-1.0`, pemilik Tomi vier).
- **Otorisasi:** `surat-izin-keamanan.md` + `surat-kuasa-tandatangan.md`.
- **Lingkungan:** 6 skrip `config/profile.d/`, `config/X11/rgb.txt` (754 warna), `sitecustomize.py`.
- **Keamanan:** policy firewall, daftar laporan, status `verify` dari `security/`.

## Cara pakai

```bash
./run_system.sh status              # ringkasan sistem
./run_system.sh snapshot            # JSON lengkap
./run_system.sh dashboard           # tulis dashboard.html
./run_system.sh serve --port 8765   # jalankan server lokal
./run_system.sh protect --seconds 10  # proteksi hardware berkelanjutan
./run_system.sh debug                 # diagnostik sistem terpadu
```

`protect` menggabungkan antivirus real-time (karantina otomatis), policy
firewall, dan korelasi SOC. Status periodik ditulis ke
`system/reports/protection_status.json`.

## Semua server yang dikelola supervisor

| Server | Port | Fungsi | Health |
|---|---|---|---|
| `server` | 8765 | Dashboard + API JSON sistem | `/api/health` |
| `protection` | — | Antivirus real-time + karantina + SOC | proses |
| `bridge` | 8766 | Copilot CLI → `hy4-flash-free` | `/v1/health` |
| `files` | 8767 | Server statis laporan & arsip workspace | `/` |

`./run_always.sh` menjaga keempatnya tetap hidup dan memulai ulang yang mati.
Heartbeat: `system/reports/heartbeat.json`.

### Always-on

Aturan permanen: **selalu jalankan komputer**. Jalankan `./run_always.sh`
(supervisor) — ia memulai ulang server dan daemon proteksi bila mati, serta
menulis heartbeat ke `system/reports/heartbeat.json`. Gunakan
`AGENTY_PORT` / `AGENTY_INTERVAL` untuk mengubah port & interval; variabel
`PORT` sengaja tidak dipakai agar tidak bentrok dengan lingkungan lain.

Endpoint server:

| Path | Keterangan |
|---|---|
| `/`, `/dashboard` | Dashboard HTML |
| `/api/snapshot` | Snapshot lengkap |
| `/api/health` | Status kesehatan |
| `/api/license` | Informasi lisensi |
| `/api/identity` | Identitas pemilik |

## Pengujian

```bash
python3 -m unittest discover -s system/tests -v
```

7 pengujian mencakup pemuatan identitas, lisensi, otorisasi, lingkungan,
kelengkapan snapshot, pembangkitan dashboard, dan sanitasi HTML.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

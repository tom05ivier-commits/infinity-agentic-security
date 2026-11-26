<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Chip Verifikasi untuk Setiap Server Localhost

## Sumber tunggal

`system/services.json` — 15 entri server. Generator `chip/server_chip_gen.py`
membuat satu modul RTL per server: `chip/rtl/srv_<nama>.v`.

## Status server saat verifikasi

| Server | Kind | Port | Health |
|---|---|---|---|
| server | http | 8765 | OK |
| protection | process | - | aktif (heartbeat) |
| bridge | http | 8766 | OK |
| files | http | 8767 | OK |
| public | process | - | dinonaktifkan (AGENTY_DISABLE_PUBLIC) |
| tunnel | process | - | dinonaktifkan (AGENTY_DISABLE_TUNNEL) |
| workflow | process | - | aktif (heartbeat) |
| sites | http | 8769 | OK |
| mirror | http | 8770 | OK |
| community | http | 8781 | OK |
| symphony | process | - | aktif (heartbeat) |
| tom05-provider | http | 8772 | OK |
| port-14713 | monitor | 14713 | PORT_TUTUP (sesuai catatan AGENTS.md) |
| chat-dispatch | process | - | aktif (heartbeat) |
| tom05-selfhost | http | 8773 | OK |

Supervisor dijalankan dengan `AGENTY_DISABLE_TUNNEL=1 AGENTY_DISABLE_PUBLIC=1`
(heartbeat 14/15 alive; yang tutup adalah monitor 14713 yang memang hanya
dipantau, bukan dijalankan).

## Logika chip per server

```
ready    = alive & healthy & enabled
degraded = alive & enabled & ~healthy
blocked  = ~alive | ~enabled
```

Tiga input → delapan kombinasi exhaustif per chip → **15 chip × 8 = 120 vektor**,
semua PASS. Model referensi: `chip/server_chip_reference.py`.

## Batas jujur

- Ini **chip verifikasi/logika status**, bukan fabrikasi silikon. Status
  `fabrication: NOT_READY` (tidak ada mitra/proses fisik yang sah).
- Tidak terhubung ke jaringan; hanya membaca registry dan menjalankan RTL.
- Tidak menambah server/port baru — semua sudah terdaftar di `services.json`.
- Jalur terpisah dari 10 modul utama: `chip/reference.py`, 2868 vektor,
  5960 check, dan skor 100/100 tidak berubah.

## Cara pakai

```bash
python3 chip/server_chip_gen.py          # regenerate RTL dari registry
python3 chip/server_chip_reference.py    # verifikasi 15 chip
python3 chip/chip_cli.py server-chip     # ringkasan JSON
python3 -m unittest chip.tests.test_server_chip -v
```

Lisensi: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.

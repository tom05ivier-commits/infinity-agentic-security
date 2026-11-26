<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# tom05_soc — System-on-Chip tom05 untuk Android Smartphone

`tom05_soc` adalah modul RTL baru di `chip/rtl/tom05_soc.v` yang menyatukan
jalur data model tom05/hy4 ke dalam satu System-on-Chip (SoC) yang ditujukan
untuk perangkat Android/smartphone. Ini adalah **desain logika digital**,
bukan fabrikasi silikon; status fabricasi tercatat `NOT_READY`.

## Tujuan

Menyediakan inti inferensi ringan yang bisa dipetakan ke jalur sensor ponsel
(kamera, IMU, atau layar) tanpa bergantung pada jaringan atau kredensial.
Semua daemon bersifat lokal dan dapat diverifikasi sepenuhnya di workspace.

## Pemetaan sinyal

| Sinyal | Lebar | Arah | Pemetaan smartphone |
|---|---|---|---|
| `cam0`–`cam3` | 2-bit | input | Empat jalur fitur sensor (kamera/IMU/touch/display) |
| `mode` | 1-bit | input | Bias konteks (mis. prioritas inferensi) |
| `irq_clear` | 1-bit | input | Sinyal acknowledge interrupt dari OS Android |
| `score[3:0]` | 4-bit | output | Skor fusi berbobot |
| `level[1:0]` | 2-bit | output | Hasil kuantisasi (keputusan model) |
| `irq` | 1-bit | output | Aktif bila `level[1]` tinggi dan interrupt belum di-clear |
| `ready` | 1-bit | output | Selalu 1 — jalur kombinasional, tanpa clock |

## Fungsi

```
score = (cam0 + 2*cam1 + 3*cam2 + 4*cam3 + mode) mod 16
level = score >> 2
irq   = level[1] & ~irq_clear
ready = 1
```

Bobot `1,2,3,4` identik dengan `hy4_dot4`, sehingga SoC mewarisi perilaku
akselerator hy4 yang sudah terverifikasi.

## Verifikasi

SoC mengikuti jalur verifikasi yang sama dengan sembilan modul chip lainnya
(total 10 modul termasuk `index_match4`):

```bash
python3 chip/chip_cli.py soc       # ringkasan + verifikasi 1.024 vektor
python3 chip/chip_cli.py verify    # 10 modul, 2.868 vektor
python3 chip/chip_cli.py synth     # 10 modul, 185 sel
python3 chip/chip_cli.py iverilog  # 2.868 vektor, 5.960 pengecekan
./site/chip/test_presets.sh       # preset tom05_soc di browser, 8 vektor
python3 chip/chip_cli.py score     # skor kualitas 100/100
tom05 --soc                        # akses lewat CLI tom05
```

Bukti: `chip/reports/chip_verification.json`, `chip/reports/chip_synthesis.json`,
`chip/reports/iverilog.json`, dan `chip/synth/tom05_soc.*`.

## Batasan

- SoC berjalan satu siklus kombinasional; tidak ada pipeline/clock domain.
- Tidak ada blok radio, modem, atau kriptografi — sengaja minimal.
- `level` 2-bit adalah keputusan model Referensi, bukan probabilitas kalibrasi.
- Integrasi ke sistem Android nyata memerlukan toolchain vendor dan tidak
  termasuk ruang lingkup izin ini.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

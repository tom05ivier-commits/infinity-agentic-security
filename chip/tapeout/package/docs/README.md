<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Infinity Mini Chip — RTL & Simulasi

Kumpulan desain digital kombinasional yang bisa disimulasikan langsung di
[Sandbox Chip Merah Putih](../site/chip/simulator.html) dan diverifikasi lewat
model referensi Python.

## Modul

| Modul | Fungsi | File RTL |
|---|---|---|
| `full_adder` | penjumlah 1-bit dengan carry-in/carry-out | `rtl/full_adder.v` |
| `mux2` | pemultiplexer 2 input | `rtl/mux2.v` |
| `decoder2` | dekoder 2-to-4 | `rtl/decoder2.v` |
| `parity4` | paritas ganjil 4-bit | `rtl/parity4.v` |
| `alu4` | ALU 4-bit: tambah, AND, OR, XOR | `rtl/alu4.v` |
| `hy4_dot4` | skor berbobot 4 fitur untuk model hy4 | `rtl/hy4_dot4.v` |
| `hy4_quant` | kuantisasi skor 4-bit menjadi level 2-bit | `rtl/hy4_quant.v` |
| `hy4_top` | inti akselerator hy4: dot product + kuantisasi | `rtl/hy4_top.v` |

`hy4_dot4` menghitung `(a0 + 2·a1 + 3·a2 + 4·a3) mod 16`, `hy4_quant`
menggeser skor dua bit ke kanan, dan `hy4_top` menggabungkan keduanya dalam
satu `assign` agar tetap kompatibel dengan subset Verilog simulator browser.
Metadata pemasangan ada di `hy4_chip.json`.

## Verifikasi

```bash
python3 chip/chip_cli.py verify   # RTL vs model referensi
python3 chip/chip_cli.py synth    # sintesis Yosys + laporan gate
python3 chip/chip_cli.py iverilog # lint + kompilasi + vvp testbench nyata
./site/chip/test_presets.sh       # preset hy4 di browser (Playwright)
python3 chip/chip_cli.py score    # skor kualitas 100/100 dari bukti
make chip-verify                  # semuanya sekaligus + scorecard
python3 -m unittest discover -s chip/tests -v
```

Hasil:
- `chip/reports/chip_verification.json` — **PASS, 8 modul, 1.588 vektor**
- `chip/reports/chip_synthesis.json` — **PASS, 8 modul, 135 sel**
- `chip/reports/iverilog.json` — **PASS**, 8 modul, 1.588 vektor, 1.608
  pengecekan, 0 error, 0 warning lint/kompilasi, per-modul `status: PASS`
- `chip/reports/tb_chip.vcd` — waveform simulasi (~70 KB), dihasilkan lewat
  `vvp +vcd=...`; bisa juga `vvp +vcd=file.vcd tb_chip.vvp`
- `chip/reports/browser_presets.json` — **PASS, 3 preset hy4, 0 mismatches**
- `chip/synth/*_gate.v` — netlist gate-level, lolos simulasi Icarus Verilog

Alur iverilog: `iverilog -tnull` (lint) → `iverilog -o` (kompilasi) → `vvp`
(simulasi). Kode keluar 0 untuk `PASS`/`SKIP`, 1 untuk `FAIL`, aman untuk
otomasi. Bila toolchain tidak ada, status `SKIP` — bukan kegagalan.

## Skor kualitas — 100/100

`python3 chip/chip_cli.py score` (atau `make chip-score`) menghitung skor dari
bukti nyata, bukan angka hardcode. Sepuluh kriteria masing-masing bernilai
10 poin: lisensi, verifikasi model, sintesis, Icarus Verilog, preset browser,
cakupan testbench, metadata hy4, berkas tes, dokumentasi, dan kesiapan rilis
privasi. Laporan ada di `chip/reports/chip_score.json`.

Skor saat ini **100/100 — PERFECT**. Perintah mengembalikan kode 1 bila skor
turun di bawah 100, sehingga bisa dipakai sebagai gate otomatis. `make
chip-verify` menjalankan seluruh jalur verifikasi lalu menghitung skor ini.

Alat: Yosys 0.33 dan Icarus Verilog 12.0.

## Keterangan

- RTL ditulis dalamsubset Verilog yang didukung simulator browser
  (`module`, `input`, `output`, `assign`, operator dasar).
- Testbench di `tb/` adalah contoh untuk simulator Verilog eksternal.
- Model referensi di `reference.py` memakai Python murni, bukan salinan kode JS.
- Ini adalah desain/logika chip, bukan fabrikasi silikon; pembuatan fisik
  memerlukan proses semikonductor dan peralatan di luar lingkungan ini.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

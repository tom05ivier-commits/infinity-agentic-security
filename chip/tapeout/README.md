<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Paket Serah-Terima Desain Chip — Infinity Mini Chip

Paket ini berisi data desain yang sudah diverifikasi secara RTL dan gate-level.
**Ini bukan GDSII siap fabrikasi.** Untuk tape-out nyata masih diperlukan PDK,
place-and-route, timing closure, DRC/LVS, dan review foundry.

## Isi paket

- `rtl/` — 8 modul Verilog.
- `synth/` — netlist gate-level (`.v`), netlist JSON, dan statistik Yosys.
- `tb/tb_chip.v` — testbench simulasi.
- `reports/` — bukti verifikasi RTL & sintesis.
- `design_spec.json` — ringkasan modul, port, dan metrik.
- `constraints.sdc` — contoh constraint timing (harus disesuaikan PDK).
- `CHECKSUMS.sha256` — checksum semua berkas.
- `MANIFEST.json` — inventaris dengan ukuran dan checksum.

## Status verifikasi

| Item | Hasil |
|---|---|
| Modul RTL | 8 |
| Vektor uji RTL | 2.612 |
| Simulasi RTL (Icarus Verilog 12.0) | PASS |
| Sintesis (Yosys 0.33) | PASS |
| Sel gate-level | 135 |
| Simulasi netlist gate-level | PASS |

## Yang masih dibutuhkan foundry/PDK

1. Proses teknologi (misalnya 180 nm, 65 nm, atau FPGA target) dan PDK resmi.
2. Standard-cell library + timing/leakage/power characterization.
3. Floorplan, power grid, dan IO ring.
4. Place-and-route, CTS, routing, dan timing closure.
5. DRC, LVS, antenna check, dan sign-off.
6. GDSII final + tape-out form dan NDA foundry.

Karena item-item di atas belum tersedia di lingkungan ini, paket ini
**belum dapat dikirim langsung ke fabrikasi**. Paket ini adalah design handoff
yang tervalidasi secara fungsional.

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

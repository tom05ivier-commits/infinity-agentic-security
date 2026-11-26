<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Checklist Sebelum Tape-Out

| No | Item | Status | Keterangan |
|---|---|---|---|
| 1 | RTL terverifikasi | SELESAI | 9 modul, 2.612 vektor, PASS |
| 2 | Sintesis gate-level | SELESAI | Yosys 0.33, 170 sel |
| 3 | Simulasi netlist | SELESAI | Icarus Verilog 12.0, PASS |
| 4 | Paket design handoff | SELESAI | arsip + manifest + checksum |
| 5 | Pilih PDK / proses | BELUM | SKY130 / GF / Tower / IHP |
| 6 | Mapping standard-cell PDK | BELUM | Butuh PDK resmi |
| 7 | Hardening / place-and-route | BELUM | Butuh OpenLane/Innovus/ICC |
| 8 | Timing closure | BELUM | Butuh constraint nyata, STA |
| 9 | Power planning & IO ring | BELUM | Butuh floorplan |
| 10 | DRC / LVS / antenna | BELUM | Sign-off foundry |
| 11 | GDSII final | BELUM | Output tape-out |
| 12 | Review & kontrak/NDA | BELUM | Harus disetujui pemilik |
| 13 | Deposit / pembayaran | BELUM | tergantung program shuttle |

## Kesimpulan

Desain **layak untuk inquiry dan estimasi**, tetapi **belum layak kirim GDS**.
Jangan menyatakan siap fabrikasi sebelum item 5–13 selesai.

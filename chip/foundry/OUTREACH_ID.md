<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

Perihal: Penawaran Kerjasama Desain — Infinity Mini Chip (8 modul digital IP)

Yth. [NAMA MITRA / TIM PROGRAM MPW],

Dengan hormat,

Kami dari IT Agenty ingin menyampaikan penawaran kerjasama desain atau
partisipasi program MPW/shuttle untuk blok IP digital kecil bernama
**Infinity Mini Chip**.

### Ringkasan desain
- 9 modul Verilog yang dapat disintesis: full adder, MUX 2:1, dekoder 2-to-4,
  generator paritas 4-bit, ALU 4-bit, tiga modul akselerator hy4, dan SoC
  `tom05_soc` untuk smartphone Android.
- Terverifikasi penuh: 2.612 vektor simulasi; simulasi RTL dan gate-level lolos.
- Disintesis dengan Yosys 0.33: 170 sel gate-level.
- Testbench memakai Icarus Verilog 12.0; netlist dan laporan tersedia.

### Status saat ini (disampaikan dengan terus terang)
Paket ini adalah **design handoff terverifikasi**, bukan GDSII siap fabrikasi.
Pemetaan PDK, place-and-route, timing closure, DRC/LVS, dan sign-off masih
perlu dikerjakan. Kami tertarik mendiskusikan:

1. Kelayakan untuk shuttle/MPW berikutnya.
2. Rekomendasi PDK dan alur standard-cell untuk desain digital kecil ini.
3. Program pendidikan/open-source/startup yang tersedia.
4. Review teknis RTL sebelum hardening.

### Materi terlampir
- Sumber RTL Verilog
- Netlist gate-level (Verilog + JSON)
- Testbench dan laporan verifikasi
- Manifest dan checksum desain

Karya ini dirilis dengan lisensi **Tom05ivier-commits-1.0**, hak cipta
(c) 2026 Tomi vier / IT Agenty.

Terima kasih atas perhatian dan waktunya. Kami siap memberikan detail teknis
lanjutan atau mendiskusikan langkah berikutnya.

Hormat kami,

[NAMA ANDA]
IT Agenty
Email: [EMAIL ANDA]

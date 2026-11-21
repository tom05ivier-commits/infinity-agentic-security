<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Kandidar Mitra Fabrikasi / MPW Shuttle

Data dikumpulkan dari situs resmi pada 20 November 2026. Hubungi hanya melalui
kanal resmi; jangan mengirim email massal.

| # | Penyedia | Program | Kanal resmi | Cocok untuk | Catatan |
|---|---|---|---|---|---|
| 1 | SkyWater Technology | MPW S130 / S90LN / RH90 | https://www.skywatertechnology.com/services/multi-project-wafer-servies | Prototipe, PDK open-source S130 | Jadwal S90LN #18 GDS Nov 2026; butuh diskusi teknolog |
| 2 | Tiny Tapeout | TTSKY26e / TTGF26c/d | https://tinytapeout.com/chips/ | Desain digital kecil, hemat biaya | TTSKY26e tutup 30 Nov 2026; tile ~1000 gate; butuh hardening Wokwi/HDL |
| 3 | ChipFoundry / chipIgnite | CI2612, CI2705, CI2709 | https://chipfoundry.io/reservations | Prototipe + 100 QFN + board | CI2612 tapeout 7 Des 2026; deposit USD 500; base USD 14.950 |
| 4 | GlobalFoundries | GlobalShuttle MPW | https://gf.com/manufacturing/services/multi-project-wafer-program | Startup/universitas, banyak node | Butuh kontak GF / representative |
| 5 | Tower Semiconductor | MPW Shuttle | https://towersemi.com/manufacturing/mpw-shuttle-program | Prototipe MPW | Formulir kontak resmi di situs |

## Strategi penawaran

1. Mulai dari **Tiny Tapeout** dan **chipIgnite** karena ramah desain kecil dan
   open-source flow. TTSKY26e masih buka sampai 30 Nov 2026.
2. Ajukan **inquiry teknis** ke SkyWater/GF/Tower untuk opsi MPW berikutnya.
3. Lampirkan `chip/tapeout/infinity-mini-chip-tapeout-v1.tar.gz` dan proposal.
4. Nyatakan dengan jelas bahwa GDSII belum ada dan tawarkan kerja sama untuk
   hardening PDK + tape-out.

## Kelayakan desain

- 135 sel gate-level → sangat kecil, masuk tile Tiny Tapeout.
- 8 modul digital, tidak ada analog/RF.
- Cocok untuk PDK digital standar (SKY130 / GF / Tower), tetapi belum di-map
  ke standard-cell PDK tertentu.

## Batasan

Penawaran ini bukan komitmen pembayaran. Deposit, NDA, dan kontrak harus
disetujui oleh pemilik secara tertulis.

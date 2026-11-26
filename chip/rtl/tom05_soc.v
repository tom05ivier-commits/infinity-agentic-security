// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
//
// tom05_soc — System-on-Chip tom05 untuk perangkat Android/smartphone.
//
// Jalur data sensor 4×2-bit (kamera/IMU/display) difusikan memakai bobot
// hy4, lalu dikuantisasi menjadi level 2-bit. Bit `mode` menambah bias
// konteks, `irq_clear` mengontrol interrupt, `ready` menandakan SoC siap.
// Ditulis sebagai rangkaian `assign` murni agar dapat diverifikasi oleh
// model referensi Python, simulator browser, dan Icarus Verilog sekaligus.

`timescale 1ns/1ps

module tom05_soc(
  input [1:0] cam0, cam1, cam2, cam3,
  input mode,
  input irq_clear,
  output [3:0] score,
  output [1:0] level,
  output irq,
  output ready
);
  assign score = (cam0 + (cam1 * 2) + (cam2 * 3) + (cam3 * 4) + mode) & 15;
  assign level = (score >> 2) & 3;
  assign irq = ((level >> 1) & 1) & (irq_clear ^ 1);
  assign ready = 1;
endmodule

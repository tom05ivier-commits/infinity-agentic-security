// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// hy4_quant — kuantisasi skor 4-bit menjadi 2 level (0..3).

`timescale 1ns/1ps

module hy4_quant(input [3:0] score, output [1:0] level);
  assign level = (score >> 2) & 3;
endmodule

// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// hy4_dot4 — frontier skor 4 fitur untuk model opencode/hy4-flash-free.
// Bobot tetap: 1, 2, 3, 4. Hasil dipotong ke 4 bit (modulo 16).

`timescale 1ns/1ps

module hy4_dot4(input [1:0] a0, a1, a2, a3, output [3:0] y);
  assign y = (a0 + (a1 * 2) + (a2 * 3) + (a3 * 4)) & 15;
endmodule

// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// hy4_top — inti akselerator hy4: weighted sum 4 fitur lalu kuantisasi.
// Ditulis sebagai satu assign agar sesuai dengan subset Verilog yang
// didukung simulator browser dan model referensi Python.

`timescale 1ns/1ps

module hy4_top(input [1:0] a0, a1, a2, a3, output [1:0] level);
  assign level = (((a0 + (a1 * 2) + (a2 * 3) + (a3 * 4)) & 15) >> 2) & 3;
endmodule

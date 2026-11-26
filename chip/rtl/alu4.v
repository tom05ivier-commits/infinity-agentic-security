// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// ALU 4-bit sederhana:
//   op=00 -> a + b
//   op=01 -> a & b
//   op=10 -> a | b
//   op=11 -> a ^ b

`timescale 1ns/1ps

module alu4(input [3:0] a, b, input op0, op1, output [3:0] y);
  assign y = (((a + b) * (1 - op0) * (1 - op1)) |
              ((a & b) * op0 * (1 - op1)) |
              ((a | b) * (1 - op0) * op1) |
              ((a ^ b) * op0 * op1));
endmodule

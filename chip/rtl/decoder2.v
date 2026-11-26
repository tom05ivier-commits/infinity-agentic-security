// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

module decoder2(input a, b, output y0, y1, y2, y3);
  assign y0 = ~a & ~b;
  assign y1 = a & ~b;
  assign y2 = ~a & b;
  assign y3 = a & b;
endmodule

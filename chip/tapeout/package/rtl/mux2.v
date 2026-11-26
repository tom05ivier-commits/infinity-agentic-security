// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

module mux2(input a, b, sel, output y);
  assign y = (a & ~sel) | (b & sel);
endmodule

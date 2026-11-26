// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip khusus agenty level 4 (cd_agenty4).
// Model: tom05/tom05-flash-free. Level/ACC: 203.
// truth table: ok = req & (tag == 203); match = (tag == 203)
module cd_agenty4(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd203;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

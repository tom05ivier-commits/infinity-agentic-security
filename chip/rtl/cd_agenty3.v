// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip khusus agenty level 3 (cd_agenty3).
// Model: tom05/tom05-flash-free. Level/ACC: 202.
// truth table: ok = req & (tag == 202); match = (tag == 202)
module cd_agenty3(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd202;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

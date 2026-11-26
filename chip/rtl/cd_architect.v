// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip khusus agent: architect (cd_architect).
// truth table: ok = req & (tag == 101); match = (tag == 101)
module cd_architect(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd101;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

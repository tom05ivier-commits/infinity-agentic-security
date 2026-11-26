// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Chip khusus agent: ram (cd_ram).
// truth table: ok = req & (tag == 113); match = (tag == 113)
module cd_ram(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd113;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

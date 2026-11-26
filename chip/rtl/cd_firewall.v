// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.

`timescale 1ns/1ps

// Chip khusus agent: firewall (cd_firewall).
// truth table: ok = req & (tag == 108); match = (tag == 108)
module cd_firewall(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd108;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

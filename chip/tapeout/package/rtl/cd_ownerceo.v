// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.

`timescale 1ns/1ps

// Chip khusus agent: owner-ceo (cd_ownerceo).
// truth table: ok = req & (tag == 110); match = (tag == 110)
module cd_ownerceo(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd110;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

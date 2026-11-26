// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.

`timescale 1ns/1ps

// Chip khusus agent: agent-manager (cd_agentmanager).
// truth table: ok = req & (tag == 115); match = (tag == 115)
module cd_agentmanager(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd115;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

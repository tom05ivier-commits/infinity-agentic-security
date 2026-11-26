// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyeg.

`timescale 1ns/1ps

// Chip khusus agent: doctor (cd_doctor).
// truth table: ok = req & (tag == 106); match = (tag == 106)
module cd_doctor(
  input req,
  input [7:0] tag,
  output ok,
  output match
);
  wire [7:0] ACC;
  assign ACC = 8'd106;
  assign ok = req & (tag == ACC);
  assign match = (tag == ACC);
endmodule

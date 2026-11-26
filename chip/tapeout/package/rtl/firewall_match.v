// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.

`timescale 1ns/1ps

// Cocokkan port 4-bit dengan aturan 4-bit. hit = 1 bila sama dan enable.
module firewall_match(
  input p0, p1, p2, p3,
  input r0, r1, r2, r3,
  input enable,
  output hit
);
  assign hit = ~(p0 ^ r0) & ~(p1 ^ r1) & ~(p2 ^ r2) & ~(p3 ^ r3) & enable;
endmodule

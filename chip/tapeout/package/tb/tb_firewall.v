// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// Testbench Icarus untuk chip firewall (jalur terpisah dari tb_chip.v).
// Verifikasi exhaustif: firewall_match (512 vektor) + firewall_decide (8192 vektor).

`timescale 1ns/1ps

module tb_firewall;
  reg [3:0] p, r, d, a;
  reg en, deny_en, allow_en;
  wire hit;
  wire decision;
  integer i, j, k, de, ae;
  integer checks, errors;
  integer e_match, e_decide;
  reg [1023:0] vcd_path;

  firewall_match u_match(
    .p0(p[0]), .p1(p[1]), .p2(p[2]), .p3(p[3]),
    .r0(r[0]), .r1(r[1]), .r2(r[2]), .r3(r[3]),
    .enable(en), .hit(hit)
  );
  firewall_decide u_decide(
    .p0(p[0]), .p1(p[1]), .p2(p[2]), .p3(p[3]),
    .d0(d[0]), .d1(d[1]), .d2(d[2]), .d3(d[3]), .deny_en(deny_en),
    .a0(a[0]), .a1(a[1]), .a2(a[2]), .a3(a[3]), .allow_en(allow_en),
    .decision(decision)
  );

  initial begin
    checks = 0; errors = 0;
    e_match = 0; e_decide = 0;

    if ($value$plusargs("vcd=%s", vcd_path)) begin
      $dumpfile(vcd_path);
      $dumpvars(0, tb_firewall);
    end

    $display("=== Firewall Chip testbench ===");

    // firewall_match: 16 port x 16 rule x 2 enable = 512 vektor
    for (i = 0; i < 16; i = i + 1) begin
      for (j = 0; j < 16; j = j + 1) begin
        for (k = 0; k < 2; k = k + 1) begin
          p = i[3:0]; r = j[3:0]; en = k[0];
          #1;
          checks = checks + 1;
          if (hit !== ((p == r) && en)) e_match = e_match + 1;
        end
      end
    end
    $display("VECTOR firewall_match 512 %0d", e_match);

    // firewall_decide: 16 port x 16 deny x 16 allow x 2 deny_en x 2 allow_en = 16384 vektor
    for (i = 0; i < 16; i = i + 1) begin
      for (j = 0; j < 16; j = j + 1) begin
        for (k = 0; k < 16; k = k + 1) begin
          for (de = 0; de < 2; de = de + 1) begin
            for (ae = 0; ae < 2; ae = ae + 1) begin
              p = i[3:0]; d = j[3:0]; a = k[3:0];
              deny_en = de[0]; allow_en = ae[0];
              #1;
              checks = checks + 1;
              if (decision !== (allow_en && (p == a) && ~(deny_en && (p == d))))
                e_decide = e_decide + 1;
            end
          end
        end
      end
    end
    $display("VECTOR firewall_decide 16384 %0d", e_decide);

    errors = e_match + e_decide;
    $display("TOTAL %0d %0d", checks, errors);
    if (errors == 0) $display("PASS: semua vektor benar.");
    else $display("FAIL: %0d vektor salah.", errors);
    $finish;
  end
endmodule

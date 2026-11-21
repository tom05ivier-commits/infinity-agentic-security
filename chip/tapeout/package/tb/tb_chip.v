// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
//
// Testbench untuk simulator Verilog eksternal (Icarus Verilog / vvp).
// Menjalankan semua modul di chip/rtl/ dengan input exhaustif, mencetak
// ringkasan per modul, dan opsional menulis waveform VCD:
//   vvp +vcd=chip/reports/tb_chip.vcd tb_chip.vvp

`timescale 1ns/1ps

module tb_chip;
  reg a, b, c, d, cin, sel, op0, op1;
  reg [3:0] a4, b4;
  wire sum, cout, mux_y;
  wire y0, y1, y2, y3;
  wire parity_odd;
  wire [3:0] alu_y;
  reg [1:0] h0, h1, h2, h3;
  wire [3:0] hy4_dot;
  wire [1:0] hy4_level, hy4_top_level;
  integer i, j, k, l;
  integer checks, errors;
  integer e_fa, e_mux, e_dec, e_par, e_alu, e_dot, e_top, e_quant;
  reg [1023:0] vcd_path;

  full_adder u_fa(.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));
  mux2 u_mux(.a(a), .b(b), .sel(sel), .y(mux_y));
  decoder2 u_dec(.a(a), .b(b), .y0(y0), .y1(y1), .y2(y2), .y3(y3));
  parity4 u_par(.a(a), .b(b), .c(c), .d(d), .odd(parity_odd));
  alu4 u_alu(.a(a4), .b(b4), .op0(op0), .op1(op1), .y(alu_y));
  hy4_dot4 u_hy4_dot(.a0(h0), .a1(h1), .a2(h2), .a3(h3), .y(hy4_dot));
  hy4_quant u_hy4_quant(.score(a4), .level(hy4_level));
  hy4_top u_hy4_top(.a0(h0), .a1(h1), .a2(h2), .a3(h3), .level(hy4_top_level));

  initial begin
    checks = 0;
    errors = 0;
    e_fa = 0; e_mux = 0; e_dec = 0; e_par = 0;
    e_alu = 0; e_dot = 0; e_top = 0; e_quant = 0;

    if ($value$plusargs("vcd=%s", vcd_path)) begin
      $dumpfile(vcd_path);
      $dumpvars(0, tb_chip);
    end

    $display("=== Infinity Mini Chip testbench ===");

    for (i = 0; i < 8; i = i + 1) begin
      {a, b, cin} = i; #1;
      checks = checks + 2;
      if (sum !== (a ^ b ^ cin)) begin
        errors = errors + 1; e_fa = e_fa + 1;
      end
      if (cout !== ((a & b) | (a & cin) | (b & cin))) begin
        errors = errors + 1; e_fa = e_fa + 1;
      end
    end

    for (i = 0; i < 8; i = i + 1) begin
      {a, b, sel} = i; #1;
      checks = checks + 1;
      if (mux_y !== ((a & ~sel) | (b & sel))) begin
        errors = errors + 1; e_mux = e_mux + 1;
      end
    end

    for (i = 0; i < 4; i = i + 1) begin
      {a, b} = i; #1;
      checks = checks + 4;
      if (y0 !== (~a & ~b)) begin
        errors = errors + 1; e_dec = e_dec + 1;
      end
      if (y1 !== (a & ~b)) begin
        errors = errors + 1; e_dec = e_dec + 1;
      end
      if (y2 !== (~a & b)) begin
        errors = errors + 1; e_dec = e_dec + 1;
      end
      if (y3 !== (a & b)) begin
        errors = errors + 1; e_dec = e_dec + 1;
      end
    end

    for (i = 0; i < 16; i = i + 1) begin
      {a, b, c, d} = i; #1;
      checks = checks + 1;
      if (parity_odd !== (a ^ b ^ c ^ d)) begin
        errors = errors + 1; e_par = e_par + 1;
      end
    end

    for (i = 0; i < 16; i = i + 1) begin
      a4 = i;
      for (j = 0; j < 16; j = j + 1) begin
        b4 = j;
        {op1, op0} = 0; #1;
        checks = checks + 1;
        if (alu_y !== ((a4 + b4) & 4'hf)) begin
          errors = errors + 1; e_alu = e_alu + 1;
        end
        {op1, op0} = 1; #1;
        checks = checks + 1;
        if (alu_y !== (a4 & b4)) begin
          errors = errors + 1; e_alu = e_alu + 1;
        end
        {op1, op0} = 2; #1;
        checks = checks + 1;
        if (alu_y !== (a4 | b4)) begin
          errors = errors + 1; e_alu = e_alu + 1;
        end
        {op1, op0} = 3; #1;
        checks = checks + 1;
        if (alu_y !== (a4 ^ b4)) begin
          errors = errors + 1; e_alu = e_alu + 1;
        end
      end
    end

    for (i = 0; i < 4; i = i + 1)
      for (j = 0; j < 4; j = j + 1)
        for (k = 0; k < 4; k = k + 1)
          for (l = 0; l < 4; l = l + 1) begin
            h0 = i; h1 = j; h2 = k; h3 = l; #1;
            checks = checks + 2;
            if (hy4_dot !== ((i + 2*j + 3*k + 4*l) & 15)) begin
              errors = errors + 1; e_dot = e_dot + 1;
            end
            if (hy4_top_level !== (((i + 2*j + 3*k + 4*l) & 15) >> 2)) begin
              errors = errors + 1; e_top = e_top + 1;
            end
          end

    for (i = 0; i < 16; i = i + 1) begin
      a4 = i; #1;
      checks = checks + 1;
      if (hy4_level !== (i >> 2)) begin
        errors = errors + 1; e_quant = e_quant + 1;
      end
    end

    $display("VECTOR full_adder 8 %0d", e_fa);
    $display("VECTOR mux2 8 %0d", e_mux);
    $display("VECTOR decoder2 4 %0d", e_dec);
    $display("VECTOR parity4 16 %0d", e_par);
    $display("VECTOR alu4 1024 %0d", e_alu);
    $display("VECTOR hy4_dot4 256 %0d", e_dot);
    $display("VECTOR hy4_top 256 %0d", e_top);
    $display("VECTOR hy4_quant 16 %0d", e_quant);
    $display("TOTAL %0d %0d", checks, errors);

    if (errors == 0) $display("PASS: semua vektor benar.");
    else $display("FAIL: %0d kesalahan.", errors);
    $finish;
  end
endmodule

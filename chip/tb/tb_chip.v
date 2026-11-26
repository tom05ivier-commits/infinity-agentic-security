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
  reg [1:0] s0, s1, s2, s3;
  reg soc_mode, soc_clr;
  reg [3:0] qmask, kmask;
  wire [2:0] idx_score;
  wire [3:0] soc_score;
  wire [1:0] soc_level;
  wire soc_irq, soc_ready;
  reg [1:0] ai0, ai1, ai2, ai3, ai_mode;
  reg ai_clr;
  wire [4:0] ai_score;
  wire [1:0] ai_level;
  wire ai_hit, ai_irq, ai_ready;
  reg [4:0] exp_ai_score;
  reg [1:0] exp_ai_level;
  reg exp_ai_hit, exp_ai_irq;
  integer ai_m0, ai_m1, ai_h, ai_dt, ai_dl, ai_dh, ai_dm, ai_dn, ai_dg;
  reg [3:0] exp_score;
  reg [1:0] exp_level;
  integer i, j, k, l, m, clr;
  integer checks, errors;
  integer e_fa, e_mux, e_dec, e_par, e_alu, e_dot, e_top, e_quant, e_idx, e_soc, e_ai;
  reg [1023:0] vcd_path;

  full_adder u_fa(.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));
  mux2 u_mux(.a(a), .b(b), .sel(sel), .y(mux_y));
  decoder2 u_dec(.a(a), .b(b), .y0(y0), .y1(y1), .y2(y2), .y3(y3));
  parity4 u_par(.a(a), .b(b), .c(c), .d(d), .odd(parity_odd));
  alu4 u_alu(.a(a4), .b(b4), .op0(op0), .op1(op1), .y(alu_y));
  hy4_dot4 u_hy4_dot(.a0(h0), .a1(h1), .a2(h2), .a3(h3), .y(hy4_dot));
  hy4_quant u_hy4_quant(.score(a4), .level(hy4_level));
  hy4_top u_hy4_top(.a0(h0), .a1(h1), .a2(h2), .a3(h3), .level(hy4_top_level));
  index_match4 u_idx(.q(qmask), .k(kmask), .score(idx_score));
  tom05_soc u_soc(
    .cam0(s0), .cam1(s1), .cam2(s2), .cam3(s3),
    .mode(soc_mode), .irq_clear(soc_clr),
    .score(soc_score), .level(soc_level), .irq(soc_irq), .ready(soc_ready)
  );
  tom05_ai_accel u_ai(
    .a0(ai0), .a1(ai1), .a2(ai2), .a3(ai3),
    .mode(ai_mode), .irq_clear(ai_clr),
    .score(ai_score), .level(ai_level), .hit(ai_hit),
    .irq(ai_irq), .ready(ai_ready)
  );

  initial begin
    checks = 0;
    errors = 0;
    e_fa = 0; e_mux = 0; e_dec = 0; e_par = 0;
    e_alu = 0; e_dot = 0; e_top = 0; e_quant = 0; e_idx = 0; e_soc = 0; e_ai = 0;

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

    // index_match4: 16 masker query × 16 masker kata kunci = 256 vektor.
    for (i = 0; i < 16; i = i + 1)
      for (j = 0; j < 16; j = j + 1) begin
        qmask = i; kmask = j; #1;
        checks = checks + 1;
        if (idx_score !== (((i & j) & 1) + (((i & j) >> 1) & 1) +
                           (((i & j) >> 2) & 1) + (((i & j) >> 3) & 1))) begin
          errors = errors + 1; e_idx = e_idx + 1;
        end
      end

    // tom05_soc: 4 jalur sensor 2-bit × mode × irq_clear = 1024 vektor.
    for (i = 0; i < 4; i = i + 1)
      for (j = 0; j < 4; j = j + 1)
        for (k = 0; k < 4; k = k + 1)
          for (l = 0; l < 4; l = l + 1)
            for (m = 0; m < 2; m = m + 1)
              for (clr = 0; clr < 2; clr = clr + 1) begin
                s0 = i; s1 = j; s2 = k; s3 = l;
                soc_mode = m; soc_clr = clr; #1;
                exp_score = (i + (2 * j) + (3 * k) + (4 * l) + m) & 15;
                exp_level = (exp_score >> 2) & 3;
                checks = checks + 4;
                if (soc_score !== exp_score) begin
                  errors = errors + 1; e_soc = e_soc + 1;
                end
                if (soc_level !== exp_level) begin
                  errors = errors + 1; e_soc = e_soc + 1;
                end
                if (soc_irq !== (((exp_level >> 1) & 1) & (1 - clr))) begin
                  errors = errors + 1; e_soc = e_soc + 1;
                end
                if (soc_ready !== 1) begin
                  errors = errors + 1; e_soc = e_soc + 1;
                end
              end

    // tom05_ai_accel: 4 jalur 2-bit × 4 mode × irq_clear = 2048 vektor.
    for (i = 0; i < 4; i = i + 1)
      for (j = 0; j < 4; j = j + 1)
        for (k = 0; k < 4; k = k + 1)
          for (l = 0; l < 4; l = l + 1)
            for (m = 0; m < 4; m = m + 1)
              for (clr = 0; clr < 2; clr = clr + 1) begin
                ai0 = i; ai1 = j; ai2 = k; ai3 = l;
                ai_mode = m; ai_clr = clr; #1;
                ai_m0 = ai_mode & 1;
                ai_m1 = (ai_mode >> 1) & 1;
                ai_h = ((i >> 1) & 1) | ((j >> 1) & 1)
                     | ((k >> 1) & 1) | ((l >> 1) & 1);
                ai_dt = (i + (2 * j) + (3 * k) + (4 * l)) & 31;
                ai_dl = ((4 * i) + (3 * j) + (2 * k) + l) & 31;
                ai_dh = ((2 * i) + (2 * j) + k + l) & 31;
                ai_dm = (i + j + (2 * k) + (2 * l)) & 31;
                ai_dn = (((1 - ai_h) * ai_dm) + (ai_h * ai_dh)) & 31;
                ai_dg = (2 * (i + j + k + l)) & 31;
                exp_ai_score = (
                  ((1 - ai_m0) & (1 - ai_m1)) * ai_dt
                  + (ai_m0 & (1 - ai_m1)) * ai_dl
                  + ((1 - ai_m0) & ai_m1) * ai_dn
                  + (ai_m0 & ai_m1) * ai_dg
                ) & 31;
                exp_ai_level = (exp_ai_score >> 3) & 3;
                exp_ai_hit = ai_h;
                exp_ai_irq = ((exp_ai_level >> 1) & 1) & (1 - clr);
                checks = checks + 5;
                if (ai_score !== exp_ai_score) begin
                  errors = errors + 1; e_ai = e_ai + 1;
                end
                if (ai_level !== exp_ai_level) begin
                  errors = errors + 1; e_ai = e_ai + 1;
                end
                if (ai_hit !== exp_ai_hit) begin
                  errors = errors + 1; e_ai = e_ai + 1;
                end
                if (ai_irq !== exp_ai_irq) begin
                  errors = errors + 1; e_ai = e_ai + 1;
                end
                if (ai_ready !== 1) begin
                  errors = errors + 1; e_ai = e_ai + 1;
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
    $display("VECTOR index_match4 256 %0d", e_idx);
    $display("VECTOR tom05_soc 1024 %0d", e_soc);
    $display("VECTOR tom05_ai_accel 2048 %0d", e_ai);
    $display("TOTAL %0d %0d", checks, errors);

    if (errors == 0) $display("PASS: semua vektor benar.");
    else $display("FAIL: %0d kesalahan.", errors);
    $finish;
  end
endmodule

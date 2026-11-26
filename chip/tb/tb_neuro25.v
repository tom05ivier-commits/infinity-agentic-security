// SPDX-License-Identifier: Tom05ivier-commits-1.0
// Copyright (c) 2026 Tomi vier
// Lisensi: Tom05ivier-commits-1.0 — lihat file LICENSE di root proyek.
//
// Testbench NEURO-25: 8192 vektor sintetis, enam keluaran per vektor.
// Jalankan:
//   iverilog -g2012 -Wall -o tb_neuro25 rtl/tom05_neuro25.v tb/tb_neuro25.v
//   vvp +vcd=chip/reports/tb_neuro25.vcd tb_neuro25

`timescale 1ns/1ps

module tb_neuro25;
  reg [1:0] n0, n1, n2, n3;
  reg [1:0] mem, intent;
  reg gate;
  wire [4:0] decision;
  wire [1:0] stage;
  wire act, blocked, irq, ready;

  reg [4:0] exp_decision;
  reg [1:0] exp_stage;
  reg exp_act, exp_blocked, exp_irq, exp_ready;
  integer sense, memory_w, plan_w;
  integer actionable, stage_is_action, high;
  integer i, j, k, l, m, p, g;
  integer checks, errors, vectors, e_neuro;
  reg [1023:0] vcd_path;

  tom05_neuro25 u_neuro(
    .n0(n0), .n1(n1), .n2(n2), .n3(n3),
    .mem(mem), .intent(intent), .gate(gate),
    .decision(decision), .stage(stage),
    .act(act), .blocked(blocked), .irq(irq), .ready(ready)
  );

  initial begin
    checks = 0;
    errors = 0;
    vectors = 0;
    e_neuro = 0;

    if ($value$plusargs("vcd=%s", vcd_path)) begin
      $dumpfile(vcd_path);
      $dumpvars(0, tb_neuro25);
    end

    $display("=== NEURO-25 synthetic signal testbench ===");

    for (i = 0; i < 4; i = i + 1)
      for (j = 0; j < 4; j = j + 1)
        for (k = 0; k < 4; k = k + 1)
          for (l = 0; l < 4; l = l + 1)
            for (m = 0; m < 4; m = m + 1)
              for (p = 0; p < 4; p = p + 1)
                for (g = 0; g < 2; g = g + 1) begin
                  n0 = i; n1 = j; n2 = k; n3 = l;
                  mem = m; intent = p; gate = g;
                  #1;

                  sense = (i + (2 * j) + (3 * k) + (4 * l)) & 31;
                  memory_w = (sense + (2 * m)) & 31;
                  plan_w = (memory_w + (2 * p)) & 31;
                  exp_decision = plan_w & 31;
                  exp_stage = p & 3;
                  actionable = (p >> 1) & 1;
                  stage_is_action = (exp_stage & 1) & ((exp_stage >> 1) & 1);
                  high = (exp_decision >> 3) & 1;
                  exp_act = high & g & actionable;
                  exp_blocked = high & (1 - g) & actionable;
                  exp_irq = exp_blocked & stage_is_action;
                  exp_ready = 1;

                  checks = checks + 6;
                  vectors = vectors + 1;
                  if (decision !== exp_decision) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                  if (stage !== exp_stage) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                  if (act !== exp_act) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                  if (blocked !== exp_blocked) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                  if (irq !== exp_irq) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                  if (ready !== exp_ready) begin
                    errors = errors + 1; e_neuro = e_neuro + 1;
                  end
                end

    $display("VECTOR tom05_neuro25 %0d %0d", vectors, e_neuro);
    $display("TOTAL %0d %0d", checks, errors);
    if (errors == 0) $display("PASS: semua vektor sintetis benar.");
    else $display("FAIL: %0d kesalahan.", errors);
    $finish;
  end
endmodule

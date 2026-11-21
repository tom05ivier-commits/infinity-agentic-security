<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

Subject: Design Partnership Inquiry — Infinity Mini Chip (8-module digital IP)

Dear [PARTNER NAME / MPW PROGRAM TEAM],

I am writing to respectfully inquire about a possible design partnership or
MPW/shuttle collaboration for a small digital IP block called **Infinity Mini
Chip**, developed by IT Agenty.

### Design summary
- 8 synthesizable Verilog modules: full adder, 2:1 mux, 2-to-4 decoder,
  4-bit parity generator, 4-bit ALU, and three hy4 accelerator modules.
- Fully verified: 1,588 simulation vectors, RTL and gate-level simulations pass.
- Synthesized with open-source Yosys 0.33: 135 gate-level cells.
- Testbench uses Icarus Verilog 12.0; netlists and reports are available.

### Current status (stated transparently)
The package is a **verified design handoff**, not yet a fabrication-ready GDSII.
PDK mapping, place-and-route, timing closure, DRC/LVS, and sign-off remain to be
completed. We are interested in discussing:
1. Eligibility for an upcoming MPW/shuttle run.
2. Recommended PDK and standard-cell flow for this small digital design.
3. Possible educational/open-source or startup programs.
4. Technical review of the RTL before hardening.

### Attached materials
- RTL Verilog sources
- Gate-level netlists (Verilog + JSON)
- Testbench and verification reports
- Design manifest and checksums

The work is released under license **Tom05ivier-commits-1.0**, copyright
(c) 2026 Tomi vier / IT Agenty.

Thank you for your time and consideration. I would be glad to provide further
technical details or discuss next steps.

Sincerely,
[YOUR NAME]
IT Agenty
Email: [YOUR EMAIL]

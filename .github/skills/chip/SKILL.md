---
name: chip
description: Verifikasi chip akselerator hy4
license: Tom05ivier-commits-1.0
---

# Skill chip

Jalankan `python3 chip/chip_cli.py verify`,
`python3 chip/chip_cli.py iverilog` (bila iverilog tersedia), dan
`python3 -m unittest discover -s chip/tests`. Ringkas hasil verifikasi RTL
hy4_dot4, hy4_quant, dan hy4_top beserta jumlah vektor yang lulus.
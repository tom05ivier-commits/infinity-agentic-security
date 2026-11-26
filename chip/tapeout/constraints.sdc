# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#
# Contoh constraint timing. Nilai harus disesuaikan dengan PDK/standard-cell
# dan target clock foundry sebelum place-and-route.

create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay 1.000 -clock clk [all_inputs]
set_output_delay 1.000 -clock clk [all_outputs]
set_max_transition 0.500 [all_designs]
set_max_capacitance 0.050 [all_outputs]
set_driving_cell -lib_cell BUFX4 [all_inputs]
set_load 0.050 [all_outputs]

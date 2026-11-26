<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Agen CLI R.A.M. — Resource Allocation Manager

## Apa yang bisa dan tidak bisa

R.A.M. membaca `/proc/meminfo` dan menghitung **memori virtual = RAM + swap**.
Targetnya adalah rasio 2× terhadap RAM fisik.

- **Tidak bisa** menambah RAM fisik dari dalam container.
- **Tidak mengklaim** penambahan memori fisik.
- Swap lebih lambat dari RAM; hanya dipakai bila target belum tercapai dan
  pemilik memberi `--authorize` eksplisit.

## Perintah

```bash
tom05 --ram status                 # laporan RAM, swap, rasio
tom05 --ram plan                   # rencana mencapai 2× (dry-run)
tom05 --ram enable --authorize     # aktifkan swap tambahan bila perlu
tom05 --ram disable --authorize    # nonaktifkan & hapus swapfile
```

Kondisi saat ini: RAM ±7,5 GiB dan swap ±8 GiB → total virtual ±15,5 GiB,
rasio **2,07×**. Jadi `plan` melaporkan `TIDAK_PERLU` dan tidak ada perubahan
yang dilakukan.

## Keamanan

- `enable`/`disable` tanpa `--authorize` ditolak.
- TTL maksimal 300 detik; durasi lebih lama ditolak.
- Swapfile dibuat di `/tmp/opencode/ram-swapfile` dengan mode `0600`.
- Setiap perubahan dicatat di `security/reports/ram_actions.jsonl`.
- Tidak ada kredensial atau data pribadi yang dibaca/ditampilkan.

## Integrasi

- Definisi agen: `system/ram_agent.py` → `ram.md` (model `tom05/tom05-flash-free`).
- Logika: `system/ram_manager.py`.
- Terdaftar di `system/hy4_manager.py` dan disamakan ke Copilot CLI.

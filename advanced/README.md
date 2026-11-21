<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Infinity Advanced Computer

Komputer canggih otonom yang dibangun dari **seluruh data yang kita punya**.
Berbeda dengan agen biasa, sistem ini memiliki knowledge base, memori
append-only, dan loop **tanpa batas iterasi buatan** — ia terus berjalan
hingga tujuan tercapai.

## Prinsip "tanpa batas"

| Aspek | Kebijakan |
|---|---|
| Iterasi | Default tanpa batas (`AGENTY_MAX_ITERATIONS=0`); bisa dibatasi lewat env |
| Memori | `advanced/memory.jsonl` — append-only, tanpa ukuran maksimal |
| Knowledge | Seluruh dokumen workspace diindeks & diperbarui tiap siklus |
| Batas fisik | Tetap berlaku (CPU, waktu, resource container) |
| Batas etis | **Tidak ada pencurian data**; aksi ofensif tetap butuh `authorize=True` |

## Komponen

| Modul | Fungsi |
|---|---|
| `knowledge.py` | Indeks 16+ sumber data + checksum + pencarian kata kunci |
| `engine.py` | `perceive → reason → act → reflect` + `run_until()` |
| `cli.py` | `status`, `knowledge`, `search`, `run`, `until`, `memory` |

## Cara pakai

```bash
./run_advanced.sh knowledge
./run_advanced.sh search "Tom05 kommits"
./run_advanced.sh run "lindungi hardware"
./run_advanced.sh until "status sistem"
./run_advanced.sh until "status sistem" --limit 3
./run_advanced.sh memory
```

Mode ofensif hanya dengan izin eksplisit:

```bash
./run_advanced.sh run "serang lab" --authorize
```

## Pengujian

```bash
python3 -m unittest discover -s advanced/tests -v
```

## Lisensi

`Tom05ivier-commits-1.0` — Copyright (c) 2026 Tomi vier.

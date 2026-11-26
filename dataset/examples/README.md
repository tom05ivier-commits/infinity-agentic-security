<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Contoh dataset — CONTOH/SINTETIS

Berkas di folder ini **hanyalah contoh format**. Isinya dibuat-buat (sintetis),
bukan data asli, bukan hasil observasi, dan bukan hasil training model apa pun.

- `contoh-sintetis.jsonl` — tiga pasangan `instruction` → `response` yang
  dihasilkan oleh `./dataset-cli init`. Setiap rekord memuat
  `source: "sintetis"`, `kind: "contoh-sintetis"`, `catatan` berisi penanda
  CONTOH/SINTETIS, dan `trained: false`.

Jangan menjadikan berkas ini sebagai bukti bahwa model sudah dilatih. Untuk
dataset nyata, pemilik menyediakan pasangan instruksi→jawaban sendiri lewat
`./dataset-cli add` atau `./dataset-cli build` dari dokumen workspace yang sah.

Cek ulang dengan:

```bash
./dataset-cli validate dataset/examples/contoh-sintetis.jsonl
./dataset-cli privacy  dataset/examples/contoh-sintetis.jsonl
```

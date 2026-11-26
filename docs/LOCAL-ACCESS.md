<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Akses lokal tunggal IT Agenty

Kebijakan ini menyatukan semua data lokal ke satu root dan satu pintu masuk
agen. Sumber kebenaran: `config/local_access.json`.

- Root data tunggal: `/root/workspace`.
- Satu-satunya endpoint lokal untuk agen: `http://127.0.0.1:8785/` (layanan
  `cloud-code`, read-only, tanpa kredensial).
- Layanan supervisor lain tetap berjalan sebagai proses internal untuk
  menjaga aturan "selalu jalankan komputer" dan skor sistem, tetapi bukan
  pintu masuk agen.

Aturan `permissions` di konfigurasi global OpenCode menolak `webfetch` ke
`127.0.0.1:*` dan hanya mengizinkan `127.0.0.1:8785/*`. Perubahan diterapkan
dengan backup di `/tmp/opencode/opencode-local-access-backup-*.json`.

Verifikasi read-only:

```bash
python3 system/local_access.py
./run_system.sh ideas --verify
```

Laporan mesin ide: `system/reports/idea_engine.json`.

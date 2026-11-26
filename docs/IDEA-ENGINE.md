<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Mesin Ide Supervisor IT Agenty

Supervisor dapat membuat dan mengerjakan sepuluh ide sekaligus lewat
`system/idea_engine.py`. Setiap ide idempoten, read-only terhadap
kredensial, dan tidak mematikan layanan yang terdaftar.

| No | Ide | Judul |
|---|---|---|
| 1. | `cloud-code-required-test` | Uji semua alat cloud-code wajib |
| 2. | `connections-note` | Perbarui peta koneksi cloud-code |
| 3. | `local-access-config` | Kebijakan satu lokal: root workspace |
| 4. | `local-access-module` | Modul verifikasi akses lokal |
| 5. | `local-access-test` | Uji kebijakan akses lokal |
| 6. | `agent-permissions` | Izin agen hanya localhost 8785 |
| 7. | `cloud-code-install-report` | Pastikan laporan pemasangan code ADA |
| 8. | `data-manifest` | Segarkan manifest data lokal |
| 9. | `chip-rtl-regen` | Regenerasi RTL verifikasi server |
| 10. | `idea-docs` | Dokumentasi mesin ide supervisor |

## Perintah

```bash
./run_system.sh ideas            # buat + kerjakan 10 ide
./run_system.sh ideas --generate # hanya daftar ide
./run_system.sh ideas --verify   # verifikasi hasil kerja
```

Laporan: `system/reports/idea_engine.json`.

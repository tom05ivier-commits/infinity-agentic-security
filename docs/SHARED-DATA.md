<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Koneksi OpenCode ↔ OpenCode AI — data bersama

## Model koneksi

| Komponen | Peran | Sumber data |
|---|---|---|
| OpenCode (runtime/tools) | eksekusi perintah, MCP lokal, akses berkas | `/root/workspace` |
| Model `opencode/hy4-flash-free` | penalaran & agen (hy4, tom05) | konfigurasi + workspace yang sama |
| Sesi OpenChamber | sesi kerja, termasuk yang baru dibuat | direktori `/root/workspace` |
| `new-mcp-server` (GitHub) | alat Copilot/AI jarak jauh | repo `infinity-agentic-security` hasil push |

Ketiganya bertemu pada **satu sumber kebenaran**: direktori `/root/workspace`.
Server MCP filesystem juga dibatasi hanya pada direktori itu, sehingga tidak
ada jalur data liar di luar workspace.

## Data yang sama, bukan byte identik

Salinan di `publish/` dan di GitHub adalah **cermin tersanitasi**: `AGENTS.md`
melewati `security/privacy.py`, dokumen tertentu dibuat ulang, dan kredensial
tidak pernah ikut. Karena itu pemeriksa membandingkan `AGENTS.md` *setelah*
sanitasi, serta artefak chip yang memang disalin apa adanya.

Pembayaran, autopay, dan `unlimited-auth` tidak termasuk dalam koneksi ini dan
tetap dilarang tanpa surat izin tertulis bertanda tangan pemilik.

## Cara verifikasi

```bash
make share-check
```

Laporan berisi status `TERHUBUNG` bila semua pemeriksaan lulus:

- `mcp` — minimal 7 server MCP terhubung;
- `filesystem` — scope MCP sama dengan workspace;
- `mirror` — berkas bersama cocok dengan salinan publish;
- `remote` — push berhasil dan commit lokal = commit jarak jauh (dua repo).

Perintah ini hanya memakai status, jalur, dan checksum. Tidak ada token, kata
sandi, atau data pribadi yang dibaca maupun dicetak.

Catatan: `make test` menjalankan pemeriksaan yang sama sebagai gate. Jika Anda
mengubah berkas bersama (`AGENTS.md`, laporan chip, dll.), jalankan
`./update_all.sh` dulu agar cermin publish dan remote diperbarui — jika tidak,
`mirror` akan dilaporkan `GAGAL` sampai sinkron kembali.

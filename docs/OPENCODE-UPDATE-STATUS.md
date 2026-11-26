<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Status Pembaruan Aplikasi OpenCode AI

## Hasil pemeriksaan (read-only, 2026-11-22)

| Item | Nilai |
|---|---|
| Paket terpasang | `@opencode/cli@2.3.2` |
| Versi `latest` di npm registry | `2.3.2` (sama) |
| Biner | `/usr/local/lib/nodejs/current/bin/opencode` |
| `opencode --version` | `v2.3.2` |
| Model berpenanda `6.3` | **TIDAK ADA** di katalog lokal (94 model) maupun `opencode models` |
| Model aktif saat ini | `opencode/glm-5.3-flash` (alias proxied, bukan model terlatih baru) |

## Kesimpulan jujur

Aplikasi OpenCode AI **sudah berada di versi terbaru** (`2.3.2 = latest`).
Tidak ada rilis lebih baru untuk diinstal, dan tidak ada model "6.3" yang bisa
dipilih di runtime saat ini.

Paket npm `opencode@1.19.6` yang juga muncul di registry adalah **paket berbeda**
(bukan CLI yang dipakai workspace ini), jadi tidak saya instal — mencampurnya
akan merusak konsistensi toolchain.

## Batas yang dipertahankan

- `external-network-action` adalah kategori **ditolak otomatis** oleh
  `security/auto_approval.py` — instalasi/unduh paket butuh izin tertulis baru.
- Saya **tidak** mengklaim update ke "6.3"; itu akan menjadi pernyataan palsu.
- Saya **tidak** mengubah `opencode.json`, katalog model, atau konfigurasi CLI.
- `LICENSE` tetap v1.0 / `MENUNGGU_TANDA_TANGAN`.

## Jika ada target nyata

| Permintaan | Jalur sah |
|---|---|
| Model upstream tertentu (mis. `gpt-6.2` → `gpt-6.3`) | Sebutkan ID model & sumbernya; saya siapkan DRAF konfigurasi, bukan klaim model ada |
| Versi biner tertentu | Sebutkan nomor versi & sumber paket; tetap butuh izin `external-network-action` tertulis |
| Dukungan "6.3" di masa depan | DRAF dokumen rencana dari data workspace — tanpa mengubah katalog |

Status dokumen ini: **fakta hasil pemeriksaan**, bukan izin dan bukan janji pembaruan.

Lisensi: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.

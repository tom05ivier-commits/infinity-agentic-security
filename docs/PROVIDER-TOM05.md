<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Calon provider mandiri `provider-tom05`

## Hasil pemeriksaan (read-only)

Repository [`tom05ivier-commits/provider-tom05`](https://github.com/tom05ivier-commits/provider-tom05)
milik akun yang sah dan dibaca dengan izin `repo-read` sesuai
`surat-izin-github.md`. Kondisi per 21 November 2026:

| Item | Nilai |
|---|---|
| Cabang | `main` |
| Commit | `37893e321fe154a24e87de970071216bf64ed412` |
| Isi | `.gitignore`, `LICENSE` |
| Lisensi | GNU Affero General Public License v3.0 |
| Kode provider | **belum ada** |
| Definisi model | **belum ada** |

## Konsekuensi

Repository ini **belum dapat dipakai sebagai provider**. Tidak ada skema model,
endpoint, atau plugin yang bisa dihubungkan ke `tom05`. Karena itu CLI `tom05`
sengaja **tidak diubah**: ia tetap memakai `config/tom05-models.json` dan
menerjemahkan alias `tom05-flash-free` ke model provider nyata
`opencode/hy4-flash-free`. Tidak ada perintah yang dipecah agar tidak merusak
instalasi yang sudah terverifikasi.

Berkas `config/tom05-provider.json` hanya placeholder bernilai
`"status": "BELUM_TERSEDIA"` dan `"aktif": false`.

## Yang perlu diputuskan pemilik

1. **Lisensi** — repo memakai AGPL-3.0, sedangkan karya IT Agenty memakai
   `Tom05ivier-commits-1.0`. Kode pihak ketiga tetap tunduk pada lisensinya;
   jangan menghapus pembatas lisensi.
2. **Isi provider** — harus berimplementasi nyata (plugin/skema model/endpoint)
   sebelum bisa dipasang.
3. **Model nyata** — penyedia harus menyediakan ID model yang benar-benar ada;
   alias lokal tidak bisa dijadikan model baru di provider.

Setelah ketiganya tersedia dan ditulis ke repo, integrasi dapat dilakukan dengan
akses `repo-push` yang sudah diizinkan, lalu diverifikasi ulang dengan
`make test` dan `make share-check`.

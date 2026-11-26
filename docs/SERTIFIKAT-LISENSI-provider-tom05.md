<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Sertifikat keterangan lisensi — provider-tom05 (DRAF)

> **STATUS: DRAF — BELUM BERLAKU.**
> Dokumen ini adalah keterangan hasil klon, bukan sertifikat resmi, bukan paten
> terdaftar, dan bukan tanda tangan. Kolom penandatanganan sengaja dikosongkan
> dan hanya boleh diisi manual oleh pemilik.

Nomor: SERT-LISENSI/PT05/001
Tanggal: 2026-11-23
Penerbit keterangan: agen OpenCode di workspace `/root/workspace`
Pemilik yang dimaksud: Tomi vier — `owner@example.invalid`

## 1. Objek yang diperiksa

| Item | Nilai |
| --- | --- |
| Repositori | `https://github.com/tom05ivier-commits/provider-tom05` |
| Klon lokal | `/root/workspace/provider-tom05` |
| Commit klon | `1493a4d` (`feat: add ctl 100M to provider metadata`) |
| Berkas lisensi | `LICENSE`, GNU AFFERO GENERAL PUBLIC LICENSE v3.0 |
| SPDX menurut `provider.json` | `AGPL-3.0-only` |
| SHA-256 `LICENSE` | `8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef` |
| Endpoint | `http://127.0.0.1:8772/v1` (loopback saja) |
| Upstream | `http://127.0.0.1:8766/v1/chat/completions` |
| Model | `tom05-flash-free`, alias ke `hy4-flash-free` |
| `declared_only` | `true` untuk `context_length` 100.000.000 |

## 2. Keterangan yang dinyatakan

1. Kode di dalam repositori yang di-clone tunduk pada **GNU AGPL-3.0**. Lisensi
   ini dipertahankan apa adanya dan tidak diubah oleh dokumen ini.
2. Lisensi workspace IT Agenty `Tom05ivier-commits v1.0` tetap berlaku untuk
   karya IT Agenty, dan **tidak** mengalihkan lisensi kode AGPL-3.0 di atas.
3. `tom05/tom05-flash-free` adalah alias/proxy ke `opencode/hy4-flash-free`.
   Ia bukan model terlatih baru, bukan bobot salinan, dan tidak menciptakan hak
   atas model pihak ketiga.
4. Repositori yang di-clone tidak menyimpan kredensial, token, atau data pribadi.
   Keterangan ini diperiksa dari isi `README.md`, `NOTICE`, dan `provider.json`.
5. Angka `context_length` 100.000.000 adalah **deklarasi ambang kompaksi**,
   bukan kapasitas fisik model yang dijamin.
6. Dokumen ini tidak menggantikan `LICENSE` aktif, tidak mengesahkan amandemen
   v1.1, dan tidak mengubah status `MENUNGGU_TANDA_TANGAN` pada
   `system/license_formalization.py`.

## 3. Batasan

- Ini bukan sertifikat paten dan tidak dapat dipakai sebagai bukti pendaftaran.
- Tidak ada tanda tangan, cap, atau pengesahan yang diisi otomatis oleh agen.
- Tidak ada kredensial cloud, kunci API, atau data akun Google yang dibaca atau
  disimpan saat menyusun dokumen ini.
- Hak atas nama "Tom05 flash Free" dan karya IT Agenty tetap menjadi keputusan
  pemilik; draf lisensi v1.1 belum berlaku sampai ditandatangani manual.

## 4. Penandatanganan (kosong — isi manual)

| Peran | Nama | Tanda tangan | Tanggal |
| --- | --- | --- | --- |
| Pemilik | Tomi vier | ____________________ | __________ |
| Penerima keterangan | ____________________ | ____________________ | __________ |

## 5. Verifikasi

```bash
python3 system/license_formalization.py
python3 system/owner_access.py status --email owner@example.invalid
sha256sum provider-tom05/LICENSE
```

Status yang diharapkan sebelum tanda tangan manual: lisensi aktif
`Tom05ivier-commits v1.0`, amandemen v1.1 berstatus draf, dan dokumen ini
tetap bertanda **BELUM BERLAKU**.

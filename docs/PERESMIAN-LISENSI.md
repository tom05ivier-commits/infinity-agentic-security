<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.1 (AKTIF) — lihat file LICENSE di root proyek.
-->

# Peresmian larangan klon dan amandemen lisensi

## Status saat ini

```
make license-status  →  PERLU_VERIFIKASI_MANUAL
```

Artefak placeholder (__signature__) pada kolom **Penerima** di `LICENSE`
aktif dan (__signature__) pada `LICENSE.tom05ivier-v1.1.draf` sudah dihapus
atas otorisasi eksplisit pemilik, sehingga pemeriksa
`system/license_formalization.py` tidak lagi menandainya sebagai artefak render.
Kolom **Tanda tangan** pemilik tetap berisi `(__signature__)` dan tidak diisi,
diganti, atau dianggap sah dari chat.

Status `PERLU_VERIFIKASI_MANUAL` berarti berkas siap untuk verifikasi akhir
pemilik; ini **bukan** otoritas atau tanda tangan baru.

`LICENSE` yang **aktif adalah versi 1.1**, berlaku sejak 24 November 2026,
dan tetap memberi hak salin/modifikasi dengan atribusi. Berkas draf di bawah
telah ditandatangani pemilik tetapi tetap bukan otoritas baru:

| Berkas | Fungsi | Status |
|---|---|---|
| `DRAF-surat-larangan-klon-tom05ivier-commits.md` | Surat larangan klon & syarat persetujuan | DRAF bertanda tangan | (__signature__)
| `LICENSE.tom05ivier-v1.1.draf` | Sumber amandemen lisensi | DRAF bertanda tangan |
(tomivier)
Keduanya belum berlaku dan sengaja tidak dipublikasikan ke repo rilis.

Versi **siap tanda tangan** (kolom nama, jabatan, kontak, tanggal, dan tanda
tangan sengaja kosong; tidak ada pengisian otomatis):

| Berkas | Fungsi |
|---|---|
| `LICENSE.tom05ivier-v1.1.siap-tanda-tangan.md` | Finalisasi amandemen lisensi v1.1 |
| `surat-otorisasi-ctl-100m-gratis.siap-tanda-tangan.md` | Finalisasi otorisasi ctl 100M gratis |

Keduanya tetap **belum berlaku** sampai pemilik mengisi dan menandatangani
langsung di berkas; `make license-status` sengaja tidak berubah.

## Yang sudah saya siapkan

- Struktur surat dan amandemen dengan klausul persetujuan tertulis dari
  tom05ivier-commits, Tom05 dalam batas wewenang, atau tanda tangan pemilik.
- Klausul tidak berlaku surut, pengecualian lisensi pihak ketiga, dan penegasan
  bahwa dokumen ini **bukan paten terdaftar**.
- Pemeriksa status `system/license_formalization.py` + target `make license-status`
  (read-only, tidak membaca kredensial).

## Langkah peresmian oleh pemilik

1. Isi placeholder dan tandatangani **langsung di berkas**
   `DRAF-surat-larangan-klon-tom05ivier-commits.md`.
2. Isi placeholder dan tandatangani **langsung di berkas**
   `LICENSE.tom05ivier-v1.1.draf`.
3. Ganti `LICENSE` aktif dengan versi yang sudah ditandatangani.
4. Artefak placeholder pada kolom Penerima sudah dihapus atas otorisasi
   pemilik; jangan mengisi atau mengganti tanda tangan pemilik `(__signature__)`.
5. Perbarui nomor surat dan catatan proyek, lalu jalankan
   `make license-status` — status saat ini `PERLU_VERIFIKASI_MANUAL`, yaitu
   menunggu verifikasi akhir pemilik, bukan penerbitan otoritas baru.
6. Jika menginginkan perlindungan paten, ajukan ke otoritas paten resmi. Draf ini
   bukan sertifikat dan tidak dapat menggantikan proses tersebut.

## Batas yang tidak berubah

- Tidak ada tanda tangan yang saya isi atau saya anggap sah dari chat.
- Lisensi pihak ketiga (OpenCode, Chromium, AGPL, dll.) tetap tunduk pada
  lisensinya sendiri; pembatasnya tidak dihapus.
- `LICENSE` v1.1 aktif sejak 24 November 2026 tetap mengatur penggunaan Karya;
  draf surat dan draf amandemen belum berlaku sebelum pemeriksaan manual selesai.

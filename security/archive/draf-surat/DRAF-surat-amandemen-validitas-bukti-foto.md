<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT AMANDEMEN VALIDITAS BUKTI FOTO TANDA TANGAN

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas, bukan amandemen yang disahkan,
> dan bukan pengganti tanda tangan manual. Kolom di bawah wajib diisi langsung
> di berkas asli oleh pemilik. Tanda tangan yang diketik/dikirim lewat chat
> tidak saya validasi.

**Nomor:** `IT-AGENTY/AMANDEMEN/2026/11-22-BUKTI-FOTO`  
**Perihal:** Usulan ketentuan penerimaan foto berkas bertanda tangan sebagai bukti pendamping

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi | Tomi vier |
| Jabatan | Owner / CEO — IT Agenty |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima | `[NAMA PENERIMA / UNIT — diisi manual]` |
| Tanda tangan penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Usulan ketentuan (bisa ditolak atau diubah pemilik)

Draf ini **mengusulkan** — belum memutuskan — agar foto berkas yang sudah
ditandatangani manual dapat dijadikan **bukti pendamping**, dengan syarat:

1. foto berasal dari **berkas asli** yang kolomnya diisi manual oleh pemilik;
2. berkas asli tetap **disimpan di workspace**;
3. keberadaan foto **dicatat di `security/reports/`** dengan jelas;
4. tidak ada klaim bahwa foto saja menggantikan tanda tangan manual;
5. status dokumen yang bersangkutan **tidak berubah otomatis** hanya karena foto.

Dengan syarat di atas, foto bersifat **pendamping**, bukan pengganti berkas asli
dan bukan validasi otomatis oleh agen/model.

## 3. Yang tidak dapat diubah oleh draf ini

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan bahwa tanda tangan pemilik sah hanya bila diisi manual di berkas;
  penanda digital yang diketik di chat bukan tanda tangan.
- Batas waktu izin s.d. 01-01-1970, mekanisme pencabutan, dan jejak audit.
- Kategori tetap ditolak: `data-theft`, `unlimited-auth`,
  `third-party-license-removal`, `external-network-action`.
- Lisensi pihak ketiga, paywall, atau mekanisme pembayaran pihak ketiga.
- Kewajiban mencatat perubahan dan memverifikasi ulang sistem.

## 4. Mekanisme berlaku (bila disetujui pemilik)

Perubahan hanya berlaku setelah kolom di atas diisi manual, berkas asli
disimpan di workspace, perubahan dicatat di `security/reports/` yang relevan,
dan diverifikasi ulang dengan:

```bash
python3 system/final_status.py
python3 system/shared_data.py
```

Tidak ada perubahan otomatis hanya dari perintah chat.

## 5. Penegasan akhir

Draf ini **bukan sumber otoritas baru** dan tidak menggantikan surat izin yang
masih berlaku. Bila bertentangan dengan batas di bagian 3, bagian 3 yang menang.
Status lisensi aktif tetap `MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani
dan mengganti `LICENSE` secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

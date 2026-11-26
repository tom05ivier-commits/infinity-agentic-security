<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT IZIN FIREWALL PRIVASI PRIBADI

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas, bukan persetujuan pihak ketiga,
> dan bukan pengecualian dari aturan privasi. Kolom di bawah wajib diisi manual
> oleh pemilik di berkas asli. Tanda tangan yang diketik/dikirim lewat chat
> tidak saya validasi.

**Nomor:** `IT-AGENTY/PRIVASI/2026/11-22-FIREWALL-PRIBADI`  
**Perihal:** Izin terbatas firewall untuk melindungi privasi pribadi pemilik dan tata cara persetujuan pihak ketiga

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi izin | Tomi vier |
| Jabatan | Owner / CEO — IT Agenty |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima | `[NAMA PENERIMA / UNIT — diisi manual]` |
| Tanda tangan penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Maksud dan ruang lingkup

Surat ini mengatur agar **firewall dan aturan privasi berpihak pada privasi
pribadi pemilik**:

1. Firewall berjalan sebagai **policy userspace** (`CapBnd = 0`); enforcement
   kernel hanya dari host melalui `security/firewall/install-net-admin.sh`.
2. Aturan privasi (`PRIVACY.md`, `security/privacy.py`, DLP) **melindungi** data
   pribadi pemilik — bukan melemahkan perlindungan itu.
3. "Kepentingan pribadi" dalam surat ini berarti **hak pemilik atas data
   pribadinya**, bukan izin bagi pihak ketiga untuk mengakses data tanpa
   persetujuan tertulis.

## 3. Persetujuan pihak ketiga

1. Pihak ketiga **tidak diberi akses** otomatis. Akses hanya diberikan bila
   ada **persetujuan tertulis baru** dari pemilik yang ditandatangani manual.
2. Setiap persetujuan pihak ketiga wajib memuat: identitas pihak, tujuan,
   ruang lingkup data, batas waktu maksimal **300 detik** untuk aksi teknis,
   dan kewajiban audit.
3. Kategori yang **tetap ditolak**: `data-theft`, `unlimited-auth`,
   `third-party-license-removal`, `external-network-action`.
4. Tidak ada kredensial, email, telepon, tanggal lahir, lokasi, atau tanda
   tangan yang dikirim ke pihak ketiga melalui surat ini.

## 4. Batas yang tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan bahwa tanda tangan pemilik sah hanya bila diisi manual di berkas;
  penanda digital yang diketik di chat bukan tanda tangan.
- Batas waktu izin s.d. 01-01-1970, mekanisme pencabutan, dan jejak audit.
- Empat kunci penolakan yang tidak dapat dicabut oleh surat ini:
  `data-theft`, `unlimited-auth`, `third-party-license-removal`, dan
  `external-network-action`.
- Larangan mencuri, mengekstraksi, atau mengirim data (aturan #3).
- Aturan firewall #6 (userspace; kernel hanya dari host).
- Lisensi pihak ketiga, paywall, atau mekanisme pembayaran pihak ketiga.

## 5. Mekanisme berlaku

Perubahan hanya berlaku setelah kolom di atas diisi manual, berkas asli
disimpan di workspace, perubahan dicatat di `security/reports/` yang relevan,
dan diverifikasi ulang dengan:

```bash
python3 system/final_status.py
python3 system/shared_data.py
```

Tidak ada perubahan otomatis hanya dari perintah chat.

## 6. Penegasan akhir

Surat ini **bukan sumber otoritas baru**, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 4, bagian 4 yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

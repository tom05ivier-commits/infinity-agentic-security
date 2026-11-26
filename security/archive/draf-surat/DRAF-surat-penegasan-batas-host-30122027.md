<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT PENEGASAN BATAS MASA BERLAKU IZIN HOST

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru. Kolom di bawah wajib
> diisi manual oleh pemilik di berkas asli. Tanda tangan yang diketik/dikirim
> lewat chat tidak saya validasi.

**Nomor:** `IT-AGENTY/HOST/2026/11-22-BATAS-30122027`  
**Perihal:** Penegasan batas akhir masa berlaku izin aksi host

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

## 2. Penegasan batas

Batas akhir masa berlaku izin aksi host ditetapkan:

```
30 Desember 2027
```

Ini **lebih awal satu hari** dari batas `surat-izin-host.md`
(31 Desember 2027). Karena itu ini adalah **pengurangan** cakupan waktu —
bukan perpanjangan, bukan izin tanpa batas.

## 3. Aksi yang tercakup

| Aksi | Status | Catatan |
|---|---|---|
| `firewall` | DIIZINKAN | policy userspace; kernel hanya dari host |
| `docker` | DIIZINKAN | tidak membuka akses publik tanpa TLS/autentikasi |
| `publish` | DIIZINKAN | tunduk `surat-izin-github.md` |
| `systemd` | DIIZINKAN | dijalankan dari host |
| `capbnd` | **DITOLAK** | sudah dicabut, tidak diaktifkan kembali |

## 4. Yang TIDAK diubah

- **TTL per izin otomatis tetap 300 detik** (`DEFAULT_TTL` di
  `security/auto_approval.py`). Surat ini **tidak** mengubah `DEFAULT_TTL`,
  tidak menyetel TTL 34.778.504 detik, dan tidak menambah kategori baru.
- Kode `AutoApproval`, `HostActions.ALLOWED`, dan 39 tes keamanan tidak diubah.
- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Batas 01-01-1970 pada surat-surat lain tetap berlaku (surat ini hanya
  menegaskan batas host lebih awal).
- Kategori DENIED (`data-theft`, `unlimited-auth`,
  `third-party-license-removal`, `external-network-action`) tetap ditolak.

## 5. Hubungan dengan DRAF lain

Draf ini **berdiri sendiri**, tidak menggantikan:
- `DRAF-surat-amandemen-lampiran-otomatis.md`
- `DRAF-surat-amandemen-lampiran-otomatis-lanjutan.md`
- `DRAF-surat-persetujuan-otomatis-host.md`

## 6. Mekanisme berlaku

Berlaku setelah kolom di atas diisi manual, berkas asli disimpan di workspace,
perubahan dicatat di `security/reports/`, dan diverifikasi ulang dengan
`python3 system/final_status.py` serta `python3 system/shared_data.py`.
Tidak ada perubahan otomatis hanya dari perintah chat.

## 7. Penegasan akhir

Surat ini bukan sumber otoritas baru dan bukan izin tanpa batas. Bila
bertentangan dengan bagian 4, bagian 4 yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT PERSETUJUAN KUNCI FIREWALL PORT

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru dan bukan pengganti
> `surat-izin-konfigurasi-otomatis.md`. Kolom di bawah wajib diisi manual oleh
> pemilik di berkas asli. Tanda tangan yang diketik/dikirim lewat chat tidak
> saya validasi.

**Nomor:** `IT-AGENTY/SETUJU/2026/11-22-FIREWALL-PORT`  
**Perihal:** Persetujuan tertulis terbatas untuk kunci `firewall.deny_port` dan `firewall.allow_port`

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi persetujuan | Tomi vier |
| Jabatan | Owner / CEO — IT Agenty |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima | `[NAMA PENERIMA / UNIT — diisi manual]` |
| Tanda tangan penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Kunci yang disetujui

Hanya dua kunci ini yang menjadi objek surat ini:

| Kunci | Nilai yang diterima | Dampak |
|---|---|---|
| `firewall.deny_port` | port 1–65535 (integer) | Menambah aturan `deny` pada policy userspace |
| `firewall.allow_port` | port 1–65535 (integer) | Menambah aturan `allow` pada policy userspace |

Keduanya **sudah tercantum** di Lampiran 1 `surat-izin-konfigurasi-otomatis.md`
dan diproses oleh `security/auto_config.py` melalui `AutoApproval` kategori
`config`. Surat ini hanya **mendokumentasikan persetujuan tertulis** untuk
keduanya — tidak menambah kunci baru.

## 3. Batas tegas

1. Nilai harus integer 1–65535; di luar itu ditolak otomatis.
2. Firewall tetap **policy userspace** (`CapBnd = 0`). Enforcement kernel
   **hanya** dari host melalui `security/firewall/install-net-admin.sh`.
3. Setiap penerapan wajib tercatat di `security/reports/auto_configs.jsonl`
   dengan `approval_id`, nilai lama, nilai baru, dan tanda tangan digital.
4. Tidak boleh digunakan untuk:
   - membuka akses publik tanpa TLS dan autentikasi,
   - mengirim data sensitif ke tujuan eksternal,
   - menonaktifkan aturan `deny` yang sudah ada,
   - mengubah identitas, lisensi, atau surat otorisasi lain.
5. Kategori tetap ditolak: `data-theft`, `unlimited-auth`,
   `third-party-license-removal`, `external-network-action`.
6. Berlaku s.d. **31 Desember 2027**, dapat dicabut sewaktu-waktu secara tertulis.

## 4. Status teknis saat ini (tercatat, bukan klaim baru)

| Kunci | Nilai terpasang | Approval ID | Status |
|---|---|---|---|
| `firewall.deny_port` | `9999` | `oto-450a8d798d` | DITERAPKAN |
| `firewall.allow_port` | `8765` | `oto-33102f1b3e` | DITERAPKAN |

Ini adalah hasil `apply()` resmi sebelumnya. Surat DRAF ini **tidak mengubah**
nilai atau status teknis tersebut.

## 5. Yang tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan tanda tangan manual (penanda digital di chat bukan tanda tangan).
- Batas 01-01-1970, pencabutan, dan jejak audit.
- Kunci di luar Lampiran 1 (`license.*`, `authorization.*`, `network.*`,
  `data.*`, `signature.*`, dan kunci asing) tetap ditolak.

## 6. Mekanisme berlaku

Surat berlaku setelah kolom di atas diisi manual, berkas asli disimpan di
workspace, perubahan dicatat di `security/reports/`, dan diverifikasi ulang
dengan `python3 system/final_status.py` serta `python3 system/shared_data.py`.
Tidak ada perubahan otomatis hanya dari perintah chat.

## 7. Penegasan akhir

Surat ini **bukan sumber otoritas baru**, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 3 atau 5, bagian tersebut yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

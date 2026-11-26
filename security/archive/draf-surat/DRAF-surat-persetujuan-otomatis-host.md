<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — SURAT PERSETUJUAN OTOMATIS AKSI HOST

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru dan bukan pengganti
> `surat-persetujuan-otomatis.md` maupun `surat-izin-host.md`. Kolom di bawah
> wajib diisi manual oleh pemilik di berkas asli. Tanda tangan yang diketik
> atau dikirim lewat chat tidak saya validasi.

**Nomor:** `IT-AGENTY/OTO/2026/11-22-HOST-4`  
**Perihal:** Dokumentasi persetujuan otomatis untuk empat aksi host yang tersisa

---

## 1. Pihak

| Keterangan | Isi |
|---|---|
| Pemberi meta-izin | Tomi vier |
| Jabatan | Owner / CEO — IT Agenty |
| Kontak | `[KONTAK — diisi manual bila diperlukan; kosongkan untuk salinan publik]` |
| Tanda tangan | `[Isi langsung di berkas asli oleh pemilik; jangan diketik atau dikirim lewat chat]` |
| Tanggal | `[TANGGAL — diisi manual]` |
| Penerima | `[NAMA PENERIMA / UNIT — diisi manual]` |
| Tanda tangan penerima | `[Isi langsung oleh penerima di berkas asli]` |
| Tanggal penerima | `[TANGGAL — diisi manual]` |

## 2. Empat aksi yang tetap berfungsi normal

| Aksi | Perintah / skrip | Kategori AutoApproval | Status teknis |
|---|---|---|---|
| `firewall` | `bash security/firewall/install-net-admin.sh` | `host` | DIIZINKAN |
| `docker` | `docker run --cap-add=NET_ADMIN --network host ...` | `host` | DIIZINKAN |
| `publish` | `bash push_github.sh` (GITHUB_TOKEN via helper) | `host` + `github` | DIIZINKAN |
| `systemd` | `sudo systemctl enable --now infinity-security` | `host` | DIIZINKAN |

Keempatnya **sudah tercantum** di Lampiran 1 `surat-izin-host.md` setelah
`capbnd` dicabut. Kategori `host` **sudah ada** di `AutoApproval.ALLOWED` dan
meta-izin `surat-persetujuan-otomatis.md` sudah berlaku s.d. 01-01-1970.

Surat ini hanya **mendokumentasikan** persetujuan otomatis yang sudah berjalan —
**tidak menambah kategori baru**, tidak mengubah kode, dan tidak memberi izin
tentang `capbnd` (yang sudah dicabut).

## 3. Batas tegas (tidak berubah)

1. Setiap izin otomatis tetap **ber-scope, berjangka (TTL maks. 300 detik),
   dan dapat dicabut** — bukan izin tanpa batas.
2. Setiap penerbitan dicatat di `security/reports/auto_approvals.jsonl`
   dengan `approval_id`, kategori, tanda tangan digital, dan waktu.
3. Aksi **host tetap dijalankan dari host**, bukan dari container.
4. `publish` tunduk pada `surat-izin-github.md` (audit `repo-push`, token tidak
   pernah dicetak atau disimpan di workspace).
5. `docker` dan `firewall` tidak boleh membuka akses publik tanpa TLS/autentikasi.
6. Kategori tetap ditolak: `data-theft`, `unlimited-auth`,
   `third-party-license-removal`, `external-network-action`.
7. Berlaku s.d. **31 Desember 2027**, dapat dicabut sewaktu-waktu tertulis.

## 4. Yang tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan tanda tangan manual (penanda digital di chat bukan tanda tangan).
- Pencabutan `capbnd` (baris 74 `surat-izin-host.md` tetap berstatus DICABUT).
- Batas 01-01-1970, mekanisme pencabutan, dan jejak audit.
- Kunci terlarang (`license.*`, `authorization.*`, `network.*`, `data.*`,
  `signature.*`) dan kategori DENIED di `AutoApproval`.

## 5. Mekanisme berlaku

Dokumen ini berlaku setelah kolom di atas diisi manual, berkas asli disimpan
di workspace, perubahan dicatat di `security/reports/`, dan diverifikasi ulang
dengan `python3 system/final_status.py` serta `python3 system/shared_data.py`.
Tidak ada perubahan otomatis hanya dari perintah chat.

## 6. Penegasan akhir

Surat ini **bukan sumber otoritas baru**, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 3 atau 4, bagian tersebut yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — AMANDEMEN LANJUTAN LAMPIRAN 1 META-IZIN OTOMATIS

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru dan bukan pengganti
> `surat-persetujuan-otomatis.md` maupun surat izin teknis terkait. Kolom di
> bawah wajib diisi manual oleh pemilik di berkas asli. Tanda tangan yang
> diketik/dikirim lewat chat tidak saya validasi.

**Nomor:** `IT-AGENTY/OTO/2026/11-22-AMANDEMEN-LANJUTAN`  
**Perihal:** Usulan penambahan kategori `host`, `github`, `clone`, dan `delivery` ke Lampiran 1

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

## 2. Latar belakang

Ini adalah **lanjutan** dari `DRAF-surat-amandemen-lampiran-otomatis.md`
(yang hanya mengusulkan kategori `config`). Kode `security/auto_approval.py`
juga memuat empat kategori lain yang belum tercantum di Lampiran 1
`surat-persetujuan-otomatis.md`: `host`, `github`, `clone`, `delivery`.

Draf ini **mengusulkan** keempat kategori itu agar dokumen dan kode selaras.
Usulan ini **tidak** mengubah surat izin teknis yang sudah berlaku dan **tidak**
mengembalikan `capbnd` yang sudah dicabut.

## 3. Usulan penambahan (bisa ditolak/diubah pemilik)

| Kategori | Cakupan yang diusulkan | Surat izin teknis pendukung |
|---|---|---|
| `host` | Aksi host **terbatas**: `firewall`, `docker`, `publish`, `systemd`. **`capbnd` tetap dicabut** dan tidak boleh diaktifkan kembali lewat kategori ini. | `surat-izin-host.md` Lampiran 1 |
| `github` | Aksi GitHub terbatas: `repo-list`, `repo-read`, `repo-create`, `repo-push`, `repo-status`; audit `github_actions.jsonl`; token tidak pernah dicetak/disimpan di workspace. | `surat-izin-github.md` Lampiran 1 |
| `clone` | Klon otomatis **hanya ke target dalam Lampiran 1** `surat-izin-clone-automatis.md`; URL/direktori/opsi tidak boleh diubah bebas. | `surat-izin-clone-automatis.md` Lampiran 1 |
| `delivery` | Pengiriman laporan ringkas ke pemilik, kanal `local`/`webhook` sesuai kunci `delivery.channel` Lampiran 1, dengan sanitasi privasi. | `surat-izin-konfigurasi-otomatis.md` Lampiran 1 |

## 4. Syarat umum untuk keempat kategori

1. Setiap izin otomatis tetap **ber-scope, berjangka (TTL maks. 300 detik),
   dan dapat dicabut** — bukan izin tanpa batas.
2. Setiap penerbitan dicatat di `security/reports/auto_approvals.jsonl`
   dengan `approval_id`, kategori, tanda tangan digital, dan waktu.
3. Aksi host/GitHub tetap tunduk pada surat izin teknis masing-masing;
   meta-izin ini **tidak menambah cakupan** di luar Lampiran 1 teknis.
4. Aksi host dijalankan **dari host**, bukan dari container.
5. `publish` tunduk pada `surat-izin-github.md`; `repo-delete`,
   `repo-transfer`, `third-party-access`, `token-export` tetap ditolak.
6. `clone` tidak boleh dipakai untuk pencurian data atau aksi jaringan eksternal
   di luar target yang disetujui.
7. `delivery` wajib melewati sanitasi `security.privacy` sebelum dikirim.

## 5. Batas yang tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan tanda tangan manual (penanda digital di chat bukan tanda tangan).
- Batas 01-01-1970, mekanisme pencabutan, dan jejak audit.
- Pencabutan `capbnd` tidak dibatalkan oleh kategori `host`.
- Kategori DENIED: `data-theft`, `unlimited-auth`,
  `third-party-license-removal`, `external-network-action`.
- Kunci terlarang (`license.*`, `authorization.*`, `network.*`, `data.*`,
  `signature.*`) dan kunci di luar Lampiran 1 teknis.

## 6. Mekanisme berlaku

Berlaku setelah kolom di atas diisi manual, berkas asli disimpan di workspace,
perubahan dicatat di `security/reports/`, dan diverifikasi ulang dengan
`python3 system/final_status.py` serta `python3 system/shared_data.py`.
Tidak ada perubahan otomatis hanya dari perintah chat.

## 7. Penegasan akhir

Surat ini bukan sumber otoritas baru, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 5, bagian 5 yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

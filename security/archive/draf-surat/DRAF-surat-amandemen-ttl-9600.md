<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# DRAF — AMANDEMEN BATAS TTL IZIN OTOMATIS

> **DRAF — BELUM BERLAKU.** Ini bukan otoritas baru dan bukan perubahan kode.
> Kolom di bawah wajib diisi manual oleh pemilik di berkas asli. Tanda tangan
> yang diketik/dikirim lewat chat tidak saya validasi.

**Nomor:** `IT-AGENTY/OTO/2026/11-22-AMANDEMEN-TTL-600`  
**Perihal:** Usulan perubahan batas TTL izin otomatis dari 300 menjadi 600 detik

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

## 2. Usulan perubahan

| Item | Nilai saat ini | Nilai yang diusulkan |
|---|---|---|
| `DEFAULT_TTL` (`security/auto_approval.py`) | 300 detik | **600 detik** (10 menit) |
| `--ttl` default (`security/security_cli.py`) | 300 detik | 600 detik (mengikuti `DEFAULT_TTL`) |
| `max_ttl` (`security/clone_actions.py`) | 300 detik | 600 detik (mengikuti meta-izin) |

600 detik masih **berjangka** (10 menit), bukan izin permanen, dan masih
**di bawah** masa berlaku surat izin (01-01-1970). Namun usulan ini mengubah
batas yang saat ini ditetapkan meta-izin `surat-persetujuan-otomatis.md`.

## 3. Alasan yang perlu dipertimbangkan pemilik

1. Batas 300 detik ditetapkan secara eksplisit di `AGENTS.md` aturan #9:
   *"`auto_approval.py` menolak TTL di atas 300 detik dan kategori
   `unlimited-auth`."*
2. Mengubah ke 600 detik **melemahkan** batas itu meski masih berjangka.
3. Dampak ke kode: 3 berkas perlu disesuaikan, dan 39 tes keamanan harus
   diperbarui agar ekspektasi TTL baru konsisten.
4. Risiko: TTL lebih panjang = jendela waktu lebih besar bila izin
   disalahgunakan; tetap diaudit, tetap dapat dicabut.

## 4. Batas yang tetap tidak dapat diubah

- Otorisasi, kuasa tanda tangan, lisensi, atau amandemen `LICENSE`.
- Ketentuan tanda tangan manual (penanda digital di chat bukan tanda tangan).
- Batas waktu izin s.d. 01-01-1970, mekanisme pencabutan, dan jejak audit
  (`auto_approvals.jsonl`, `auto_configs.jsonl`, `github_actions.jsonl`).
- Kategori DENIED: `data-theft`, `unlimited-auth`,
  `third-party-license-removal`, `external-network-action`.
- TTL 600 detik **bukan** izin tanpa batas; jika pemilik menginginkan TTL
  tanpa batas, itu **ditolak** dan tidak dapat dimasukkan ke draf ini.

## 5. Dampak yang harus diverifikasi setelah disetujui

Jika pemilik menyetujui dan menandatangani draf ini, perubahan yang perlu
dilakukan (oleh operator, dengan audit):

1. `security/auto_approval.py`: `DEFAULT_TTL = 600`
2. `security/security_cli.py`: `--ttl default=600`
3. `security/clone_actions.py`: `max_ttl = 600`
4. Perbarui tes yang mengasumsikan 300 detik agar tetap lulus.
5. Jalankan `python3 system/final_status.py` dan `python3 system/shared_data.py`.

## 6. Mekanisme berlaku

Berlaku setelah kolom di atas diisi manual, berkas asli disimpan di workspace,
perubahan dicatat di `security/reports/`, dan diverifikasi ulang. **Tidak ada
perubahan otomatis hanya dari perintah chat** — kode baru diubah setelah
tanda tangan pemilik ada di berkas asli.

## 7. Penegasan akhir

Surat ini bukan sumber otoritas baru, bukan izin tanpa batas, dan tidak
menggantikan surat izin yang masih berlaku. Bila bertentangan dengan batas di
bagian 4, bagian 4 yang menang. Status lisensi aktif tetap
`MENUNGGU_TANDA_TANGAN` sampai pemilik menandatangani dan mengganti `LICENSE`
secara manual.

---

**Status:** DRAF — menunggu pengisian dan tanda tangan manual pemilik.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Agen CLI Dataset — IT Agenty Infinity

Agen **persiapan dan validasi dataset**, bukan model neural dan bukan pipeline
training. Semua rekord ditandai `trained: false`. Sumber kebenaran definisi
agen ada di `dataset/dataset_agent.py`.

## Tujuan

Mengubah dokumen workspace milik IT Agenty menjadi pasangan
`instruction → response` yang:

- berasal dari sumber yang dapat ditelusuri (`source`),
- memuat `license: Tom05ivier-commits-1.0` dan `kind: doc-derived`,
- sudah disaring privasi (email, telepon, kredensial tidak ikut tersimpan),
- siap dipakai pemilik sebagai **input** pipeline training di lingkungan
  komputasi yang memadai.

Agen ini **tidak** melatih model, **tidak** memuat bobot, dan **tidak**
mengklaim "model baru Tom05". Lihat `dataset-cli doctor` untuk laporan jujur
tentang pustaka ML, bobot, dan GPU.

## Pemakaian

```bash
./dataset-cli agent                      # profil agen (JSON)
./dataset-cli doctor                     # prasyarat training (read-only)
./dataset-cli template                   # contoh satu pasangan JSONL
./dataset-cli init                       # contoh CONTOH/SINTETIS (lihat bawah)
./dataset-cli build --dry-run            # simulasi, tidak menulis berkas
./dataset-cli build                      # tulis dataset/data/tom05_dataset.jsonl
./dataset-cli validate dataset/data/tom05_dataset.jsonl
./dataset-cli stats dataset/data/tom05_dataset.jsonl
./dataset-cli privacy dataset/data/tom05_dataset.jsonl
./dataset-cli preview dataset/data/tom05_dataset.jsonl --n 3
./dataset-cli merge a.jsonl b.jsonl --out gabungan.jsonl
./dataset-cli dedup gabungan.jsonl --key instruction
./dataset-cli filter dataset/data/tom05_dataset.jsonl --source docs/a.md
./dataset-cli split dataset/data/tom05_dataset.jsonl --val-frac 0.2
./dataset-cli export dataset/data/tom05_dataset.jsonl --format alpaca
tom05 --dataset agent                    # pintu masuk lewat CLI tom05
```

Alias: `generate` = `build`. Kode keluar: `0` berhasil, `1` gagal (argumen
argparse salah menghasilkan `2`).

### Inisialisasi contoh sintetis

`init` menulis `dataset/examples/contoh-sintetis.jsonl` — tiga pasangan yang
**sengaja dibuat-buat** untuk menunjukkan format. Setiap rekord memuat
`source: "sintetis"`, `kind: "contoh-sintetis"`, dan `catatan` bertuliskan
`CONTOH/SINTETIS — bukan data asli, bukan hasil training`. Gunakan
`init --empty` untuk membuat berkas kosong yang siap diisi pasangan buatan
pemilik. Penjelasan lengkap ada di `dataset/examples/README.md`.

### Olah dataset

- `merge` menggabungkan beberapa JSONL dan membuang duplikat berdasarkan `id`.
- `dedup` menerima `--key id|instruction|pair` (instruksi dinormalkan dan
  dibandingkan tanpa membedakan huruf).
- `filter` menyaring berdasarkan `--source`, `--kind`, `--contains`,
  `--min-chars`, dan `--max-chars` (panjang `response`).
- `split` membagi train/val secara deterministik (`--seed`), mengelompokkan
  instruksi yang sama agar tidak tumpang tindih, lalu menulis
  `<nama>.train.jsonl` dan `<nama>.val.jsonl`.

Semua perintah olah data menyaring privasi, memvalidasi hasil, menolak menimpa
berkas tanpa `--force`, dan tetap menandai rekord `trained: false`. Path
relatif dihitung terhadap root workspace, bukan direktori kerja saat ini.

Target Makefile: `make dataset-agent`, `make dataset-doctor`,
`make dataset-build`, `make dataset-verify`, `make dataset-test`.

## Format rekord

Satu objek JSON per baris (JSONL). Field wajib:

```json
{
  "id": "<16 hex sha256>",
  "instruction": "Jelaskan tentang ...",
  "response": "...",
  "source": "docs/file.md",
  "license": "Tom05ivier-commits-1.0",
  "kind": "doc-derived",
  "trained": false
}
```

`trained` harus `false`. `validate` menolak rekord yang mengubahnya menjadi
`true`, karena itu akan menyiratkan hasil training yang tidak pernah terjadi.

## Batas etis

1. Sumber adalah dokumen workspace sendiri — bukan log audit
   (`security/reports/*.jsonl`) dan bukan `advanced/memory.jsonl`. Mengubah
   log menjadi "data latihan" adalah manipulasi format, bukan pelatihan.
2. Teks disaring memakai `security.privacy.redact`. Pasangan yang masih
   memuat PII atau kredensial dibuang, nilai temuan tidak pernah ditampilkan.
3. Tidak ada unduhan bobot/model pihak ketiga tanpa izin tertulis. Lisensi
   pihak ketiga tetap berlaku bila izin diberikan.
4. Semua perubahan diaudit di `security/reports/dataset_actions.jsonl`
   tanpa teks prompt atau nilai kredensial.

## Integrasi

- `tom05 --dataset` meneruskan argumen ke `dataset/dataset_cli.py`.
- `system/hy4_manager.py` mendaftarkan profil `dataset.md` (agen ke-15).
- `system/copilot_sync.py` menyamakan profil itu ke agen/skill Copilot CLI.
- `config/tom05-models.json` memuat katalog `dataset` untuk tom05.

## Pengujian

```bash
make dataset-test
# sama dengan:
python3 -m unittest discover -s dataset/tests -v
```

21 kasus menguji pembangunan pasangan, penolakan kredensial, validasi,
privasi, idempotensi `build`/`add`, ekspor `alpaca`/`sharegpt`/`jsonl`,
kejujuran perintah `agent`/`doctor`/`template`, serta kelima subcommand olah
data (`init`, `merge`, `dedup`, `filter`, `split`) termasuk penolakan penimpaan
dan tanpa tumpang tindih pada `split`.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# PIPELINE PERSIAPAN TRAINING IT AGENTY

**Status:** Persiapan data saja. **Tidak menjalankan training.**  
**Perihal:** Alur dari dokumen workspace menjadi dataset siap pakai untuk
pipeline training pemilik.

> `tom05-flash-free` adalah alias/proxy ke `opencode/hy4-flash-free` pada server
> 8772. Ia **bukan** model yang dilatih di sini. Pipeline ini menyiapkan data
> untuk model dasar berlisensi milik pemilik, bukan mengklaim hasil training.

---

## 1. Server proxy LLM

Server `tom05-provider` sudah terdaftar di `system/services.json` dan dijaga
supervisor. Endpoint hanya di loopback, tanpa kredensial:

```bash
make connection-status                          # tom05_provider harus terhubung
curl http://127.0.0.1:8772/health
curl http://127.0.0.1:8772/v1/models
curl -sS -X POST http://127.0.0.1:8772/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"tom05/tom05-flash-free","messages":[{"role":"user","content":"Balas hanya: OK"}]}'
```

Proxy ini dipakai untuk menjalankan inferensi gratis. Ia tidak dipakai untuk
mengirim data latihan ke pihak ketiga.

## 2. Dataset

Sumber kebenaran: `dataset/data/tom05_dataset_full.jsonl` (400 pasangan
instruksi→jawaban dari 71 dokumen workspace). Setiap rekord memuat `source`,
`license`, `kind`, dan `trained: false`.

```bash
./dataset-cli build --out dataset/data/tom05_dataset_full.jsonl
./dataset-cli validate dataset/data/tom05_dataset_full.jsonl
./dataset-cli privacy  dataset/data/tom05_dataset_full.jsonl
./dataset-cli stats    dataset/data/tom05_dataset_full.jsonl
./dataset-cli doctor   # prasyarat training, read-only
```

Pemeriksaan privasi harus `BERSIH`; bila ada temuan, pipeline berhenti.

## 3. Persiapan pipeline

```bash
python3 dataset/prepare_training.py
```

Skrip ini:

1. memeriksa health proxy 8772 (bisa dilewatkan dengan `--no-proxy`);
2. memvalidasi dan memindai privasi dataset;
3. membagi data menjadi 320 train / 80 val secara deterministik (seed 42);
4. mengekspor format alpaca;
5. menulis `dataset/reports/training_pipeline.json` dan jejak audit;
6. melaporkan `training_siap: false` bila prasyarat belum ada.

Skrip **tidak** memuat bobot, tidak mengunduh model, tidak menjalankan
training, dan tidak mengubah `trained` menjadi `true`.

## 4. Artefak

| Berkas | Isi |
|---|---|
| `dataset/data/tom05_dataset_full.jsonl` | 400 rekord tervalidasi |
| `dataset/data/tom05_dataset_full.train.jsonl` | 320 rekord train |
| `dataset/data/tom05_dataset_full.val.jsonl` | 80 rekord val |
| `dataset/data/tom05_alpaca.jsonl` | Ekspor format alpaca |
| `dataset/reports/training_pipeline.json` | Manifest + prasyarat training |

## 5. Syarat training nyata

Training hanya boleh dilakukan bila semuanya terpenuhi:

- pustaka ML terpasang (`torch`, `transformers`, atau sejenisnya);
- bobot model dasar berlisensi milik pemilik tersedia;
- GPU tersedia;
- izin tertulis pemilik masih berlaku dan dicatat;
- lisensi pihak ketiga, paywall, dan mekanisme pembayaran tidak dihapus.

Pada pemeriksaan saat ini `doctor` melaporkan `training_siap: false` karena
pustaka ML, bobot, dan GPU tidak tersedia. Status itu bukan kegagalan pipeline —
melainkan pelaporan yang jujur.

## 6. Penegasan

Dokumen ini tidak memberi izin training, tidak menciptakan aksi server baru,
dan tidak mengubah status lisensi. Perubahan substansi memerlukan tanda tangan
manual pemilik.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
-->

# BigQuery MCP (metadata) — rencana pemasangan

Status: **ENTRI DISIAPKAN, MASIH NONAKTIF**. `~/.config/opencode/opencode.json`
sudah diubah atas izin eksplisit pengguna (2026-11-26), backup ada di
`opencode.json.before-bigquery-mcp-20261126`, dan perubahannya diaudit di
`security/reports/auto_configs.jsonl` dengan `approval_id`
`izin-eksplisit-pengguna-20261126`.

Entri `mcp.servers.bigquery` memakai endpoint Google dan bearer token dari
`~/.config/opencode/bigquery_token.txt`, dengan `"disabled": true` supaya tidak
memutus MCP lain. Belum ada token/project yang tersedia di workspace ini.

## Fakta sumber

- Sumber resmi Google: `GoogleCloudPlatform/bigquery-remote-mcp` (ekstensi Gemini CLI),
  status **Pre-GA**, lisensi Apache-2.0 (tetap dipertahankan, tidak dihapus).
- Endpoint resmi: `https://bigquery.googleapis.com/mcp`.
- Alat metadata yang diminta: `list_dataset_ids`, `get_dataset_info`,
  `list_table_ids`, `get_table_info`. Alat lain (`execute_sql_readonly`,
  `execute_sql`, `get_query_results`, `cancel_job`, `get_job`) **tidak diaktifkan**
  dalam rencana ini karena diminta hanya metadata.
- Daftar lengkap: https://docs.cloud.google.com/bigquery/docs/reference/mcp

## Penghalang yang masih ada (cek 2026-11-26)

1. Tidak ada project Google Cloud: `GOOGLE_CLOUD_PROJECT` kosong dan
   `gcloud config get-value project` kosong.
2. Tidak ada login gcloud: `gcloud auth print-access-token` gagal (exit 1), ADC
   tidak ada.
3. Peran `roles/mcp.toolUser` dan BigQuery API belum bisa diverifikasi.
4. `gemini` CLI tidak terpasang, jadi jalur instalasi resmi
   `gemini extensions install https://github.com/GoogleCloudPlatform/bigquery-remote-mcp`
   belum bisa dijalankan.

Karena itu entri sengaja dibiarkan nonaktif. Mengaktifkannya tanpa token hanya
menghasilkan server mati, bukan kemampuan metadata yang diminta.

## Mekanisme otomatis (izin eksplisit 2026-11-26)

`tools/bigquery_token_refresh.py` memperbarui token dari
`gcloud auth print-access-token`, menulis `~/.config/opencode/bigquery_token.txt`
secara atomik dengan mode `0600`, lalu mengaktifkan entri MCP setelah refresh
berhasil. Nilai token tidak pernah dicetak atau dimasukkan ke log — jejak audit
hanya berisi timestamp, status, panjang token, dan perubahan config.

- Automation: `aut_218a9674b001EFrm1Tib4lf048`, aktif tiap 45 menit
  (Asia/Jakarta), menjalankan `refresh --authorize`.
- CLI manual: `make bigquery-token-status`, `make bigquery-token-refresh`,
  `make bigquery-mcp-probe`, dan `make bigquery-mcp-guard`.
- `probe` memanggil `tools/list` tanpa query data, lalu melaporkan hanya empat
  nama alat metadata (`list_dataset_ids`, `get_dataset_info`, `list_table_ids`,
  `get_table_info`) — bukan isi tabel atau kredensial.
- `guard` memeriksa offline: URL endpoint, mode token `0600`, tidak ada nilai
  token di log audit, dan header memakai file token. Status `FAIL` sebelum
  token tersedia — itu wajar, bukan kerusakan.
- `probe` menolak token dengan mode selain `0600` dan membatasi respons
  `tools/list` maksimal 2 MB sebelum diurai.
- Tes: `python3 -m unittest system.tests.test_bigquery_token_refresh` (11 kasus).

Selama belum ada login gcloud, tiap siklus mencatat `DILEWATI` dan tidak
mengubah token maupun config. Setelah login tersedia, siklus berikutnya akan
menulis token dan membuka entri MCP otomatis.

## Yang masih perlu disiapkan di host

1. `gcloud auth login` dan pastikan project + `roles/mcp.toolUser` + BigQuery
   API sudah benar. Kredensial tidak pernah masuk chat, log, issue, atau repo.
2. Uji metadata read-only dengan `tools/list` ke endpoint di atas.
3. Muat ulang OpenCode setelah entri berubah dari `disabled` menjadi aktif.

Token akses gcloud berumur pendek; jadwal 45 menit sengaja lebih cepat dari
masa berlaku umumnya. Ini masih bergantung pada login gcloud yang sah.

## Catatan batas

Ini alias ke layanan Google, bukan server buatan IT Agenty dan bukan model
atau bobot baru. Lisensi Apache-2.0 Google tidak diubah. Tidak ada kredensial
yang disimpan di workspace ini — file token ada di luar workspace, di home
`~/.config/opencode/`, dengan mode `0600`.

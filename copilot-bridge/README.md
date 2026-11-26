<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Copilot Bridge v2

Jembatan OpenAI-compatible untuk GitHub Copilot CLI → **OpenCode hy4-flash-free**.

## Kemampuan

| Fitur | Keterangan |
|---|---|
| Model | `opencode/hy4-flash-free`, varian bisa diatur via `COPILOT_BRIDGE_VARIANT` |
| System prompt | Otomatis memuat identitas, lisensi, dan aturan dari `.github/copilot-instructions.md` |
| Streaming | SSE `text/event-stream` dengan potongan 120 karakter + `[DONE]` |
| Retry | 2 percobaan dengan jeda eksponensial bila OpenCode gagal |
| Cache | 64 respons terakhir (SHA-256 prompt) untuk mempercepat pengulangan |
| Riwayat | Hanya 8 pesan terakhir yang diteruskan agar konteks tetap terukur |
| Metrik | `/v1/metrics`: calls, errors, cache hits, latency rata-rata |
| Health | `/v1/health` dan `/v1/models` |

## Endpoint

- `GET /v1/health` — status bridge
- `GET /v1/models` — daftar model (`hy4-flash-free`)
- `GET /v1/metrics` — statistik operasional
- `POST /v1/chat/completions` — kompletasi chat (streaming & non-streaming)

## Konfigurasi

| Variabel | Default | Fungsi |
|---|---|---|
| `COPILOT_BRIDGE_PORT` | 8766 | Port bridge |
| `COPILOT_BRIDGE_MODEL` | `opencode/hy4-flash-free` | Model OpenCode |
| `COPILOT_BRIDGE_VARIANT` | kosong | Varian model, mis. `high` |
| `COPILOT_BRIDGE_TIMEOUT` | 180 | Timeout subprocess (detik) |

Entry point: `./run_copilot.sh` (menyalakan bridge otomatis bila mati).

## Batas

Bridge tidak mengekspos tool-calling penuh; Copilot CLI dapat memakai mode chat dan
perintah non-interaktif (`-p`). Fitur cloud GitHub (Copilot agent, code review)
tetap memakai model GitHub, bukan model lokal ini.

## Pengujian

```bash
python3 -m unittest discover -s copilot-bridge/tests -v
```

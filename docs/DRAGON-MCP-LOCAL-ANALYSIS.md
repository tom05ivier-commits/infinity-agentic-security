<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Analisis Lokal: Dragon MCP ↔ IT Agenty

## Sumber & atribusi

- Halaman: **Dragon** di MCP Market — https://mcpmarket.com/server/dragon
- Repo: https://github.com/arthurpanhku/dragonmcp
- Penulis: **arthurpanhku** · Lisensi kode: **MIT** (© arthurpanhku — haknya
  tetap dipertahankan; saya **tidak** menyalin, mengklaim, atau memodifikasi
  kode itu).
- Ringkasan ini hanya **fakta + tautan + atribusi**, seperti pola
  `docs/CHINESE-AI-AGENTS-ANALYSIS.md`.

## Ringkasan fakta

DragonMCP adalah server **Model Context Protocol (MCP)** yang memberi agen AI
akses ke data publik Hong Kong & perbatasan Tiongkok:

| Tool | Sumber | API key |
|---|---|---|
| `search_mtr_schedule` | MTR via `data.gov.hk` | tidak perlu |
| `hk_weather_current` | Hong Kong Observatory | tidak perlu |
| `hk_typhoon_signal` | Hong Kong Observatory | tidak perlu |
| `search_transit_route` | MTR / Amap | CN only |
| `system_run_selftest` | semua upstream | tidak perlu |
| `amap_*` (POI, jalan kaki, mobil, transit, sepeda) | Amap/Gaode | **perlu key own** |

Fakta penting:
- Dibangun dengan **Express + MCP SDK + TypeScript**, Node.js ≥ 18.
- Prinsip tegas: **"no mock tools"** — bila upstream mati, tool bilang mati,
  bukan mengarang jawaban; ada `system_run_selftest` untuk verifikasi.
- Batas yang dinyatakan sendiri: rute meminimalkan **transfer**, bukan waktu;
  arrival real-time hanya untuk leg pertama; 2 stasiun tanpa feed; Amap hanya
  untuk daratan Tiongkok dan butuh key; lintas batas belum jadi.
- Roadmap: provenance (`source`, `fetched_at`, `freshness`), lintas batas,
  lebih banyak sumber `data.gov.hk`, Macau.
- ~22 GitHub stars (per halaman MCP Market).

## Hubungan dengan pekerjaan sebelumnya ("ingat ini")

| Dragon MCP | ↔ | IT Agenty (bukti lokal) |
|---|---|---|
| Prinsip **"no mock tools"** | ↔ | `chat_dispatch` tidak mengarang jawaban: pesan gagal diarsip `GAGAL`, tidak diulang; `trained: false` pada model lokal | `system/chat_dispatch.py`, `system/tom05_knowledge.py` |
| `system_run_selftest` (cek semua upstream) | ↔ | `make chip-verify`, `make dataset-verify`, `chip/firewall_drill.py` (mutation testing) — verifikasi sebelum klaim | `Makefile`, `chip/firewall_drill.py` |
| **MCP server** untuk agen | ↔ | MCP kita sudah ada: `filesystem`, `sequential-thinking`, `playwright` di `opencode.json`; ini contoh server MCP eksternal, bukan milik kita | `~/.config/opencode/opencode.json` (hanya nama, bukan kredensial) |
| Data publik **tanpa key** (HK) | ↔ | sumber data lokal kita: `rules.json`, katalog model, laporan chip — semuanya read-only, tanpa kredensial | `config/opencode-localhost.json` |
| Alat butuh **API key own** (Amap) | ↔ | kami **tidak** menyimpan/menampilkan kunci; `auto_approval` menolak `external-network-action` dan kategori `unlimited-auth` | `security/auto_approval.py` |
| Agen↔layanan **lokal** (last-mile) | ↔ | jalur lokal `:8773` (`tom05-selfhost`, retrieval dari data workspace) dan `chip-local-ai` (lokal, tak dipublish) | `system/tom05_selfhost.py`, `chip-local-ai/README.md` |
| Artikel **Chinese AI Agents** (Second Talent) sebelumnya | ↔ | Dragon melengkapi "local life services" yang disebut artikel itu (WorkBuddy/AutoClaw lewat chat; Coze self-host). Kita pilih yang **self-host & read-only**, bukan yang pembayaran | `docs/CHINESE-AI-AGENTS-ANALYSIS.md` |

## Keputusan saya (jujur)

1. **Tidak** meng-clone repo `arthurpanhku/dragonmcp`, tidak `npm install`, tidak
   menjalankan server itu — semuanya butuh akses jaringan eksternal
   (`external-network-action` = kategori **ditolak otomatis** oleh meta-izin).
2. **Tidak** memasang `AMAP_API_KEY` atau kredensial lain; tidak ada kunci yang
   saya minta, simpan, atau tampilkan.
3. **Tidak** mengklaim Dragon sebagai bagian dari tom05/IT Agenty. Ini proyek
   pihak ketiga berlisensi MIT.
4. Yang saya buat hanyalah **dokumen lokal ini** — agar model retrieval `:8773`
   (yang mengindeks `docs/*.md`) bisa menjawab pertanyaan tentang Dragon dari
   data yang kita punya, dengan atribusi yang benar.

## Bila ingin pemasangan sungguhan (butuh Anda)

| Langkah | Syarat |
|---|---|
| Clone + `npm install` + `npm run build` | Izin tertulis `external-network-action` (baru; meta-izin menolak) |
| Daftarkan sebagai server | `./run_system.sh service-add` (aturan #11) — bukan server liar |
| Konek ke `opencode.json` `mcp` | Review + cadangan konfigurasi; **tanpa** kredensial di chat/file proyek |
| Pakai tool Amap | Kunci milik Anda, disimpan di pengelola kredensial (0600), tidak pernah dicetak |

Itu semua **tidak saya lakukan** tanpa perintah & izin tertulis Anda.

Lisensi dokumen ini: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.
Kode DragonMCP tetap **MIT © arthurpanhku**.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Analisis: Chinese AI Agents (Second Talent) ↔ IT Agenty

## Sumber & atribusi

- Artikel: **"10 Best Chinese AI Agents to Try in 2026"** — Matt Li, Second Talent,
  17 September 2026.
- URL: https://www.secondtalent.com/resources/chinese-ai-agents/
- Hak cipta artikel tetap milik **Second Talent / Cowsquare Technology Limited**.
  Di sini hanya **ringkasan fakta + tautan + atribusi** — tidak menyalin konten,
  tidak membuka akses jaringan tambahan, tidak mengklaim lisensi atas tulisan itu.

## Ringkasan fakta (10 agen)

| Agen | Perusahaan | Fokus | Mulai berbayar |
|---|---|---|---|
| Kimi | Moonshot AI | riset, slide, parallel tasks | $19/bln |
| QwenWork | Alibaba | dokumen, web, computer use | $20/bln |
| MiniMax Agent | MiniMax | web, dokumen, video | $22/bln |
| WorkBuddy | Tencent | tugas tim dari Slack/Telegram | $10/bln |
| AutoClaw | Z.ai | otomasi kantor & browser | $18/bln (GLM Coding Plan) |
| Accio Work | Alibaba International | e-commerce | $19,90/bln |
| Lovart | Evoken | desain brand & marketing | $19/bln |
| Skywork | Kunlun Tech | web bisnis & slide | setelah login |
| Coze | ByteDance | membangun agen sendiri (Apache 2.0) | $9/bln |
| Flowith | Flowith | gambar & video | $19,90/bln |

Fakta lain yang tercantum: Kimi Swarm memecah tugas hingga **300 sub-agen /
4.000+ tool call**; AutoClaw memberi **100 juta token GLM-5.3-Flash** gratis untuk
pengguna baru; Coze Studio **open-source di bawah Apache 2.0** dan bisa di-self-host.

## Hubungan satu-ke-lain dengan data IT Agenty

| Fakta artikel | Hubungan dengan workspace kita | Bukti lokal |
|---|---|---|
| AutoClaw memakai **GLM-5.3-Flash** (100M token) | Model aktif OpenCode kita sebelumnya adalah `opencode/glm-5.3-flash` (alias proxied, ctl 100M); kini default beralih ke jalur lokal karena kuota habis | `docs/OPENCODE-UPDATE-STATUS.md`, `config/tom05-provider-models.json` |
| Kimi **Swarm** = 300 sub-agen + tool call | Kita punya **relai chat messenger-only** dengan 11 responder (agen, CLI, skill, tool, docker) — Pola yang sama: satu pesan → banyak responder | `config/chat_dispatch.json`, `docs/CHAT-DISPATCH.md` |
| WorkBuddy / AutoClaw dikendalikan lewat **chat apps** | `chat-dispatch` menerima pesan tom05 → antrean → responder, dengan anti-loop & klaim atomik | `system/chat_dispatch.py`, `security/reports/chat_dispatch.jsonl` |
| Coze Studio **self-host**, data tetap di server sendiri | Kita punya server mandiri `:8773` (`tom05-selfhost`) yang menjawab dari data lokal, tanpa pihak ketiga | `system/tom05_selfhost.py`, `docs/FIREWALL-CHIP-ANALYSIS.md` |
| miniMax: koordinasi agen longgar pakai **2,1–3,4× token** tanpa akurasi lebih | Kita membatasi responder ke 11 entri & TTL 300 detik — efisiensi over "makin banyak agen" | `config/chat_dispatch.json`, `security/auto_approval.py` |
| Skywork memakai model Claude/ChatGPT/Gemini di dalam agen | Kita memisahkan identitas tom05 dari model pihak ketiga: katalog tom05 **0 model proxied** | `config/tom05-models.json`, `docs/PROVIDER-TOM05.md` |
| "For confidential work, self-hosted builder keeps data on your own servers" | Prinsip yang sama dipakai `chip-local-ai` (proyek lokal, tidak dipublish) dan `tom05-selfhost` | `chip-local-ai/README.md`, jalur lokal `:8773` |

## Catatan kritis (jujur)

1. Ini **perbandingan eksternal**, bukan rekomendasi komersial. Saya tidak
   menyarankan berlangganan layanan mana pun (pembayaran dilarang tanpa izin
   tertulis baru).
2. Model di artikel (Kimi K3, Qwen3.8, MiniMax-M3, GLM-5.3) adalah **model pihak
   ketiga**. Menyebutnya di sini tidak berarti kita memilikinya atau melatihnya.
3. `glm-5.3-flash` masih ada di `tom05-provider-models.json` sebagai **alias
   proxied** — statusnya sudah tercatat di `AGENTS.md`, bukan model baru tom05.
4. Tidak ada data yang dikirim ke layanan artikel ini; pengambilan artikel
   bersifat read-only dan selesai.

## Hubungan langsung ke proyek `chip-local-ai`

`chip-local-ai` (lokal, tidak dipublish) memiliki scope: chip AI local, hardware,
software, malware-analytics. Titik sambungnya:

- **Kimi Swarm** ↔ ide multi-responder → responder count dijaga 11 (bukan 300).
- **WorkBuddy chat-control** ↔ `chat-dispatch` (pesan → responder).
- **Coze self-host** ↔ `tom05-selfhost` `:8773`.
- **GLM-5.3** ↔ katalog provider (alias, bukan latihan).

Dengan demikian "hubungan satu sama lain" yang diminta adalah:
**artikel (external landscape) → prinsip arsitektur yang sudah kita terapkan
secara lokal & terbatas.**

Lisensi dokumen ini: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.
Artikel sumber tetap © Second Talent.

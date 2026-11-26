<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Alur Kerja Relai Chat — tom05 flash Free

## Prinsip pemisahan peran

`tom05/tom05-flash-free` bertindak **messenger-only**: ia hanya mengirim pesan.
Pesannya diantar ke antrean; yang menjalankan tugas adalah responder lokal
(agen, CLI, skill, tool, dan docker). Model tidak pernah mengeksekusi perintah,
tidak memegang kredensial, dan tidak menerima izin baru.

```
tom05 --dispatch "tugas"
        │
        ▼
system/reports/chat_dispatch/inbox/<id>.json     (pesan, belum dijalankan)
        │  daemon chat-dispatch (terdaftar di system/services.json)
        ▼
system/reports/chat_dispatch/processing/<id>.json (klaim atomik)
        │  config/chat_dispatch.json → argv responder (tanpa shell)
        ▼
system/reports/chat_dispatch/outbox/<id>.json     (jawaban semua responder)
system/reports/chat_dispatch/processed/<id>.json  (arsip, idempoten)
security/reports/chat_dispatch.jsonl              (audit append-only)
```

## Cara pakai

```bash
./tom05 --dispatch "Status sistem, keamanan, chip, koneksi, perangkat, container"
./tom05 --dispatch-status          # antrean, responder, jalur (JSON)
./tom05 --dispatch-run             # proses sekali jalan (manual/uji)
./tom05 --dispatch --to agent,docker "tugas tertentu"
python3 system/chat_dispatch.py recover   # pulihkan klaim stale (proses mati)
```

Atau langsung: `./chat-dispatch.sh send|run|daemon|status|history|responders`.

### Pemicu otomatis (default)

Chat biasa juga memicu alur ini tanpa perintah tambahan:

```bash
./tom05 "Status sistem dan keamanan"
# -> pesan langsung masuk antrean responder, lalu model tetap menjawab seperti biasa
./tom05 --no-dispatch "tanya tanpa responder"   # opsi keluar
TOM05_AUTO_DISPATCH=0 ./tom05 "..."             # lewat environment
```

Pemicu memakai `system/chat_dispatch.py auto-send`, yang hanya menaruh pesan
ke antrean (messenger-only). Dua pengaman: variabel `AGENTY_CHAT_TASK` ada
di dalam responder sehingga panggilan `tom05` dari responder tidak membuat
loop, dan `TOM05_AUTO_DISPATCH=0` mematikan pemicu. Perintah eksplisit
`--dispatch` tetap tersedia bila hanya ingin mengirim pesan tanpa memanggil
model.

Daemon dijalankan otomatis oleh supervisor (`run_always.sh`) lewat entri
`chat-dispatch` di `system/services.json`. Tidak ada server/port baru.

## Responder yang merespons

| Kind | Responder | Peran |
|---|---|---|
| `agent` | `agen-computer`, `advanced-computer` | perencana/runtime/memori & penalaran |
| `cli` | `cli-sistem`, `cli-keamanan`, `cli-chip`, `cli-platform`, `cli-parity` | status, verifikasi, skor, doctor, parity |
| `skill` | `skill-koneksi`, `skill-perangkat` | koneksi & hardware (read-only) |
| `tool` | `tool-status-akhir` | agregat seluruh gate |
| `docker` | `docker-verify` | verifikasi statis container tanpa daemon |

Daftar lengkap dan perintahnya ada di `config/chat_dispatch.json`. Responder
dengan placeholder `{task}` menerima pesan sebagai argumen. Semua responder
juga menerima konteks lewat variabel `AGENTY_CHAT_TASK`, sehingga responder
berbasis status tetap menjawab dalam konteks tugas yang dikirim.

## Keamanan & batas

- **Tanpa shell**: perintah dijalankan dengan `argv`, bukan `sh -c`; tidak ada
  interpolasi variabel shell dari pesan chat. Pesan dibersihkan (NUL/karakter
  kontrol ditolak, maks. 4000 karakter).
- **Tanpa PORT**: variabel `PORT` dibuang dari lingkungan responder, sesuai
  aturan proyek (pakai `AGENTY_PORT`).
- **Redaksi output**: hasil responder disaring `security.privacy.redact`
  sebelum disimpan. Kredensial tidak pernah dicetak.
- **Idempoten & race-proof**: berkas dipindah dengan `os.rename` atomik ke
  `processing/` sebelum dieksekusi. Proses kedua mendapat `SKIP`, sehingga
  tidak ada eksekusi ganda dan tidak ada duplikasi audit walau daemon dan
  `run` manual bersamaan.
- **Anti-loop**: pesan yang gagal tetap diarsipkan (status `GAGAL`), tidak
  dikembalikan ke inbox, agar daemon tidak mengulang tanpa henti.
- **Klaim stale**: klaim yang ditinggalkan proses mati dikembalikan setelah
  1800 detik (margin di atas total batas waktu 11 responder × 120 detik).
- **Tidak ada eskalasi izin**: responder hanya lokal/rutin. Aksi ofensif
  tidak pernah dikirim otomatis; tetap butuh `--authorize` eksplisit dan
  token `AGENTY_RED_AUTH_TOKEN` di lab/localhost maks. 300 detik.

## Pengujian

```bash
python3 -m unittest system.tests.test_chat_dispatch -v
# atau bagian dari: make test
```

Tes mencakup: messenger-only, sanitasi, eksekusi seluruh responder, **regresi
race condition**, pencatatan gagal sekali saja, pemulihan klaim stale,
penyampaian tugas via argv/env, dan larangan `PORT`.

Lisensi: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**.

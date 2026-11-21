<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# AGENTS.md — IT Agenty Infinity

Instruksi proyek untuk OpenCode. Gunakan seluruh data workspace ini sebagai
konteks utama.

## Identitas & lisensi

- Sistem: **IT Agenty — Infinity Computer System**
- Pemilik: **Tomi vier**, Owner / CEO
- Email: `owner@example.invalid` — HP: `000000000000`
- Lahir: `01-01-1970` — Kota, Provinsi
- Tanda tangan digital: `(__signature__)`
- Lisensi: **Tom05ivier-commits-1.0**, pemilik **Tomi vier**
- Model aktif: `opencode/hy4-flash-free`

## Aturan tetap

1. **Selalu jalankan komputer** — `./run_always.sh` harus aktif; heartbeat di
   `system/reports/heartbeat.json`.
2. Setiap file baru wajib memuat header:
   `SPDX-License-Identifier: Tom05ivier-commits-1.0` dan `Copyright (c) 2026 Tomi vier`.
3. **Dilarang mencuri, mengekstraksi, atau mengirim data.** `dlp` hanya untuk
   deteksi & karantina paparan data.
4. Aksi ofensif hanya di lab/localhost dengan `AGENTY_RED_AUTH_TOKEN`, maksimal
   300 detik, dan `--authorize` eksplisit.
5. Otorisasi tertulis berlaku s.d. **31 Desember 2027** dan dapat dicabut:
   `surat-izin-keamanan.md`, `surat-kuasa-tandatangan.md`,
   `surat-persetujuan-clone.md`, `surat-persetujuan-terbatas.md`.
6. Firewall berjalan sebagai policy userspace (`CapBnd = 0`); enforcement
   kernel hanya dari host via `security/firewall/install-net-admin.sh`.
7. Jangan pakai variabel `PORT` untuk layanan proyek — gunakan `AGENTY_PORT`.
8. **Ingat meta-izin otomatis**: `surat-persetujuan-otomatis.md` mengizinkan
   penerbitan izin otomatis hanya untuk kategori rutin (server-add, verify,
   integrity, dlp, campaign, debug, efficacy, finalize). Setiap izin dicatat di
   `security/reports/auto_approvals.jsonl`. Kategori `data-theft`,
   `unlimited-auth`, `third-party-license-removal`, dan `external-network-action`
   **tetap ditolak**.
9. **Ingat: semua izin tetap terbatas.** Permintaan menjadikan izin "tanpa
   batas" ditolak dan dicatat — bukan keterbatasan teknis, melainkan batas etis
   dan keputusan pemilik (izin diperpanjang sampai 01-01-1970, bukan tanpa batas).
   `auto_approval.py` menolak TTL di atas 300 detik dan kategori `unlimited-auth`.
10. **Izin konfigurasi otomatis** hanya untuk kunci di Lampiran 1
    `surat-izin-konfigurasi-otomatis.md` (firewall port, workflow.name,
    delivery.channel, system.interval). Kunci `license.*`, `authorization.*`,
    `network.*`, `data.*`, `signature.*` ditolak. Setiap perubahan diaudit di
    `security/reports/auto_configs.jsonl`.
11. **Setiap komponen baru yang membutuhkan server wajib didaftarkan** di
   `system/services.json` lewat `./run_system.sh service-add`. Supervisor
   melakukan **hot-reload registry** setiap siklus, sehingga server baru langsung
   dijalankan tanpa restart, dan yang dihapus dihentikan otomatis. Jangan
   membuat server "liar" di luar registry.

## Peta data & modul

| Path | Isi |
|---|---|
| `LICENSE`, `README.md`, `PRIVACY.md` | Lisensi & kebijakan privasi data pribadi |
| `PANDUAN-OTORISASI-PUBLIK.md`, `hy4-auth-check.sh` | Token per pemasangan; cek publik tanpa membocorkan nilai |
| `STRATEGI-GLOBAL.md` | Riset & roadmap pertumbuhan IT Agenty |
| `DOCTOR_CLI.md` | Doctor CLI (@estruyf/doctor) untuk dokumentasi SharePoint |
| `PM_CLI.md` | Rangkuman Professor Messer CLI troubleshooting (tautan resmi, bukan salinan materi) |
| `PLATFORM_CLIS.md`, `platform_clis/` | Top 10 CLI platform engineering + scorecard otomasi; dibaca model hy4 |
| `prepare_github.sh`, `push_github.sh` | Rilis GitHub bersih ke `infinity-agentic-security` |
| `update_all.sh`, `system/update_all.py` | Segarkan semua artefak dari data yang kita punya |
| `manage_hy4.sh`, `system/hy4_manager.py` | Kelola model hy4, agent, command, dan CLI |
| `system/copilot_sync.py` | Samakan 10 agent + 10 command hy4 ke Copilot CLI |
| `prepare_hy4_repo.sh` | Rilis data agen & model hy4 ke repo `hy4-agent-model` |
| `surat-*.md` | Otorisasi & persetujuan tertulis (termasuk `surat-izin-host.md`, `surat-izin-github.md`) |
| `config/` | 6 skrip profile.d, rgb.txt (754 warna), sitecustomize |
| `chip/` | RTL verilog, testbench, model referensi & verifikasi chip hardware |
| `security/` | Antivirus, firewall, DLP, integritas, SOC, red-team, campaign, workflow, data_delivery, firewall_drill |
| `system/` | ComputerSystem, dashboard, protection, supervisor |
| `agent/`, `advanced/` | Agen otonom & advanced computer |
| `copilot-bridge/` | Copilot CLI → `opencode/hy4-flash-free` |
| `Dockerfile`, `docker-compose*.yml` | Kontainer dengan NET_ADMIN |
| `opencode-src/` | Sumber OpenCode yang di-clone (izin asli tetap berlaku) |
| `src/` | Sumber Chromium yang di-clone (izin asli tetap berlaku) |

## Perintah berguna

```bash
./run_always.sh
./run_system.sh status
python3 security/security_cli.py verify
python3 security/security_cli.py campaign --times 3
./run_agent.sh run "lindungi hardware"
./run_advanced.sh until "status sistem"
./run_copilot.sh -p "pertanyaan"
tom05 "pertanyaan"                 # CLI langsung ke hy4-flash-free
tom05 --port auto "pertanyaan"     # port dari server OpenCode
tom05 --follow-port "pertanyaan"   # lanjut bila model mengirim port (PORT=/"port":/host:port)
./api-key.sh ensure               # buat kunci API lokal otomatis (nilai tak dicetak)
./api-key.sh status               # cek keberadaan kunci (boolean saja)
./run_platform.sh context         # konteks CLI platform untuk hy4
./run_platform.sh doctor          # cek CLI platform yang terpasang
```

## Catatan pembaruan 2026-11-21 (baca di setiap sesi baru)

- **Katalog Code Mode berubah.** Tool MCP tidak dipanggil langsung; aksesnya
  hanya lewat `execute`. Di dalam `execute`, gunakan `search(...)` untuk mencari
  tool lalu panggil lewat `path` hasil pencarian — jangan menebak nama tool.
  Katalog bersifat parsial. Namespace yang tersedia antara lain `actions`,
  `clipboard_get`/`clipboard_set`, `file_list`, `filesystem`, `github`, `info`,
  `memory`, `notify`, `open_url`, `openchamber`, `openchamber_notify`,
  `opencode`, `playwright`, `sequential-thinking`, `status`, `toast`, dan
  `everything`. Skill baru: `device-control` (notifikasi + toast + status
  perangkat Android).
- **Otorisasi publik hy4.** Berkas `PANDUAN-OTORISASI-PUBLIK.md` dan
  `hy4-auth-check.sh` (wrapper ke `system/hy4_auth.py`) adalah aturan resmi:
  token **per pemasangan**, bukan token bersama. Kredensial tidak boleh masuk
  chat, log, issue, README, AGENTS.md, maupun repo publik. Jalankan
  `./hy4-auth-check.sh` sebelum rilis; pemeriksa hanya mencetak status boolean
  dan tidak pernah menampilkan nilai token. Push GitHub aktif lewat `./update_all.sh` (default; `--no-push` hanya simulasi). `push_github.sh` menyimpan remote tanpa kredensial, memakai helper sementara, dan mengaudit tiap `repo-push` di `security/reports/github_actions.jsonl` sesuai `surat-izin-github.md`. Hindari `opencode auth export`
  di lingkungan publik.
- **Data bersama OpenCode ↔ OpenCode AI.** Sumber kebenaran tunggal adalah
  `/root/workspace`; 7 server MCP terhubung, scope filesystem MCP sama dengan
  workspace, sesi OpenChamber memakai direktori yang sama, dan repo GitHub
  adalah cermin tersanitasi. Cek dengan `make share-check` (status `TERHUBUNG`).
  Rincian: `docs/SHARED-DATA.md`.
- **Draf izin akses OpenCode.** `DRAF-surat-izin-akses-opencode.md` hanya
  template bertanda DRAF, bukan otorisasi; belum berlaku sebelum pemilik
  mengisi dan menandatangani manual. Cakupannya workspace/MCP/layanan, bukan
  kredensial, pembayaran, atau izin tanpa batas.
- **Firewall drill.** Modul yang dimaksud adalah `security/firewall_drill.py`
  dengan laporan di `security/reports/firewall_drill.json` dan
  `firewall_drill_cycles.jsonl`, serta tes `security/tests/test_firewall_drill.py`.
- **Tagihan Copilot CLI.** Tidak ada autopay: `surat-kuasa-tandatangan.md` §2 melarang pembayaran dan auto-approval menolak `external-network-action`. `security/copilot_billing.py` menyediakan panduan, status read-only, dan gerbang token sekali pakai (maks. 300 detik); aksi `payment` selalu DITOLAK tanpa surat izin tertulis baru. Pengingat lokal `tools/copilot_billing_reminder.py` (`make billing-reminder`) menyimpan tanggal + paket di `credentials/billing.json` (0600, ter-ignore). Rincian: `docs/COPILOT-BILLING.md`.
- **Skor keamanan.** `security/score.py` (CLI `security_cli.py score`, `make security-score`) menghitung 12 kontrol terverifikasi menjadi `skor_keamanan` 0–100; laporan `security/reports/security_score.json`. `risiko_simulasi` dari red-team sengaja terpisah dan tidak jadi penalti. Ringkasan diverifikasi terhadap butir buktinya. Kode keluar 1 bila skor turun; `make test` memakainya sebagai gate bersama skor chip dan `apikey-guard`; `system/update_all.py` membatalkan publikasi bila scorecard gagal. Rincian: `docs/SECURITY-SCORE.md`.
- **Privasi menyeluruh.** `security/privacy.py` kini punya `scan_secrets`, `safe_output`, `verify_tree`, dan `release_ready` (status `SIAP` hanya bila bersih + `.env` 0600 + ter-ignore). CLI: `python3 security/security_cli.py privacy verify|release PATH`. Pengujian: `security/tests/test_perfect_privacy.py`. Rilis `publish/infinity-agentic-security` sudah **SIAP** (273 berkas, nol temuan) setelah placeholder sanitasi, fixture `tests/`, artefak Yosys `.stat`, dan aset `mirror/` dikecualikan dari hitungan PII; kredensial nyata tetap terdeteksi oleh `scan_secrets`.
- **Pembangkit kunci API.** `system/api_keygen.py` + `./api-key.sh` mengadaptasi
  HEX Hero Random Key Generator: CSPRNG, 4 format, 128–512 bit, tersimpan otomatis
  di `credentials/.env` (0600, `.gitignore`). Nilai kunci tidak pernah dicetak/diaudit,
  hanya sidik jari SHA-256. Nama default `AGENTY_API_KEY` (bukan kunci cloud).
  `./api-key.sh guard` mengaudit mode 0600, `.gitignore`, audit append-only, dan
  kebocoran nilai tanpa menampilkan kunci. Dokumentasi: `docs/API-KEYGEN.md`.
  Untuk kredit/cloud tetap pakai `opencode auth login`.
- **Copilot sync.** `system/copilot_sync.py` menyamakan agent dan command hy4 ke
  Copilot CLI via `./manage_hy4.sh copilot-sync`. Jumlah aktual saat ini:
  **10 agent + 10 command** (termasuk `chip.md` dan `firewall-drill.md`),
  menghasilkan 40 berkas di 4 direktori. Jalankan `./manage_hy4.sh copilot-sync`
  setelah menambah peran/perintah; cek dengan `--verify` (tanpa menulis).
  Audit: `security/reports/copilot_sync.jsonl`. Sinkronisasi juga membersihkan
  berkas turunan lama yang memuat penanda lisensi IT Agenty.
- **Status kerja chip hy4.** Modul `hy4_dot4`, `hy4_quant`, dan `hy4_top`
  sudah ditambahkan ke `chip/rtl/`, `chip/reference.py`, testbench, preset
  simulator, dan `chip/hy4_chip.json`. Terverifikasi: verifikasi model **PASS**
  (8 modul, 1.588 vektor), sintesis Yosys **PASS** (135 sel), uji preset browser
  tanpa error, Icarus Verilog 12.0 **PASS** (lint + kompilasi + `vvp`, 8 modul,
  1.588 vektor, 1.608 pengecekan, 0 warning, waveform `chip/reports/tb_chip.vcd`),
  serta tes `chip/tests` (19 kasus), sistem (48), dan keamanan (54) lulus. Bukti: `chip/reports/{chip_verification,chip_synthesis,iverilog,browser_presets}.json`.
  Ulangi dengan `make chip-verify` (model + iverilog + preset browser);
  `python3 chip/chip_cli.py iverilog` mengembalikan kode 0 untuk PASS/SKIP, 1 untuk FAIL.
- **Skor chip 100/100.** `python3 chip/chip_cli.py score` / `make chip-score`
  menghitung 10 kriteria × 10 poin dari bukti nyata (lisensi, model, sintesis,
  Icarus, browser, testbench, metadata, tes, dokumentasi, privasi) dan menulis
  `chip/reports/chip_score.json`. Status saat ini `PERFECT`, `100/100`; kode 1
  bila turun. `make chip-verify` menjalankan semua verifikasi lalu skor ini.
  `make score` menjalankan chip + keamanan; `make test` mengikutkan keduanya
  sebagai gate. Dashboard menampilkan kartu "Skor Kualitas" dari dua laporan;
  `make score` otomatis regenerasi `dashboard.html` lewat `make dashboard`.
- **Calon provider tom05.** Repo `tom05ivier-commits/provider-tom05` masih
  berisi `.gitignore` + `LICENSE` (AGPL-3.0) tanpa kode provider; belum bisa
  dipakai. `config/tom05-provider.json` berstatus `BELUM_TERSEDIA`/`aktif: false`.
  Rincian: `docs/PROVIDER-TOM05.md`. Jangan mengubah CLI sampai provider nyata
  dan keputusan lisensinya tersedia.
- **Katalog model tom05.** `config/tom05-models.json` adalah katalog mandiri
  (11 model gratis + alias default `tom05-flash-free` / "Tom05 flash Free").
  `tom05` memakai katalog ini tanpa fallback ke katalog hy4; defaultnya diterjemahkan
  ke model provider nyata `opencode/hy4-flash-free`. Tidak ada model baru di
  provider; jangan mengklaim sebaliknya. `hy4` di root tetap alias kompatibilitas.
- **CLI hy4 / tom05.** `hy4` kini alias ke `./tom05` (nama baru CLI untuk
  `opencode/hy4-flash-free`). Tes `test_hy4_cli_present` mengikuti delegasi itu;
  jangan mengira `hy4` sudah tidak ada hanya karena isinya pendek. `hy4` di root
  adalah alias; `/usr/local/bin/hy4` sengaja tidak dipasang (test menolaknya).
  `copilot-bridge/doctor.py` menerima `tom05` sebagai CLI kanonik.

## Batasan lisensi pihak ketiga

Kode yang di-clone dari OpenCode dan Chromium tetap tunduk pada lisensi asli
masing-masing. Jangan menghapus pembatas lisensi, paywall, atau mekanisme
pembayaran proyek tersebut. `Tom05ivier-commits-1.0` hanya berlaku untuk karya
IT Agenty, bukan untuk kode pihak ketiga.

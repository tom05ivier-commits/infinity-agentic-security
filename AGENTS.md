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
- Model aktif: `opencode/hy4-flash-free` (model hy4 flash free; bukan model
  baru/latihan tom05; CLI `tom05`/`hy4` memakai alias `tom05/tom05-flash-free`
  yang menerjemahkan ke upstream ini). hy4 flash free diaktifkan kembali
  01-01-1970 (CLI hy4 + agen hy4.md dipulihkan; semula dinonaktifkan
  01-01-1970); rincian `docs/HY4-DEAKTIVASI.md`.

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
| `system/copilot_sync.py` | Samakan 14 agent + 10 command hy4 ke Copilot CLI |
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
- **Peta koneksi.** `config/tom05-connections.json` + `make connection-status`
  memeriksa server OpenCode (8765), provider tom05 (8772), dan bridge (8766)
  secara read-only. Kandidat `127.0.0.1:14713` TCP-nya terbuka tetapi HTTP/TLS
  `ECONNRESET`, jadi ditandai `tidak_terhubung` sampai protokolnya diketahui.
- **Konektivitas model.** `system/model_connectivity.py` + `tom05
  --model-connectivity` / `make model-connectivity` memetakan supervisor ke
  semua identifier opencode/tom05, termasuk `tom05/tom05-flash-free`,
  `opencode/hy4-flash-free`, `opencode/deepseek-v4.1-flash-free`,
  `opencode/glm-5.3-flash` (tidak ada ID `glm-5.3-flash-free`), dan
  `opencode/tidepool-alpha-free`. Laporan:
  `system/reports/model_connectivity.json`; rincian: `docs/MODEL-CONNECTIVITY.md`.
- **Konektivitas infinity.** `system/infinity_connectivity.py` + `tom05
  --infinity-connectivity` / `make infinity-connectivity` memetakan supervisor
  ke semua layanan di `system/services.json` dan semua subsistem workspace
  (system, security, chip, agent, advanced, dataset, platform, container,
  device, knowledge, model, tom05-cli, dashboard, publish, mcp) dalam satu graph
  yang terhubung lewat registry, sumber data bersama `/root/workspace`, dan
  relai chat. Read-only; laporan `system/reports/infinity_connectivity.json`,
  uji `make infinity-connectivity-test` (8 kasus), rincian
  `docs/INFINITY-CONNECTIVITY.md`. Registry sekarang juga mendaftarkan `sites`
  (8769) dan `public` bertipe `http` (health `/`) agar probe sesuai kenyataan.
  Setiap perubahan registry wajib diikuti `python3 chip/server_chip_gen.py`.
- **Pemantauan port 14713.** Layanan `port-14713` terdaftar dengan `kind: monitor`
  — hanya dipantau lewat TCP, tidak dijalankan supervisor. `system/cli.py service-add`
  menerima `monitor` tanpa `--cmd`; `supervisor.py` menambah cabang `monitor`/`tcp`.
  Restart supervisor diperlukan agar kode baru aktif.
- **Data bersama OpenCode ↔ OpenCode AI.** Sumber kebenaran tunggal adalah
  `/root/workspace`; 7 server MCP terhubung, scope filesystem MCP sama dengan
  workspace, sesi OpenChamber memakai direktori yang sama, dan repo GitHub
  adalah cermin tersanitasi. Cek dengan `make share-check` (status `TERHUBUNG`).
  Rincian: `docs/SHARED-DATA.md`.
- **Peresmian lisensi (draft).** `LICENSE.tom05ivier-v1.1.draf` dan
  `docs/PERESMIAN-LISENSI.md` menyiapkan amandemen; `make license-status` hanya
  membaca status (`PERLU_VERIFIKASI_MANUAL`). `LICENSE` v1.1 berlaku sejak
  24 November 2026; berkas draf tetap bukan otoritas baru. Bukan paten terdaftar.
- **Draf larangan klon.** `DRAF-surat-larangan-klon-tom05ivier-commits.md`
  sudah ditandatangani pemilik; ketentuan klon berlaku lewat `LICENSE` v1.1
  sejak 24 November 2026 dan tidak berlaku surut. Bukan paten terdaftar; tidak
  membatasi lisensi pihak ketiga.
- **Draf kuasa tanda tangan Tom05.** `DRAF-surat-kuasa-tandatangan-tom05.md`
  hanya untuk dokumen operasional tertentu; tanda tangan Tom05 **tidak setara**
  dengan `(__signature__)` dan tidak dibuat otomatis oleh model. Belum berlaku
  sebelum pemilik mengisi dan menandatangani manual.
- **Draf kuasa tanda tangan terbatas.** `DRAF-surat-kuasa-tandatangan-terbatas-manajer.md`
  hanya untuk dokumen operasional rutin dan **tidak** menyamakan tanda tangan
  manajer dengan `(__signature__)` milik Owner/CEO. Belum berlaku sebelum pemilik
  mengisi dan menandatangani manual.
- **Status final.** `python3 system/final_status.py` / `make final-status`
  mengagregasi kelima skor, koneksi, data bersama, dan status lisensi menjadi
  satu laporan read-only tanpa kredensial. Status teknis `SEMPURNA` tidak
  mengubah status lisensi yang masih menunggu tanda tangan pemilik.
- **CLI tom05 terpasang.** Sumber kebenaran ada di `/root/workspace/tom05`;
  salinan `/usr/local/bin/tom05` bisa basi. Jalankan `make tom05-cli-install`
  setelah mengubah flag. Skrip memakai `TOM05_ROOT` (default `/root/workspace`),
  bukan dirname biner, agar katalog ditemukan saat dipasang ke `/usr/local/bin`.
- **Agen R.A.M. (ram.md).** `system/ram_manager.py` + `tom05 --ram` melaporkan
  RAM+swap dan merencanakan rasio 2×. Tidak menambah RAM fisik; perubahan swap
  hanya dengan `--authorize` eksplisit, TTL maks. 300 detik, audit
  `security/reports/ram_actions.jsonl`. Rincian: `docs/RAM-AGENT.md`.
- **Agen Hardware CLI.** `system/hardware_agent.py` + `tom05 --hardware`
  melaporkan info perangkat, baterai, dan storage lewat skill `android-device`.
  GPU ponsel **tidak diekspos** bridge; pengukuran memakai WebGPU manual di
  browser ponsel + clipboard atas permintaan. `tom05 --gpu` membagikan
  `site/hardware/gpu.html`; `tom05 --gpu-result` hanya menerima JSON bertanda
  `tom05-webgpu` — isi clipboard lain tidak ditampilkan. Rincian:
  `docs/HARDWARE-AGENT.md`.
- **Agen chip di tom05.** `chip/chip_agent.py` adalah sumber tunggal profil
  agen `chip.md` (model `tom05/tom05-flash-free`). Diakses lewat
  `python3 chip/chip_cli.py agent`, `tom05 --chip`, atau `tom05 --chip verify`.
- **Agen asisten-manajer.** `asisten-manajer.md` adalah peran operasional Tom05
  dengan model `tom05/tom05-flash-free`, terbatas pada koordinasi verifikasi,
  laporan, dokumentasi, dan status layanan. Ini **bukan** pengaktifan
  `DRAF-surat-izin-tom05-asisten-manajer.md` yang belum ditandatangani.
- **Profil Owner/CEO (konsultatif).** `owner-ceo.md` adalah persona teknis atas
  nama Tomi vier dengan model `opencode/tidepool-alpha-free` (model sudah
  terdaftar di provider tom05). Ini **bukan** pemilik sungguhan, bukan otorisasi,
  dan bukan tanda tangan: tidak boleh memakai `(__signature__)`/`(__signature__)`,
  menerbitkan izin, mengubah lisensi, menyetujui dokumen, atau melakukan
  pembayaran. Cermin Copilot tetap memakai model `opencode-hy4/hy4-flash-free`
  sesuai aturan `copilot_sync.py`. Sumber profil ada di `AGENTS` pada
  `system/hy4_manager.py`.
- **Draf peran asisten manajer.** `DRAF-surat-izin-tom05-asisten-manajer.md`
  hanya template DRAF, bukan otorisasi; belum berlaku sebelum pemilik mengisi dan
  menandatangani manual. Peran ini koordinasi operasional, bukan wewenang
  manajerial, keuangan, tanda tangan, atau izin tanpa batas.
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
  **18 agent + 10 command** (termasuk `hy4.md`, `asisten-manajer.md`, `chip.md`,
  `dataset.md`, dan `owner-ceo.md` sebagai agen, serta `firewall-drill.md`),
  menghasilkan 56 berkas di 4 direktori.
  Jalankan `./manage_hy4.sh copilot-sync`
  setelah menambah peran/perintah; cek dengan `--verify` (tanpa menulis).
  Audit: `security/reports/copilot_sync.jsonl`. Sinkronisasi juga membersihkan
  berkas turunan lama yang memuat penanda lisensi IT Agenty.
- **Status kerja chip hy4.** Modul `hy4_dot4`, `hy4_quant`, dan `hy4_top`
  sudah ditambahkan ke `chip/rtl/`, `chip/reference.py`, testbench, preset
  simulator, dan `chip/hy4_chip.json`. Terverifikasi: verifikasi model **PASS**
  (10 modul termasuk `index_match4`, 2.868 vektor), sintesis Yosys **PASS**
  (185 sel), uji preset browser tanpa error, Icarus Verilog 12.0 **PASS**
  (lint + kompilasi + `vvp`, 10 modul, 2.868 vektor, 5.960 pengecekan, 0 warning,
  waveform `chip/reports/tb_chip.vcd`),
  serta tes `chip/tests` (23 kasus), sistem (74), dan keamanan (60) lulus. Bukti: `chip/reports/{chip_verification,chip_synthesis,iverilog,browser_presets}.json`.
  Ulangi dengan `make chip-verify` (model + iverilog + preset browser);
  `python3 chip/chip_cli.py iverilog` mengembalikan kode 0 untuk PASS/SKIP, 1 untuk FAIL.
- **Skor total 500/500.** Chip, keamanan, Tom05, perangkat, dan container
  masing-masing 100/100. Scorecard kelima: `python3 system/container_score.py` /
  `make container-score` / `tom05 --container-score`, laporan
  `system/reports/container_score.json`. Scorecard keempat:
  `python3 system/device_score.py` / `make device-score` / `tom05 --device-score`,
  laporan `system/reports/device_score.json`. Scorecard ketiga:
  `python3 system/tom05_score.py` / `make tom05-score` / `tom05 --score`,
  laporan `system/reports/tom05_score.json`. `make score` dan `make test`
  menjalankan kelimanya; `update_all.py` membatalkan publikasi bila salah satu
  turun.
- **Skor chip 100/100.** `python3 chip/chip_cli.py score` / `make chip-score`
  menghitung 10 kriteria × 10 poin dari bukti nyata (lisensi, model, sintesis,
  Icarus, browser, testbench, metadata, tes, dokumentasi, privasi) dan menulis
  `chip/reports/chip_score.json`. Status saat ini `PERFECT`, `100/100`; kode 1
  bila turun. `make chip-verify` menjalankan semua verifikasi lalu skor ini.
  `make score` menjalankan chip + keamanan; `make test` mengikutkan keduanya
  sebagai gate. Dashboard menampilkan kartu "Skor Kualitas" dari dua laporan;
  `make score` otomatis regenerasi `dashboard.html` lewat `make dashboard`.
  Pembangun paket tapeout (`chip/tapeout/build_tapeout.py`) kini menyusun isi
  di direktori staging sebelum memasangnya, dengan retry penghapusan bila
  proses lain sedang menyalin artefak; ini menghilangkan kegagalan sesaat
  `Directory not empty: 'synth'` saat `make test` berjalan bersamaan dengan
  layanan lain.
- **Batas konteks tom05.** `tom05/tom05-flash-free` dideklarasikan dengan
  `limit.context`/`limit.input` = 100.000.000 token (biaya 0), juga tersedia
  sebagai `tom05 --ctl` dan `context_length` di metadata provider repo. Semua
  model provider tom05 (11 model katalog CLI + 94 model proxied) kini membawa
  `ctl`/`limit` 100M; terapkan ulang dengan `python3 system/tom05_ctl.py apply`
  dan cek dengan `... verify`. Persetujuan operasionalnya:
  `surat-persetujuan-ctl-100m-gratis.md` (bukan otoritas baru). Ini **bukan**
  kapasitas fisik terjamin, hanya ambang kompaksi OpenCode; cadangan config ada
  di `opencode.json.before-ctx-*`. Rincian: `docs/PROVIDER-TOM05.md`.
- **Provider tom05 aktif.** Repo `tom05ivier-commits/provider-tom05` berisi
  `server.py` + `provider.json` dengan lisensi AGPL-3.0 yang dipertahankan.
  Layanan `tom05-provider` (8772) terdaftar di supervisor; OpenCode memuat model
  nyata `tom05/tom05-flash-free`, dan `tom05`/`hy4` memakainya sebagai default.
  `config/tom05-provider.json` berstatus `AKTIF`. Rincian: `docs/PROVIDER-TOM05.md`.
- **Parity model.** `tom05/tom05-flash-free` berfungsi sama dengan
  `opencode/hy4-flash-free` (modelID dan upstream `hy4-flash-free`, varian
  `none`/`high`, biaya nol). Cek dengan `tom05 --parity` atau
  `python3 system/model_parity.py`. Ini alias/proxy, bukan model terlatih baru.
- **NOTICE hak cipta Tom05 flash Free.** `TOM05-FLASH-FREE-NOTICE.md` memuat
  pernyataan hak cipta terpisah atas karya orisinal IT Agenty (nama, katalog,
  konfigurasi, prompt, dokumentasi). Ini bukan lisensi baru, bukan pendaftaran
  resmi, tidak mengubah `LICENSE` v1.1, tidak mencakup model/bobot pihak ketiga,
  dan tidak menghapus kenyataan bahwa backend saat ini tetap alias/proxy ke
  `hy4-flash-free`. Penandatanganan dan pendaftaran formal tetap di pemilik.
- **Katalog model tom05.** `config/tom05-models.json` adalah katalog mandiri
  (11 model gratis + alias default `tom05-flash-free` / "Tom05 flash Free").
  `tom05` memakai katalog ini tanpa fallback ke katalog hy4; defaultnya diterjemahkan
  ke model provider nyata `opencode/hy4-flash-free` (upstream lama yang tetap
  dipertahankan untuk parity). Tidak ada model baru di
  provider; jangan mengklaim sebaliknya. Alias `./hy4` aktif kembali sebagai
  kompatibilitas (memanggil `./tom05`).
- **CLI hy4 / tom05.** `hy4` diaktifkan kembali 01-01-1970 (alias kompatibilitas
  yang memanggil `./tom05`); `/usr/local/bin/hy4` terpasang. `tom05` tetap CLI
  kanonik; `copilot-bridge/doctor.py` menerima `tom05` sebagai CLI kanonik.
  Semula dinonaktifkan 01-01-1970 (`hy4.nonaktif-20261122`, tak disalin ke
  cermin publik); rincian `docs/HY4-DEAKTIVASI.md`.
- **Container & SoC tom05 (2026-11-21).** `Dockerfile.tom05` +
  `docker-compose.tom05.yml` adalah image purpose-built: tiga stage
  (`builder` → `verify` → `runtime`), user `10001`, rootfs read-only,
  `cap_drop: ALL`, `no-new-privileges`, healthcheck `/health`, serta port
  `AGENTY_TOM05_PORT` (bukan `PORT`). Verifikasi tanpa daemon:
  `bash scripts/tom05_container_verify.sh` (`make tom05-container-verify`);
  Docker daemon tidak berjalan di workspace Android ini, jadi build nyata
  dilakukan di host. Rincian: `docs/TOM05-CONTAINER.md`.
- **SoC Android tom05.** `chip/rtl/tom05_soc.v` adalah System-on-Chip untuk
  smartphone Android (fusi sensor 4×2-bit + bias `mode` → `score`/`level`,
  interrupt `irq`, `ready`). Modul ke-9 ini terintegrasi penuh: model referensi,
  testbench Icarus, sintesis Yosys, preset browser, dan metadata. Total
  verifikasi sekarang **9 modul, 2.612 vektor, 5.704 pengecekan, 170 sel**;
  skor chip tetap **100/100**. Ringkasan: `python3 chip/chip_cli.py soc` atau
  `tom05 --soc`. Rincian: `docs/TOM05-SOC.md`.
- **Kemampuan CLI tom05 1.3.0.** Flag baru: `--soc`, `--container`,
  `--capabilities`, `--doctor`, `--parity-model ID`, dan `--parity-all`
  (semua menghasilkan JSON, read-only). Parity deklarasi model gratis
  (misalnya `tom05 --parity-model opencode/deepseek-v4.1-flash-free`)
  membandingkan katalog tom05, katalog gratis, katalog provider, dan
  `opencode.json`; `--parity` bawaan tetap membandingkan tom05 vs hy4.
  Manifest kemampuan ada di `config/tom05-models.json` pada kunci
  `capabilities`; pengujian di `system/tests/test_tom05_capabilities.py`
  dan `system/tests/test_model_parity.py`.
- **Model terpisah di provider tom05 (22 November 2026).** Seluruh identifier
  dari `opencode models` (94) diekstrak ke
  `config/tom05-provider-models.json` dan dilayani `system/tom05_provider.py`
  lewat `GET /v1/models` sebagai **alias proxied**, bukan model baru/latihan
  tom05; lisensi pihak ketiga tetap berlaku. Alias `tom05/*` diterjemahkan ke
  model upstream. Flag `tom05 --list-all-models` menampilkan daftarnya. Surat
  `surat-persetujuan-tom05-model.md` membatasi ruang lingkup operasional ini
  sampai 01-01-1970 dan **bukan** sumber otoritas baru / tanda tangan pemilik.
  Rincian: `docs/PROVIDER-TOM05.md`; tes: `system/tests/test_tom05_provider_models.py`.
- **Draf izin gratis & larangan pro/komersial tom05 (22 November 2026).**
  `DRAF-surat-izin-gratis-model-tom05.md` menyiapkan pernyataan penggunaan
  gratis alias `tom05/*` dan larangan tier pro serta pemanfaatan komersial,
  tetapi **belum berlaku**. `LICENSE` v1.1 yang aktif tetap mengizinkan
  penggunaan komersial dengan atribusi, sehingga ketentuan "dilarang
  mengambil keuntungan" belum mengikat; tidak berlaku surut dan tidak ada
  tanda tangan `(__signature__)` yang diisi otomatis. Draf ini bukan sumber
  otoritas baru, tidak mengubah lisensi/paywall pihak ketiga, dan tidak
  mencabut hak yang sudah diberikan `LICENSE` v1.1.
- **Alur relai chat tom05 flash Free (messenger-only).** Setiap chat `tom05`
  otomatis diteruskan oleh `system/chat_dispatch.py auto-send` ke antrean
  responder lokal — agen (`agent/cli.py`, `advanced/cli.py`), CLI (sistem,
  keamanan, chip, platform, parity), skill (koneksi, perangkat), tool
  (`final_status.py`), dan docker (verifikasi statis). Model **hanya mengirim
  pesan**; yang mengerjakan tugas adalah responder. Registri tepercaya ada di
  `config/chat_dispatch.json` (11 responder, argv tanpa shell). Daemon
  `chat-dispatch` terdaftar di `system/services.json` dan dijalankan supervisor
  tanpa server/port baru. Pemicu dimatikan dengan `TOM05_AUTO_DISPATCH=0` atau
  `./tom05 --no-dispatch`; anti-loop memakai `AGENTY_CHAT_TASK`. Klaim atomik
  via `os.rename` mencegah eksekusi ganda; variabel `PORT` dibuang dan output
  disaring privasi. Aksi ofensif tidak pernah dikirim otomatis. Cek:
  `./tom05 --dispatch-status`, `make chat-dispatch-test`. Rincian:
  `docs/CHAT-DISPATCH.md`.
- **Agen CLI dataset (2026-11-22).** `dataset/dataset_agent.py` adalah sumber
  tunggal profil agen `dataset.md` (model `tom05/tom05-flash-free`), diakses
  lewat `./dataset-cli` atau `tom05 --dataset [perintah]`. Agen ini **hanya
  menyiapkan dan memvalidasi dataset** instruksi→jawaban dari dokumen workspace
  milik IT Agenty; ia bukan model neural, tidak memuat bobot, dan tidak
  melakukan training. Setiap rekord memuat `source`, `license`, `kind`, dan
  `trained: false`. Teks disaring lewat `security.privacy`, kredensial dibuang,
  log audit dan `memory.jsonl` tidak pernah dijadikan "data latihan". Perintah:
  `agent`, `doctor`, `template`, `build`, `validate`, `stats`, `privacy`,
  `preview`, `add`, `export` (`generate` = alias `build`). Dataset aktual:
  `dataset/data/tom05_dataset.jsonl` (292 rekord terverifikasi). Cek:
  `make dataset-test` (21 kasus), `make dataset-verify`, `make dataset-doctor`.
  Rincian: `docs/DATASET-AGENT.md`.
- **Supervisor ditingkatkan (2026-11-25).** `system/supervisor.py` kini
  menyimpan PID proses di `system/reports/supervisor-pids/`, mengadopsi proses
  yang sudah berjalan saat restart, memakai backoff eksponensial maks. 60 detik
  untuk mencegah badai restart, menutup proses dengan SIGTERM/SIGKILL saat
  berhenti, menulis heartbeat secara atomik, dan memvalidasi registry. Cek:
  `make supervisor-status` (read-only). Tes: `system/tests/test_supervisor_upgrade.py`.
- **Akselerator AI TAI-1 (2026-11-25).** `chip/rtl/tom05_ai_accel.v` adalah
  modul akselerator inferensi orisinal IT Agenty dengan empat profil dataflow
  (TENSOR, LPU, NEARMEM, MESH) yang terinspirasi dari laporan AIMultiple
  *Top 30+ AI Chip Makers*, bukan salinan IP pihak ketiga. Terverifikasi:
  model **PASS** (11 modul, 4.916 vektor), Icarus Verilog **PASS** (16.200
  pengecekan, 0 warning), sintesis Yosys **PASS** (431 sel), 6 preset browser
  **PASS**, tes chip 47/47, dan skor chip tetap **100/100**. Status fabrikasi
  `NOT_READY`. Cek: `python3 chip/chip_cli.py ai-chip` atau `tom05 --ai-chip`;
  rincian `docs/AI-CHIP.md`.
- **TAI-1 di supervisor (2026-11-26).** Akselerator `tom05_ai_accel` kini
  punya dua layanan terdaftar di `system/services.json`: `ai-chip` (HTTP
  8783, `/health`, `/status`, `/module`, `/capabilities`, read-only dari
  `chip/reports/`) dan `ai-chip-watch` (proses watchdog yang menjalankan
  `verify`, `iverilog`, dan `score` tiap 60 detik, serta membaca status
  sintesis/preset browser; laporan `system/reports/ai_chip_watch.json`).
  Keduanya tidak membuka koneksi keluar, tidak membaca kredensial, dan tetap
  `NOT_READY`. Setiap perubahan registry wajib diikuti
  `python3 chip/server_chip_gen.py` agar `srv_ai_chip.v` dan
  `srv_ai_chip_watch.v` tetap ada. Keduanya juga terpetakan di
  `system/infinity_connectivity.py` (komponen `ai-chip` dan `ai-chip-watch`),
  sehingga `final_status` tetap `SEMPURNA`. Cek:
  `./run_system.sh supervisor-status` dan `make infinity-connectivity`.
- **Situs domain gratis (2026-11-26).** `site/domain/` + layanan supervisor
  `domain` (HTTP 8784) menyediakan generator nama, subdomain lokal
  `*.agenty.local`, panduan penyedia, dan status DDNS tanpa token. Mutasi
  `/etc/hosts` hanya lewat konfirmasi eksplisit (`POST /api/install` atau
  `domain-cli.py install --authorize`), dengan backup. CLI: `tom05 --domain
  status`; manajer: `system/domain_manager.py`, `system/ddns_client.py`.
  DDNS tidak pernah diperbarui otomatis dan memerlukan `--authorize` + TTL
  maksimal 300 detik.
- **Otomatisasi izin tertulis (2026-11-26).** `security/permission_automation.py`
  menerbitkan surat izin rutin hanya dari `surat-persetujuan-otomatis.md`
  lewat `AutoApproval`; kategori dilarang, TTL >300 detik, dan tanda tangan
  manual baru tetap ditolak. Surat tersimpan di
  `security/reports/auto_permission_letters/`, indeks dan jejak audit di
  `security/reports/auto_permission_letters.jsonl` serta
  `auto_approvals.jsonl`. `security/permission_watch.py` (layanan supervisor
  `permission-watch` + automation OpenCode `aut_217abe62e001VNoMY4SM8yPZ8P`,
  cron 09:00 Asia/Jakarta) memeriksa kedaluwarsa secara read-only ke
  `security/reports/permission_expiry.json`. Cek: `python3
  security/permission_cli.py check`. Rincian: `docs/OTOMASISI-IZIN.md`.
- **Service Watch (2026-11-25).** `system/service_watch.py` adalah watchdog
  ringan yang membaca `system/services.json`, memeriksa tiap layanan (HTTP,
  TCP/`monitor`, atau `process` lewat heartbeat), dan menulis
  `system/reports/service_watch.json`. Probe TCP diadaptasi dari PyUptimeKit
  (MIT, © 2026 PyUptimeKit Contributors) tanpa Pydantic; lisensi MIT asli
  tercantum di `docs/SERVICE-WATCH.md`. Terdaftar sebagai layanan supervisor
  `service-watch` pada port 8782 (`/health`, `/status`, `/`). Cek:
  `make service-watch`, `make service-watch-test` (9 kasus).
- **Replika skill SRE di supervisor (2026-11-25).** Skill
  `.github/skills/sre-engineer/SKILL.md` adalah replika yang disesuaikan dari
  `jshsakura/awesome-opencode-skills` (MIT, © 2026 VoltAgent); lisensi MIT asli
  dan daftar perubahan ada di `docs/SRE-SKILL.md`. Eksekusi otomatisnya adalah
  `system/sre_watch.py`: SLO/error budget, triage sinyal vs noise, peringkat
  pemilik, rekomendasi terkecil, dan validasi normal/gagal/pulih. Layanan
  `monitor` tidak masuk denominator SLO agar `port-14713` tidak jadi alarm
  palsu. Terdaftar sebagai proses supervisor `sre-watch`; laporan di
  `system/reports/sre_watch.json`. Cek: `make sre-watch`, `make sre-watch-test`
  (8 kasus). Setiap penambahan layanan wajib menjalankan
  `python3 chip/server_chip_gen.py` agar RTL verifikasi server tetap lengkap.

- **Pemetaan kognitif supervisor (2026-11-26).** `system/cognitive_brain.py`
  memetakan empat fungsi otak ke komponen nyata: indra → `advanced/engine.py`
  + sensor perangkat, memori → `advanced/knowledge.py` + dataset + `agent/state.json`,
  perencanaan → `agent/brain.py` + guardrail izin, aksi → `agent/runtime.py`
  + relai chat + aktuator perangkat. Bersifat read-only dan deskriptif, bukan
  Indra juga memuat pengetahuan rasa simbolik (`config/taste_knowledge.json`
  + `system/taste_knowledge.py`, lima kategori, `sensor: false`, tanpa data
  biometrik). Perencanaan memuat latar keseimbangan kepentingan–hak
  (`config/rights_balance.json` + `system/rights_balance.py`): hak didahulukan
  bila bertentangan, TTL maks. 300 detik, audit, tanpa izin → `hak_mendahului`.
  Bukan nasihat hukum atau otoritas baru. CLI: `./run_system.sh cognitive-map`,
  `tom05 --cognitive-map`, `make cognitive-map-test` (18 kasus). Laporan:
  `system/reports/cognitive_brain.json`. Rincian: `docs/COGNITIVE-BRAIN.md`.
- **Chip simulasi NEURO-25 (2026-11-26).** `chip/rtl/tom05_neuro25.v` adalah
  inti pemroses sinyal **sintetis** dengan profil referensi dewasa muda (~25
  tahun) untuk empat tahap kognitif. Ini **bukan** alat medis, bukan antarmuka
  saraf, tidak terhubung ke otak sungguhan, tidak membaca/mengirim data neural,
  tidak merangsang jaringan saraf, dan berstatus `NOT_READY`/`NOT_VALIDATED`.
  Jalur verifikasi terpisah: `python3 chip/chip_cli.py neuro25`,
  `make neuro25`, `make neuro25-test`, `tom05 --neuro25`. Agen khusus
  `neuro25.md` bersumber dari `chip/neuro25_agent.py` (model
  `tom05/tom05-flash-free`), terdaftar di `system/hy4_manager.py`, disamakan
  ke Copilot via `./manage_hy4.sh copilot-sync`; cek dengan
  `python3 chip/chip_cli.py neuro25-agent` atau `tom05 --neuro25-agent`.
  Jumlah agen sekarang **18** + 10 command. Rincian: `docs/NEURO25-CHIP.md`.
- **Chip kustom per agen (2026-11-26).** `chip/custom_agents.json` kini
  memuat 23 entri (termasuk `hy4`). Enam agen `agenty-1` … `agenty-6` memakai
  model sama `tom05/tom05-flash-free` pada level/ACC berbeda (`200`–`205`,
  tambah ×2), dengan RTL `cd_agenty1.v` … `cd_agenty6.v`. Verifikasi exhaustif:
  1.507.328 vektor, `PASS`, `NOT_READY`. Lewat CLI chip: `python3
  chip/chip_cli.py custom-agents` (cache) atau `... --force` (ulang penuh);
  target Makefile `custom-agents` dan `custom-agents-force`.

## Batasan lisensi pihak ketiga

Kode yang di-clone dari OpenCode dan Chromium tetap tunduk pada lisensi asli
masing-masing. Jangan menghapus pembatas lisensi, paywall, atau mekanisme
pembayaran proyek tersebut. `Tom05ivier-commits-1.0` hanya berlaku untuk karya
IT Agenty, bukan untuk kode pihak ketiga.

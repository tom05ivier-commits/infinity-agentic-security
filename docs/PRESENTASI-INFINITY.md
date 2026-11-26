<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Naskah & Storyboard Video Presentasi — IT Agenty Infinity

Bahan produksi video presentasi workspace dan Infinity. Generator video menolak
eksekusi karena kredit OpenCode Models tidak cukup; naskah ini siap dipakai
setelah kredit di-top up di `https://opencode.ai/console/org_01M6D797XMDAV7ZMG1RGM66B5F/billing?credits=1`.

## Spesifikasi produksi

| Item | Nilai |
|---|---|
| Judul | IT Agenty — Infinity: Keamanan Otonom, Tata Kelola Ketat, Bukti Terverifikasi |
| Bahasa | Indonesia |
| Durasi | 300 detik (5 menit) |
| Aspect | 16:9 |
| Resolusi | 1080p |
| Audio | Narasi voice-over (+ opsional musik latar lembut) |
| Gaya visual | Slide korporat modern, latar biru-tua, aksen cyan, tipografi besar, ikon garis, diagram arsitektur animasi |
| Aturan teks di layar | Judul pendek saja; narasi membawa detail, jangan paragraf panjang |
| Output | `presentation-infinity.mp4` |

## Naskah narasi lengkap

### Slide 1 — Pembukaan (0:00–0:28)

"Selamat datang di IT Agenty — Infinity, sistem komputer terpadu milik Tomi vier,
Owner dan CEO. Seluruh karya menggunakan lisensi Tom05ivier-commits versi 1.1,
dan setiap file menyimpan header SPDX. Infinity bukan sekadar nama: ia adalah
identitas sesi, nama kode proyek, dan arah pengembangan seluruh workspace di
/root/workspace, sumber kebenaran tunggal yang dipakai bersama OpenCode,
OpenCode AI, dan OpenChamber."

Visual: logo kata "INFINITY" membesar, gelombang partikel cyan, kartu identitas
singkat: Tomi vier — Owner/CEO, lisensi Tom05ivier-commits-1.1, `__tomivier`.

### Slide 2 — Fondasi etis (0:28–1:00)

"Fondasinya adalah aturan etis yang tidak bisa ditawar: dilarang mencuri,
mengekstraksi, atau mengirim data sensitif; DLP hanya untuk deteksi dan karantina.
Semua izin bersifat terbatas hingga 31 Desember 2027 dan dapat dicabut, dicatat
di audit JSONL. Otorisasi otomatis hanya untuk kategori rutin, dan kategori
seperti pencurian data, izin tanpa batas, atau aksi jaringan eksternal tetap
ditolak. Aksi ofensif hanya di lab lokal dengan token dan batas 300 detik."

Visual: ikon gembok dan perisai; diagram alur izin → audit JSONL; kolom
"DIIZINKAN" vs "DITOLAK" dengan transisi halus; angka 01-01-1970 dan 300 detik
muncul sebagai aksen.

### Slide 3 — Arsitektur inti (1:00–1:30)

"Arsitektur intinya: run_always.sh menjaga komputer tetap hidup dengan heartbeat
di system/reports/heartbeat.json. Supervisor melakukan hot-reload registry setiap
siklus dari system/services.json, sehingga layanan baru langsung jalan dan yang
dihapus berhenti otomatis — tidak ada server liar. Dashboard dan API berjalan di
port 8765, dan layanan baru wajib didaftarkan lewat service-add. Port selalu
memakai AGENTY_PORT, bukan PORT."

Visual: diagram node bergerak: heartbeat → supervisor → services.json → layanan;
kartu port 8765, 8772, 8766, 8782; label merah "PORT dilarang" vs hijau
"AGENTY_PORT".

### Slide 4 — Keamanan (1:30–2:02)

"Lapisan keamanan adalah jantung sistem: antivirus continuous polling dengan
karantina otomatis, firewall userspace berpolicy dengan CapBnd nol yang
enforcement kernelnya hanya dari host lewat install-net-admin, pemantauan
integritas SHA-256 berkas kritis, SOC, serta red-team laboratorium dengan payload
jinak EICAR dan target hanya localhost. Alur kerja harian, kampanye, dan lengkap
berjalan otomatis dengan izin per langkah. Skor keamanan dihitung dari 12 kontrol
terverifikasi menjadi angka 0 sampai 100, dan menjadi gate dalam make test."

Visual: radar memindai berkas; garis firewall menyaring paket; hash SHA-256
bermunculan; grafik skor 12 kontrol naik ke 100; badge "EICAR / localhost only".

### Slide 5 — Jaringan agen (2:02–2:34)

"Jaringan agen otonom meliputi Agent Computer yang merencanakan dan menjalankan
tugas, Advanced Computer dengan knowledge base dan memori persisten tanpa batas
iterasi buatan, asisten-manajer untuk koordinasi, persona Owner/CEO yang
konsultatif dan tidak berwenang menandatangani, agen R.A.M. untuk laporan memori
virtual dan swap, agen Hardware yang membaca info perangkat Android tanpa
mengekspos GPU, dan agen Dataset yang menyiapkan dan memvalidasi 292 rekord
instruksi–jawaban dari dokumen workspace dengan penanda trained false."

Visual: peta radial delapan ikon agen mengelilingi inti "Infinity"; kartu data
"292 rekord, trained: false"; badge "GPU tidak diekspos".

### Slide 6 — Model & relai (2:34–3:04)

"Model andalannya adalah tom05/tom05-flash-free, alias proxied yang berfungsi
setara hy4-flash-free dengan batas konteks 100 juta token dan biaya nol — bukan
model latihan baru. Ia bersifat messenger-only: setiap chat diteruskan
chat-dispatch ke sebelas responder lokal seperti agen, CLI, skill, tool, dan
docker yang benar-benar mengerjakan tugas, dengan klaim atomik dan penyaringan
privasi. Provider tom05 di port 8772 melayani 94 model alias, sementara hy4 sudah
dinonaktifkan dan tom05 menjadi CLI kanonik. Copilot CLI disamakan dengan 15 agen
dan 10 perintah."

Visual: alur chat → antrean → 11 responder; angka 100M, 94, 15, 10 muncul sebagai
kartu metrik; label "messenger-only" dan "alias/proxy, bukan model baru".

### Slide 7 — Chip (3:04–3:32)

"Chip hy4 adalah bukti rekayasa nyata: sepuluh modul RTL Verilog termasuk
hy4_dot4, hy4_quant, hy4_top dan tom05_soc untuk smartphone Android, terverifikasi
dengan 2868 vektor dan 5960 pengecekan, sintesis Yosys 185 sel, Icarus Verilog
lolos tanpa warning, preset browser bebas error, dan skor chip 100 dari 100
berdasarkan bukti nyata. Paket tapeout disusun ulang agar andal saat build
bersamaan."

Visual: tampilan waveform VCD bergerak; grid modul RTL menyala satu per satu;
kartu "10 modul / 2868 vektor / 185 sel / 100-100".

### Slide 8 — Privasi (3:32–3:58)

"Privasi menyeluruh dijaga security.privacy: scan_secrets, safe_output,
verify_tree, dan release_ready. Cermin publik publish/infinity-agentic-security
dinyatakan SIAP dengan 273 berkas dan nol temuan, setelah placeholder dan aset
sanitasi dikecualikan sementara kredensial nyata tetap terdeteksi. Kunci API
dibangkitkan CSPRNG, disimpan 0600, dan hanya sidik jari SHA-256 yang dicatat."

Visual: pulse scanner hijau melewati pohon berkas; kartu "273 berkas / 0 temuan /
SIAP"; ikon kunci dengan mode 0600 dan sidik jari hash.

### Slide 9 — Skor & strategi (3:58–4:36)

"Secara keseluruhan lima scorecard — chip, keamanan, tom05, perangkat, dan
container — masing-masing 100 dari 100, total 500 dari 500. Strategi global
menargetkan posisi nomor satu di kategori agentic security operations Asia
Tenggara, dengan roadmap empat fase: turbocharge inti, sistem pertumbuhan,
ekspansi adjansi dua puluh persen, dan ekosistem breakout, sambil menjaga prinsip
tidak mencuri data dan tidak menjanjikan izin tanpa batas."

Visual: lima kartu 100/100 berkumpul jadi "500/500"; peta Asia Tenggara dengan
titik Kota, Provinsi → Jakarta → Singapura; empat fase roadmap sebagai tangga.

### Slide 10 — Penutup (4:36–5:00)

"IT Agenty — Infinity: keamanan otonom, tata kelola ketat, bukti terverifikasi.
Terima kasih. (__signature__)."

Visual: kartu judul final "IT Agenty — Infinity", tanda tangan digital
`(__signature__)`, gelombang cyan memudar.

## Prompt generator video (siap pakai setelah kredit tersedia)

```text
Buat video presentation korporat teknologi berbahasa Indonesia dengan narasi
voice-over yang jelas, profesional, dan terperinci. Gaya visual: slide modern
bersih, latar gelap biru-tua dengan aksen cyan, tipografi besar dan minimal
(judul pendek saja, jangan paragraf panjang di layar), animasi transisi halus,
ikon garis, diagram arsitektur bergerak, dan peta modul yang tersorot. Narasi
harus mengikuti skrip pada docs/PRESENTASI-INFINITY.md secara urut dan lengkap,
dengan sound on, aspect 16:9, resolusi 1080p, durasi 300 detik, dan kartu judul
final IT Agenty — Infinity.
```

Perintah setara:

```bash
generate_video(
  prompt="<prompt di atas>",
  sound=true, aspect="16:9", resolution="1080p",
  duration=300, path="presentation-infinity.mp4"
)
```

## Catatan produksi

- Teks di layar sengaja dipendek; detail disampaikan narasi agar huruf yang
  dihasilkan model tidak berantakan.
- Semua angka di naskah berasal dari data workspace: 292 rekord dataset, 94 model
  alias, 15 agen + 10 command Copilot, 10 modul chip, 2868 vektor, 5960
  pengecekan, 185 sel, 12 kontrol keamanan, 273 berkas publik, 500/500 skor.
- Bila model video membatasi durasi, potong menjadi 5 klip 60 detik lalu
  concatenate; naskah sudah dipotong per slide sehingga mudah dipetakan.
- Jangan memasukkan kredensial atau nilai token ke dalam prompt/output video.
- Suara narasi disetel menyerupai warna suara perempuan pada
  `inbox/hy4-tutorial-9x16.mp4`: F0 target 234,6 Hz dicapai dengan espeak-ng
  pitch 99 + `asetrate=22050*1.366,aresample=22050,atempo=0.732`. Ini cocokan
  pitch/timbre perkiraan, bukan kloning suara; naskah tetap dibaca TTS.

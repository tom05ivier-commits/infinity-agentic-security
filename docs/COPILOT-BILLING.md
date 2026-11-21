<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Tagihan Copilot CLI — panduan, status, dan otorisasi

Sistem **tidak melakukan pembayaran otomatis**. Tidak ada data kartu, token
pembayaran, atau kredensial yang disimpan di workspace, log, chat, atau repo.
`surat-kuasa-tandatangan.md` §2 melarang transaksi keuangan, dan auto-approval
menolak `external-network-action` serta `unlimited-auth`.

## 1. Panduan pembayaran manual

```bash
make billing-guide
python3 security/security_cli.py billing guide
```

Langkahnya: buka `https://github.com/settings/billing`, bandingkan paket di
`https://github.com/features/copilot/plans`, lakukan pembayaran sendiri di
browser, lalu catat referensinya:

```bash
python3 security/copilot_billing.py record "INV-2026-11-001"
```

## 2. Cek status langganan (read-only)

```bash
python3 security/security_cli.py billing status
python3 copilot-bridge/doctor.py
```

Status lokal hanya boolean: CLI tersedia, model terkonfigurasi, kredensial ada
atau tidak. Status langganan tidak dapat ditentukan offline — periksa sendiri
di halaman tagihan GitHub. Tidak ada perubahan apa pun yang dilakukan.

## 3. Pengingat jatuh tempo (lokal)

```bash
python3 tools/copilot_billing_reminder.py --init 2026-12-01 --plan Copilot-Pro
make billing-reminder
```

Konfigurasi `credentials/billing.json` berisi tanggal dan nama paket saja,
mode 0600, dan masuk `.gitignore`. Tidak ada jaringan yang diakses.

## 4. Alur otorisasi terkendali

`security/copilot_billing.py` memisahkan aksi:

- `guide`, `status`, `plan-review`, `record-confirmation` — dapat diizinkan
  dengan token sekali pakai dari pemilik.
- `payment`, `auto-renew`, `card-update`, `token-export` — **selalu ditolak**
  kecuali ada `surat-izin-pembayaran-copilot.md` bertanda tangan pemilik.
  Surat itu sengaja **tidak dibuat** oleh sistem; hanya pemilik yang boleh
  menerbitkannya.

Token diberikan lewat variabel lingkungan `AGENTY_BILLING_AUTH` berisi JSON:

```json
{"token_id":"copilot-2026-11","issued_by":"Tomi vier","action":"status","issued_at":1763740800,"expires_at":1763741100}
```

Berlaku maksimal 300 detik, harus cocok dengan aksi, dan tidak pernah dicetak.
Jejak audit di `security/reports/copilot_billing.jsonl` memuat aksi, status,
waktu, dan sidik jari token — bukan nilainya.

Bila izin tertulis baru tersedia, sistem tetap tidak menekan tombol bayar:
pemilik mengeksekusi pembayaran di browser, lalu mencatat referensinya.

<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Top 10 CLI Platform Engineering (AI Agent Era)

Ringkasan dari <https://stackgen.com/blog/top-10-clis-for-platform-engineers>
(Srinivas, 3 Jul 2026), disesuaikan untuk sistem IT Agenty.

## Temuan utama

- Agent AI kini berjalan di terminal bersama engineer, bukan hanya di chat window.
- CLI menjadi penting karena otomasi bergantung padanya.
- Perbandingan 75 task pada agent berbasis MCP vs CLI: pendekatan CLI memakai
  **~10–32× lebih sedikit token** dengan reliabilitas mendekati **100%**.
- CLI yang baik untuk agent harus memberi output terstruktur, autentikasi
  andal, dan bisa dijalankan berulang dalam workflow.

## 10 CLI

| # | CLI | Kegunaan utama | Khusus agent |
|---|---|---|---|
| 1 | StackGen CLI | infra + AI agent | `stackgen mcp`, live context |
| 2 | kubectl | Kubernetes | `get/describe/apply/delete`, `-o json` |
| 3 | Terraform / OpenTofu | IaC | `plan` → review → `apply` |
| 4 | Crossplane CLI | infra Kubernetes-native | Compositions, satu API |
| 5 | Argo CD CLI | GitOps | diff/sync/rollback |
| 6 | Vault CLI | secrets | short-lived scoped credentials |
| 7 | GitHub CLI (`gh`) | PR/issue/release/actions | konteks GitHub |
| 8 | Pulumi CLI | IaC dengan bahasa pemrograman | `preview` → `up` |
| 9 | Claude Code | coding agent | Skills & Subagents |
| 10 | OpenCode / Kilo CLI | coding agent model-flexible | ganti model tanpa ganti CLI |

## Kriteria memilih CLI untuk otomasi

1. Structured output (JSON/YAML).
2. Plan/diff/dry-run sebelum perubahan.
3. Idempoten.
4. Exit code yang dapat diprediksi.
5. Autentikasi short-lived/SSO/workload identity.
6. Mudah dirangkai di script, pipeline, GitOps.
7. Struktur perintah konsisten.
8. State bisa diinspeksi, dibandingkan, dan di-troubleshoot.

## Penerapan di IT Agenty

- Model **`hy4-flash-free`** dipakai lewat OpenCode, masuk kategori #10.
- `copilot` (#7 ekosistem GitHub) terhubung lewat bridge lokal.
- `docker`, supervisor, dan registry server menjadi execution layer untuk
  kontainer dan layanan.
- Prinsip `plan → review → apply` tercermin pada `--dry-run`, izin otomatis
  terbatas, dan audit JSONL.
- Kredensial tidak disimpan permanen; token berjangka dan dapat dicabut.

## Status terpasang (24 November 2026)

Terverifikasi di lingkungan ini (aarch64, Ubuntu 24.04): `gh` 2.45.0,
`kubectl` 1.31.0, `terraform` 1.9.8, `tofu` 1.9.0, `crossplane` 2.5.0,
`argocd` 3.6.2, `vault` 2.2.2, `pulumi` 3.277.0, `stackgen` 0.82.0,
`claude` 2.1.327, `opencode` 2.4.1, `kilo` 7.8.32, `docker` 29.10.0.
Script pemasang: `scripts/install_github_tools.sh`; audit:
`security/reports/github_tools_install.jsonl`. Katalog tool GitHub MCP:
`docs/GITHUB-TOOLS.md` (26 tool, diakses lewat `execute`). Repo IT Agenty
di-clone ke `tools/github-tools/`; wrapper `copilot-ui` dan `copilot-ui-stop`
terpasang dari repo `copilot-CLI-agenty`. Terraform masih di bawah versi
terbaru (1.17.2) — bukan penghalang scorecard. Tool tambahan dari repo GitHub:
`gemini-api` 0.5.0 (repo `google-gemini/gemini-api-cli`, lisensi Apache-2.0
tetap dipertahankan), wrapper `copilot-ui`/`copilot-ui-stop`, dan 26 repo
`tom05ivier-commits` di-clone ke `tools/github-tools/`. Hasil
`./run_platform.sh doctor`: 10/10 terpasang, `missing: []`; skor 920/1000.

Kode scorecard ada di `platform_clis/` (nama sengaja bukan `platform` agar tidak
menimpa modul standar Python).

## Cara pakai scorecard

```bash
./run_platform.sh list
./run_platform.sh doctor
./run_platform.sh score
./run_platform.sh context   # teks untuk konteks model hy4
```

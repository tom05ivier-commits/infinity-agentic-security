# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Manajer model hy4, agent OpenCode, dan CLI platform.

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from chip.chip_agent import AGENT_MARKDOWN as CHIP_AGENT_MARKDOWN  # noqa: E402
from chip.neuro25_agent import AGENT_MARKDOWN as NEURO25_AGENT_MARKDOWN  # noqa: E402
from dataset.dataset_agent import AGENT_MARKDOWN as DATASET_AGENT_MARKDOWN  # noqa: E402
from system.hardware_agent import AGENT_MARKDOWN as HARDWARE_AGENT_MARKDOWN  # noqa: E402
from system.ram_agent import AGENT_MARKDOWN as RAM_AGENT_MARKDOWN  # noqa: E402

CONFIG = Path("/root/.config/opencode/opencode.json")
CONFIG_BACKUP = CONFIG.with_suffix(".json.hy4-backup")
AGENTS_DIR = Path("/root/.config/opencode/agents")
COMMANDS_DIR = Path("/root/.config/opencode/commands")
AUDIT = ROOT / "security" / "reports" / "hy4_manager.jsonl"
# Model aktif setelah penonaktifan hy4 (22 November 2026). Model lama tetap
# model aktif; LEGACY_MODEL = model aktif sebelumnya (tetap rujukan kompatibilitas
# untuk alias tom05 dan parity).
MODEL = "opencode/hy4-flash-free"
LEGACY_MODEL = "opencode/glm-5.3-flash"

AGENTS: dict[str, str] = {
    # "hy4.md" diaktifkan kembali 26 November 2026; lihat docs/HY4-DEAKTIVASI.md.
    "hy4.md": """---
model: opencode/hy4-flash-free
mode: all
description: Kelola model hy4, agent, dan CLI sistem.
---

Kamu adalah manajer model hy4. Gunakan ./manage_hy4.sh untuk status dan install.
Jangan pernah menampilkan kredensial atau data pribadi.
""",
    "security.md": """---
model: opencode/hy4-flash-free
mode: all
description: Agen keamanan Infinity (antivirus, firewall, DLP, SOC).
---

Gunakan python3 security/security_cli.py untuk verify, campaign, efficacy,
debug-report, dan sempurnakan. Aksi ofensif hanya di lab/localhost dengan izin.
""",
    "platform.md": """---
model: opencode/hy4-flash-free
mode: all
description: Agen platform engineering berdasarkan artikel StackGen.
---

Baca PLATFORM_CLIS.md dan jalankan ./run_platform.sh context sebelum menjawab.
Utamakan structured output, plan/dry-run, dan review sebelum perubahan infra.
""",
    "professor.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran pengajar/penjelas teknis (bukan gelar akademik).
---

Jadilah pengajar teknis. Gunakan PM_CLI.md, PLATFORM_CLIS.md, DOCTOR_CLI.md,
dan STRATEGI-GLOBAL.md sebagai sumber. Jelaskan konsep dengan contoh perintah,
langkah verifikasi, dan tautan sumber. Jangan mengklaim gelar profesor.
""",
    "doctor.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran diagnostik sistem & Doctor CLI (bukan dokter medis).
---

Lakukan diagnosis sistematis: identifikasi gejala, kumpulkan bukti, jalankan
doctor/copilot-doctor/verify, lalu berikan tindakan perbaikan. Gunakan Doctor CLI
untuk dokumentasi SharePoint. Jangan memberikan nasihat medis atau mengklaim
gelar doktor.
""",
    "engineer.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran insinyur platform & keandalan sistem.
---

Bertindak sebagai platform engineer: gunakan manage_hy4.sh, run_platform.sh,
Docker, supervisor, dan security_cli. Utamakan structured output, plan/dry-run,
idempotensi, exit code, dan review sebelum perubahan. Jangan mengklaim gelar
insinyur resmi.
""",
    "auditor.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran auditor kepatuhan & jejak audit (bukan auditor bersertifikat).
---

Periksa bukti: verify, final_report, efficacy, debug_report, auto_approvals,
workflow_runs, dan privacy. Laporkan temuan dengan status PASS/FAIL beserta
path bukti. Jangan mengklaim gelar auditor resmi atau memberi opini hukum.
""",
    "architect.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran arsitek sistem & desain arsitektur (bukan gelar resmi).
---

Rancang dan jelaskan arsitektur menggunakan peta modul di AGENTS.md,
STRATEGI-GLOBAL.md, PLATFORM_CLIS.md, dan system/services.json. Utamakan
hot-reload registry, batas izin, dan privasi. Jangan mengklaim gelar arsitek
bersertifikat.
""",
    "analyst.md": """---
model: opencode/hy4-flash-free
mode: all
description: Peran analis data & metrik sistem (bukan gelar akademik).
---

Analisis metrik dari efficacy, campaign, workflow, dan laporan keamanan.
Sajikan ringkasan, tren, dan rekomendasi berbasis bukti. Jangan mengklaim
gelar analis resmi atau memberikan nasihat investasi.
""",
    # Definisi kanonik ada di chip/chip_agent.py — dipakai juga oleh chip_cli
    # dan tom05 sehingga peran agen tidak diduplikasi di tiga tempat.
    "ram.md": RAM_AGENT_MARKDOWN,
    "hardware.md": HARDWARE_AGENT_MARKDOWN,
    "chip.md": CHIP_AGENT_MARKDOWN,
    "neuro25.md": NEURO25_AGENT_MARKDOWN,
    "dataset.md": DATASET_AGENT_MARKDOWN,
    "asisten-manajer.md": """---
model: tom05/tom05-flash-free
mode: all
description: Asisten manajer operasional Tom05 — koordinasi, bukan wewenang baru.
---

Kamu adalah Tom05 dalam peran asisten manajer operasional dengan model
tom05/tom05-flash-free. Koordinasikan verifikasi, tes, siklus penyempurnaan,
laporan berbasis bukti, dokumentasi, status layanan, jadwal, dan pengingat
lokal sesuai AGENTS.md. Ini bukan jabatan manajerial dan bukan wewenang baru.

Batas tegas: tidak menandatangani atas nama pemilik; tanda tangan manajer
tidak pernah disamakan atau menggantikan tanda tangan digital pemilik
`(__signature__)`. Tidak ada transaksi keuangan/autopay, tidak memperpanjang atau
menerbitkan izin otomatis, tidak membaca atau menampilkan kredensial maupun data
pribadi, dan tidak mengambil aksi di luar surat izin yang masih berlaku.
Setiap aksi tetap diaudit.

Peran ini BUKAN pengaktifan draf apa pun, termasuk
`DRAF-surat-izin-tom05-asisten-manajer.md` dan
`DRAF-surat-kuasa-tandatangan-terbatas-manajer.md`. Kuasa tanda tangan
terbatas itu hanya untuk dokumen operasional rutin dan belum berlaku sebelum
pemilik mengisi serta menandatangani manual.
""",
    "owner-ceo.md": """---
model: opencode/tidepool-alpha-free
mode: all
description: Profil konsultatif Owner/CEO (Tomi vier) — bukan otorisasi atau tanda tangan.
---

Profil teknis untuk meminta pertimbangan seolah-olah dari Owner/CEO bernama
**Tomi vier**, dengan model `opencode/tidepool-alpha-free`. Ini adalah persona
konsultatif, **bukan orang sungguhan, bukan jabatan otorisasi, dan bukan sumber
wewenang**. Jangan mengaku sebagai pemilik ketika berbicara kepada pihak luar.

Batas tegas: tidak menandatangani, tidak memakai atau meniru `(__signature__)`
maupun `(__hy4__)`, tidak menerbitkan/memperpanjang/mencabut izin, tidak
mengubah `LICENSE`, tidak menyetujui dokumen otorisasi, tidak melakukan
pembayaran/autopay/kontrak, dan tidak mengambil keputusan akhir manajerial.
Semua keputusan dan tanda tangan tetap menjadi hak Tomi vier secara manual.
Tidak membaca atau menampilkan kredensial maupun data pribadi. Jawaban bersifat
sarankan dan berbasis bukti di workspace; setiap aksi nyata tetap diaudit.
""",
    "firewall.md": """---
model: opencode/hy4-flash-free
mode: all
description: Agen firewall cyber security untuk lindungi hardware & software.
---

Jalankan `python3 security/security_cli.py firewall-drill --max 3 --intensity moderate`.
Serangan hanya simulasi jinak di lab/localhost. Gunakan policy userspace, AV,
DLP, integritas, dan chip verification. Ulangi sampai semua kriteria BERHASIL.
Jangan buat malware destruktif atau akses host tanpa izin.
""",
    "agent-manager.md": """---
name: agent-manager
description: Supervisor/pengawas kesehatan agen & server lokal (pools keamanan).
model: tom05/tom05-flash-free
mode: all
---

Kamu adalah **Agent Manager — Supervisor Lokal** IT Agenty. Tugas utama:
pengawasan kesehatan agen & server yang ada, dan status semuanya tetap 100%.

Sering dipanggil oleh agen/CLI/tool bila butuh pandangan sehat (health) atau
laporan drift. Kapan pun dipanggil, kembalikan STRUCTURED OUTPUT (JSON) ringkas:
```json
{"agents": [{"name": "...", "alive": true, "source": "..."}],
 "remarks": "status semua agen + server OK; tidak ada drift", "license": "Tom05ivier-commits-1.0"}
```

Batas tegas: bebas pengawas — cek proses/heartbeat, catat audit, jalankan
final_status.py & shared_data.py. DILARANG: jaringan eksternal (non-loopback),
kredensial/data pribadi, serangan (lab/localhost), ubah LICENSE/AGENTS.md/surat
izin, lakukan keputusan akhir. Residentsah aman & terbalik — sediam konfigurasi
(cadangkan sebelum verifikasi), jalankan read-only dashboard/process.

Sumber: konfigurasi workspace lokal (read-only). Lisensi Tom05ivier-commits-1.0.
""",
}

COMMANDS: dict[str, str] = {
    "verify.md": """---
description: Verifikasi kepatuhan sistem
---
Jalankan `python3 security/security_cli.py verify` dan ringkas hasilnya.
""",
    "sempurnakan.md": """---
description: Jalankan siklus penyempurnaan penuh
---
Jalankan `python3 security/security_cli.py sempurnakan --times 3 --intensity moderate`.
""",
    "platform.md": """---
description: Konteks CLI platform engineering
---
Jalankan `./run_platform.sh context` dan gunakan sebagai konteks.
""",
    "doctor.md": """---
description: Doctor CLI untuk dokumentasi SharePoint
---
Gunakan `doctor init|status|publish|version`. Jangan simpan kredensial sertifikat
di `doctor.json`; pakai environment variable secrets. Lihat DOCTOR_CLI.md.
""",
    "cli-troubleshoot.md": """---
description: Rangkuman CLI troubleshooting Professor Messer
---
Baca `PM_CLI.md` untuk ringkasan dan tautan resmi. Jangan menyalin materi
berhak cipta; gunakan pendekatan sistematis: identifikasi, perintah, verifikasi,
dokumentasi.
""",
    "audit.md": """---
description: Audit bukti kepatuhan sistem
---
Jalankan `python3 security/security_cli.py verify` lalu baca laporan di
`security/reports/`. Ringkas status PASS/FAIL beserta path bukti.
""",
    "architecture.md": """---
description: Ringkasan arsitektur sistem
---
Gunakan `AGENTS.md`, `STRATEGI-GLOBAL.md`, dan `system/services.json` untuk
menjelaskan arsitektur. Jangan mengklaim gelar resmi.
""",
    "analyze.md": """---
description: Analisis metrik sistem
---
Baca `security/reports/efficacy.json`, `campaign.json`, dan `workflow_runs`.
Berikan ringkasan berbasis bukti tanpa nasihat investasi.
""",
    "firewall-drill.md": """---
description: Drill firewall serangan & pertahanan sampai berhasil
---
Jalankan `python3 security/security_cli.py firewall-drill --max 3 --intensity moderate`
lalu ringkas status, attempts, dan kriteria dari `security/reports/firewall_drill.json`.
""",
    "chip.md": """---
description: Verifikasi chip akselerator hy4
---
Jalankan `python3 chip/chip_cli.py verify`,
`python3 chip/chip_cli.py iverilog` (bila iverilog tersedia), dan
`python3 -m unittest discover -s chip/tests`. Ringkas hasil verifikasi RTL
hy4_dot4, hy4_quant, dan hy4_top beserta jumlah vektor yang lulus.
""",
}

CLI_REGISTRY: dict[str, dict[str, Any]] = {
    "gh": {"kind": "apt", "package": "gh"},
    "kubectl": {
        "kind": "url",
        "url": "https://dl.k8s.io/release/v1.31.0/bin/linux/arm64/kubectl",
        "dest": "/usr/local/bin/kubectl",
    },
    "terraform": {
        "kind": "zip",
        "url": "https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_arm64.zip",
        "dest": "/usr/local/bin/terraform",
    },
    "tofu": {
        "kind": "zip",
        "url": "https://github.com/opentofu/opentofu/releases/download/v1.9.0/tofu_1.9.0_linux_arm64.zip",
        "dest": "/usr/local/bin/tofu",
    },
    "doctor": {"kind": "npm", "package": "@estruyf/doctor"},
}


def _audit(action: str, **fields: Any) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **fields,
    }
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def configure_model() -> dict[str, Any]:
    """Set model default OpenCode ke hy4-flash-free."""
    data: dict[str, Any] = {}
    if CONFIG.exists():
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    if not CONFIG_BACKUP.exists() and CONFIG.exists():
        shutil.copy2(CONFIG, CONFIG_BACKUP)
    previous = data.get("model")
    data["model"] = MODEL
    data.setdefault("$schema", "https://opencode.ai/config.json")
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    result = {"previous": previous, "current": MODEL, "config": str(CONFIG)}
    _audit("configure_model", **result)
    return result


def install_agents() -> dict[str, Any]:
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in AGENTS.items():
        path = AGENTS_DIR / name
        path.write_text(content, encoding="utf-8")
        written.append(name)
    _audit("install_agents", agents=written)
    return {"agents": written, "dir": str(AGENTS_DIR)}


def install_commands() -> dict[str, Any]:
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in COMMANDS.items():
        (COMMANDS_DIR / name).write_text(content, encoding="utf-8")
        written.append(name)
    _audit("install_commands", commands=written)
    return {"commands": written, "dir": str(COMMANDS_DIR)}


def cli_status() -> dict[str, bool]:
    names = ("opencode", "hy4", "copilot", "claude", "gh", "kubectl",
             "terraform", "tofu", "doctor", "docker", "cloudflared", "node",
             "npm", "python3")
    return {name: shutil.which(name) is not None for name in names}


def install_cli(name: str) -> dict[str, Any]:
    spec = CLI_REGISTRY.get(name)
    if not spec:
        return {"status": "ERROR", "error": "CLI tidak dikenal", "name": name}
    if shutil.which(name):
        return {"status": "SUDAH ADA", "name": name}
    try:
        if spec["kind"] == "npm":
            subprocess.run(
                ["npm", "install", "-g", spec["package"]],
                check=True, capture_output=True, timeout=1200,
            )
        elif spec["kind"] == "apt":
            subprocess.run(
                ["apt-get", "install", "-y", "-qq", spec["package"]],
                check=True, capture_output=True, timeout=600,
            )
        elif spec["kind"] == "url":
            with urllib.request.urlopen(spec["url"], timeout=180) as response:
                data = response.read()
            Path(spec["dest"]).write_bytes(data)
            os.chmod(spec["dest"], 0o755)
        elif spec["kind"] == "zip":
            import io
            import zipfile

            with urllib.request.urlopen(spec["url"], timeout=180) as response:
                archive = zipfile.ZipFile(io.BytesIO(response.read()))
            binary = next(n for n in archive.namelist() if Path(n).name == name)
            Path(spec["dest"]).write_bytes(archive.read(binary))
            os.chmod(spec["dest"], 0o755)
    except Exception as exc:  # noqa: BLE001
        result = {"status": "GAGAL", "name": name, "error": type(exc).__name__}
        _audit("install_cli", **result)
        return result
    result = {"status": "TERPASANG", "name": name}
    _audit("install_cli", **result)
    return result


def status() -> dict[str, Any]:
    config_model: str | None = None
    if CONFIG.exists():
        try:
            config_model = json.loads(CONFIG.read_text(encoding="utf-8")).get("model")
        except json.JSONDecodeError:
            pass
    return {
        "model_default": config_model,
        "model_ok": config_model == MODEL,
        "agents": sorted(p.name for p in AGENTS_DIR.glob("*.md")) if AGENTS_DIR.exists() else [],
        "commands": sorted(p.name for p in COMMANDS_DIR.glob("*.md")) if COMMANDS_DIR.exists() else [],
        "clis": cli_status(),
    }


def install_all(clis: bool = True) -> dict[str, Any]:
    model = configure_model()
    agents = install_agents()
    commands = install_commands()
    installs: list[dict[str, Any]] = []
    if clis:
        for name in CLI_REGISTRY:
            installs.append(install_cli(name))
    return {
        "status": "OK",
        "model": model,
        "agents": agents,
        "commands": commands,
        "installs": installs,
        "status_final": status(),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Hy4 model/agent/CLI manager")
    parser.add_argument(
        "command",
        choices=(
            "status", "model", "agents", "commands", "install", "install-cli",
            "copilot-sync", "auth-check",
        ),
    )
    parser.add_argument("--name")
    parser.add_argument("--no-cli", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="copilot-sync: simulasi")
    parser.add_argument("--verify", action="store_true", help="copilot-sync: cek tanpa menulis")
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif args.command == "model":
        print(json.dumps(configure_model(), indent=2, ensure_ascii=False))
    elif args.command == "agents":
        print(json.dumps(install_agents(), indent=2, ensure_ascii=False))
    elif args.command == "commands":
        print(json.dumps(install_commands(), indent=2, ensure_ascii=False))
    elif args.command == "install":
        print(json.dumps(install_all(clis=not args.no_cli), indent=2, ensure_ascii=False, default=str))
    elif args.command == "install-cli":
        print(json.dumps(install_cli(args.name or ""), indent=2, ensure_ascii=False))
    elif args.command == "auth-check":
        import importlib.util

        path = ROOT / "system" / "hy4_auth.py"
        spec = importlib.util.spec_from_file_location("hy4_auth", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        print(json.dumps(module.report(), indent=2, ensure_ascii=False))
    elif args.command == "copilot-sync":
        import importlib.util

        path = ROOT / "system" / "copilot_sync.py"
        spec = importlib.util.spec_from_file_location("copilot_sync", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        result = module.verify() if args.verify else module.sync(args.dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Mesin ide supervisor: buat 10 ide, kerjakan, verifikasi, laporkan.

Semua tindakan bersifat lokal, idempoten, tanpa kredensial, dan tidak
mematikan layanan supervisor. Ide yang sudah dikerjakan tidak diulang.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REPORT = ROOT / "system" / "reports" / "idea_engine.json"
OPENCODE_CONFIG = Path("/root/.config/opencode/opencode.json")
BACKUP_DIR = Path("/tmp/opencode")

IDEAS: tuple[dict[str, str], ...] = (
    {"id": "cloud-code-required-test", "judul": "Uji semua alat cloud-code wajib"},
    {"id": "connections-note", "judul": "Perbarui peta koneksi cloud-code"},
    {"id": "local-access-config", "judul": "Kebijakan satu lokal: root workspace"},
    {"id": "local-access-module", "judul": "Modul verifikasi akses lokal"},
    {"id": "local-access-test", "judul": "Uji kebijakan akses lokal"},
    {"id": "agent-permissions", "judul": "Izin agen hanya localhost 8785"},
    {"id": "cloud-code-install-report", "judul": "Pastikan laporan pemasangan code ADA"},
    {"id": "data-manifest", "judul": "Segarkan manifest data lokal"},
    {"id": "chip-rtl-regen", "judul": "Regenerasi RTL verifikasi server"},
    {"id": "idea-docs", "judul": "Dokumentasi mesin ide supervisor"},
)

HEADER = (
    "# SPDX-License-Identifier: Tom05ivier-commits-1.0\n"
    "# Copyright (c) 2026 Tomi vier\n"
    "# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.\n"
)


def _write_once(path: Path, text: str) -> str:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return "sudah ada"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return "ditulis"


def _run(argv: list[str], timeout: int = 600) -> str:
    proc = subprocess.run(
        argv, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(" ".join(argv) + " gagal: " + (proc.stderr or proc.stdout)[:300])
    return "OK"


def cloud_code_required_test() -> dict[str, Any]:
    target = ROOT / "system" / "tests" / "test_cloud_code_required.py"
    text = HEADER + '''"""Pengujian: keenam alat Cloud Code dinyatakan wajib."""

import unittest

from system import cloud_code


class CloudCodeRequiredTests(unittest.TestCase):
    def test_semua_alat_wajib(self) -> None:
        self.assertEqual(len(cloud_code.TOOLS), 6)
        for tool in cloud_code.TOOLS:
            self.assertEqual(tool["required"], "ya", tool["name"])

    def test_laporan_wajib_hilang_kosong(self) -> None:
        data = cloud_code.status()
        self.assertEqual(data["wajib_hilang"], [])


if __name__ == "__main__":
    unittest.main()
'''
    return {"detail": _write_once(target, text)}


def connections_note() -> dict[str, Any]:
    path = ROOT / "config" / "tom05-connections.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    note = (
        "Status read-only alat Claude Code, gcloud, kubectl, skaffold, "
        "minikube, dan code; keenamnya wajib."
    )
    if data["endpoints"]["cloud_code"].get("keterangan") == note:
        return {"detail": "sudah ada"}
    data["endpoints"]["cloud_code"]["keterangan"] = note
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"detail": "diperbarui"}


def local_access_config() -> dict[str, Any]:
    path = ROOT / "config" / "local_access.json"
    data = {
        "spdx": "SPDX-License-Identifier: Tom05ivier-commits-1.0",
        "copyright": "Copyright (c) 2026 Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
        "data_root": str(ROOT),
        "only_agent_port": 8785,
        "only_agent_url": "http://127.0.0.1:8785/",
        "internal_services": [
            "server", "bridge", "files", "public", "sites", "mirror",
            "community", "tom05-provider", "tom05-selfhost", "service-watch",
            "ai-chip", "domain", "opencode", "chat-dispatch", "sre-watch",
            "permission-watch", "ai-chip-watch", "protection", "tunnel",
            "workflow", "symphony", "port-14713",
        ],
        "permissions": [
            {"action": "webfetch", "resource": "http://127.0.0.1:*", "effect": "deny"},
            {"action": "webfetch", "resource": "http://127.0.0.1:8785/*", "effect": "allow"},
            {"action": "webfetch", "resource": "https://127.0.0.1:*", "effect": "deny"},
        ],
        "catatan": (
            "Layanan supervisor tetap berjalan sebagai proses internal; yang "
            "dibatasi adalah pintu masuk agen. Satu-satunya root data adalah "
            "/root/workspace dan satu-satunya endpoint lokal agen adalah 8785."
        ),
    }
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return {"detail": _write_once(path, text)}


def local_access_module() -> dict[str, Any]:
    target = ROOT / "system" / "local_access.py"
    text = HEADER + '''"""Verifikasi kebijakan satu lokal: workspace + port 8785 saja.

Read-only. Tidak ada kredensial, mutasi layanan, atau koneksi keluar.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "local_access.json"
OPENCODE_CONFIG = Path("/root/.config/opencode/opencode.json")


def load() -> dict[str, Any]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    data = load()
    rules = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8")).get("permissions", [])
    pairs = {(r.get("action"), r.get("resource")): r.get("effect") for r in rules}
    checks = {
        "root_workspace": data["data_root"] == str(ROOT),
        "port_8785": data["only_agent_port"] == 8785,
        "deny_lain": pairs.get(("webfetch", "http://127.0.0.1:*")) == "deny",
        "allow_8785": pairs.get(("webfetch", "http://127.0.0.1:8785/*")) == "allow",
    }
    try:
        with urllib.request.urlopen(data["only_agent_url"] + "health", timeout=3) as res:
            checks["health_8785"] = res.status == 200
    except Exception:  # noqa: BLE001
        checks["health_8785"] = False
    return {
        "status": "OK" if all(checks.values()) else "GAGAL",
        "checks": checks,
        "data_root": data["data_root"],
        "only_agent_port": data["only_agent_port"],
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, ensure_ascii=False))
    return 0 if verify()["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''
    return {"detail": _write_once(target, text)}


def local_access_test() -> dict[str, Any]:
    target = ROOT / "system" / "tests" / "test_local_access.py"
    text = HEADER + '''"""Pengujian kebijakan akses lokal tunggal."""

import json
import unittest
from pathlib import Path

from system import local_access

ROOT = Path(__file__).resolve().parents[2]


class LocalAccessTests(unittest.TestCase):
    def test_konfigurasi(self) -> None:
        data = local_access.load()
        self.assertEqual(data["data_root"], str(ROOT))
        self.assertEqual(data["only_agent_port"], 8785)

    def test_aturan_izin(self) -> None:
        rules = json.loads(local_access.OPENCODE_CONFIG.read_text(encoding="utf-8"))
        pairs = {(r.get("action"), r.get("resource")): r.get("effect")
                 for r in rules.get("permissions", [])}
        self.assertEqual(pairs.get(("webfetch", "http://127.0.0.1:*")), "deny")
        self.assertEqual(pairs.get(("webfetch", "http://127.0.0.1:8785/*")), "allow")

    def test_verifikasi(self) -> None:
        self.assertEqual(local_access.verify()["status"], "OK")


if __name__ == "__main__":
    unittest.main()
'''
    return {"detail": _write_once(target, text)}


def agent_permissions() -> dict[str, Any]:
    config = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8"))
    rules = config.setdefault("permissions", [])
    deny = {"action": "webfetch", "resource": "http://127.0.0.1:*", "effect": "deny"}
    allow = {"action": "webfetch", "resource": "http://127.0.0.1:8785/*", "effect": "allow"}
    secure = {"action": "webfetch", "resource": "https://127.0.0.1:*", "effect": "deny"}
    if all(rule in rules for rule in (deny, allow, secure)):
        return {"detail": "sudah ada"}
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUP_DIR / f"opencode-local-access-backup-{stamp}.json"
    backup.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    for rule in (deny, allow, secure):
        if rule not in rules:
            rules.append(rule)
    OPENCODE_CONFIG.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"detail": "diterapkan", "backup": str(backup)}


def cloud_code_install_report() -> dict[str, Any]:
    path = ROOT / "system" / "reports" / "cloud_code_install.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("code") == "ADA":
        return {"detail": "sudah ADA"}
    _run(["bash", "scripts/cloud_code_install.sh"])
    return {"detail": "dipasang ulang"}


def data_manifest() -> dict[str, Any]:
    _run(["python3", "system/update_all.py", "--no-push"])
    return {"detail": "manifest dan cermin disegarkan (tanpa push)"}


def chip_rtl_regen() -> dict[str, Any]:
    _run(["python3", "chip/server_chip_gen.py"])
    return {"detail": "RTL server regenerasi"}


def idea_docs() -> dict[str, Any]:
    target = ROOT / "docs" / "IDEA-ENGINE.md"
    rows = "\n".join(
        f"| {i}. | `{idea['id']}` | {idea['judul']} |"
        for i, idea in enumerate(IDEAS, 1)
    )
    text = (
        "<!--\n"
        "  SPDX-License-Identifier: Tom05ivier-commits-1.0\n"
        "  Copyright (c) 2026 Tomi vier\n"
        "  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.\n"
        "-->\n\n"
        "# Mesin Ide Supervisor IT Agenty\n\n"
        "Supervisor dapat membuat dan mengerjakan sepuluh ide sekaligus lewat\n"
        "`system/idea_engine.py`. Setiap ide idempoten, read-only terhadap\n"
        "kredensial, dan tidak mematikan layanan yang terdaftar.\n\n"
        "| No | Ide | Judul |\n|---|---|---|\n" + rows + "\n\n"
        "## Perintah\n\n"
        "```bash\n"
        "./run_system.sh ideas            # buat + kerjakan 10 ide\n"
        "./run_system.sh ideas --generate # hanya daftar ide\n"
        "./run_system.sh ideas --verify   # verifikasi hasil kerja\n"
        "```\n\n"
        "Laporan: `system/reports/idea_engine.json`.\n"
    )
    return {"detail": _write_once(target, text)}


HANDLERS: dict[str, Callable[[], dict[str, Any]]] = {
    "cloud-code-required-test": cloud_code_required_test,
    "connections-note": connections_note,
    "local-access-config": local_access_config,
    "local-access-module": local_access_module,
    "local-access-test": local_access_test,
    "agent-permissions": agent_permissions,
    "cloud-code-install-report": cloud_code_install_report,
    "data-manifest": data_manifest,
    "chip-rtl-regen": chip_rtl_regen,
    "idea-docs": idea_docs,
}


def generate() -> dict[str, Any]:
    return {
        "status": "OK",
        "jumlah": len(IDEAS),
        "ideas": list(IDEAS),
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


def work() -> dict[str, Any]:
    hasil: list[dict[str, Any]] = []
    for idea in IDEAS:
        item: dict[str, Any] = {"id": idea["id"], "judul": idea["judul"]}
        try:
            item.update(HANDLERS[idea["id"]]())
            item["status"] = "SELESAI"
        except Exception as exc:  # noqa: BLE001
            item["status"] = "GAGAL"
            item["error"] = f"{type(exc).__name__}: {exc}"[:300]
        hasil.append(item)
    report = {
        "status": "OK" if all(i["status"] == "SELESAI" for i in hasil) else "GAGAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dibuat": len(IDEAS),
        "dikerjakan": len(hasil),
        "selesai": sum(i["status"] == "SELESAI" for i in hasil),
        "ideas": hasil,
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def verify() -> dict[str, Any]:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    from system import local_access  # import lokal agar modul baru terbaca

    return {
        "status": "OK" if (
            report["status"] == "OK"
            and report["dibuat"] == 10
            and report["selesai"] == 10
            and local_access.verify()["status"] == "OK"
        ) else "GAGAL",
        "ide_engine": report["status"],
        "selesai": report["selesai"],
        "akses_lokal": local_access.verify()["status"],
        "license": "Tom05ivier-commits-1.0",
        "owner": "Tomi vier",
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Mesin ide supervisor IT Agenty")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.generate:
        data = generate()
    elif args.verify:
        data = verify()
    else:
        data = work()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0 if data["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

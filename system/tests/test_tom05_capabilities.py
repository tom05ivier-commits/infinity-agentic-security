# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian kemampuan baru tom05: SoC Android, container, dan diagnostik."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CATALOG = ROOT / "config" / "tom05-models.json"
CLI = ROOT / "tom05"
VERIFY = ROOT / "scripts" / "tom05_container_verify.sh"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(CLI), *args], capture_output=True, text=True, timeout=120,
        cwd=str(ROOT),
    )


class Tom05CapabilityTests(unittest.TestCase):
    def test_catalog_declares_capabilities(self) -> None:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        caps = data["capabilities"]
        self.assertEqual(caps["soc"]["module"], "tom05_soc")
        self.assertEqual(caps["soc"]["target"], "android-smartphone")
        self.assertEqual(caps["soc"]["vectors"], 1024)
        self.assertEqual(caps["ai_chip"]["module"], "tom05_ai_accel")
        self.assertEqual(caps["ai_chip"]["vectors"], 2048)
        self.assertEqual(caps["ai_chip"]["fabrication"], "NOT_READY")
        self.assertEqual(caps["chip"]["score"], "100/100")
        self.assertFalse(caps["safety"]["credentials_in_chat"])
        self.assertFalse(caps["safety"]["unlimited_authorization"])

    def test_catalog_declares_display_profile(self) -> None:
        disp = json.loads(CATALOG.read_text(encoding="utf-8"))["capabilities"]["display"]
        self.assertEqual(disp["name"], "Tom05 Landscape Display")
        self.assertEqual(disp["orientation"], "lanskap")
        self.assertEqual(disp["gpu_acceleration"]["backends"], ["panfrost", "mali"])
        self.assertEqual(disp["gpu_acceleration"]["preferred"], "panfrost")
        self.assertFalse(disp["gpu_acceleration"]["bridge_exposed"])

    def test_cli_display_flag(self) -> None:
        done = run_cli("--display")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["name"], "Tom05 Landscape Display")
        self.assertEqual(data["orientation"], "lanskap")
        self.assertEqual(data["gpu_acceleration"]["backends"], ["panfrost", "mali"])

    def test_container_declares_display_profile(self) -> None:
        dockerfile = (ROOT / "Dockerfile.tom05").read_text()
        compose = (ROOT / "docker-compose.tom05.yml").read_text()
        entrypoint = (ROOT / "scripts" / "tom05_container_entrypoint.sh").read_text()
        for token in ("TOM05_DISPLAY_ORIENTATION", "TOM05_GPU_BACKENDS"):
            self.assertIn(token, dockerfile)
            self.assertIn(token, compose)
        self.assertIn("display)", entrypoint)

    def test_container_joins_manager_network(self) -> None:
        import json as _json

        tom05 = (ROOT / "docker-compose.tom05.yml").read_text()
        dev = (ROOT / "docker-compose.dev.yml").read_text()
        for token in ("agenty-net", "infinity:8766", "TOM05_MANAGER_HOST", "infinity:host-gateway"):
            self.assertIn(token, tom05)
        for token in ("agenty-net", "infinity", "manager"):
            self.assertIn(token, dev)
        services = _json.loads((ROOT / "system" / "services.json").read_text())
        svc = next(s for s in services["services"] if s["name"] == "tom05-provider")
        self.assertEqual(svc["container"], "tom05-inference")
        self.assertEqual(svc["container_network"], "agenty-net")
        self.assertEqual(svc["manager"], "infinity")

    def test_soc_and_container_artifacts_exist(self) -> None:
        rtl = ROOT / "chip" / "rtl" / "tom05_soc.v"
        self.assertTrue(rtl.exists())
        self.assertIn("Tom05ivier-commits-1.0", rtl.read_text()[:300])
        dockerfile = (ROOT / "Dockerfile.tom05").read_text()
        self.assertIn("USER 10001:10001", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)
        compose = (ROOT / "docker-compose.tom05.yml").read_text()
        self.assertIn("read_only: true", compose)
        self.assertIn("no-new-privileges:true", compose)
        self.assertNotIn("network_mode: host", compose)
        self.assertTrue(VERIFY.exists())

    def test_cli_soc_flag(self) -> None:
        done = run_cli("--soc")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["name"], "tom05_soc")
        self.assertEqual(data["target"], "android-smartphone")
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["vectors"], 1024)
        self.assertEqual(data["mismatches"], 0)

    def test_cli_ai_chip_flag(self) -> None:
        done = run_cli("--ai-chip")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["name"], "tom05_ai_accel")
        self.assertEqual(data["target"], "ai-inference-accelerator")
        self.assertEqual(data["fabrication"], "NOT_READY")
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["vectors"], 2048)
        self.assertEqual(data["mismatches"], 0)

    def test_cli_domain_and_permission_flags(self) -> None:
        caps = json.loads(CATALOG.read_text(encoding="utf-8"))["capabilities"]
        self.assertEqual(caps["domain"]["root_domain"], "agenty.local")
        self.assertFalse(caps["domain"]["ddns_automatic"])
        self.assertEqual(caps["permission"]["max_ttl"], 300)
        self.assertFalse(caps["permission"]["automatic_signature"])
        domain = run_cli("--domain")
        self.assertEqual(domain.returncode, 0, domain.stderr)
        self.assertEqual(json.loads(domain.stdout)["root_domain"], "agenty.local")
        permission = run_cli("--permission")
        self.assertEqual(permission.returncode, 0, permission.stderr)
        self.assertEqual(json.loads(permission.stdout)["valid_until"], "2027-12-31")

    def test_cli_container_flag(self) -> None:
        done = run_cli("--container")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertGreaterEqual(data["pass"], 8)
        self.assertEqual(data["fail"], 0)

    def test_cli_capabilities_flag(self) -> None:
        done = run_cli("--capabilities")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["cli_version"], "1.3.0")
        self.assertEqual(data["default_model"], "tom05/tom05-flash-free")
        self.assertEqual(data["context_length"], 100_000_000)
        self.assertEqual(data["capabilities"]["soc"]["module"], "tom05_soc")

    def test_cli_doctor_flag(self) -> None:
        done = run_cli("--doctor")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertIn(data["status"], ("PASS", "DEGRADED"))
        names = {item["name"] for item in data["checks"]}
        self.assertEqual(names, {"catalog", "soc", "container", "provider"})

    def test_verify_script_json(self) -> None:
        done = subprocess.run(
            ["bash", str(VERIFY), "--json"], capture_output=True, text=True,
            timeout=120, cwd=str(ROOT),
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout.strip().splitlines()[-1])
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["fail"], 0)

    def test_help_lists_new_flags(self) -> None:
        out = run_cli("--help").stdout
        for flag in ("--soc", "--container", "--display", "--capabilities", "--doctor",
                     "--domain", "--permission"):
            self.assertIn(flag, out)

    def test_catalog_declares_parity(self) -> None:
        caps = json.loads(CATALOG.read_text(encoding="utf-8"))["capabilities"]
        parity = caps["parity"]
        self.assertEqual(parity["status"], "SAMA")
        self.assertEqual(parity["alias"], "tom05/tom05-flash-free")
        self.assertEqual(parity["upstream"], "opencode/hy4-flash-free")
        self.assertEqual(parity["declared_model"], "opencode/deepseek-v4.1-flash-free")
        self.assertIn("bukan model terlatih baru", parity["catatan"])

    def test_cli_parity_flags(self) -> None:
        self.assertIn("--parity-model", run_cli("--help").stdout)
        self.assertIn("--parity-all", run_cli("--help").stdout)
        model = run_cli("--parity-model", "opencode/deepseek-v4.1-flash-free")
        self.assertEqual(model.returncode, 0, model.stderr)
        self.assertEqual(json.loads(model.stdout)["status"], "SAMA")
        semua = run_cli("--parity-all")
        self.assertEqual(semua.returncode, 0, semua.stderr)
        data = json.loads(semua.stdout)
        self.assertEqual(data["status"], "SAMA")
        self.assertEqual(data["jumlah"], 11)


if __name__ == "__main__":
    unittest.main(verbosity=2)

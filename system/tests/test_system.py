# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian sistem komputer terpadu."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.core import ComputerSystem  # noqa: E402
from system.dashboard import generate, render  # noqa: E402
from system.protection import ProtectionDaemon  # noqa: E402


class ComputerSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = ComputerSystem()

    def test_identity_loaded(self) -> None:
        identity = self.system.identity()
        self.assertEqual(identity["nama"], "Tomi vier")
        self.assertIn(
            identity["tanda_tangan"], ("(__signature__)", "(__signature__)")
        )

    def test_license_loaded(self) -> None:
        license_info = self.system.license()
        self.assertEqual(license_info["identitas"], "Tom05ivier-commits")
        self.assertEqual(license_info["pemilik"], "Tomi vier")

    def test_authorization_loaded(self) -> None:
        authorization = self.system.authorization()
        self.assertTrue(authorization["surat_izin"])
        self.assertTrue(authorization["surat_kuasa"])
        self.assertTrue(authorization["bertanda_tangan"])

    def test_environment_loaded(self) -> None:
        environment = self.system.environment()
        self.assertGreaterEqual(environment["jumlah_script"], 6)
        self.assertEqual(environment["rgb_colors"], 754)

    def test_snapshot_complete(self) -> None:
        snapshot = self.system.snapshot()
        for key in (
            "identitas",
            "lisensi",
            "otorisasi",
            "lingkungan",
            "keamanan",
            "agen",
            "kampanye",
            "advanced",
            "berkas",
        ):
            self.assertIn(key, snapshot)

    def test_dashboard_generated(self) -> None:
        path = generate()
        content = path.read_text(encoding="utf-8")
        self.assertIn("Tomi vier", content)
        self.assertIn("Tom05ivier-commits", content)
        self.assertIn("<!DOCTYPE html>", content)

    def test_render_escapes_html(self) -> None:
        snapshot = self.system.snapshot()
        snapshot["identitas"]["nama"] = "<script>alert(1)</script>"
        rendered = render(snapshot)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_protection_daemon_runs(self) -> None:
        daemon = ProtectionDaemon(seconds=0.6, interval=0.1)
        result = daemon.run()
        self.assertGreaterEqual(result["samples"], 1)
        self.assertIn("denied_ports", result["baseline"])
        self.assertTrue(Path(result["status_path"]).exists())

    def test_tom05_cli_present(self) -> None:
        cli = ROOT / "tom05"
        self.assertTrue(cli.exists())
        text = cli.read_text(encoding="utf-8")
        self.assertIn("opencode/hy4-flash-free", text)
        self.assertNotIn("hy4 CLI", text)
        self.assertIn("AGENTS.md", text)
        for flag in ("--port-file", "--port-stdin", "--follow-port", "--continue"):
            self.assertIn(flag, text)
        self.assertTrue((Path("/usr/local/bin") / "tom05").exists())
        self.assertFalse((Path("/usr/local/bin") / "hy4").exists())

    def test_credentials_framework_present(self) -> None:
        base = ROOT / "credentials"
        self.assertTrue((base / ".env.example").exists())
        self.assertTrue((base / "README.md").exists())
        self.assertTrue((base / "check.sh").exists())
        text = (base / ".env.example").read_text(encoding="utf-8")
        self.assertIn("OPENCODE_API_KEY", text)
        self.assertIn("GITHUB_TOKEN", text)
        script = (base / "check.sh").read_text(encoding="utf-8")
        self.assertIn("ADA", script)
        self.assertIn("kosong", script)

    def test_update_all_module_present(self) -> None:
        script = ROOT / "update_all.sh"
        module = ROOT / "system" / "update_all.py"
        self.assertTrue(script.exists() and module.exists())
        text = module.read_text(encoding="utf-8")
        self.assertIn("surat-izin-github.md", text)
        self.assertIn("Tom05ivier-commits-1.0", text)
        self.assertIn("hy4-agent-model", text)

    def test_update_all_score_gate(self) -> None:
        from system.update_all import scores_ok

        self.assertTrue(scores_ok({"chip": "OK", "security": "OK"}))
        self.assertFalse(scores_ok({"chip": "OK", "security": "GAGAL"}))
        self.assertFalse(scores_ok({}))

    def test_container_config_polished(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("EXPOSE 8765 8766 8767 8768", dockerfile)
        self.assertIn("AGENTY_DISABLE_TUNNEL=1", dockerfile)
        ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        for pattern in ("src/", "opencode-src/", "surat-*.md", "publish/"):
            self.assertIn(pattern, ignore)
        entrypoint = (ROOT / "docker-entrypoint.sh").read_text(encoding="utf-8")
        self.assertIn("supervise", entrypoint)
        self.assertIn("ENABLE_KERNEL_FIREWALL", entrypoint)
        prod = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn('command: ["supervise"]', prod)
        self.assertIn("system-reports", prod)
        dev = (ROOT / "docker-compose.dev.yml").read_text(encoding="utf-8")
        self.assertIn("8766:8766", dev)
        self.assertIn("AGENTY_BIND_HOST: 0.0.0.0", dev)

    def test_host_chrome_connector_present(self) -> None:
        connector = ROOT / "connect_host_chrome.sh"
        self.assertTrue(connector.exists())
        text = connector.read_text(encoding="utf-8")
        self.assertIn("cdpEndpoint", text)
        self.assertIn("/json/version", text)

    def test_copilot_integration_present(self) -> None:
        instructions = ROOT / ".github" / "copilot-instructions.md"
        launcher = ROOT / "run_copilot.sh"
        bridge = ROOT / "copilot-bridge" / "bridge.py"
        for path in (instructions, launcher, bridge):
            self.assertTrue(path.exists(), f"{path} tidak ada")
        text = instructions.read_text(encoding="utf-8")
        for token in ("Tomi vier", "Tom05ivier-commits-1.0", "hy4-flash-free", "run_always.sh"):
            self.assertIn(token, text)
        self.assertIn("opencode-hy4/hy4-flash-free", launcher.read_text(encoding="utf-8"))

    def test_service_registry_loaded(self) -> None:
        from system.supervisor import load_services

        services = load_services()
        self.assertTrue(
            {"server", "protection", "bridge", "files"}.issubset(
                {item["name"] for item in services}
            )
        )
        self.assertTrue((ROOT / "system" / "services.json").exists())

    def test_supervisor_hot_reload(self) -> None:
        import json as _json
        import tempfile

        import system.supervisor as sup

        with tempfile.TemporaryDirectory() as tmp:
            registry = Path(tmp) / "services.json"
            registry.write_text(
                _json.dumps(
                    {
                        "services": [
                            {
                                "name": "dummy",
                                "kind": "process",
                                "command": ["python3", "-c", "pass"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            original = sup.REGISTRY
            sup.REGISTRY = registry
            try:
                supervisor = sup.Supervisor(interval=1.0)
                supervisor.refresh()
                self.assertEqual(supervisor.names, ["dummy"])
            finally:
                sup.REGISTRY = original

    def test_supervisor_heartbeat(self) -> None:
        from system.supervisor import HEARTBEAT, Supervisor

        supervisor = Supervisor(interval=1.0)
        status = supervisor.heartbeat()
        self.assertIn("services", status)
        self.assertTrue(
            {"server", "protection", "bridge", "files"}.issubset(
                set(status["services"])
            )
        )
        self.assertIn("selalu jalankan komputer", status["rule"])
        self.assertIn("komponen baru", status["rule"])
        self.assertTrue(HEARTBEAT.exists())

    def test_hosts_setup_present(self) -> None:
        hosts = ROOT / "hosts"
        setup = ROOT / "setup-hosts.sh"
        self.assertTrue(hosts.exists() and setup.exists())
        text = hosts.read_text(encoding="utf-8")
        self.assertIn("infinity.local", text)
        self.assertIn("agent.local", text)
        script = setup.read_text(encoding="utf-8")
        self.assertIn("MARK_BEGIN", script)

    def test_docker_files_present(self) -> None:
        dockerfile = ROOT / "Dockerfile"
        compose = ROOT / "docker-compose.yml"
        dev_compose = ROOT / "docker-compose.dev.yml"
        makefile = ROOT / "Makefile"
        env_example = ROOT / ".env.example"
        guide = ROOT / "DOCKER.md"
        cli_check = ROOT / "docker-cli-check.sh"
        capability_setup = ROOT / "capability-setup.sh"
        systemd_unit = ROOT / "systemd" / "infinity-security.service"
        for path in (
            dockerfile,
            compose,
            dev_compose,
            makefile,
            env_example,
            guide,
            cli_check,
            capability_setup,
            systemd_unit,
        ):
            self.assertTrue(path.exists(), f"{path} tidak ada")

        compose_text = compose.read_text(encoding="utf-8")
        dev_text = dev_compose.read_text(encoding="utf-8")
        dockerfile_text = dockerfile.read_text(encoding="utf-8")
        self.assertIn("NET_ADMIN", compose_text)
        self.assertIn("healthcheck", compose_text)
        self.assertIn("mem_limit", compose_text)
        self.assertNotIn("cap_add:", dev_text)
        self.assertIn("iptables", dockerfile_text)
        self.assertIn("locale-gen", dockerfile_text)
        self.assertIn("BIND_HOST", env_example.read_text(encoding="utf-8"))
        self.assertIn("docker-check", makefile.read_text(encoding="utf-8"))
        unit = systemd_unit.read_text(encoding="utf-8")
        self.assertIn("AmbientCapabilities=CAP_NET_ADMIN", unit)
        self.assertIn("CapabilityBoundingSet=CAP_NET_ADMIN", unit)
        self.assertIn("cap_add", capability_setup.read_text(encoding="utf-8"))


    def test_static_sites_present(self) -> None:
        base = ROOT / "site"
        files = (
            base / "server.py",
            base / "index.html",
            base / "README.md",
            base / "chip" / "index.html",
            base / "chip" / "styles.css",
            base / "chip" / "app.js",
            base / "chip" / "simulator.html",
            base / "chip" / "simulator.css",
            base / "chip" / "simulator.js",
            base / "agency" / "index.html",
            base / "mirror" / "index.html",
            base / "mirror" / "fetch.sh",
            base / "mirror_server.py",
            base / "mirror-info.html",
        )
        for path in files:
            self.assertTrue(path.exists(), f"{path} tidak ada")
            head = path.read_text(encoding="utf-8")[:600]
            self.assertIn("Tom05ivier-commits-1.0", head, f"{path} tanpa header SPDX")

    def test_site_service_registered(self) -> None:
        import json as _json

        data = _json.loads((ROOT / "system" / "services.json").read_text(encoding="utf-8"))
        sites = [s for s in data["services"] if s.get("name") == "sites"]
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]["port"], 8769)
        self.assertEqual(sites[0]["kind"], "http")
        self.assertIn("site/server.py", " ".join(sites[0]["command"]))

        mirrors = [s for s in data["services"] if s.get("name") == "mirror"]
        self.assertEqual(len(mirrors), 1)
        self.assertEqual(mirrors[0]["port"], 8770)
        self.assertIn("site/mirror_server.py", " ".join(mirrors[0]["command"]))

    def test_dashboard_links_to_sites(self) -> None:
        content = (ROOT / "dashboard.html").read_text(encoding="utf-8")
        for token in ("Situs &amp; Layanan", "/chip/simulator.html", "/agency/", "8769"):
            self.assertIn(token, content)

    def test_site_port_exposed(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        dev = (ROOT / "docker-compose.dev.yml").read_text(encoding="utf-8")
        self.assertIn("EXPOSE 8765 8766 8767 8768 8769 8770", dockerfile)
        self.assertIn("127.0.0.1:8769:8769", dev)
        self.assertIn("127.0.0.1:8770:8770", dev)

    def test_simulator_component_present(self) -> None:
        script = (ROOT / "site" / "chip" / "simulator.js").read_text(encoding="utf-8")
        for token in ("parseDesign", "parseExpression", "simulate", "renderWave", "PRESETS"):
            self.assertIn(token, script)
        page = (ROOT / "site" / "chip" / "simulator.html").read_text(encoding="utf-8")
        self.assertIn("og:title", page)
        self.assertIn("assets/favicon-32.png", page)

    def test_mirror_offline_assets_and_stub(self) -> None:
        server = (ROOT / "site" / "server.py").read_text(encoding="utf-8")
        self.assertIn("api_stub", server)
        self.assertIn("captcha_enabled", server)
        mirror = (ROOT / "site" / "mirror_server.py").read_text(encoding="utf-8")
        self.assertIn("api_stub=True", mirror)

        pdf = ROOT / "site" / "mirror" / "materi_design_chip_pemula_v1.pdf"
        self.assertTrue(pdf.exists())
        with pdf.open("rb") as fh:
            self.assertEqual(fh.read(5), b"%PDF-")

        for asset in (
            "assets/untuk-siapa-a.png",
            "assets/untuk-siapa-b.png",
            "assets/assets/img/katalog-bleed.webp",
            "assets/fonts/PeruriSans-Regular.woff2",
        ):
            self.assertTrue((ROOT / "site" / "mirror" / asset).exists(), asset)


    def test_chip_installation_assets(self) -> None:
        import json as _json
        import os

        launcher = ROOT / "run_chip.sh"
        self.assertTrue(launcher.exists())
        self.assertTrue(os.access(launcher, os.X_OK), "run_chip.sh tidak bisa dieksekusi")
        self.assertIn("AGENTY_PORT", launcher.read_text(encoding="utf-8"))

        guide = (ROOT / "PASANG-CHIP.md").read_text(encoding="utf-8")
        self.assertIn("chip.localhost", guide)
        self.assertIn("Install app", guide)

        desktop = (ROOT / "chip-merah-putih.desktop").read_text(encoding="utf-8")
        self.assertIn("Exec=/root/workspace/run_chip.sh", desktop)
        self.assertTrue(Path("/usr/share/applications/chip-merah-putih.desktop").exists())

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("chip:", makefile)
        self.assertIn("./run_chip.sh", makefile)

        hosts = (ROOT / "hosts").read_text(encoding="utf-8")
        for alias in ("chip.local", "chip.localhost", "chip-mirror.localhost"):
            self.assertIn(alias, hosts)

        chip = ROOT / "site" / "chip"
        manifest = _json.loads((chip / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["start_url"], "/chip/simulator.html")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(len(manifest["icons"]), 2)
        self.assertIn("navigator.serviceWorker.register", (chip / "app.js").read_text(encoding="utf-8"))
        self.assertIn("navigator.serviceWorker.register", (chip / "simulator.js").read_text(encoding="utf-8"))
        sw = (chip / "sw.js").read_text(encoding="utf-8")
        self.assertIn("caches.open", sw)
        for size in (192, 512):
            icon = chip / "assets" / f"icon-{size}.png"
            self.assertTrue(icon.exists())
            with icon.open("rb") as fh:
                self.assertEqual(fh.read(8), b"\x89PNG\r\n\x1a\n")


    def test_symphony_watcher_waits_for_docker(self) -> None:
        import json

        script = (ROOT / "scripts" / "symphony-deploy.sh").read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits-1.0", script[:300])
        self.assertIn("while true; do", script)
        self.assertIn("MENUNGGU: Docker Engine tidak aktif", script)
        self.assertIn("SYMPHONY_WAIT_SECONDS", script)
        # Wrapper tidak boleh keluar saat Engine belum ada; itu yang dulu
        # menyebabkan supervisor melakukan ribuan restart.
        self.assertNotIn("Docker Engine tidak aktif; Symphony tidak dapat dijalankan", script)

        example = (ROOT / ".env.symphony.example").read_text(encoding="utf-8")
        self.assertIn("SYMPHONY_WAIT_SECONDS", example)

        docs = (ROOT / "docs" / "SYMPHONY-DEPLOYMENT.md").read_text(encoding="utf-8")
        compact = " ".join(docs.split())
        self.assertIn("tetap hidup sebagai penjaga", compact)
        self.assertIn("tidak lagi keluar dengan kode `1`", compact)

        registry = json.loads((ROOT / "system" / "services.json").read_text(encoding="utf-8"))
        symphony = [s for s in registry["services"] if s["name"] == "symphony"][0]
        self.assertEqual(symphony["kind"], "process")
        self.assertNotIn("port", symphony)


if __name__ == "__main__":
    unittest.main(verbosity=2)

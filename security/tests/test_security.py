# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian unit untuk komponen keamanan."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from security.common.authorization import (  # noqa: E402
    AuthorizationError,
    issue_token,
    token_to_env,
)
from security.common.config import EICAR_SIGNATURE  # noqa: E402
from security.blue.antivirus_agent import AntivirusAgent  # noqa: E402
from security.blue.firewall_agent import FirewallAgent  # noqa: E402
from security.blue.dlp import (  # noqa: E402
    exposure_report,
    quarantine_sensitive,
    scan_file,
)
from security.blue.integrity import IntegrityMonitor  # noqa: E402
from security.blue.capabilities import (  # noqa: E402
    bounding_capabilities,
    has_cap_net_admin,
    read_capabilities,
    status as capability_status,
)
from security.blue.policy import FirewallPolicy  # noqa: E402
from security.blue.soc_agent import SOCAgent  # noqa: E402
from security.red.attack_agent import AttackAgent  # noqa: E402
from security.red.modules.scanner import parse_ports  # noqa: E402
from security.red.modules.stress import hardware_stress  # noqa: E402
from security.red.modules.telemetry import capture, diff  # noqa: E402


class AntivirusTests(unittest.TestCase):
    def test_detects_eicar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eicar.bin"
            path.write_bytes(EICAR_SIGNATURE)
            result = AntivirusAgent().scan_file(path)
            self.assertTrue(result.infected)
            self.assertTrue(any(f.evidence.startswith("EICAR") for f in result.findings))

    def test_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "clean.txt"
            path.write_text("hello world", encoding="utf-8")
            result = AntivirusAgent().scan_file(path)
            self.assertFalse(result.infected)


class FirewallTests(unittest.TestCase):
    def test_dry_run_does_not_execute(self) -> None:
        result = FirewallAgent(dry_run=True).block_ip("203.0.113.66")
        self.assertFalse(result.executed)
        self.assertIn("DROP", result.command)

    def test_invalid_ip_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FirewallAgent().block_ip("999.999.999.999")

    def test_dlp_detects_exposure_without_extracting_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("contact: contoh@domain.test", encoding="utf-8")
            result = scan_file(path)
            self.assertTrue(result.findings)
            report = exposure_report([result])
            self.assertGreaterEqual(report["total_exposures"], 1)
            self.assertNotIn("contoh@domain.test", str(report))

    def test_dlp_quarantines_sensitive_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "rahasia.txt"
            source.write_text(
                "password: rahasia123\n", encoding="utf-8"
            )
            result = scan_file(source)
            moved = quarantine_sensitive([result])
            self.assertEqual(len(moved), 1)
            self.assertFalse(source.exists())
            self.assertTrue(Path(moved[0]).exists())

    def test_integrity_detects_modification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "critical.txt"
            path.write_text("original", encoding="utf-8")
            monitor = IntegrityMonitor(
                [path], baseline_path=Path(tmp) / "baseline.json"
            )
            monitor.create_baseline()
            self.assertFalse(monitor.check()["changed"])
            path.write_text("dimodifikasi", encoding="utf-8")
            result = monitor.check()
            self.assertTrue(result["changed"])
            self.assertIn(str(path), result["modified"])

    def test_firewall_installer_present(self) -> None:
        installer = Path(__file__).resolve().parents[1] / "firewall" / "install-net-admin.sh"
        self.assertTrue(installer.exists())
        text = installer.read_text(encoding="utf-8")
        self.assertIn("CAP_NET_ADMIN", text)
        self.assertIn("dry_run=False", text)
        self.assertIn("iptables -S", text)

    def test_capbnd_launcher_present(self) -> None:
        base = Path(__file__).resolve().parents[1] / "firewall"
        launcher = base / "capbnd.sh"
        self.assertTrue(launcher.exists())
        text = launcher.read_text(encoding="utf-8")
        self.assertIn("CapBnd", text)
        self.assertIn("cap_net_admin+eip", text)
        self.assertIn("--cap-add=NET_ADMIN", text)

        setup = base / "setup-capbnd.sh"
        self.assertTrue(setup.exists())
        setup_text = setup.read_text(encoding="utf-8")
        self.assertIn("CapabilityBoundingSet=CAP_NET_ADMIN", setup_text)
        self.assertIn("--dry-run", setup_text)

    def test_capability_status_reports_environment(self) -> None:
        caps = read_capabilities()
        self.assertIn("CapEff", caps)
        self.assertIsInstance(has_cap_net_admin(), bool)
        self.assertIsInstance(bounding_capabilities(), list)
        report = capability_status()
        self.assertIn("bounding_capabilities", report)
        self.assertIn("kernel_enforcement", report)
        self.assertIn("remediation", report)
        self.assertIn(
            report["effective_mode"], ("kernel-iptables", "userspace-policy")
        )

    def test_policy_engine_persists_and_evaluates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.json"
            policy = FirewallPolicy(path)
            policy.block_ip("198.51.100.7")
            policy.deny_port(23)
            reloaded = FirewallPolicy(path)
            self.assertEqual(reloaded.evaluate("198.51.100.7", 22), "DENY")
            self.assertEqual(reloaded.evaluate("192.0.2.10", 23), "DENY")
            self.assertEqual(reloaded.evaluate("192.0.2.10", 80), "ALLOW")
            reloaded.unblock_ip("198.51.100.7")
            self.assertEqual(reloaded.evaluate("198.51.100.7", 22), "ALLOW")


class AuthorizationTests(unittest.TestCase):
    def test_gating_without_token(self) -> None:
        with self.assertRaises(AuthorizationError):
            AttackAgent().recon()

    def test_lab_only_target(self) -> None:
        token = issue_token("test", "unittest", ("lab",), 60)
        agent = AttackAgent(token)
        with self.assertRaises(AuthorizationError):
            agent.malware_attack(target="127.0.0.1")

    def test_token_serialization(self) -> None:
        token = issue_token("t1", "op", ("lab", "127.0.0.1"), 60)
        os.environ["AGENTY_RED_AUTH_TOKEN"] = token_to_env(token)
        self.addCleanup(
            os.environ.pop, "AGENTY_RED_AUTH_TOKEN", None
        )
        from security.common.authorization import AuthorizationToken

        loaded = AuthorizationToken.from_env()
        self.assertEqual(loaded.token_id, "t1")


class UtilityTests(unittest.TestCase):
    def test_parse_ports(self) -> None:
        self.assertEqual(parse_ports("22,80,443"), [22, 80, 443])
        self.assertEqual(parse_ports("80-82"), [80, 81, 82])

    def test_soc_risk_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eicar.bin"
            path.write_bytes(EICAR_SIGNATURE)
            results = [AntivirusAgent().scan_file(path)]
            alerts = SOCAgent().correlate(results)
            self.assertGreater(SOCAgent().risk_score(alerts), 0)

    def test_hardware_stress_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = hardware_stress(
                Path(tmp),
                duration=20.0,   # harus dipotong ke batas maksimal
                memory_mb=999,
                file_count=999,
                socket_count=999,
            )
            self.assertLessEqual(result.metadata["elapsed_seconds"], 4.0)
            self.assertTrue(result.findings)
            cpu = next(f for f in result.findings if f.location == "cpu")
            self.assertLessEqual(cpu.metadata["duration_seconds"], 2.0)
            disk = next(f for f in result.findings if f.location.startswith(str(tmp)))
            self.assertLessEqual(disk.metadata["files"], 20)

    @staticmethod
    def _fake_campaign(tmp: str) -> Path:
        import json as _json

        path = Path(tmp) / "campaign.json"
        debug = {
            "capability": {"effective_mode": "userspace-policy"},
            "policy": {"blocked_ips": 1},
            "integrity": {"changed": True},
        }
        path.write_text(
            _json.dumps(
                {
                    "status": "SELESAI",
                    "times": 3,
                    "risk_score": 48,
                    "debug_before": debug,
                    "debug_after": debug,
                    "response": {
                        "quarantined": ["a"],
                        "policy_decision": "DENY",
                        "risk_score": 48,
                    },
                    "cycles": [
                        {
                            "cycle": i,
                            "attack": {
                                "findings": [
                                    {"type": "SIGNATURE"},
                                    {"type": "HASH"},
                                    {"type": "HEURISTIC"},
                                    {"type": "SUSPICIOUS_ACTIVITY"},
                                ],
                                "metadata": {"telemetry": {"elapsed_seconds": 0.3}},
                            },
                            "debug": debug,
                        }
                        for i in (1, 2, 3)
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_perfect_until_succeeds(self) -> None:
        from security.finalize import perfect_until

        result = perfect_until(max_attempts=2, times=3, intensity="light")
        self.assertEqual(result["status"], "SEMPURNA")
        self.assertGreaterEqual(result["attempts_used"], 1)
        self.assertLessEqual(result["attempts_used"], 2)

    def test_perfect_chain_runs(self) -> None:
        from security.finalize import perfect

        result = perfect(times=3, intensity="light")
        self.assertEqual(result["status"], "SEMPURNA")
        self.assertEqual(result["campaign_cycles"], 3)
        self.assertEqual(result["verification"], "COMPLIANT")
        self.assertEqual(result["final"], "SELESAI")

    def test_github_account_permission_bounded(self) -> None:
        from security.github_account import GitHubAccount

        account = GitHubAccount()
        self.assertIn("repo-list", GitHubAccount.allowlist())
        self.assertTrue(account.letter_valid)
        allowed = account.authorize("repo-list")
        self.assertIn(allowed["status"], ("DIIZINKAN", "DITOLAK"))
        denied = account.authorize("token-export")
        self.assertEqual(denied["status"], "DITOLAK")

    def test_host_actions_allowlist_and_gate(self) -> None:
        from security.host_actions import HostActions

        self.assertNotIn("capbnd", HostActions.allowlist())
        result = HostActions().authorize("capbnd")
        self.assertEqual(result["status"], "DITOLAK")
        denied = HostActions().authorize("unknown")
        self.assertEqual(denied["status"], "DITOLAK")

    def test_auto_config_is_bounded(self) -> None:
        from security.auto_config import apply

        ok = apply("workflow.name", "harian", dry_run=True)
        self.assertEqual(ok["status"], "SIMULASI")
        denied = apply("license.owner", "Tomi vier", dry_run=True)
        self.assertEqual(denied["status"], "DITOLAK")
        bad_value = apply("system.interval", "99999", dry_run=True)
        self.assertEqual(bad_value["status"], "DITOLAK")

    def test_denied_key_license(self) -> None:
        from security.auto_config import apply

        result = apply("license.mode", "pro", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("dilarang", result["reason"].lower())

    def test_denied_key_authorization(self) -> None:
        from security.auto_config import apply

        result = apply("authorization.scope", "unlimited", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("dilarang", result["reason"].lower())

    def test_denied_key_network(self) -> None:
        from security.auto_config import apply

        result = apply("network.public", "true", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("dilarang", result["reason"].lower())

    def test_denied_key_data(self) -> None:
        from security.auto_config import apply

        result = apply("data.export", "true", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("dilarang", result["reason"].lower())

    def test_denied_key_signature(self) -> None:
        from security.auto_config import apply

        result = apply("signature.key", "x", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("dilarang", result["reason"].lower())

    def test_denied_key_unknown(self) -> None:
        from security.auto_config import apply

        result = apply("kunci.asing", "y", dry_run=True)
        self.assertEqual(result["status"], "DITOLAK")
        self.assertIn("lampiran", result["reason"].lower())

    def test_data_delivery_is_gated(self) -> None:
        from security.data_delivery import deliver

        result = deliver("local")
        self.assertEqual(result["status"], "TERKIRIM")
        self.assertTrue(Path(result["file"]).exists())
        denied = deliver("https-plain")
        self.assertEqual(denied["status"], "DITOLAK")

    def test_workflow_runs_with_approval(self) -> None:
        from security.workflow import WorkflowEngine

        engine = WorkflowEngine()
        self.assertIn("harian", engine.names())
        report = engine.run("harian")
        self.assertEqual(
            report["status"],
            "SELESAI",
            f"langkah: {[(s['name'], s['status'], str(s.get('result'))[:200]) for s in report['steps']]}",
        )
        self.assertEqual(len(report["steps"]), 4)
        self.assertTrue(all(step.get("approval_id") for step in report["steps"]))

    def test_auto_approval_is_bounded(self) -> None:
        from security.auto_approval import AutoApproval

        agent = AutoApproval()
        self.assertTrue(agent.valid_meta)
        allowed = agent.approve("verify")
        self.assertTrue(allowed["approved"])
        self.assertIn("expires_at", allowed)
        denied = agent.approve("data-theft")
        self.assertFalse(denied["approved"])
        unlimited = agent.approve("verify", ttl=999999)
        self.assertFalse(unlimited["approved"])
        self.assertIn("tanpa batas", unlimited["reason"])

    def test_clone_automation_is_bounded(self) -> None:
        from security.clone_actions import CloneActions

        agent = CloneActions()
        self.assertTrue(agent.letter_valid)
        ok = agent.authorize("opencode-src")
        self.assertEqual(ok["status"], "DIIZINKAN")
        self.assertIn("git clone", ok["command"])
        self.assertIn("expires_at", ok)
        denied = agent.authorize("arbitrary-url")
        self.assertEqual(denied["status"], "DITOLAK")
        unknown = agent.authorize("unknown-target")
        self.assertEqual(unknown["status"], "DITOLAK")

    def test_finalize_reports_all_requirements(self) -> None:
        from security.finalize import finalize

        result = finalize()
        self.assertIn(result["status"], ("SELESAI", "BELUM LENGKAP"))
        self.assertEqual(len(result["requirements"]), 16)
        self.assertTrue(any(r["requirement"] == "curi data" and r["status"] == "DITOLAK" for r in result["requirements"]))
        self.assertTrue(Path(result["report"]).exists())

    def test_debug_report_from_campaign(self) -> None:
        import tempfile

        import security.debugging as mod

        with tempfile.TemporaryDirectory() as tmp:
            original = mod.CAMPAIGN
            mod.CAMPAIGN = self._fake_campaign(tmp)
            try:
                result = mod.report()
                self.assertEqual(result["status"], "STABIL")
                self.assertEqual(result["siklus"], 3)
                self.assertIn("diff", result)
                self.assertIn("debug_per_siklus", result)
            finally:
                mod.CAMPAIGN = original

    def test_efficacy_reports_campaign(self) -> None:
        import tempfile

        import security.efficacy as mod

        with tempfile.TemporaryDirectory() as tmp:
            original = mod.CAMPAIGN
            original_out = mod.OUTPUT
            mod.CAMPAIGN = self._fake_campaign(tmp)
            mod.OUTPUT = Path(tmp) / "efficacy.json"
            try:
                result = mod.evaluate()
                self.assertEqual(result["status"], "EFEKTIF")
                self.assertEqual(result["actual_cycles"], 3)
                self.assertTrue(mod.OUTPUT.exists())
            finally:
                mod.CAMPAIGN = original
                mod.OUTPUT = original_out

    def test_campaign_runs_full_cycle(self) -> None:
        from security.campaign import run_campaign

        report = run_campaign(times=2, intensity="light")
        self.assertEqual(report["status"], "SELESAI")
        self.assertEqual(len(report["cycles"]), 2)
        self.assertIn("debug_before", report)
        self.assertIn("debug_after", report)
        self.assertIn("response", report)
        self.assertIn("policy_decision", report["response"])
        self.assertGreater(report["risk_score"], 0)
        self.assertIn("pencurian data", report["catatan"].lower())
        self.assertTrue(Path(report["report"]).exists())

    def test_firewall_policy_blocks_agent_port_scan(self) -> None:
        from security.common.authorization import issue_token
        from security.red.attack_agent import AttackAgent

        policy = FirewallPolicy()
        policy.deny_port(65534)
        token = issue_token("policy-test", "unittest", ("lab", "127.0.0.1"), 60)
        result = AttackAgent(token).port_scan("127.0.0.1", "65534,65535")
        self.assertTrue(result.metadata["policy_enforced"])
        self.assertIn(65534, result.metadata["skipped_ports"])
        self.assertNotIn(65534, [f.location.split(":")[-1] for f in result.findings])

    def test_repeated_attack_runs_three_cycles_with_debug(self) -> None:
        token = issue_token("repeat-test", "unittest", ("lab",), 60)
        from security.red.attack_agent import AttackAgent

        cycles = AttackAgent(token).repeated_attack(times=3, intensity="light")
        self.assertEqual(len(cycles), 3)
        self.assertEqual([c["cycle"] for c in cycles], [1, 2, 3])
        for cycle in cycles:
            self.assertIn("attack", cycle)
            self.assertIn("debug", cycle)
            self.assertIn("capability", cycle["debug"])
            self.assertIn("integrity", cycle["debug"])

    def test_telemetry_captures_real_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = capture(tmp)
            self.assertIn("cpu", before)
            self.assertIn("memory", before)
            self.assertIn("disk", before)
            if before["cpu"]:
                after = capture(tmp)
                delta = diff(before, after)
                self.assertIn("cpu_active_delta", delta)
                self.assertGreater(delta["elapsed_seconds"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

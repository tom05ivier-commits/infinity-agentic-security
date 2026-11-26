# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Pengujian alur relai chat tom05-flash-free -> responder (messenger-only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system import chat_dispatch as dispatch  # noqa: E402

GLOBALS = ("REGISTRY", "BASE", "INBOX", "OUTBOX", "PROCESSED", "CLAIMED", "AUDIT")


def registry(responders: list[dict]) -> dict:
    return {
        "schema": "tom05-chat-dispatch-responder-registry/1",
        "defaults": {"timeout_seconds": 10, "max_output_chars": 1000},
        "responders": responders,
    }


class DispatchQueueTests(unittest.TestCase):
    """Uji antrean dengan jalur sementara agar tidak menyentuh data nyata."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.paths = {
            "REGISTRY": root / "config" / "chat_dispatch.json",
            "BASE": root / "reports" / "chat_dispatch",
            "INBOX": root / "reports" / "chat_dispatch" / "inbox",
            "OUTBOX": root / "reports" / "chat_dispatch" / "outbox",
            "PROCESSED": root / "reports" / "chat_dispatch" / "processed",
            "CLAIMED": root / "reports" / "chat_dispatch" / "processing",
            "AUDIT": root / "security" / "reports" / "chat_dispatch.jsonl",
        }
        for key in ("INBOX", "OUTBOX", "PROCESSED", "CLAIMED"):
            self.paths[key].mkdir(parents=True, exist_ok=True)
        self.paths["AUDIT"].parent.mkdir(parents=True, exist_ok=True)
        self._original = {key: getattr(dispatch, key) for key in GLOBALS}
        for key, value in self.paths.items():
            setattr(dispatch, key, value)

    def tearDown(self) -> None:
        for key, value in self._original.items():
            setattr(dispatch, key, value)
        self.tmp.cleanup()

    def write_registry(self, responders: list[dict]) -> None:
        path = self.paths["REGISTRY"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(registry(responders)), encoding="utf-8")

    def audit_rows(self) -> list[dict]:
        path = self.paths["AUDIT"]
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_send_is_messenger_only(self) -> None:
        ack = dispatch.send("Periksa status sistem")
        self.assertEqual(ack["status"], "TERKIRIM")
        self.assertEqual(ack["executor"], "responders (bukan tom05)")
        self.assertEqual(len(list(self.paths["INBOX"].glob("*.json"))), 1)
        # Mengirim tidak boleh langsung menulis hasil/audit.
        self.assertEqual(list(self.paths["OUTBOX"].glob("*.json")), [])
        self.assertEqual(self.audit_rows(), [])
        envelope = json.loads(next(self.paths["INBOX"].glob("*.json")).read_text(encoding="utf-8"))
        self.assertEqual(envelope["sender"], "tom05/tom05-flash-free")
        self.assertEqual(envelope["role"], "messenger-only")

    def test_auto_send_enqueues_with_messenger_role(self) -> None:
        ack = dispatch.auto_send("status sistem otomatis")
        self.assertEqual(ack["status"], "TERKIRIM")
        self.assertTrue(ack["auto"])
        self.assertEqual(ack["source"], "tom05-chat")
        envelope = json.loads(
            next(self.paths["INBOX"].glob("*.json")).read_text(encoding="utf-8")
        )
        self.assertEqual(envelope["role"], "messenger-only")
        self.assertEqual(envelope["message"], "status sistem otomatis")

    def test_auto_send_skips_inside_responder_and_when_disabled(self) -> None:
        previous_task = os.environ.get("AGENTY_CHAT_TASK")
        previous_auto = os.environ.get("TOM05_AUTO_DISPATCH")
        try:
            os.environ["AGENTY_CHAT_TASK"] = "dari responder"
            self.assertEqual(dispatch.auto_send("jangan diulang")["status"], "DILEWATI")
            os.environ.pop("AGENTY_CHAT_TASK", None)
            os.environ["TOM05_AUTO_DISPATCH"] = "0"
            self.assertEqual(dispatch.auto_send("dimatikan")["status"], "DILEWATI")
            self.assertEqual(list(self.paths["INBOX"].glob("*.json")), [])
        finally:
            os.environ.pop("AGENTY_CHAT_TASK", None)
            os.environ.pop("TOM05_AUTO_DISPATCH", None)
            if previous_task is not None:
                os.environ["AGENTY_CHAT_TASK"] = previous_task
            if previous_auto is not None:
                os.environ["TOM05_AUTO_DISPATCH"] = previous_auto

    def test_sanitize_rejects_empty_control_chars_and_oversize(self) -> None:
        self.assertEqual(dispatch.sanitize_message("  aman  "), "aman")
        with self.assertRaises(ValueError):
            dispatch.sanitize_message("   ")
        with self.assertRaises(ValueError):
            dispatch.sanitize_message("a\x00b")
        with self.assertRaises(ValueError):
            dispatch.sanitize_message("x" * (dispatch.MAX_MESSAGE_CHARS + 1))

    def test_all_responders_run_and_audit_written_once(self) -> None:
        self.write_registry([
            {"name": "satu", "kind": "agent", "command": [sys.executable, "-c", "print('satu')"]},
            {"name": "dua", "kind": "cli", "command": [sys.executable, "-c", "print('dua')"]},
        ])
        dispatch.send("tugas gabungan")
        results = dispatch.run_pending()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "SELESAI")
        self.assertEqual(results[0]["ringkasan"], {"total_responder": 2, "berhasil": 2, "gagal": 0})
        self.assertEqual(len(self.audit_rows()), 1)
        self.assertEqual(len(list(self.paths["OUTBOX"].glob("*.json"))), 1)
        self.assertEqual(len(list(self.paths["PROCESSED"].glob("*.json"))), 1)
        self.assertEqual(list(self.paths["INBOX"].glob("*.json")), [])

    def test_atomic_claim_prevents_duplicate_execution(self) -> None:
        """Regresi race: daemon dan `run` manual tidak boleh menjalankan pesan sama."""
        self.write_registry([
            {"name": "satu", "kind": "agent", "command": [sys.executable, "-c", "print('dijalankan')"]},
        ])
        dispatch.send("tugas race")
        inbox_file = next(self.paths["INBOX"].glob("*.json"))
        # Simulasikan daemon memenangkan klaim lebih dulu.
        os.rename(inbox_file, self.paths["CLAIMED"] / inbox_file.name)
        claimed = dispatch.process_message(inbox_file)
        self.assertEqual(claimed["status"], "SKIP")
        self.assertEqual(self.audit_rows(), [])
        self.assertEqual(list(self.paths["OUTBOX"].glob("*.json")), [])

    def test_failed_responder_recorded_once_and_not_retried(self) -> None:
        self.write_registry([
            {"name": "gagal", "kind": "cli", "command": [sys.executable, "-c", "import sys; sys.exit(3)"]},
        ])
        dispatch.send("tugas gagal")
        first = dispatch.run_pending()
        self.assertEqual(first[0]["status"], "GAGAL")
        second = dispatch.run_pending()
        self.assertEqual(second, [])
        self.assertEqual(len(self.audit_rows()), 1)
        self.assertEqual(len(list(self.paths["PROCESSED"].glob("*.json"))), 1)

    def test_stale_claim_recovered_fresh_claim_kept(self) -> None:
        self.write_registry([
            {"name": "satu", "kind": "cli", "command": [sys.executable, "-c", "print('ok')"]},
        ])
        stale = self.paths["CLAIMED"] / "stale.json"
        fresh = self.paths["CLAIMED"] / "fresh.json"
        stale.write_text("{}", encoding="utf-8")
        fresh.write_text("{}", encoding="utf-8")
        old = time.time() - (dispatch.STALE_CLAIM_SECONDS + 60)
        os.utime(stale, (old, old))
        self.assertEqual(dispatch.recover_stale_claims(), 1)
        self.assertTrue((self.paths["INBOX"] / "stale.json").exists())
        self.assertTrue(fresh.exists())

    def test_task_available_to_all_responders(self) -> None:
        self.write_registry([
            {
                "name": "env-task",
                "kind": "tool",
                "command": [sys.executable, "-c", "import os; print(os.environ['AGENTY_CHAT_TASK'])"],
            },
            {
                "name": "argv-task",
                "kind": "docker",
                "command": [sys.executable, "-c", "import sys; print(sys.argv[1])", "{task}"],
            },
        ])
        dispatch.send("tugas khusus ${HOME}; rm -rf /")
        result = dispatch.run_pending()[0]
        self.assertEqual(result["status"], "SELESAI")
        for answer in result["responder"]:
            self.assertIn("tugas khusus", answer["output"])
            self.assertNotIn("rm -rf", answer["command"][0])

    def test_no_port_env_leaks_to_responder(self) -> None:
        self.write_registry([
            {
                "name": "port-check",
                "kind": "cli",
                "command": [sys.executable, "-c", "import os; print('PORT' in os.environ)"],
            },
        ])
        previous = os.environ.pop("PORT", None)
        try:
            os.environ["PORT"] = "9999"
            dispatch.send("cek PORT")
            result = dispatch.run_pending()[0]
            self.assertEqual(result["responder"][0]["output"].strip(), "False")
        finally:
            os.environ.pop("PORT", None)
            if previous is not None:
                os.environ["PORT"] = previous


class DispatchContractTests(unittest.TestCase):
    """Uji kontrak registri nyata dan integrasi CLI."""

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(ROOT / "tom05"), *args], capture_output=True, text=True,
            cwd=str(ROOT), timeout=120,
        )

    def test_registry_covers_all_responder_kinds(self) -> None:
        data = json.loads((ROOT / "config" / "chat_dispatch.json").read_text(encoding="utf-8"))
        kinds = {item["kind"] for item in data["responders"]}
        self.assertTrue({"agent", "cli", "skill", "tool", "docker"}.issubset(kinds))
        self.assertGreaterEqual(len(data["responders"]), 11)
        self.assertEqual(data["sender"]["role"], "messenger-only")
        for item in data["responders"]:
            command = item["command"]
            self.assertIsInstance(command, list)
            self.assertTrue(command)
            # Dilarang shell interpolation; perintah harus argv langsung.
            self.assertNotIn("-c", command[:2])
            for part in command:
                self.assertNotIn("$(", str(part))
            for candidate in command:
                if str(candidate).endswith(".py") and not str(candidate).startswith("-"):
                    self.assertTrue((ROOT / str(candidate)).exists(), candidate)

    def test_registry_is_licensed(self) -> None:
        data = (ROOT / "config" / "chat_dispatch.json").read_text(encoding="utf-8")
        self.assertIn("Tom05ivier-commits-1.0", data)
        self.assertIn("Copyright (c) 2026 Tomi vier", data)

    def test_cli_flags_and_wrapper(self) -> None:
        wrapper = ROOT / "chat-dispatch.sh"
        self.assertTrue(wrapper.exists())
        self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", wrapper.read_text()[:400])
        done = self.run_cli("--dispatch-status")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["status"], "AKTIF")
        self.assertEqual(data["sender_role"], "messenger-only")
        self.assertGreaterEqual(len(data["responder"]), 11)

    def test_cli_dispatch_forwards_targets_and_message(self) -> None:
        """Regresi: `--to` tidak boleh ditelan sebagai pesan (bug wrapper lama)."""
        message = "uji regresi --to lewat wrapper tom05"
        done = self.run_cli("--dispatch", message, "--to", "cli-parity,docker-verify")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["status"], "TERKIRIM")
        self.assertEqual(data["message_chars"], len(message))
        self.assertEqual(data["targets"], ["cli-parity", "docker-verify"])
        self.assertEqual(data["executor"], "responders (bukan tom05)")

    def test_cli_auto_dispatch_wiring(self) -> None:
        script = (ROOT / "tom05").read_text(encoding="utf-8")
        self.assertIn("--no-dispatch", script)
        self.assertIn("auto-send", script)
        self.assertIn("Pemicu otomatis", script)
        done = self.run_cli("--help")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("--no-dispatch", done.stdout)
        self.assertIn("otomatis relay", done.stdout)

    def test_supervisor_registers_daemon(self) -> None:
        services = json.loads((ROOT / "system" / "services.json").read_text(encoding="utf-8"))
        names = {item["name"] for item in services["services"]}
        self.assertIn("chat-dispatch", names)
        entry = next(item for item in services["services"] if item["name"] == "chat-dispatch")
        self.assertEqual(entry["command"][-1], "daemon")

    def test_documentation_exists(self) -> None:
        doc = (ROOT / "docs" / "CHAT-DISPATCH.md")
        self.assertTrue(doc.exists())
        text = doc.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: Tom05ivier-commits-1.0", text[:400])
        self.assertIn("messenger-only", text)


if __name__ == "__main__":
    unittest.main()

# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""CLI terpadu untuk Infinity Security Suite.

Contoh:
    python3 security_cli.py hardware
    python3 security_cli.py protect
    python3 security_cli.py av scan security/lab
    python3 security_cli.py firewall block-ip 203.0.113.66
    python3 security_cli.py red issue-token --minutes 5
    AGENTY_RED_AUTH_TOKEN='...' python3 security_cli.py red drill
    python3 security_cli.py drill
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

# Pastikan paket `security` dapat diimpor dari lokasi mana pun.
_WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from security.common.authorization import issue_token, token_to_env  # noqa: E402
from security.common.config import (  # noqa: E402
    EICAR_SIGNATURE,
    LAB_ROOT,
    SIGNATURE_DIR,
    ensure_dirs,
)
from security.blue.antivirus_agent import AntivirusAgent  # noqa: E402
from security.blue.defense_agent import DefenseAgent  # noqa: E402
from security.blue.firewall_agent import FirewallAgent  # noqa: E402
from security.blue.hardware_agent import HardwareAgent  # noqa: E402
from security.blue.soc_agent import SOCAgent  # noqa: E402
from security.red.attack_agent import AttackAgent  # noqa: E402


def _print(data: object) -> None:
    try:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    except BrokenPipeError:
        # Pemipaan ke `head` tidak dianggap kegagalan.
        try:
            sys.stdout.close()
        except OSError:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="security_cli.py",
        description="Infinity Security Suite — laboratorium keamanan",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("hardware", help="Tampilkan inventaris hardware")
    sub.add_parser("protect", help="Lindungi hardware (baseline firewall + AV)")

    fw = sub.add_parser("firewall", help="Kelola aturan firewall")
    fw_sub = fw.add_subparsers(dest="fw_command", required=True)
    fw_sub.add_parser("list", help="Tampilkan aturan (dry run)")
    fw_sub.add_parser("debug", help="Diagnostik backend firewall")
    fw_sub.add_parser("policy", help="Tampilkan kebijakan firewall userspace")
    fw_sub.add_parser(
        "capability", help="Cek CAP_NET_ADMIN & kesiapan firewall kernel"
    )
    fw_block = fw_sub.add_parser("block-ip", help="Blokir alamat IP")
    fw_block.add_argument("ip")
    fw_port = fw_sub.add_parser("deny-port", help="Tolong port")
    fw_port.add_argument("port", type=int)

    av = sub.add_parser("av", help="Antivirus")
    av_sub = av.add_subparsers(dest="av_command", required=True)
    av_scan = av_sub.add_parser("scan", help="Pindai berkas/direktori")
    av_scan.add_argument("path")

    sub.add_parser("soc", help="Buat laporan SOC dari hasil pemindaian lab")
    dlp = sub.add_parser("dlp", help="Deteksi/cegah paparan data sensitif (DLP)")
    dlp.add_argument("path", nargs="?", default=None)
    dlp.add_argument(
        "--protect", action="store_true", help="Karantina berkas sensitif"
    )
    sub.add_parser(
        "authorization",
        help="Tampilkan kebijakan otorisasi (selalu terbatas & berakhir)",
    )
    integrity = sub.add_parser("integrity", help="Cek integritas berkas kritis")
    integrity.add_argument(
        "--reset", action="store_true", help="Perbarui baseline hash"
    )

    red = sub.add_parser("red", help="Agen ofensif tersah")
    red_sub = red.add_subparsers(dest="red_command", required=True)
    issue = red_sub.add_parser("issue-token", help="Terbitkan token otorisasi")
    issue.add_argument("--minutes", type=int, default=5)
    issue.add_argument("--operator", default="operator-lab")
    red_sub.add_parser("recon", help="Rekonesan hardware")
    scan = red_sub.add_parser("scan", help="Pindai port localhost")
    scan.add_argument("--target", default="127.0.0.1")
    scan.add_argument("--ports", default="22,80,443,8080")
    red_sub.add_parser("attack", help="Simulasi serangan malware ke lab")
    severe = red_sub.add_parser("severe", help="Serangan serius ke hardware")
    severe.add_argument(
        "--intensity",
        choices=("light", "moderate", "severe"),
        default="moderate",
    )
    repeat = red_sub.add_parser("repeat", help="Ulangi serangan dengan debug tiap siklus")
    repeat.add_argument("--times", type=int, default=3)
    repeat.add_argument(
        "--intensity",
        choices=("light", "moderate", "severe"),
        default="moderate",
    )
    red_sub.add_parser("weak-config", help="Cek konfigurasi lemah")
    red_sub.add_parser("drill", help="Jalankan semua simulasi serangan")

    sub.add_parser(
        "drill",
        help="Latihan penuh: lindungi hardware → serang lab → respons insiden",
    )
    sub.add_parser("debug", help="Diagnostik sistem keamanan")
    privacy = sub.add_parser("privacy", help="Deteksi/samarkan data pribadi")
    privacy.add_argument(
        "action",
        choices=("scan", "redact", "sanitize", "secrets", "verify", "release"),
    )
    privacy.add_argument("path", nargs="?", default=".")

    firewall_drill = sub.add_parser(
        "firewall-drill", help="Serang & lindungi hardware/software sampai berhasil"
    )
    firewall_drill.add_argument("--max", type=int, default=3)
    firewall_drill.add_argument(
        "--intensity", choices=("light", "moderate", "severe"), default="moderate"
    )

    sub.add_parser("verify", help="Verifikasi kepatuhan objective")
    score_cmd = sub.add_parser(
        "score", help="Skor keamanan terpadu 0–100 (kontrol terverifikasi)"
    )
    score_cmd.add_argument("--json", action="store_true")
    sub.add_parser("efficacy", help="Nilai efikasi pertahanan pasca-kampanye")
    doctor = sub.add_parser(
        "copilot-doctor", help="Diagnostik Copilot CLI + bridge"
    )
    doctor.add_argument("--smoke", action="store_true")
    sub.add_parser("debug-report", help="Laporan debugging sebelum/sesudah serangan")
    sub.add_parser("finalize", help="Laporan penyelesaian terpadu objective")
    sempurna = sub.add_parser(
        "sempurnakan", help="Jalankan seluruh rantai penyempurnaan dari awal"
    )
    sempurna.add_argument("--times", type=int, default=3)
    sempurna.add_argument(
        "--intensity", choices=("light", "moderate", "severe"), default="moderate"
    )
    gh = sub.add_parser("github-allow", help="Verifikasi izin aksi GitHub")
    gh.add_argument(
        "action",
        choices=(
            "repo-list", "repo-read", "repo-create", "repo-push", "repo-status",
            "token-export", "repo-delete",
        ),
    )
    sub.add_parser("github-actions", help="Daftar aksi GitHub yang diizinkan")
    sub.add_parser("github-ready", help="Cek kesiapan izin & token GitHub")
    sub.add_parser("github-repos", help="Daftar repo akun (hanya nama)")
    host = sub.add_parser("host-allow", help="Verifikasi izin aksi host")
    host.add_argument("action", choices=("capbnd", "firewall", "docker", "publish", "systemd"))
    sub.add_parser("host-actions", help="Tampilkan daftar aksi host yang diizinkan")
    sub.add_parser("host-ready", help="Cek kesiapan host tanpa membocorkan kredensial")
    clone = sub.add_parser("clone-allow", help="Verifikasi izin klon otomatis")
    clone.add_argument("action", choices=("opencode-src", "chromium-src", "hy4-repo"))
    sub.add_parser("clone-actions", help="Daftar target klon otomatis yang diizinkan")
    sub.add_parser("clone-ready", help="Cek kesiapan izin klon otomatis")
    sub.add_parser("clone-history", help="Riwayat persetujuan klon otomatis")
    config_cmd = sub.add_parser(
        "auto-config", help="Terapkan konfigurasi otomatis terbatas"
    )
    config_cmd.add_argument("key")
    config_cmd.add_argument("value")
    config_cmd.add_argument("--dry-run", action="store_true")
    deliver = sub.add_parser("deliver", help="Kirim laporan ringkas ke pemilik")
    deliver.add_argument(
        "--channel",
        choices=("local", "webhook"),
        default=os.environ.get("AGENTY_DELIVERY_CHANNEL", "local"),
    )
    workflow = sub.add_parser("workflow", help="Jalankan alur kerja otomatis")
    workflow.add_argument("action", choices=("list", "run", "history", "daemon"))
    workflow.add_argument("--name", default="harian")
    workflow.add_argument("--interval", type=float, default=86400)
    auto = sub.add_parser(
        "auto-approve", help="Terbitkan izin otomatis sesuai meta-izin"
    )
    auto.add_argument("task", help="kategori tugas")
    auto.add_argument("--ttl", type=int, default=300)
    sub.add_parser("auto-approvals", help="Tampilkan riwayat izin otomatis")
    ulangi = sub.add_parser(
        "ulangi-sempurna", help="Ulangi serangan sampai status SEMPURNA"
    )
    ulangi.add_argument("--max", type=int, default=5)
    ulangi.add_argument("--times", type=int, default=3)
    campaign = sub.add_parser(
        "campaign", help="Kampanye lengkap: protect → debug → serang 3x → respons"
    )
    campaign.add_argument("--times", type=int, default=3)
    campaign.add_argument(
        "--intensity",
        choices=("light", "moderate", "severe"),
        default="moderate",
    )
    monitor = sub.add_parser("monitor", help="Antivirus real-time pada lab")
    monitor.add_argument("--seconds", type=float, default=5.0)
    monitor.add_argument("--interval", type=float, default=0.5)
    sub.add_parser(
        "live-drill",
        help="Serangan serius saat antivirus real-time aktif",
    )
    sub.add_parser("lab", help="Inisialisasi/ulang data laboratorium")
    keygen = sub.add_parser(
        "api-keygen", help="Pembangkit kunci API aman (nilai tidak dicetak)"
    )
    keygen.add_argument("keygen_args", nargs=argparse.REMAINDER)
    billing = sub.add_parser(
        "billing", help="Panduan & gerbang tagihan Copilot CLI (tanpa pembayaran)"
    )
    billing.add_argument(
        "billing_action",
        choices=("guide", "status", "authorize", "record", "history"),
    )
    billing.add_argument("value", nargs="?", default="")
    return parser


def _attack_agent_from_env() -> AttackAgent:
    from security.common.authorization import AuthorizationToken

    agent = AttackAgent()
    agent.authorize(AuthorizationToken.from_env())
    return agent


def main(argv: list[str] | None = None) -> int:
    ensure_dirs()
    args = build_parser().parse_args(argv)

    if args.command == "hardware":
        _print(HardwareAgent().report())

    elif args.command == "protect":
        _print(DefenseAgent().protect_hardware())

    elif args.command == "firewall":
        agent = FirewallAgent()
        if args.fw_command == "list":
            _print(agent.list_rules().to_dict())
        elif args.fw_command == "policy":
            from security.blue.policy import FirewallPolicy

            _print(FirewallPolicy().rules)
        elif args.fw_command == "capability":
            from security.blue.capabilities import status

            _print(status())
        elif args.fw_command == "debug":
            from security.blue.capabilities import status
            from security.blue.policy import FirewallPolicy

            capability = status()
            _print(
                {
                    "backend": agent.backend,
                    "dry_run": agent.dry_run,
                    "effective_mode": capability["effective_mode"],
                    "cap_net_admin": capability["cap_net_admin"],
                    "can_gain": capability["can_gain"],
                    "kernel_enforcement": capability["kernel_enforcement"],
                    "policy": FirewallPolicy().summary(),
                    "capabilities": capability["capabilities"],
                    "reason": capability["remediation"],
                }
            )
        elif args.fw_command == "block-ip":
            _print(agent.block_ip(args.ip).to_dict())
        elif args.fw_command == "deny-port":
            _print(agent.deny_port(args.port).to_dict())

    elif args.command == "av":
        if args.av_command == "scan":
            target = Path(args.path)
            av = AntivirusAgent()
            results = (
                av.scan_directory(target) if target.is_dir() else [av.scan_file(target)]
            )
            _print([r.to_dict() for r in results])

    elif args.command == "soc":
        av = AntivirusAgent()
        results = av.scan_directory(LAB_ROOT)
        alerts = SOCAgent().correlate(results)
        _print({"alerts": [a.to_dict() for a in alerts]})

    elif args.command == "dlp":
        from security.blue.dlp import (
            exposure_report,
            quarantine_sensitive,
            scan_paths,
        )

        target = Path(args.path) if args.path else LAB_ROOT
        if not target.is_absolute():
            target = (Path.cwd() / target).resolve()
        results = scan_paths([target])
        moved = quarantine_sensitive(results) if args.protect else []
        _print(
            {
                "report": exposure_report(results),
                "quarantined": moved,
                "findings": [r.to_dict() for r in results if r.findings],
            }
        )

    elif args.command == "authorization":
        from security.common.authorization import ALLOWED_TARGETS  # type: ignore

        _print(
            {
                "prinsip": "Otorisasi selalu terbatas, berlaku, dan dapat dicabut.",
                "target_diizinkan": list(ALLOWED_TARGETS),
                "durasi_maksimum_detik": 300,
                "izin_tanpa_batas": "TIDAK disediakan — bertentangan dengan surat izin.",
                "pencurian_data": "TIDAK disediakan — hanya deteksi kebocoran (DLP).",
                "dasar": "surat-izin-keamanan.md / surat-kuasa-tandatangan.md",
            }
        )

    elif args.command == "integrity":
        from security.blue.integrity import IntegrityMonitor

        monitor = IntegrityMonitor()
        if args.reset:
            path = monitor.create_baseline()
            _print({"baseline": str(path), "files": len(monitor.snapshot())})
        else:
            _print(monitor.check())

    elif args.command == "red":
        if args.red_command == "issue-token":
            token = issue_token(
                token_id=f"lab-{hashlib.sha256(str(args.minutes).encode()).hexdigest()[:8]}",
                issued_by=args.operator,
                duration_seconds=args.minutes * 60,
            )
            print(token_to_env(token))
        else:
            agent = _attack_agent_from_env()
            if args.red_command == "recon":
                _print(agent.recon().to_dict())
            elif args.red_command == "scan":
                _print(agent.port_scan(args.target, args.ports).to_dict())
            elif args.red_command == "attack":
                _print(agent.malware_attack().to_dict())
            elif args.red_command == "severe":
                _print(agent.severe_attack(args.intensity).to_dict())
            elif args.red_command == "repeat":
                _print(agent.repeated_attack(args.times, args.intensity))
            elif args.red_command == "weak-config":
                _print(agent.weak_config_check().to_dict())
            elif args.red_command == "drill":
                _print([r.to_dict() for r in agent.full_drill()])

    elif args.command == "drill":
        defense = DefenseAgent()
        protection = defense.protect_hardware()
        token = issue_token(
            token_id="full-drill",
            issued_by="security_cli",
            allowed_targets=("lab", "127.0.0.1"),
            duration_seconds=300,
        )
        attack = AttackAgent(token)
        results = attack.full_drill()
        response = defense.respond_to_attack(results)
        _print(
            {
                "protection": protection,
                "attack": [r.to_dict() for r in results],
                "response": response,
            }
        )

    elif args.command == "debug":
        checks: dict[str, object] = {}
        issues: list[str] = []

        checks["python"] = sys.version.split()[0]
        from security.common import config as cfg

        directories = {
            "logs": cfg.LOG_DIR,
            "reports": cfg.REPORT_DIR,
            "quarantine": cfg.QUARANTINE_DIR,
            "lab": cfg.LAB_ROOT,
            "signatures": cfg.SIGNATURE_DIR,
        }
        ensure_dirs()
        for name, directory in directories.items():
            writable = os.access(directory, os.W_OK)
            checks[f"writable:{name}"] = writable
            if not writable:
                issues.append(f"Direktori {directory} tidak dapat ditulis")

        backend = FirewallAgent().backend
        from security.blue.capabilities import status
        from security.blue.policy import FirewallPolicy

        capability = status()
        checks["firewall_backend"] = backend
        checks["firewall_available"] = capability["backend_available"]
        checks["cap_net_admin"] = capability["cap_net_admin"]
        checks["cap_net_admin_gainable"] = capability["can_gain"]
        checks["firewall_policy"] = FirewallPolicy().summary()
        checks["firewall_mode"] = capability["effective_mode"]
        checks["firewall_note"] = capability["remediation"]

        try:
            from security.common.authorization import AuthorizationToken

            token = AuthorizationToken.from_env()
            checks["authorization"] = f"valid ({token.token_id})"
        except Exception as exc:  # noqa: BLE001
            checks["authorization"] = f"invalid: {exc}"
            issues.append("Token otorisasi red-team tidak valid atau tidak ada")

        try:
            from security.blue.hardware_agent import HardwareAgent

            interfaces = HardwareAgent().network_interfaces()
            checks["hardware_interfaces"] = len(interfaces)
            if not interfaces:
                issues.append("Tidak ada antarmuka hardware yang terdeteksi")
        except Exception as exc:  # noqa: BLE001
            checks["hardware_error"] = str(exc)
            issues.append("Gagal membaca inventaris hardware")

        checks["issues"] = issues
        checks["status"] = "OK" if not issues else "DEGRADED"
        _print(checks)

    elif args.command == "privacy":
        import importlib.util

        path = Path(__file__).resolve().parents[1] / "security" / "privacy.py"
        spec = importlib.util.spec_from_file_location("privacy_guard", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        target = Path(args.path)
        if not target.is_absolute():
            target = (Path.cwd() / target).resolve()
        if args.action == "sanitize":
            _print(module.sanitize_tree(target))
        elif args.action == "verify":
            _print(module.verify_tree(target))
        elif args.action == "release":
            _print(module.release_ready(target))
        elif args.action == "secrets":
            text = target.read_text(encoding="utf-8", errors="ignore") if target.is_file() else str(target)
            _print(module.scan_secrets(text))
        else:
            text = target.read_text(encoding="utf-8", errors="ignore") if target.is_file() else str(target)
            _print(module.scan(text) if args.action == "scan" else module.redact(text))

    elif args.command == "firewall-drill":
        from security.firewall_drill import run_until_success

        report = run_until_success(args.max, args.intensity)
        _print(
            {
                "status": report["status"],
                "attempts": report["attempts"],
                "criteria": report["criteria"],
                "failed": report["failed"],
                "report": "security/reports/firewall_drill.json",
            }
        )

    elif args.command == "verify":
        from security.verify import ComplianceVerifier

        _print(ComplianceVerifier().run())

    elif args.command == "campaign":
        from security.campaign import run_campaign

        _print(run_campaign(args.times, args.intensity))

    elif args.command == "efficacy":
        from security.efficacy import evaluate

        _print(evaluate())

    elif args.command == "copilot-doctor":
        import importlib.util

        path = Path(__file__).resolve().parents[1] / "copilot-bridge" / "doctor.py"
        spec = importlib.util.spec_from_file_location("copilot_doctor", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        _print(module.diagnose(args.smoke))

    elif args.command == "debug-report":
        from security.debugging import report

        _print(report())

    elif args.command == "finalize":
        from security.finalize import finalize

        _print(finalize())

    elif args.command == "sempurnakan":
        from security.finalize import perfect

        _print(perfect(args.times, args.intensity))

    elif args.command == "github-allow":
        from security.github_account import GitHubAccount

        _print(GitHubAccount().authorize(args.action))

    elif args.command == "github-actions":
        from security.github_account import GitHubAccount

        _print(GitHubAccount.allowlist())

    elif args.command == "github-ready":
        from security.github_account import GitHubAccount

        _print(GitHubAccount().ready())

    elif args.command == "github-repos":
        from security.github_account import GitHubAccount

        _print(GitHubAccount().list_repos())

    elif args.command == "host-allow":
        from security.host_actions import HostActions

        _print(HostActions().authorize(args.action))

    elif args.command == "host-actions":
        from security.host_actions import HostActions

        _print(HostActions.allowlist())

    elif args.command == "host-ready":
        from security.host_actions import HostActions

        _print(HostActions.readiness())

    elif args.command == "auto-config":
        from security.auto_config import apply

        _print(apply(args.key, args.value, args.dry_run))

    elif args.command == "deliver":
        from security.auto_approval import AutoApproval
        from security.data_delivery import deliver

        approval = AutoApproval().approve("delivery")
        if not approval["approved"]:
            _print({"status": "DITOLAK", "reason": approval["reason"]})
        else:
            _print(deliver(args.channel))

    elif args.command == "workflow":
        from security.workflow import WorkflowEngine, daemon

        engine = WorkflowEngine()
        if args.action == "list":
            _print(engine.names())
        elif args.action == "run":
            _print(engine.run(args.name))
        elif args.action == "history":
            _print(engine.history())
        elif args.action == "daemon":
            daemon(args.name, args.interval)

    elif args.command == "clone-allow":
        from security.clone_actions import CloneActions

        _print(CloneActions().authorize(args.action))

    elif args.command == "clone-actions":
        from security.clone_actions import CloneActions

        _print(CloneActions.allowlist())

    elif args.command == "clone-ready":
        from security.clone_actions import CloneActions

        _print(CloneActions().readiness())

    elif args.command == "clone-history":
        from security.clone_actions import CloneActions

        _print(CloneActions.history())

    elif args.command == "auto-approve":
        from security.auto_approval import AutoApproval

        _print(AutoApproval().approve(args.task, args.ttl))

    elif args.command == "auto-approvals":
        from security.auto_approval import AutoApproval

        _print(AutoApproval.history())

    elif args.command == "ulangi-sempurna":
        from security.finalize import perfect_until

        _print(perfect_until(args.max, args.times))

    elif args.command == "monitor":
        from security.blue.monitor import FileMonitor

        monitor = FileMonitor(LAB_ROOT, interval=args.interval)
        monitor.run(args.seconds)
        _print(monitor.report())

    elif args.command == "live-drill":
        from security.blue.monitor import FileMonitor

        monitor = FileMonitor(LAB_ROOT, interval=0.25)
        thread: threading.Thread = monitor.start(seconds=10)
        token = issue_token(
            token_id="live-drill",
            issued_by="security_cli",
            allowed_targets=("lab", "127.0.0.1"),
            duration_seconds=60,
        )
        attack = AttackAgent(token)
        results = [attack.severe_attack("moderate")]
        time.sleep(1.5)
        monitor.stop()
        thread.join(timeout=3)
        monitor.poll_once()
        response = DefenseAgent().respond_to_attack(results)
        _print(
            {
                "attack": [r.to_dict() for r in results],
                "monitor": monitor.report(),
                "response": response,
            }
        )

    elif args.command == "lab":
        lab_payloads = LAB_ROOT / "payloads"
        lab_payloads.mkdir(parents=True, exist_ok=True)
        eicar = lab_payloads / "eicar_test.bin"
        eicar.write_bytes(EICAR_SIGNATURE)
        (lab_payloads / "sample_suspicious.py").write_text(
            "# SPDX-License-Identifier: Tom05ivier-commits-1.0\n"
            "# Copyright (c) 2026 Tomi vier\n"
            "# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.\n"
            "# UJI JINAK: os.system( subprocess.Popen( base64.b64decode( socket.socket(\n",
            encoding="utf-8",
        )
        sig = SIGNATURE_DIR / "malware_hashes.txt"
        digest = hashlib.sha256(EICAR_SIGNATURE).hexdigest()
        header = (
            "# SPDX-License-Identifier: Tom05ivier-commits-1.0\n"
            "# Copyright (c) 2026 Tomi vier\n"
        )
        sig.write_text(
            header + f"{digest}  eicar-test-file\n", encoding="utf-8"
        )
        _print({"lab_ready": True, "eicar_sha256": digest})

    elif args.command == "score":
        from security.score import main as score_main

        return score_main(["--json"] if args.json else [])

    elif args.command == "api-keygen":
        from system.api_keygen import main as keygen_main

        return keygen_main(args.keygen_args)

    elif args.command == "billing":
        from security.copilot_billing import main as billing_main

        argv = [args.billing_action]
        if args.billing_action in ("authorize", "record") and args.value:
            argv.append(args.value)
        return billing_main(argv)

    return 0


if __name__ == "__main__":
    sys.exit(main())

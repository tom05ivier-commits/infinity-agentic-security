# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# CLI untuk Infinity Computer System.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system.core import ComputerSystem  # noqa: E402
from system.dashboard import generate  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="system_cli.py", description="Infinity Computer System"
    )
    parser.add_argument(
        "command",
        choices=(
            "status", "snapshot", "dashboard", "serve", "serve-files",
            "protect", "debug", "supervise", "supervisor-status",
            "infinity-connectivity", "services", "service-add", "ideas",
            "cognitive-map",
        ),
        help=(
            "status ringkas, snapshot lengkap, buat dashboard, jalankan server, "
            "jalankan proteksi, status supervisor, peta konektivitas infinity, "
            "peta kognitif, atau diagnostik sistem"
        ),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--name")
    parser.add_argument("--cmd", nargs="+")
    parser.add_argument("--kind", default="process")
    parser.add_argument("--health", default="/")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--ideas-verify", "--verify", dest="ideas_verify",
                        action="store_true")
    parser.add_argument("--cognitive-verify", dest="cognitive_verify",
                        action="store_true")
    parser.add_argument("--cognitive-cycle", dest="cognitive_cycle",
                        action="store_true")
    parser.add_argument("--cognitive-goal", default="status sistem")
    args = parser.parse_args(argv)

    if args.command == "status":
        data = ComputerSystem().snapshot()
        print(
            f"Sistem      : {data['sistem']} v{data['versi']}\n"
            f"Pemilik     : {data['identitas']['nama']} ({data['identitas']['jabatan']})\n"
            f"Lisensi     : {data['lisensi']['identitas']} v{data['lisensi']['versi']}\n"
            f"Otorisasi   : {data['otorisasi']['bertanda_tangan']}\n"
            f"Verifikasi  : {data['keamanan']['verifikasi']} "
            f"({data['keamanan']['verifikasi_pass']} lulus)\n"
            f"Script env  : {data['lingkungan']['jumlah_script']}\n"
            f"Warna X11   : {data['lingkungan']['rgb_colors']}"
        )
    elif args.command == "snapshot":
        print(json.dumps(ComputerSystem().snapshot(), indent=2, ensure_ascii=False))
    elif args.command == "dashboard":
        path = generate()
        print(f"Dashboard ditulis: {path}")
    elif args.command == "serve-files":
        from system.fileserver import serve

        serve(args.port)
    elif args.command == "protect":
        from system.protection import ProtectionDaemon

        result = ProtectionDaemon(
            seconds=args.seconds, interval=args.interval
        ).run()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "services":
        registry = ROOT / "system" / "services.json"
        print(registry.read_text(encoding="utf-8"))
    elif args.command == "service-add":
        registry = ROOT / "system" / "services.json"
        data = json.loads(registry.read_text(encoding="utf-8"))
        if not args.name or (not args.cmd and args.kind != "monitor"):
            print("--name diperlukan; --cmd diperlukan kecuali kind=monitor")
            return 1
        entry = {
            "name": args.name,
            "kind": args.kind,
            "command": args.cmd or ["true"],
        }
        if args.kind in ("http", "monitor"):
            entry["port"] = args.port
        if args.kind == "http":
            entry["health"] = args.health
        data["services"] = [
            item for item in data["services"] if item.get("name") != args.name
        ]
        data["services"].append(entry)
        registry.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Server '{args.name}' terdaftar di {registry}")
    elif args.command == "supervise":
        from system.supervisor import Supervisor

        Supervisor(interval=args.interval, port=args.port).run()
    elif args.command == "supervisor-status":
        from system.supervisor import Supervisor

        print(json.dumps(Supervisor(interval=args.interval, port=args.port).status(),
                         indent=2, ensure_ascii=False))
    elif args.command == "infinity-connectivity":
        from system.infinity_connectivity import check, write_report

        result = check()
        write_report(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "ideas":
        from system.idea_engine import generate as idea_generate, verify, work

        if args.generate:
            result = idea_generate()
        elif args.ideas_verify:
            result = verify()
        else:
            result = work()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "OK" else 1
    elif args.command == "cognitive-map":
        from system.cognitive_brain import cycle, map_cognitive, write_report

        if args.cognitive_cycle:
            result = cycle(args.cognitive_goal)
        else:
            result = map_cognitive(args.cognitive_goal)
            write_report(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if not args.cognitive_verify or result["status"] == "TERPETAKAN" else 1
    elif args.command == "debug":
        data = ComputerSystem().snapshot()
        issues: list[str] = []
        if not data["otorisasi"]["bertanda_tangan"]:
            issues.append("Surat izin/kuasa belum bertanda tangan")
        if data["keamanan"]["verifikasi"] != "COMPLIANT":
            issues.append("Verifikasi keamanan belum COMPLIANT")
        print(
            json.dumps(
                {
                    "status": "OK" if not issues else "DEGRADED",
                    "identitas": data["identitas"]["nama"],
                    "lisensi": data["lisensi"]["identitas"],
                    "verifikasi": data["keamanan"]["verifikasi"],
                    "otorisasi": data["otorisasi"]["bertanda_tangan"],
                    "masalah": issues,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    elif args.command == "serve":
        from system.server import serve

        server = serve(args.host, args.port)
        print(f"Server berjalan di http://{args.host}:{args.port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Output dipipe ke perintah seperti head; hentikan dengan anggun.
        sys.exit(0)

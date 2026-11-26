# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Alur kerja relai chat: pesan tom05-flash-free -> semua responder.

Pemisahan peran:
  * tom05/tom05-flash-free HANYA mengirim pesan (messenger-only).
  * Responder (agen, CLI, skill, tool, docker) yang menjawab/mengerjakan tugas.

Antrean berbasis berkas, idempoten, tanpa server baru, tanpa kredensial, dan
tanpa shell interpolation: perintah diambil dari registri tepercaya lalu
dijalankan dengan argv.

Keamanan konkurensi:
  * Sebelum menjalankan responder, berkas inbox dipindah (os.rename atomik)
    ke direktori ``processing/``. Hanya satu proses yang menang klaim; proses
    lain mendapat SKIP. Ini mencegah eksekusi ganda dan duplikasi audit saat
    daemon dan perintah ``run`` manual bekerja bersamaan.
  * Klaim yang ditinggalkan proses mati dikembalikan ke inbox setelah
    ``STALE_CLAIM_SECONDS`` (lebih besar dari total batas waktu responder).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REGISTRY = ROOT / "config" / "chat_dispatch.json"
BASE = ROOT / "system" / "reports" / "chat_dispatch"
INBOX = BASE / "inbox"
OUTBOX = BASE / "outbox"
PROCESSED = BASE / "processed"
CLAIMED = BASE / "processing"
AUDIT = ROOT / "security" / "reports" / "chat_dispatch.jsonl"

SCHEMA_MESSAGE = "tom05-chat-dispatch/1"
SCHEMA_RESULT = "tom05-chat-dispatch-result/1"
LICENSE = "Tom05ivier-commits-1.0"
OWNER = "Tomi vier"
SENDER = "tom05/tom05-flash-free"
MAX_MESSAGE_CHARS = 4000
DEFAULT_INTERVAL = 2.0
# 11 responder x batas 120 detik = 1320 detik; 1800 detik memberi margin aman.
STALE_CLAIM_SECONDS = 1800

try:  # Samarkan PII/kredensial dari keluaran responder sebelum disimpan.
    from security.privacy import redact  # noqa: E402
except Exception:  # pragma: no cover - fallback bila modul privasi tidak ada
    def redact(text: str) -> str:  # type: ignore[misc]
        return text


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Tulis atomik agar daemon tidak pernah membaca berkas setengah jadi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex[:8]}.tmp")
    temp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temp, path)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def load_registry() -> dict[str, Any]:
    data = _read_json(REGISTRY) or {}
    if not data.get("responders"):
        raise RuntimeError(f"Registri responder tidak valid: {REGISTRY}")
    return data


def responders(registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = registry or load_registry()
    defaults = registry.get("defaults", {})
    result: list[dict[str, Any]] = []
    for item in registry["responders"]:
        entry = dict(item)
        entry.setdefault(
            "timeout_seconds", int(defaults.get("timeout_seconds", 90))
        )
        result.append(entry)
    return result


def sanitize_message(text: str) -> str:
    """Bersihkan pesan; tolak NUL/karakter kontrol selain newline & tab."""
    raw = str(text)
    # Tolak (bukan buang diam-diam) NUL dan karakter kontrol lain. Newline dan
    # tab diizinkan agar pesan multi-baris tetap bisa dikirim.
    for char in raw:
        if char in "\n\t":
            continue
        code = ord(char)
        if code < 32 or code == 127:
            raise ValueError("Pesan mengandung karakter kontrol yang dilarang")
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("Pesan chat kosong")
    if len(cleaned) > MAX_MESSAGE_CHARS:
        raise ValueError(f"Pesan terlalu panjang (maks. {MAX_MESSAGE_CHARS} karakter)")
    return cleaned


def _normalize_targets(targets: list[str] | None) -> list[str]:
    """Terima `--to agent docker` maupun `--to agent,docker`."""
    result: list[str] = []
    for item in targets or ["all"]:
        for part in str(item).split(","):
            part = part.strip()
            if part and part not in result:
                result.append(part)
    return result or ["all"]


def send(message: str, targets: list[str] | None = None) -> dict[str, Any]:
    """Masukkan pesan ke antrean. TIDAK menjalankan apa pun (messenger-only)."""
    payload: dict[str, Any] = {
        "schema": SCHEMA_MESSAGE,
        "id": f"chat-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}",
        "timestamp": _now(),
        "sender": SENDER,
        "role": "messenger-only",
        "message": sanitize_message(message),
        "targets": _normalize_targets(targets),
        "license": LICENSE,
        "owner": OWNER,
        "note": "tom05 hanya mengirim pesan; responder yang menjawab tugas.",
    }
    _write_json(INBOX / f"{payload['id']}.json", payload)
    return {
        "status": "TERKIRIM",
        "id": payload["id"],
        "targets": payload["targets"],
        "executor": "responders (bukan tom05)",
        "message_chars": len(payload["message"]),
    }


def auto_send(message: str, source: str = "tom05-chat") -> dict[str, Any]:
    """Teruskan chat tom05 ke responder secara otomatis.

    Dipanggil oleh CLI ``tom05`` sebelum menjalankan model. Tidak menjalankan
    tugas apa pun sendiri (messenger-only). Dua pengaman:
      * ``TOM05_AUTO_DISPATCH=0`` mematikan pemicu otomatis.
      * Berada di dalam responder (``AGENTY_CHAT_TASK``) mencegah loop bila
        responder memanggil ``tom05`` lagi.
    """
    switch = os.environ.get("TOM05_AUTO_DISPATCH", "1").strip().lower()
    if switch in {"0", "false", "no", "off"}:
        return {"status": "DILEWATI", "reason": "auto-dispatch dinonaktifkan", "auto": True}
    if os.environ.get("AGENTY_CHAT_TASK"):
        return {"status": "DILEWATI", "reason": "dalam responder (anti-loop)", "auto": True}
    ack = send(message)
    ack["auto"] = True
    ack["source"] = source
    return ack


def pending() -> list[Path]:
    if not INBOX.exists():
        return []
    files = sorted(INBOX.glob("*.json"))
    # Idempotensi: berkas yang sudah diproses tidak boleh dijalankan ulang.
    return [path for path in files if not (PROCESSED / path.name).exists()]


def recover_stale_claims() -> int:
    """Kembalikan klaim proses yang mati ke inbox; jumlah berkas dipulihkan."""
    if not CLAIMED.exists():
        return 0
    INBOX.mkdir(parents=True, exist_ok=True)
    restored = 0
    now = time.time()
    for path in sorted(CLAIMED.glob("*.json")):
        try:
            age = now - path.stat().st_mtime
        except OSError:
            continue
        if age < STALE_CLAIM_SECONDS:
            continue
        try:
            os.replace(path, INBOX / path.name)
            restored += 1
        except OSError:
            continue
    return restored


def _select(targets: list[str], registry: dict[str, Any]) -> list[dict[str, Any]]:
    available = responders(registry)
    if not targets or "all" in targets:
        return available
    wanted = set(targets)
    kinds = {item["kind"] for item in available}
    selected = [
        item for item in available
        if item["name"] in wanted or item["kind"] in wanted
    ]
    unknown = sorted(wanted - {item["name"] for item in available} - kinds)
    if unknown:
        print(
            f"[chat-dispatch] Target tidak dikenal diabaikan: {', '.join(unknown)}",
            file=sys.stderr,
        )
    return selected


def _run_responder(item: dict[str, Any], task: str, max_output: int) -> dict[str, Any]:
    command = [
        str(part).replace("{task}", task) for part in item.get("command", [])
    ]
    started = time.monotonic()
    # Aturan proyek: variabel PORT tidak dipakai layanan proyek.
    env = dict(os.environ)
    env.pop("PORT", None)
    # Responder tanpa placeholder {task} tetap menerima konteks pesan.
    env["AGENTY_CHAT_TASK"] = task
    try:
        done = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=float(item.get("timeout_seconds", 90)),
            check=False,
        )
        raw = (done.stdout or "") + (("\n" + done.stderr) if done.stderr else "")
        status = "OK" if done.returncode == 0 else "ERROR"
        exit_code: int | None = done.returncode
    except subprocess.TimeoutExpired:
        raw = f"Responder melebihi batas {item.get('timeout_seconds', 90)} detik."
        status, exit_code = "TIMEOUT", None
    except Exception as exc:  # noqa: BLE001
        raw = f"{type(exc).__name__}: {exc}"
        status, exit_code = "ERROR", None
    output = redact(raw).strip()[-max_output:]
    return {
        "name": item["name"],
        "kind": item["kind"],
        "status": status,
        "exit_code": exit_code,
        "duration_seconds": round(time.monotonic() - started, 2),
        "command": command,
        "output": output,
    }


def _execute(envelope: dict[str, Any], fallback_id: str) -> dict[str, Any]:
    """Jalankan responder untuk satu pesan yang sudah diklaim."""
    registry = load_registry()
    max_output = int(registry.get("defaults", {}).get("max_output_chars", 4000))
    task = str(envelope.get("message", ""))
    targets = list(envelope.get("targets", ["all"]))
    selected = _select(targets, registry)
    answers = [_run_responder(item, task, max_output) for item in selected]
    ok = sum(1 for item in answers if item["status"] == "OK")
    failed = len(answers) - ok
    return {
        "schema": SCHEMA_RESULT,
        "id": envelope.get("id", fallback_id),
        "timestamp": _now(),
        "sender": envelope.get("sender", SENDER),
        "sender_role": "messenger-only",
        "message": task,
        "targets": targets,
        "status": "SELESAI" if answers and not failed else "GAGAL",
        "ringkasan": {
            "total_responder": len(answers),
            "berhasil": ok,
            "gagal": failed,
        },
        "responder": answers,
        "license": LICENSE,
        "owner": OWNER,
        "authority_note": (
            "Tidak ada izin baru: responder lokal rutin/read-only; "
            "aksi ofensif tidak pernah dikirim tanpa --authorize eksplisit."
        ),
    }


def _persist_result(result: dict[str, Any]) -> None:
    """Tulis hasil ke outbox dan audit tepat sekali per pesan."""
    identifier = str(result["id"])
    _write_json(OUTBOX / f"{identifier}.json", result)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False, default=str) + "\n")


def process_message(path: Path) -> dict[str, Any]:
    """Klaim satu pesan secara atomik lalu jalankan semua responder."""
    identifier = path.stem
    CLAIMED.mkdir(parents=True, exist_ok=True)
    claim = CLAIMED / path.name
    try:
        # rename atomik: hanya satu proses yang boleh memegang berkas ini.
        os.rename(path, claim)
    except FileNotFoundError:
        return {
            "id": identifier,
            "status": "SKIP",
            "reason": "pesan sudah diambil proses lain",
        }
    except OSError as exc:  # noqa: BLE001
        return {"id": identifier, "status": "GAGAL", "error": f"{type(exc).__name__}: {exc}"}

    result: dict[str, Any]
    try:
        result = _execute(_read_json(claim) or {}, identifier)
    except Exception as exc:  # noqa: BLE001
        result = {
            "schema": SCHEMA_RESULT,
            "id": identifier,
            "timestamp": _now(),
            "sender": SENDER,
            "sender_role": "messenger-only",
            "message": "",
            "targets": [],
            "status": "GAGAL",
            "error": f"{type(exc).__name__}: {exc}",
            "license": LICENSE,
            "owner": OWNER,
        }

    try:
        _persist_result(result)
    except Exception as exc:  # noqa: BLE001 - daemon harus tetap hidup
        print(f"[chat-dispatch] gagal menulis hasil {identifier}: {exc}", file=sys.stderr)
    finally:
        # Pesan gagal sengaja tidak dikembalikan ke inbox agar tidak looping.
        try:
            PROCESSED.mkdir(parents=True, exist_ok=True)
            os.replace(claim, PROCESSED / path.name)
        except OSError as exc:  # noqa: BLE001
            print(f"[chat-dispatch] gagal mengarsipkan {identifier}: {exc}", file=sys.stderr)
    return result


def run_pending(limit: int | None = None) -> list[dict[str, Any]]:
    recover_stale_claims()
    results: list[dict[str, Any]] = []
    for path in pending():
        if limit is not None and len(results) >= limit:
            break
        results.append(process_message(path))
    return results


def daemon(interval: float = DEFAULT_INTERVAL) -> None:
    recovered = recover_stale_claims()
    print(
        f"[chat-dispatch] daemon aktif; mendengar pesan {SENDER} "
        f"(interval {interval}s, klaim dipulihkan: {recovered})", flush=True,
    )
    while True:
        for report in run_pending():
            if report.get("status") == "SKIP":
                continue
            ringkasan = report.get("ringkasan", {})
            print(
                f"[{report.get('timestamp', _now())}] {report['id']}: "
                f"{report['status']} "
                f"({ringkasan.get('berhasil', 0)}/{ringkasan.get('total_responder', 0)} responder)",
                flush=True,
            )
        time.sleep(max(0.5, interval))


def status() -> dict[str, Any]:
    registry = load_registry()
    history = _history(5)
    return {
        "status": "AKTIF",
        "sender": SENDER,
        "sender_role": "messenger-only",
        "antrean": len(pending()),
        "diproses": len(list(CLAIMED.glob("*.json"))) if CLAIMED.exists() else 0,
        "selesai": len(list(PROCESSED.glob("*.json"))) if PROCESSED.exists() else 0,
        "hasil": len(list(OUTBOX.glob("*.json"))) if OUTBOX.exists() else 0,
        "responder": [
            {"name": item["name"], "kind": item["kind"]}
            for item in responders(registry)
        ],
        "jalur": {
            "inbox": str(INBOX),
            "processing": str(CLAIMED),
            "outbox": str(OUTBOX),
            "audit": str(AUDIT),
        },
        "riwayat_terakhir": [
            {"id": item.get("id"), "status": item.get("status")}
            for item in history
        ],
        "license": LICENSE,
        "owner": OWNER,
    }


def _history(limit: int = 10) -> list[dict[str, Any]]:
    if not AUDIT.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in AUDIT.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records[-limit:]


def main(argv: list[str] | None = None) -> int:
    global STALE_CLAIM_SECONDS
    parser = argparse.ArgumentParser(
        prog="chat_dispatch.py",
        description="Relai chat tom05-flash-free -> semua agen/CLI/skill/tool/docker",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    send_cmd = sub.add_parser("send", help="kirim pesan (tom05 hanya mengirim)")
    send_cmd.add_argument("message")
    send_cmd.add_argument("--to", nargs="*", default=None)
    auto_cmd = sub.add_parser("auto-send", help="pemicu otomatis dari chat tom05")
    auto_cmd.add_argument("message")
    run_cmd = sub.add_parser("run", help="proses antrean sekali jalan")
    run_cmd.add_argument("--limit", type=int, default=None)
    daemon_cmd = sub.add_parser("daemon", help="pantau antrean terus-menerus")
    daemon_cmd.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    sub.add_parser("status", help="status antrean & responder")
    hist_cmd = sub.add_parser("history", help="riwayat eksekusi")
    hist_cmd.add_argument("--limit", type=int, default=10)
    sub.add_parser("responders", help="daftar responder aktif (JSON)")
    recover_cmd = sub.add_parser("recover", help="pulihkan klaim stale ke inbox")
    recover_cmd.add_argument("--after", type=int, default=STALE_CLAIM_SECONDS)
    args = parser.parse_args(argv)

    if args.command == "send":
        print(json.dumps(send(args.message, args.to), indent=2, ensure_ascii=False))
    elif args.command == "auto-send":
        print(json.dumps(auto_send(args.message), indent=2, ensure_ascii=False))
    elif args.command == "run":
        print(json.dumps(run_pending(args.limit), indent=2, ensure_ascii=False))
    elif args.command == "daemon":
        daemon(args.interval)
    elif args.command == "status":
        print(json.dumps(status(), indent=2, ensure_ascii=False))
    elif args.command == "history":
        print(json.dumps(_history(args.limit), indent=2, ensure_ascii=False))
    elif args.command == "responders":
        print(json.dumps(responders(), indent=2, ensure_ascii=False))
    elif args.command == "recover":
        STALE_CLAIM_SECONDS = args.after
        print(json.dumps({"dipulihkan": recover_stale_claims()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

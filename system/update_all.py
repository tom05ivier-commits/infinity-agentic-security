# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Pembaruan menyeluruh dari data yang kita punya ke semua artefak turunan.

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "system" / "reports" / "data_manifest.json"
HY4_DIR = ROOT / "publish" / "hy4-agent-model"
COPILOT_CONFIG = Path("/root/.copilot/config.json")
ACCOUNT = "tom05ivier-commits"

DATA_FILES: tuple[str, ...] = (
    "LICENSE",
    "README.md",
    "AGENTS.md",
    "PANDUAN-OTORISASI-PUBLIK.md",
    "STRATEGI-GLOBAL.md",
    "PLATFORM_CLIS.md",
    "DOCKER.md",
    "surat-izin-keamanan.md",
    "surat-kuasa-tandatangan.md",
    "surat-persetujuan-clone.md",
    "surat-persetujuan-terbatas.md",
    "surat-persetujuan-otomatis.md",
    "surat-izin-konfigurasi-otomatis.md",
    "surat-izin-host.md",
    "surat-izin-github.md",
    "surat-izin-clone-automatis.md",
    "Makefile",
    "hosts",
    "manage_hy4.sh",
    "DOCTOR_CLI.md",
    "PM_CLI.md",
    "run_doctor.sh",
    "chip/README.md",
    "prepare_hy4_repo.sh",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect() -> list[dict[str, Any]]:
    """Kumpulkan data sumber yang tersedia beserta checksum."""
    entries: list[dict[str, Any]] = []
    for relative in DATA_FILES:
        path = ROOT / relative
        if not path.exists():
            continue
        entries.append(
            {
                "file": relative,
                "size": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return entries


def write_manifest() -> dict[str, Any]:
    entries = collect()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": "Tomi vier",
        "license": "Tom05ivier-commits-1.0",
        "github_account": ACCOUNT,
        "files": len(entries),
        "total_bytes": sum(item["size"] for item in entries),
        "entries": entries,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def _token() -> str:
    if not COPILOT_CONFIG.exists():
        return ""
    try:
        text = COPILOT_CONFIG.read_text(encoding="utf-8")
        text = "\n".join(
            line for line in text.splitlines()
            if not line.strip().startswith("//")
        )
        data = json.loads(text)
        tokens = data.get("authTokens", {})
        key = next(
            (k for k in tokens if k.endswith(ACCOUNT) and not k.endswith(":github")),
            None,
        ) or next(iter(tokens), None)
        return tokens[key].get("token", "") if key else ""
    except (OSError, json.JSONDecodeError, AttributeError):
        return ""


def scores_ok(scores: dict[str, str]) -> bool:
    """Publikasi hanya boleh jalan bila semua scorecard bernilai OK."""
    return bool(scores) and all(value == "OK" for value in scores.values())


def _clean_stale_prepare_errors() -> None:
    """Hapus berkas error prepare dari siklus sebelumnya.

    Berkas ini hanya ditulis saat prepare gagal; bila dibiarkan, siklus sukses
    berikutnya meninggalkan working tree kotor dan gate 100/100 jadi tidak
    determinis. Dipisahkan agar perilaku ini bisa diuji langsung.
    """
    for name in ("prepare_github_error.txt", "prepare_hy4_error.txt"):
        (MANIFEST.parent / name).unlink(missing_ok=True)


def update(push: bool = True) -> dict[str, Any]:
    """Jalankan seluruh rantai pembaruan."""
    _clean_stale_prepare_errors()
    manifest = write_manifest()
    subprocess.run(
        ["python3", str(ROOT / "security" / "security_cli.py"), "sempurnakan",
         "--times", "3", "--intensity", "moderate"],
        cwd=str(ROOT), check=True, capture_output=True, timeout=600,
    )
    final = json.loads(
        (ROOT / "security" / "reports" / "final_report.json").read_text(encoding="utf-8")
    )

    try:
        subprocess.run(
            ["bash", str(ROOT / "prepare_github.sh")],
            cwd=str(ROOT), check=True, capture_output=True, text=True, timeout=300,
        )
    except subprocess.CalledProcessError as exc:
        (MANIFEST.parent / "prepare_github_error.txt").write_text(
            (exc.stderr or "") + "\n" + (exc.stdout or ""), encoding="utf-8"
        )
        raise
    commit = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=str(ROOT / "publish" / "infinity-agentic-security"),
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    # Repository data agen & model hy4.
    try:
        subprocess.run(
            ["bash", str(ROOT / "prepare_hy4_repo.sh")],
            cwd=str(ROOT), check=True, capture_output=True, text=True, timeout=300,
        )
    except subprocess.CalledProcessError as exc:
        (MANIFEST.parent / "prepare_hy4_error.txt").write_text(
            (exc.stderr or "") + "\n" + (exc.stdout or ""), encoding="utf-8"
        )
        raise
    hy4_commit = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=str(HY4_DIR), capture_output=True, text=True, check=True,
    ).stdout.strip()

    # Nilai scorecard setelah cermin publish disegarkan. Sebagian membaca
    # status rilis dari direktori publish, jadi harus dihitung setelah prepare.
    # Skor yang gagal (= di bawah 100/100) membatalkan publikasi: laporan lama
    # tidak boleh dipakai sebagai kedok untuk merilis keadaan yang menurun.
    scores: dict[str, str] = {}
    for key, argv in (
        ("chip", ["python3", str(ROOT / "chip" / "chip_cli.py"), "score"]),
        ("security", ["python3", str(ROOT / "security" / "security_cli.py"),
                      "score", "--json"]),
        ("tom05", ["python3", str(ROOT / "system" / "tom05_score.py")]),
        ("device", ["python3", str(ROOT / "system" / "device_score.py")]),
        ("container", ["python3", str(ROOT / "system" / "container_score.py")]),
    ):
        try:
            proc = subprocess.run(
                argv, cwd=str(ROOT), capture_output=True, text=True, timeout=300
            )
            scores[key] = "OK" if proc.returncode == 0 else "GAGAL"
        except (OSError, subprocess.SubprocessError):
            scores[key] = "GAGAL"

    if not scores_ok(scores):
        blocked = {
            "status": "GAGAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alasan": "skor di bawah 100/100; publikasi dibatalkan",
            "final_status": final["status"],
            "scores": scores,
            "pushed": False,
        }
        (MANIFEST.parent / "update_all.json").write_text(
            json.dumps(blocked, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return blocked

    pushed = False
    remote_commit = ""
    hy4_remote_commit = ""
    if push:
        token = _token()
        if token:
            env = dict(os.environ, GITHUB_TOKEN=token)
            subprocess.run(
                ["bash", str(ROOT / "push_github.sh")],
                cwd=str(ROOT), env=env, check=True, capture_output=True, timeout=600,
            )
            pushed = True
            remote_commit = subprocess.run(
                ["git", "ls-remote", "origin", "refs/heads/main"],
                cwd=str(ROOT / "publish" / "infinity-agentic-security"),
                capture_output=True, text=True, check=True,
            ).stdout.split()[0]

            hy4_env = dict(
                env, REPO_NAME="hy4-agent-model", REPO_DIR=str(HY4_DIR)
            )
            subprocess.run(
                ["bash", str(ROOT / "push_github.sh")],
                cwd=str(ROOT), env=hy4_env, check=True, capture_output=True, timeout=600,
            )
            hy4_remote_commit = subprocess.run(
                ["git", "ls-remote", "origin", "refs/heads/main"],
                cwd=str(HY4_DIR), capture_output=True, text=True, check=True,
            ).stdout.split()[0]

    report = {
        "status": "OK" if final["status"] == "SELESAI" else "GAGAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_files": manifest["files"],
        "data_bytes": manifest["total_bytes"],
        "final_status": final["status"],
        "fulfilled": final["fulfilled"],
        "scores": scores,
        "local_commit": commit,
        "pushed": pushed,
        "remote_commit": remote_commit,
        "hy4_commit": hy4_commit,
        "hy4_remote_commit": hy4_remote_commit,
        "manifest": str(MANIFEST),
    }
    (MANIFEST.parent / "update_all.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Update all from our data")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()
    print(json.dumps(update(push=not args.no_push), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

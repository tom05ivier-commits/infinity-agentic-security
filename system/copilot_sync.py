# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Samakan fungsi Copilot CLI dengan model hy4 (agent + command → skill).

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from system.hy4_manager import AGENTS, COMMANDS, MODEL  # noqa: E402

COPILOT_MODEL = "opencode-hy4/hy4-flash-free"
USER_AGENTS = Path("/root/.copilot/agents")
USER_SKILLS = Path("/root/.copilot/skills")
PROJECT_AGENTS = ROOT / ".github" / "agents"
PROJECT_SKILLS = ROOT / ".github" / "skills"
LICENSE_LINE = "Tom05ivier-commits-1.0"
AUDIT = ROOT / "security" / "reports" / "copilot_sync.jsonl"
BASE_DIRS = (USER_AGENTS, USER_SKILLS, PROJECT_AGENTS, PROJECT_SKILLS)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Ambil field YAML sederhana dan isi Markdown setelah frontmatter."""
    fields: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    fields[key.strip()] = value.strip()
            body = parts[2].strip()
    return fields, body


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", name.replace(".md", "").lower().replace("_", "-"))


def agent_profile(name: str, source: str) -> str:
    """Ubah definisi agent hy4 menjadi profil agent Copilot CLI."""
    fields, body = _parse_frontmatter(source)
    slug = _slug(name)
    description = fields.get("description", f"Peran {slug} untuk sistem IT Agenty.")
    lines = [
        "---",
        f"name: {slug}",
        f"description: {description}",
        f"model: {COPILOT_MODEL}",
        "infer: true",
        "---",
        "",
        f"# Agen {slug}",
        "",
        body,
        "",
        f"Sumber: model {MODEL}. Lisensi {LICENSE_LINE}.",
        "Jangan menampilkan kredensial atau data pribadi.",
    ]
    return "\n".join(lines)


def skill_file(name: str, source: str) -> str:
    """Ubah command hy4 menjadi skill Copilot CLI."""
    fields, body = _parse_frontmatter(source)
    slug = _slug(name)
    description = fields.get("description", f"Perintah {slug}.")
    lines = [
        "---",
        f"name: {slug}",
        f"description: {description}",
        f"license: {LICENSE_LINE}",
        "---",
        "",
        f"# Skill {slug}",
        "",
        body,
    ]
    return "\n".join(lines)


def _expected() -> dict[Path, str]:
    """Petakan semua berkas hasil sinkronisasi → isi yang diharapkan."""
    expected: dict[Path, str] = {}
    for name, source in AGENTS.items():
        slug = _slug(name)
        content = agent_profile(name, source)
        for base in (USER_AGENTS, PROJECT_AGENTS):
            expected[base / f"{slug}.agent.md"] = content
    for name, source in COMMANDS.items():
        slug = _slug(name)
        content = skill_file(name, source)
        for base in (USER_SKILLS, PROJECT_SKILLS):
            expected[base / slug / "SKILL.md"] = content
    return expected


def _generated_files(expected: dict[Path, str]) -> list[Path]:
    """Berkas turunan lama yang masih menyimpan penanda lisensi kita."""
    stale: list[Path] = []
    for base in BASE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path in expected:
                continue
            try:
                if LICENSE_LINE in path.read_text(encoding="utf-8"):
                    stale.append(path)
            except (OSError, UnicodeDecodeError):
                continue
    return stale


def _audit(action: str, **fields: Any) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **fields,
    }
    with AUDIT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def sync(dry_run: bool = False) -> dict[str, Any]:
    """Tulis profil agent & skill ke scope user dan proyek.

    Berkas turunan yang tidak lagi memiliki pasangan di hy4_manager dihapus
    hanya bila memuat penanda lisensi IT Agenty, sehingga konten buatan
    pengguna lain tidak tersentuh.
    """
    expected = _expected()
    written: list[str] = []
    for path, content in expected.items():
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        written.append(str(path))
    removed = [str(p) for p in _generated_files(expected)]
    if not dry_run:
        for raw in removed:
            Path(raw).unlink(missing_ok=True)
    result: dict[str, Any] = {
        "status": "SIMULASI" if dry_run else "OK",
        "agents": len(AGENTS),
        "commands": len(COMMANDS),
        "files": len(written),
        "removed": removed,
        "copilot_model": COPILOT_MODEL,
        "paths": [str(p) for p in BASE_DIRS],
    }
    if not dry_run:
        _audit("sync", **{k: v for k, v in result.items() if k != "paths"})
    return result


def verify() -> dict[str, Any]:
    """Cocokkan isi di disk dengan AGENTS/COMMANDS tanpa mengubahnya."""
    expected = _expected()
    missing: list[str] = []
    mismatch: list[str] = []
    present: list[str] = []
    for path, content in expected.items():
        if not path.is_file():
            missing.append(str(path))
            continue
        present.append(str(path))
        if path.read_text(encoding="utf-8") != content:
            mismatch.append(str(path))
    stale = [str(p) for p in _generated_files(expected)]
    ok = not (missing or mismatch or stale)
    result: dict[str, Any] = {
        "status": "PASS" if ok else "FAIL",
        "agents": len(AGENTS),
        "commands": len(COMMANDS),
        "expected_files": len(expected),
        "present_files": len(present),
        "missing": missing,
        "content_mismatch": mismatch,
        "stale": stale,
        "copilot_model": COPILOT_MODEL,
    }
    _audit("verify", **result)
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Sync hy4 → Copilot CLI")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify", action="store_true", help="Cek kesesuaian tanpa menulis")
    args = parser.parse_args()
    result = verify() if args.verify else sync(args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

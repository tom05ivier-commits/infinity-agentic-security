# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#" Registry 10 CLI platform engineering + kriteria automation-friendly.

from __future__ import annotations

import shutil
from typing import Any

TOP10: tuple[dict[str, Any], ...] = (
    {"rank": 1, "name": "StackGen CLI", "binary": "stackgen", "category": "infra/AI", "note": "MCP server via `stackgen mcp`"},
    {"rank": 2, "name": "kubectl", "binary": "kubectl", "category": "kubernetes", "note": "get/describe/apply/delete + -o json"},
    {"rank": 3, "name": "Terraform / OpenTofu", "binary": "terraform", "alternative": "tofu", "category": "iac", "note": "plan → review → apply"},
    {"rank": 4, "name": "Crossplane CLI", "binary": "crossplane", "category": "kubernetes/iac", "note": "Compositions, satu control plane"},
    {"rank": 5, "name": "Argo CD CLI", "binary": "argocd", "category": "gitops", "note": "diff/sync/rollback"},
    {"rank": 6, "name": "Vault CLI", "binary": "vault", "category": "secrets", "note": "short-lived scoped credentials"},
    {"rank": 7, "name": "GitHub CLI", "binary": "gh", "category": "github", "note": "PR/issue/release/actions"},
    {"rank": 8, "name": "Pulumi CLI", "binary": "pulumi", "category": "iac", "note": "preview → up"},
    {"rank": 9, "name": "Claude Code", "binary": "claude", "category": "coding agent", "note": "Skills & Subagents"},
    {"rank": 10, "name": "OpenCode / Kilo CLI", "binary": "opencode", "alternative": "kilo", "category": "coding agent", "note": "model-flexible, compliance-friendly"},
)

CRITERIA: tuple[str, ...] = (
    "structured_output",
    "plan_or_dry_run",
    "idempotency",
    "exit_codes",
    "auth",
    "automation_compatibility",
    "consistent_structure",
    "state_inspection",
)


def which(item: dict[str, Any]) -> str | None:
    """Temukan biner utama atau alternatif yang terpasang."""
    for binary in (item.get("binary"), item.get("alternative")):
        if binary and shutil.which(binary):
            return binary
    return None


def inventory() -> list[dict[str, Any]]:
    """Daftar 10 CLI dengan status keberadaan di sistem ini."""
    return [
        {
            **item,
            "installed_binary": which(item),
            "installed": which(item) is not None,
        }
        for item in TOP10
    ]


def score(item: dict[str, Any]) -> dict[str, Any]:
    """Skor automation 0-100 berdasarkan kriteria artikel.

    Skor dasar 70 untuk desain yang disebut artikel; tambah 30 bila terpasang
    di sistem ini. Ini ukuran kesiapan, bukan benchmark kinerja.
    """
    base = 70 + (10 if item.get("alternative") else 0)
    if item.get("installed"):
        base += 20
    return {
        "name": item["name"],
        "installed": item["installed"],
        "binary": item.get("installed_binary"),
        "score": min(base, 100),
        "note": item["note"],
    }

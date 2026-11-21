# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Otak agen: mengubah tujuan menjadi rencana tugas yang aman."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .tasks import KEYWORDS, TASKS


@dataclass(frozen=True)
class Step:
    """Satu langkah dalam rencana agen."""

    task: str
    params: dict[str, Any]


class AgentBrain:
    """Perencana berbasis aturan dengan prinsip keamanan."""

    def plan(self, goal: str, authorize: bool = False) -> list[Step]:
        """Susun rencana dari tujuan berbahasa Indonesia/Inggris sederhana."""
        text = goal.lower()
        steps: list[Step] = []

        # Selalu awali dengan status agar agen punya konteks.
        steps.append(Step(task="status", params={}))

        matched = [
            name
            for name, words in KEYWORDS.items()
            if name != "status" and any(word in text for word in words)
        ]

        if "perfect" in matched:
            # Siklus penyempurnaan sudah mencakup capability/integrity/protect/
            # verify/dashboard, jadi tidak perlu langkah individual duplikat.
            steps.append(Step(task="perfect", params={"seconds": 2.0}))
            return steps

        if "campaign" in matched:
            # Kampanye sudah mencakup proteksi, serangan 3x, dan respons.
            steps.append(
                Step(task="campaign", params={"times": 3, "intensity": "moderate"})
            )
            if "verify" not in matched:
                steps.append(Step(task="verify", params={}))
            return steps

        if "integrity" in matched:
            steps.append(Step(task="integrity", params={}))
        if "capability" in matched:
            steps.append(Step(task="capability", params={}))
        if "protect" in matched:
            steps.append(Step(task="protect", params={"seconds": 2.0}))
        if "drill" in matched:
            steps.append(Step(task="drill", params={"authorize": authorize}))
        if "verify" in matched:
            steps.append(Step(task="verify", params={}))
        if "dashboard" in matched:
            steps.append(Step(task="dashboard", params={}))

        # Jika tidak ada yang cocok, setidaknya verifikasi kondisi sistem.
        if not matched:
            steps.append(Step(task="verify", params={}))
        return steps

    @staticmethod
    def available_tasks() -> list[str]:
        return sorted(TASKS)

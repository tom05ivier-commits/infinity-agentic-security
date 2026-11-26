# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
# Mesin penalaran komputer canggih dengan memori persisten tanpa batas buatan.

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .knowledge import KnowledgeBase

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

MEMORY_PATH = ROOT / "advanced" / "memory.jsonl"


def _unlimited_limit() -> int:
    """Batas iterasi dari environment; 0 berarti tidak ada batas."""
    try:
        return max(0, int(os.environ.get("AGENTY_MAX_ITERATIONS", "0")))
    except ValueError:
        return 0


class AdvancedComputer:
    """Komputer otonom: persepsi → penalaran → aksi → refleksi."""

    def __init__(self) -> None:
        self.knowledge = KnowledgeBase()
        self.knowledge.refresh()
        self.history: list[dict[str, Any]] = self._load_memory()

    def _load_memory(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if MEMORY_PATH.exists():
            for line in MEMORY_PATH.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def _remember(self, record: dict[str, Any]) -> None:
        """Tulis memori append-only tanpa batas ukuran."""
        MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.history.append(record)

    def perceive(self) -> dict[str, Any]:
        """Kumpulkan keadaan sistem + knowledge base."""
        from system.core import ComputerSystem

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": ComputerSystem().snapshot(),
            "knowledge": self.knowledge.stats(),
        }

    def reason(self, goal: str) -> list[str]:
        """Tentukan tugas berdasarkan tujuan dan data yang tersedia."""
        from agent.brain import AgentBrain

        steps = AgentBrain().plan(goal)
        names = [step.task for step in steps]
        if self.knowledge.search(goal):
            names.append("knowledge")
        return names

    def act(self, task: str, authorize: bool = False, **params: Any) -> dict[str, Any]:
        """Jalankan satu tugas melalui AgentRuntime."""
        from agent.runtime import AgentRuntime, Step

        if task == "knowledge":
            return {"task": task, "status": "OK", "result": self.knowledge.stats()}
        result = AgentRuntime().execute(Step(task=task, params=params))
        if task == "drill":
            result.setdefault("result", {})
            if not authorize and not result["result"].get("skipped"):
                result["result"] = {
                    "skipped": True,
                    "reason": "Aksi ofensif memerlukan authorize=True.",
                }
        return result

    def reflect(self, goal: str, trace: list[dict[str, Any]]) -> dict[str, Any]:
        """Nilai hasil dan simpan ke memori."""
        errors = [item for item in trace if item.get("status") == "ERROR"]
        skipped = [
            item for item in trace if item.get("result", {}).get("skipped")
        ]
        status = "FAILED" if errors else ("PARTIAL" if skipped else "SUCCESS")
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "goal": goal,
            "status": status,
            "tasks": [item.get("task") for item in trace],
        }
        self._remember(record)
        return {"status": status, "errors": len(errors), "skipped": len(skipped)}

    def run(self, goal: str, authorize: bool = False) -> dict[str, Any]:
        """Satu siklus persepsi → penalaran → aksi → refleksi."""
        perception = self.perceive()
        tasks = self.reason(goal)
        trace = [self.act(task, authorize=authorize) for task in tasks]
        reflection = self.reflect(goal, trace)
        return {
            "goal": goal,
            "perception": perception,
            "tasks": tasks,
            "trace": trace,
            "reflection": reflection,
        }

    def run_until(
        self,
        goal: str,
        authorize: bool = False,
        target_status: str = "SUCCESS",
        delay: float = 0.2,
    ) -> dict[str, Any]:
        """Ulangi siklus tanpa batas hingga status target tercapai.

        Default iterasi tanpa batas (0). Set AGENTY_MAX_ITERATIONS untuk
        membatasi bila diperlukan. Setiap putaran disimpan di memori.
        """
        limit = _unlimited_limit()
        iterations = 0
        last: dict[str, Any] = {}
        while limit == 0 or iterations < limit:
            iterations += 1
            last = self.run(goal, authorize=authorize)
            if last["reflection"]["status"] == target_status:
                break
            if last["reflection"]["skipped"] and not authorize:
                # Aksi ofensif ditolak; mengulang tidak akan mengubah hasil.
                break
            time.sleep(max(0.0, delay))
        return {
            "goal": goal,
            "iterations": iterations,
            "limit": "unlimited" if limit == 0 else limit,
            "status": last.get("reflection", {}).get("status", "UNKNOWN"),
            "last_result": last,
            "memory_size": len(self.history),
        }

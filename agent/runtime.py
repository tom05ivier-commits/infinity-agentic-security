# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
#  Runtime eksekusi agen dengan jejak audit dan refleksi hasil.

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .brain import AgentBrain, Step
from .tasks import TASKS

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "agent" / "state.json"


class AgentRuntime:
    """Menjalankan rencana agen dan menyimpan jejak keputusan."""

    def __init__(self) -> None:
        self.brain = AgentBrain()
        self.state: dict[str, Any] = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if STATE_PATH.exists():
            try:
                return json.loads(STATE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"runs": [], "owner": "Tomi vier", "license": "Tom05ivier-commits-1.0"}

    def _save_state(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def execute(self, step: Step) -> dict[str, Any]:
        """Jalankan satu langkah dengan penanganan kesalahan."""
        handler = TASKS.get(step.task)
        if handler is None:
            return {"task": step.task, "status": "ERROR", "error": "tugas tidak dikenal"}
        try:
            result = handler(**step.params)
        except Exception as exc:  # noqa: BLE001
            return {
                "task": step.task,
                "status": "ERROR",
                "error": str(exc),
                "traceback": traceback.format_exc(limit=2),
            }
        return {"task": step.task, "status": "OK", "result": result}

    def run(self, goal: str, authorize: bool = False) -> dict[str, Any]:
        """Rencanakan + jalankan + refleksikan satu tujuan."""
        steps = self.brain.plan(goal, authorize=authorize)
        trace = [self.execute(step) for step in steps]

        errors = [item for item in trace if item["status"] == "ERROR"]
        skipped = [
            item
            for item in trace
            if item.get("result", {}).get("skipped") is True
        ]
        status = "FAILED" if errors else ("PARTIAL" if skipped else "SUCCESS")

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "goal": goal,
            "authorized": authorize,
            "plan": [step.task for step in steps],
            "status": status,
            "errors": len(errors),
            "skipped": len(skipped),
            "trace": trace,
        }
        self.state["runs"].append(entry)
        self.state["last_status"] = status
        self._save_state()
        return entry

    def loop(self, goals: list[str], authorize: bool = False) -> list[dict[str, Any]]:
        """Jalankan banyak tujuan secara berurutan."""
        return [self.run(goal, authorize=authorize) for goal in goals]

# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Security Operations Center (SOC) agent.

Menggabungkan temuan dari AV, firewall, dan red-team menjadi alert prioritas
serta laporan ringkas dalam format JSON.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..common.config import REPORT_DIR, ensure_dirs
from ..common.logging import audit, get_logger
from ..common.models import Alert, Finding, ScanResult, Severity

logger = get_logger("blue.soc")

_SEVERITY_RANK = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class SOCAgent:
    """Korelasi temuan dan pembuatan alert."""

    def correlate(self, results: list[ScanResult]) -> list[Alert]:
        """Kelompokkan temuan menjadi alert berdasarkan tingkat keparahan."""
        by_severity: dict[Severity, list[Finding]] = {
            severity: [] for severity in Severity
        }
        for result in results:
            for finding in result.findings:
                by_severity[finding.severity].append(finding)

        alerts: list[Alert] = []
        for severity in sorted(Severity, key=lambda s: _SEVERITY_RANK[s], reverse=True):
            findings = by_severity[severity]
            if not findings:
                continue
            alerts.append(
                Alert(
                    title=f"{severity.value}: {len(findings)} temuan terdeteksi",
                    severity=severity,
                    source="antivirus/firewall/red-team",
                    detail="；".join(sorted({f.description for f in findings})),
                    findings=findings,
                )
            )
        audit(logger, "soc.correlated", alerts=len(alerts))
        return alerts

    def risk_score(self, alerts: list[Alert]) -> int:
        """Hitung skor risiko 0-100."""
        score = sum(_SEVERITY_RANK[alert.severity] * 8 for alert in alerts)
        return min(100, score)

    def write_report(
        self, alerts: list[Alert], filename: str = "soc_report.json"
    ) -> Path:
        ensure_dirs()
        report: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": self.risk_score(alerts),
            "summary": dict(Counter(a.severity.value for a in alerts)),
            "alerts": [alert.to_dict() for alert in alerts],
        }
        path = REPORT_DIR / filename
        path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        audit(logger, "soc.report_written", path=str(path))
        return path

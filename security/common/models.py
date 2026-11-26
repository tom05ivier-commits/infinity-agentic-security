# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Struktur data bersama untuk seluruh agen."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingType(str, Enum):
    SIGNATURE = "SIGNATURE"
    HASH = "HASH"
    HEURISTIC = "HEURISTIC"
    WEAK_CONFIG = "WEAK_CONFIG"
    OPEN_PORT = "OPEN_PORT"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"


@dataclass
class Finding:
    """Satu temuan dari pemindaian atau analisis."""

    finding_type: FindingType
    severity: Severity
    description: str
    location: str = ""
    evidence: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.finding_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "location": self.location,
            "evidence": self.evidence[:200],
            "metadata": self.metadata,
        }


@dataclass
class ScanResult:
    """Hasil pemindaian satu file atau satu target."""

    target: str
    findings: list[Finding] = field(default_factory=list)
    scanned_items: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def infected(self) -> bool:
        return any(
            f.finding_type
            in (FindingType.SIGNATURE, FindingType.HASH, FindingType.HEURISTIC)
            for f in self.findings
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "infected": self.infected,
            "scanned_items": self.scanned_items,
            "findings": [f.to_dict() for f in self.findings],
            "errors": self.errors,
            "metadata": self.metadata,
        }


@dataclass
class Alert:
    """Alert yang dihasilkan SOC agent."""

    title: str
    severity: Severity
    source: str
    detail: str = ""
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity.value,
            "source": self.source,
            "detail": self.detail,
            "findings": [f.to_dict() for f in self.findings],
        }

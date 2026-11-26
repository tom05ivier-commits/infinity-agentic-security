# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Logging terstruktur (JSON) untuk audit semua aktivitas agen."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from .config import LOG_DIR, ensure_dirs


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in getattr(record, "audit", {}).items():
            payload[f"audit.{key}"] = value
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    ensure_dirs()
    logger = logging.getLogger(f"agenty.{name}")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream = logging.StreamHandler()
    stream.setFormatter(JsonFormatter())

    file_handler = logging.FileHandler(
        LOG_DIR / "security.log", encoding="utf-8"
    )
    file_handler.setFormatter(JsonFormatter())

    logger.addHandler(stream)
    logger.addHandler(file_handler)
    return logger


def audit(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Catat kejadian dengan konteks audit tambahan."""
    extra = {"audit": fields}
    logger.info(event, extra=extra)

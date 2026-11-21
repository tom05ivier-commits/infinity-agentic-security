# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Otorisasi untuk aktivitas ofensif.

Prinsip: tidak ada sicherheits penetrate tanpa izin tertulis. Token otorisasi
harus diberikan secara eksplisit oleh operator melalui variabel lingkungan.
Target hanya boleh localhost / direktori lab yang ditunjuk.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

from .config import (
    ALLOWED_TARGETS,
    AUTH_TOKEN_ENV,
    LAB_TARGET,
)


class AuthorizationError(PermissionError):
    """Dilempar ketika otorisasi tidak ada, kedaluwarsa, atau target di luar scope."""


@dataclass(frozen=True)
class Scope:
    """Batasan ruang lingkup pengujian."""

    allowed_targets: tuple[str, ...]
    max_duration_seconds: int = 300
    allow_network_scan: bool = False

    def contains(self, target: str) -> bool:
        return target in self.allowed_targets


@dataclass(frozen=True)
class AuthorizationToken:
    """Token otorisasi bertanda tangan sederhana (untuk laboratorium)."""

    token_id: str
    issued_by: str
    scope: Scope
    issued_at: float
    expires_at: float

    @classmethod
    def from_env(cls) -> "AuthorizationToken":
        raw = os.environ.get(AUTH_TOKEN_ENV)
        if not raw:
            raise AuthorizationError(
                f"Token otorisasi tidak ditemukan. Atur {AUTH_TOKEN_ENV} "
                "dengan JSON token yang diterbitkan operator."
            )
        try:
            data: dict[str, Any] = json.loads(raw)
            scope_data = data["scope"]
            scope = Scope(
                allowed_targets=tuple(scope_data["allowed_targets"]),
                max_duration_seconds=int(
                    scope_data.get("max_duration_seconds", 300)
                ),
                allow_network_scan=bool(
                    scope_data.get("allow_network_scan", False)
                ),
            )
            token = cls(
                token_id=str(data["token_id"]),
                issued_by=str(data["issued_by"]),
                scope=scope,
                issued_at=float(data["issued_at"]),
                expires_at=float(data["expires_at"]),
            )
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise AuthorizationError(f"Format token tidak valid: {exc}") from exc

        token.validate()
        return token

    def validate(self) -> None:
        now = time.time()
        if now < self.issued_at:
            raise AuthorizationError("Token belum berlaku.")
        if now > self.expires_at:
            raise AuthorizationError("Token sudah kedaluwarsa.")
        if self.expires_at - self.issued_at > self.scope.max_duration_seconds:
            raise AuthorizationError("Masa berlaku token melebihi batas scope.")
        unexpected = set(self.scope.allowed_targets) - set(ALLOWED_TARGETS)
        if unexpected:
            raise AuthorizationError(
                f"Target di luar daftar putih laboratorium: {sorted(unexpected)}"
            )

    def require_target(self, target: str) -> str:
        """Validasi target; mengembalikan path lab bila target == 'lab'."""
        self.validate()
        if target not in self.scope.allowed_targets:
            raise AuthorizationError(
                f"Target '{target}' tidak ada dalam scope token."
            )
        if target == LAB_TARGET:
            from ..common.config import LAB_ROOT

            return str(LAB_ROOT)
        return target


def issue_token(
    token_id: str,
    issued_by: str,
    allowed_targets: tuple[str, ...] = (LAB_TARGET,),
    duration_seconds: int = 300,
    allow_network_scan: bool = False,
) -> AuthorizationToken:
    """Terbitkan token untuk keperluan laboratorium (operator sah)."""
    now = time.time()
    scope = Scope(
        allowed_targets=allowed_targets,
        max_duration_seconds=duration_seconds,
        allow_network_scan=allow_network_scan,
    )
    token = AuthorizationToken(
        token_id=token_id,
        issued_by=issued_by,
        scope=scope,
        issued_at=now,
        expires_at=now + duration_seconds,
    )
    token.validate()
    return token


def token_to_env(token: AuthorizationToken) -> str:
    """Serialisasi token ke format JSON untuk variabel lingkungan."""
    return json.dumps(
        {
            "token_id": token.token_id,
            "issued_by": token.issued_by,
            "scope": {
                "allowed_targets": list(token.scope.allowed_targets),
                "max_duration_seconds": token.scope.max_duration_seconds,
                "allow_network_scan": token.scope.allow_network_scan,
            },
            "issued_at": token.issued_at,
            "expires_at": token.expires_at,
        }
    )


def require_authorization(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: memastikan token valid sebelum metode ofensif dijalankan."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if getattr(self, "_auth", None) is None:
            raise AuthorizationError(
                "Agen ofensif memerlukan token otorisasi."
            )
        self._auth.validate()
        return func(self, *args, **kwargs)

    return wrapper

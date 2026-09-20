"""Firestore client, initialized from a service-account key stored ONLY in
an environment variable (`FIREBASE_CREDENTIALS_JSON`) - never a file
committed to the repo, never a hardcoded key in source.

Firestore is treated as an optional integration, the same way OPENAI_API_KEY
is: if it isn't configured, every caller gets a clear "not configured"
result instead of a crash, and the core pipeline/API never depends on it.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger("firestore_client")

_client: Any = None
_init_attempted = False


class FirestoreUnavailableError(RuntimeError):
    pass


def get_firestore_client() -> Any:
    """Return a cached Firestore client, or raise FirestoreUnavailableError.

    Lazily initializes firebase_admin exactly once per process. Safe to call
    repeatedly - after the first failed attempt it keeps returning the same
    clear error instead of retrying a broken credential on every request.
    """
    global _client, _init_attempted

    if _client is not None:
        return _client
    if _init_attempted:
        raise FirestoreUnavailableError(_last_error)

    _init_attempted = True
    if not settings.firebase_credentials_json:
        _set_last_error(
            "[BLOCKED] FIREBASE_CREDENTIALS_JSON not set. Paste the Firebase "
            "service-account key JSON (Project Settings -> Service accounts -> "
            "Generate new private key) as a single-line env var - see .env.example."
        )
        raise FirestoreUnavailableError(_last_error)

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as exc:
        _set_last_error("firebase-admin package not installed; run `uv add firebase-admin`.")
        raise FirestoreUnavailableError(_last_error) from exc

    try:
        cred_dict = json.loads(settings.firebase_credentials_json)
    except ValueError as exc:
        _set_last_error("FIREBASE_CREDENTIALS_JSON is not valid JSON.")
        raise FirestoreUnavailableError(_last_error) from exc

    try:
        if not firebase_admin._apps:  # avoid "app already exists" on reload
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        _client = firestore.client()
        return _client
    except Exception as exc:  # noqa: BLE001 - surface any auth/init failure clearly
        _set_last_error(f"Failed to initialize Firestore client: {exc}")
        raise FirestoreUnavailableError(_last_error) from exc


_last_error = "Firestore not initialized."


def _set_last_error(msg: str) -> None:
    global _last_error
    _last_error = msg
    logger.warning(msg)


def firestore_status() -> dict[str, Any]:
    """Non-throwing status check, used by /health and for UI display."""
    if not settings.firebase_credentials_json:
        return {"configured": False, "reason": "FIREBASE_CREDENTIALS_JSON not set"}
    try:
        get_firestore_client()
        return {"configured": True, "reason": None}
    except FirestoreUnavailableError as exc:
        return {"configured": False, "reason": str(exc)}

from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any, Callable, TypeVar

from sqlalchemy.orm import Session

from app.schemas import AiChatResponse
from app.services.crm_context import build_crm_context

T = TypeVar("T")

CONTEXT_TTL_SEC = float((__import__("os").environ.get("AI_CRM_CONTEXT_TTL") or "180").strip() or "180")
ANSWER_TTL_SEC = float((__import__("os").environ.get("AI_CRM_ANSWER_TTL") or "600").strip() or "600")

_lock = threading.RLock()
_context_entry: dict[str, Any] = {"at": 0.0, "data": None, "fp": ""}
_answer_entries: dict[str, dict[str, Any]] = {}


def _fingerprint(context: dict[str, Any]) -> str:
    raw = json.dumps(context, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def get_cached_context(db: Session) -> tuple[dict[str, Any], str, bool]:
    now = time.time()
    with _lock:
        data = _context_entry.get("data")
        at = float(_context_entry.get("at") or 0)
        if data is not None and now - at < CONTEXT_TTL_SEC:
            return data, str(_context_entry.get("fp") or ""), True

    fresh = build_crm_context(db)
    fp = _fingerprint(fresh)
    with _lock:
        _context_entry["data"] = fresh
        _context_entry["at"] = now
        _context_entry["fp"] = fp
    return fresh, fp, False


def invalidate_context_cache() -> None:
    with _lock:
        _context_entry["at"] = 0.0
        _context_entry["data"] = None
        _context_entry["fp"] = ""
        _answer_entries.clear()


def _answer_key(message: str, context_fp: str) -> str:
    normalized = " ".join((message or "").lower().split())
    digest = hashlib.sha1(f"{context_fp}|{normalized}".encode("utf-8")).hexdigest()
    return digest


def get_cached_answer(message: str, context_fp: str) -> AiChatResponse | None:
    key = _answer_key(message, context_fp)
    now = time.time()
    with _lock:
        entry = _answer_entries.get(key)
        if not entry:
            return None
        if now - float(entry["at"]) > ANSWER_TTL_SEC:
            _answer_entries.pop(key, None)
            return None
        payload: AiChatResponse = entry["payload"]
        return AiChatResponse(
            reply=payload.reply,
            insights=[*payload.insights],
            suggested_actions=[*payload.suggested_actions],
        )


def store_cached_answer(message: str, context_fp: str, payload: AiChatResponse) -> None:
    key = _answer_key(message, context_fp)
    with _lock:
        _answer_entries[key] = {
            "at": time.time(),
            "payload": AiChatResponse(
                reply=payload.reply,
                insights=list(payload.insights),
                suggested_actions=list(payload.suggested_actions),
            ),
        }
        if len(_answer_entries) > 64:
            oldest = sorted(_answer_entries.items(), key=lambda item: item[1]["at"])[:16]
            for old_key, _ in oldest:
                _answer_entries.pop(old_key, None)


def cache_stats() -> dict[str, Any]:
    with _lock:
        age = time.time() - float(_context_entry.get("at") or 0) if _context_entry.get("data") else None
        return {
            "context_cached": _context_entry.get("data") is not None,
            "context_age_sec": round(age, 1) if age is not None else None,
            "context_ttl_sec": CONTEXT_TTL_SEC,
            "answer_entries": len(_answer_entries),
            "answer_ttl_sec": ANSWER_TTL_SEC,
        }


def with_db_session(factory: Callable[[], Session], fn: Callable[[Session], T]) -> T:
    db = factory()
    try:
        return fn(db)
    finally:
        db.close()

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request

from app.env_bootstrap import load_local_env

load_local_env()

TRY_MAX = int(os.environ.get("AI_CRM_TRY_MAX", "5") or "5")
DAY_MAX = int(os.environ.get("AI_CRM_DAILY_MAX", "48") or "48")
GAP_MS = int(os.environ.get("AI_CRM_GAP_MS", "1500") or "1500")
WINDOW_MS = 24 * 60 * 60 * 1000
UNLIMITED_MAX = 9999
STORE = Path(
    os.environ.get(
        "AI_CRM_LIMIT_FILE",
        str(Path(__file__).resolve().parent.parent / "data" / "limits.json"),
    )
)

_lock = threading.RLock()
_inflight: set[str] = set()
_mem: dict[str, Any] = {"day": "", "global": 0, "ips": {}}


def _flag_on(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _flag_off(name: str, default: str = "1") -> bool:
    return (os.environ.get(name, default) or default).strip().lower() in {"0", "false", "no", "off"}


def limits_enabled() -> bool:
    """Limits stay on in production (Passenger). Disable only on local PC with AI_CRM_LOCAL_DEV=1."""
    if _flag_on("AI_CRM_PASSENGER"):
        return True
    if not _flag_on("AI_CRM_LOCAL_DEV"):
        return True
    if _flag_on("AI_CRM_DISABLE_LIMITS"):
        return False
    if _flag_off("AI_CRM_LIMITS_ENABLED", "1"):
        return False
    if TRY_MAX <= 0:
        return False
    return True


def _utc_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_store() -> None:
    global _mem
    try:
        raw = json.loads(STORE.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("ips"), dict):
            _mem = {
                "day": str(raw.get("day") or _utc_day()),
                "global": int(raw.get("global") or 0),
                "ips": raw["ips"],
            }
    except Exception:
        _mem = {"day": _utc_day(), "global": 0, "ips": {}}
    if _mem.get("day") != _utc_day():
        _mem = {"day": _utc_day(), "global": 0, "ips": {}}


def _save_store() -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STORE.with_suffix(".tmp")
    tmp.write_text(json.dumps(_mem, separators=(",", ":")), encoding="utf-8")
    tmp.replace(STORE)


_load_store()


def _row(ip: str) -> dict[str, int]:
    now = int(datetime.now(timezone.utc).timestamp() * 1000)
    if _mem.get("day") != _utc_day():
        _mem.clear()
        _mem.update({"day": _utc_day(), "global": 0, "ips": {}})
    ips: dict[str, Any] = _mem["ips"]
    hit = ips.get(ip)
    if not hit or int(hit.get("resetAt") or 0) <= now:
        fresh = {"used": 0, "resetAt": now + WINDOW_MS, "lastAt": 0}
        ips[ip] = fresh
        return fresh
    return hit


def _is_loopback(remote: str) -> bool:
    return remote in {"127.0.0.1", "::1", "::ffff:127.0.0.1"}


def _clean_ip(value: str) -> str | None:
    ip = value.strip()
    if not ip or ip.lower() == "unknown":
        return None
    if not re.fullmatch(r"[\w.:]+", ip):
        return None
    return ip


def client_ip(request: Request) -> str:
    remote = request.client.host if request.client else "0.0.0.0"
    trust = os.environ.get("AI_CRM_TRUST_PROXY", "").strip() == "1"
    if trust and _is_loopback(remote):
        real = request.headers.get("x-real-ip")
        if real:
            parsed = _clean_ip(real)
            if parsed:
                return parsed
        xf = request.headers.get("x-forwarded-for")
        if xf:
            parts = [part.strip() for part in xf.split(",") if part.strip()]
            if parts:
                parsed = _clean_ip(parts[-1])
                if parsed:
                    return parsed
    return remote


def usage_for(ip: str) -> dict[str, Any]:
    if not limits_enabled():
        return {
            "used": 0,
            "left": UNLIMITED_MAX,
            "max": UNLIMITED_MAX,
            "resetAt": 0,
            "dailyLeft": UNLIMITED_MAX,
            "limitsEnabled": False,
        }
    with _lock:
        hit = _row(ip)
        used = max(0, min(TRY_MAX, int(hit.get("used") or 0)))
        return {
            "used": used,
            "left": max(0, TRY_MAX - used),
            "max": TRY_MAX,
            "resetAt": int(hit.get("resetAt") or 0),
            "dailyLeft": max(0, DAY_MAX - int(_mem.get("global") or 0)),
            "limitsEnabled": True,
        }


def begin_flight(ip: str) -> bool:
    if not limits_enabled():
        return True
    with _lock:
        if ip in _inflight:
            return False
        _inflight.add(ip)
        return True


def end_flight(ip: str) -> None:
    if not limits_enabled():
        return
    with _lock:
        _inflight.discard(ip)


def peek_try(ip: str) -> dict[str, Any]:
    if not limits_enabled():
        return {
            "ok": True,
            "reason": "",
            "used": 0,
            "left": UNLIMITED_MAX,
            "max": UNLIMITED_MAX,
        }
    with _lock:
        hit = _row(ip)
        used = int(hit.get("used") or 0)
        if int(_mem.get("global") or 0) >= DAY_MAX:
            return {
                "ok": False,
                "reason": "daily",
                "used": used,
                "left": max(0, TRY_MAX - used),
                "max": TRY_MAX,
            }
        if used >= TRY_MAX:
            return {"ok": False, "reason": "spent", "used": used, "left": 0, "max": TRY_MAX}
        return {
            "ok": True,
            "reason": "",
            "used": used,
            "left": max(0, TRY_MAX - used),
            "max": TRY_MAX,
        }


def take_try(ip: str) -> dict[str, Any]:
    if not limits_enabled():
        return {
            "ok": True,
            "reason": "",
            "used": 0,
            "left": UNLIMITED_MAX,
            "max": UNLIMITED_MAX,
        }
    with _lock:
        hit = _row(ip)
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        used = int(hit.get("used") or 0)
        if int(_mem.get("global") or 0) >= DAY_MAX:
            return {
                "ok": False,
                "reason": "daily",
                "used": used,
                "left": max(0, TRY_MAX - used),
                "max": TRY_MAX,
            }
        if used >= TRY_MAX:
            return {"ok": False, "reason": "spent", "used": used, "left": 0, "max": TRY_MAX}
        last_at = int(hit.get("lastAt") or 0)
        if last_at and now - last_at < GAP_MS:
            return {
                "ok": False,
                "reason": "wait",
                "used": used,
                "left": max(0, TRY_MAX - used),
                "max": TRY_MAX,
            }
        hit["used"] = used + 1
        hit["lastAt"] = now
        _mem["global"] = int(_mem.get("global") or 0) + 1
        _save_store()
        return {
            "ok": True,
            "reason": "",
            "used": hit["used"],
            "left": max(0, TRY_MAX - hit["used"]),
            "max": TRY_MAX,
        }


def deny_message(reason: str) -> str:
    if reason == "spent":
        return f"You have used all {TRY_MAX} AI analyst prompts for now. Come back later."
    if reason == "daily":
        return "The AI-CRM demo hit its daily prompt budget. Come back tomorrow."
    if reason == "wait":
        return "Give it a moment, then try again."
    if reason == "busy":
        return "One AI prompt at a time."
    return "AI analyst is temporarily unavailable."

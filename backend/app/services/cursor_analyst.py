from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.schemas import AiChatResponse
from app.services.crm_cache import get_cached_answer, get_cached_context, store_cached_answer
from app.services.crm_context import heuristic_answer

SANDBOX = Path(__file__).resolve().parent.parent.parent / "sandbox"
MODEL = os.environ.get("AI_CRM_MODEL", "auto").strip() or "auto"
PROMPT_CAP = 1800


def _apply_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue
        name, value = trimmed.split("=", 1)
        name = name.strip()
        value = value.strip()
        if name and name not in os.environ:
            os.environ[name] = value


def load_cursor_env() -> None:
    ordered: list[Path] = []
    explicit = (os.environ.get("AI_CRM_ENV_FILE") or os.environ.get("CHART_ENV_FILE") or "").strip()
    if explicit:
        ordered.append(Path(explicit).expanduser())
    home = Path.home()
    ordered.extend(
        [
            home / ".config" / "etorrefranca4-chart" / "env",
            home / "etorrefranca4-secrets" / "chart.env",
        ]
    )
    for path in ordered:
        _apply_env_file(path)


def cursor_keys() -> list[str]:
    load_cursor_env()
    names = sorted(
        (name for name in os.environ if re.fullmatch(r"API_KEY\d+", name)),
        key=lambda n: int(n[7:]),
        reverse=True,
    )
    found: list[str] = []
    seen: set[str] = set()
    for name in [*names, "CURSOR_API_KEY"]:
        value = (os.environ.get(name) or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        found.append(value)
    return found


def extract_json(text: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.I)
    raw = (fenced.group(1) if fenced else text).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no json object")
    return json.loads(raw[start : end + 1])


def normalize_payload(obj: dict[str, Any], fallback: AiChatResponse) -> AiChatResponse:
    reply = obj.get("reply")
    insights = obj.get("insights")
    actions = obj.get("suggested_actions") or obj.get("actions")
    return AiChatResponse(
        reply=(str(reply).strip() if isinstance(reply, str) and reply.strip() else fallback.reply),
        insights=(
            [str(x).strip() for x in insights if str(x).strip()][:8]
            if isinstance(insights, list)
            else fallback.insights
        ),
        suggested_actions=(
            [str(x).strip() for x in actions if str(x).strip()][:5]
            if isinstance(actions, list)
            else fallback.suggested_actions
        ),
    )


def build_prompt(message: str, context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are AI-CRM Analyst for a live CRM workspace.",
            "Answer ONLY from CONTEXT. Do not invent accounts, deals, or numbers.",
            "Do not use tools, read files, browse, or explore a codebase.",
            "Return JSON only (no markdown fences):",
            '{"reply":"2-4 sentences","insights":["up to 5 short bullets"],"suggested_actions":["up to 4"]}',
            f"CONTEXT:{json.dumps(context, separators=(',', ':'))}",
            f"USER:{(message or '').strip()[:600]}",
        ]
    )[:PROMPT_CAP]


class CursorAnalystPool:
    """Reusable local Cursor agent with tools disabled for low-latency CRM chat."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._client: Any = None
        self._agent: Any = None
        self._key: str | None = None
        self._failed_keys: set[str] = set()

    def close(self) -> None:
        with self._lock:
            if self._agent is not None:
                try:
                    self._agent.close()
                except Exception:
                    pass
                self._agent = None
            if self._client is not None:
                try:
                    self._client.close()
                except Exception:
                    pass
                self._client = None

    def _ensure(self, key: str) -> None:
        from cursor_sdk import Agent, AgentOptions, CursorClient, LocalAgentOptions

        SANDBOX.mkdir(parents=True, exist_ok=True)
        cwd = str(SANDBOX)
        if self._client is None:
            self._client = CursorClient.launch_bridge(
                workspace=cwd,
                allow_api_key_env_fallback=True,
            )
        if self._agent is None or self._key != key:
            if self._agent is not None:
                try:
                    self._agent.close()
                except Exception:
                    pass
            self._agent = Agent.create(
                AgentOptions(
                    api_key=key,
                    model=MODEL,
                    local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                    tools=[],
                ),
                client=self._client,
            )
            self._key = key

    def ask(self, prompt: str) -> tuple[str, dict[str, Any]]:
        keys = [k for k in cursor_keys() if k not in self._failed_keys]
        if not keys:
            raise RuntimeError("No Cursor API key configured for AI-CRM")

        last_err: Exception | None = None
        for key in keys:
            with self._lock:
                try:
                    self._ensure(key)
                    assert self._agent is not None
                    t0 = time.time()
                    result = self._agent.send(prompt).wait()
                    meta = {
                        "model": MODEL,
                        "status": str(result.status),
                        "duration_ms": int(getattr(result, "duration_ms", 0) or 0),
                        "wall_ms": int((time.time() - t0) * 1000),
                        "provider": "cursor",
                    }
                    if str(result.status) != "finished":
                        raise RuntimeError(f"cursor run {result.status}")
                    text = (result.result or "").strip()
                    if not text:
                        raise RuntimeError("cursor returned empty result")
                    return text, meta
                except Exception as err:
                    last_err = err
                    message = str(err).lower()
                    if "plan_required" in message or "authentication" in message:
                        self._failed_keys.add(key)
                    self.close()
                    continue
        raise RuntimeError(str(last_err) if last_err else "cursor unavailable")


_POOL = CursorAnalystPool()


def answer_with_cursor(db: Session, message: str) -> AiChatResponse:
    context, context_fp, context_hit = get_cached_context(db)
    cached = get_cached_answer(message, context_fp)
    if cached is not None:
        cached.insights = [
            *[i for i in cached.insights if not i.startswith("Cursor ") and not i.startswith("Cache ")],
            "Cache hit · reused CRM context + prior answer",
        ][:8]
        return cached

    fallback = heuristic_answer(db, message)
    prompt = build_prompt(message, context)
    try:
        text, meta = _POOL.ask(prompt)
        payload = normalize_payload(extract_json(text), fallback)
        source = "context cache" if context_hit else "fresh snapshot"
        payload.insights = [
            *payload.insights,
            f"Live analyst · {meta['duration_ms']}ms · {source}",
        ][:8]
        store_cached_answer(message, context_fp, payload)
        return payload
    except Exception as err:
        soft = heuristic_answer(db, message)
        soft.reply = (
            f"{soft.reply} (Local fallback - Cursor SDK unavailable: {str(err)[:160]})"
        )
        soft.suggested_actions = [
            "Set AI_CRM_ENV_FILE or CURSOR_API_KEY for live Cursor LLM answers",
            *soft.suggested_actions,
        ][:5]
        return soft

from __future__ import annotations

import os
from pathlib import Path

from app.env_bootstrap import load_local_env

load_local_env()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.routers import analytics, companies, contacts, deals, leads, workspace
from app.seed import seed_if_empty

APP_ROOT = Path(__file__).resolve().parent.parent.parent
CLIENT_DIST = APP_ROOT / "client" / "dist"


def _normalize_base(value: str, *, trailing_slash: bool) -> str:
    text = (value or "").strip() or "/"
    if not text.startswith("/"):
        text = f"/{text}"
    if trailing_slash:
        return text if text.endswith("/") else f"{text}/"
    return text.rstrip("/") or "/"


SAMPLE_BASE = _normalize_base(
    os.environ.get("AI_CRM_SAMPLE_BASE", "/sample/ai-crm/"),
    trailing_slash=True,
)
SAMPLE_PREFIX = SAMPLE_BASE.rstrip("/") or "/sample/ai-crm"
API_BASE = _normalize_base(
    os.environ.get("AI_CRM_API_BASE", "/api/ai-crm"),
    trailing_slash=False,
)
PASSENGER = os.environ.get("AI_CRM_PASSENGER", "").strip() == "1"

ALLOWED_ORIGINS = {
    item.strip()
    for item in os.environ.get(
        "AI_CRM_CORS_ORIGINS",
        "https://torrefranca.site,http://127.0.0.1:3096,http://localhost:3096",
    ).split(",")
    if item.strip()
}


def build_api() -> FastAPI:
    api_app = FastAPI(title="AI-CRM API", version="0.1.0")
    api_app.include_router(contacts.router)
    api_app.include_router(companies.router)
    api_app.include_router(deals.router)
    api_app.include_router(leads.router)
    api_app.include_router(workspace.router)
    api_app.include_router(analytics.router)

    @api_app.get("/health")
    def health():
        from app.services.crm_cache import cache_stats

        return {"ok": True, "service": "ai-crm", "cache": cache_stats()}

    return api_app


api = build_api()
app = api if PASSENGER else FastAPI(title="AI-CRM", version="0.1.0")

if not PASSENGER:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(ALLOWED_ORIGINS) or ["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.mount(f"{SAMPLE_PREFIX}/api", api)
    app.mount(API_BASE, api)


@app.on_event("startup")
def on_startup():
    import fcntl
    import time

    lock_path = Path(__file__).resolve().parent.parent / "data" / "startup.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lock_file:
        for _ in range(40):
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(0.25)
        else:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    def warm_cursor() -> None:
        try:
            from app.services.crm_cache import get_cached_context
            from app.services.cursor_analyst import _POOL, build_prompt, cursor_keys

            keys = cursor_keys()
            db_warm = SessionLocal()
            try:
                get_cached_context(db_warm)
            finally:
                db_warm.close()
            if not keys:
                return
            with _POOL._lock:
                _POOL._ensure(keys[0])
            _POOL.ask(build_prompt("ping", {"kpis": {"ok": True}, "warm": True}))
        except Exception:
            pass

    import threading

    threading.Thread(target=warm_cursor, daemon=True, name="ai-crm-cursor-warm").start()


if not PASSENGER and CLIENT_DIST.exists():
    assets = CLIENT_DIST / "assets"
    if assets.exists():
        app.mount(
            f"{SAMPLE_PREFIX}/assets",
            StaticFiles(directory=assets),
            name="assets",
        )

    @app.get(SAMPLE_PREFIX)
    @app.get(f"{SAMPLE_PREFIX}/")
    @app.get(f"{SAMPLE_PREFIX}/{{full_path:path}}")
    def spa(full_path: str = ""):
        index = CLIENT_DIST / "index.html"
        candidate = CLIENT_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)

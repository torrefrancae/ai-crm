from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.routers import analytics, companies, contacts, deals, leads, workspace
from app.seed import seed_if_empty

APP_ROOT = Path(__file__).resolve().parent.parent.parent
CLIENT_DIST = APP_ROOT / "client" / "dist"
URL_PREFIX = "/sample/ai-crm"

app = FastAPI(title="AI-CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI()
api.include_router(contacts.router)
api.include_router(companies.router)
api.include_router(deals.router)
api.include_router(leads.router)
api.include_router(workspace.router)
api.include_router(analytics.router)


@api.get("/health")
def health():
    return {"ok": True, "service": "ai-crm"}


app.mount(f"{URL_PREFIX}/api", api)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


if CLIENT_DIST.exists():
    assets = CLIENT_DIST / "assets"
    if assets.exists():
        app.mount(
            f"{URL_PREFIX}/assets",
            StaticFiles(directory=assets),
            name="assets",
        )

    @app.get(URL_PREFIX)
    @app.get(f"{URL_PREFIX}/")
    @app.get(f"{URL_PREFIX}/{{full_path:path}}")
    def spa(full_path: str = ""):
        index = CLIENT_DIST / "index.html"
        candidate = CLIENT_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
os.chdir(ROOT)
sys.path.insert(0, str(BACKEND))

os.environ.setdefault("AI_CRM_PASSENGER", "1")
os.environ.setdefault("AI_CRM_TRUST_PROXY", "1")
os.environ.setdefault("AI_CRM_MODEL", "auto")

from a2wsgi import ASGIMiddleware
from app.main import api

application = ASGIMiddleware(api)

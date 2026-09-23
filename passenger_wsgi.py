import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
os.chdir(ROOT)
sys.path.insert(0, str(BACKEND))

os.environ["AI_CRM_PASSENGER"] = "1"
os.environ["AI_CRM_TRUST_PROXY"] = "1"
os.environ.setdefault("AI_CRM_MODEL", "auto")
os.environ.setdefault("AI_CRM_SAMPLE_BASE", "/sample/ai-crm/")
os.environ.setdefault("AI_CRM_API_BASE", "/api/ai-crm")
os.environ["AI_CRM_LIMITS_ENABLED"] = "1"
os.environ.pop("AI_CRM_DISABLE_LIMITS", None)
os.environ.pop("AI_CRM_LOCAL_DEV", None)

from a2wsgi import ASGIMiddleware
from app.main import api

application = ASGIMiddleware(api)

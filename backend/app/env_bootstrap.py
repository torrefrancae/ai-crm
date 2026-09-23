from __future__ import annotations

import os
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent.parent


def _apply_env_file(path: Path, *, override: bool = False) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue
        name, value = trimmed.split("=", 1)
        name = name.strip()
        value = value.strip().strip("'").strip('"')
        if not name:
            continue
        if override or name not in os.environ:
            os.environ[name] = value


def load_local_env() -> None:
    """Load apps/ai-crm/.env then .env.local for local PCs only.

    Skip entirely under Passenger so a copied .env on the server cannot turn limits off.
    """
    if (os.environ.get("AI_CRM_PASSENGER") or "").strip() == "1":
        os.environ["AI_CRM_LIMITS_ENABLED"] = "1"
        os.environ.pop("AI_CRM_DISABLE_LIMITS", None)
        return
    _apply_env_file(APP_ROOT / ".env", override=False)
    _apply_env_file(APP_ROOT / ".env.local", override=True)

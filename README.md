# AI-CRM

Full-workspace CRM demo with a FastAPI backend and a React client. The twist is an AI Analyst that answers pipeline, lead, risk, and team questions from live seeded CRM data.

## Stack

- Frontend: React, TypeScript, Vite, Recharts
- Backend: FastAPI, SQLAlchemy, SQLite
- Local path: `/sample/ai-crm/`

## Features

- AI Analyst powered by Cursor SDK (`auto` model routing, tools disabled, warm agent pool)
- Dashboard KPIs and charts
- Pipeline board with drag-and-drop stage moves
- Contacts, companies, leads
- Tasks, activities, inbox
- Reports
- AI Analyst chat grounded in CRM metrics
- Settings overview

## Paths (mono sample on torrefranca.site)

| Role | Default | Env |
|------|---------|-----|
| Sample SPA | `/sample/ai-crm/` | `AI_CRM_SAMPLE_BASE` / `VITE_BASE` |
| Main-site API | `/api/ai-crm` | `AI_CRM_API_BASE` / `VITE_API_BASE` |

Copy `.env.example` to a gitignored `.env` for local overrides only. Do not deploy `.env` to Z.com.

## Prompt limits

Limits are **always on** under Passenger / production (`AI_CRM_PASSENGER=1`). Deployed API forces `AI_CRM_LIMITS_ENABLED=1` and ignores local disable flags.

| Env | Default | Meaning |
|-----|---------|---------|
| `AI_CRM_LOCAL_DEV` | unset | Must be `1` on this PC before disable is allowed |
| `AI_CRM_LIMITS_ENABLED` | `1` | Set `0` only with `AI_CRM_LOCAL_DEV=1` on this PC |
| `AI_CRM_DISABLE_LIMITS` | unset | Alternate local off switch (also requires `AI_CRM_LOCAL_DEV=1`) |
| `AI_CRM_TRY_MAX` | `5` | Live prompts per visitor window |
| `AI_CRM_DAILY_MAX` | `48` | Global daily live-prompt budget |
| `AI_CRM_GAP_MS` | `1500` | Cooldown between live asks |

Local `.env` on this PC only:

```bash
AI_CRM_LOCAL_DEV=1
AI_CRM_LIMITS_ENABLED=0
```

## Local run

```bash
./serve.sh --headless --port=3096
```

Open `http://127.0.0.1:3096/sample/ai-crm/`

API health: `http://127.0.0.1:3096/api/ai-crm/health`

Stop with:

```bash
./serve.sh --restore --port=3096
```

## API

- Local unified: `GET /api/ai-crm/health` and `GET /sample/ai-crm/api/health`
- Production: `GET https://torrefranca.site/api/ai-crm/health`


## Cursor API

Local `serve.sh` loads keys from `AI_CRM_ENV_FILE` or `~/.config/etorrefranca4-chart/env` (`API_KEY*` / `CURSOR_API_KEY`).

Speed path:
- compact CRM JSON snapshot injected into the prompt
- `tools=[]` so the agent does not explore files
- reusable local bridge + agent across requests
- default model `auto` (override with `AI_CRM_MODEL` privately; never shown in UI)

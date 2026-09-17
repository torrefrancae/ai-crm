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

## Local run

```bash
./serve.sh --headless --port=3096
```

Open `http://127.0.0.1:3096/sample/ai-crm/`

Stop with:

```bash
./serve.sh --restore --port=3096
```

## API

Health check: `GET /sample/ai-crm/api/health`

OpenAPI docs when the API app is reached through the mounted path, or run uvicorn directly against `app.main:api` during backend-only work.


## Cursor API

Local `serve.sh` loads keys from `AI_CRM_ENV_FILE` or `~/.config/etorrefranca4-chart/env` (`API_KEY*` / `CURSOR_API_KEY`).

Speed path:
- compact CRM JSON snapshot injected into the prompt
- `tools=[]` so the agent does not explore files
- reusable local bridge + agent across requests
- default model `auto` (override with `AI_CRM_MODEL` privately; never shown in UI)

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-3096}"
MODE=""
cd "$ROOT"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --headless) MODE="headless" ;;
    --restore|stop) MODE="restore" ;;
    --port=*) PORT="${1#*=}" ;;
    --port)
      shift
      PORT="${1:-}"
      ;;
    -h|--help)
      echo "Usage: $0 [--headless] [--restore] [--port=3096]"
      exit 0
      ;;
  esac
  shift
done

if [[ -s "${HOME}/.nvm/nvm.sh" ]]; then
  unset npm_config_prefix || true
  # shellcheck disable=SC1091
  . "${HOME}/.nvm/nvm.sh"
  nvm use >/dev/null 2>&1 || nvm use 22 >/dev/null 2>&1 || true
fi

PID_FILE="$ROOT/.serve-headless-${PORT}.pid"
LOG_FILE="$ROOT/debug.log"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"

is_up() {
  curl -fsS -o /dev/null --max-time 2 "http://127.0.0.1:${PORT}/sample/ai-crm/api/health" >/dev/null 2>&1
}

stop_old() {
  if [[ -f "$PID_FILE" ]]; then
    old="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${old:-}" ]] && kill -0 "$old" 2>/dev/null; then
      pkill -P "$old" 2>/dev/null || true
      kill "$old" 2>/dev/null || true
      sleep 1
      kill -9 "$old" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi
}

if [[ "$MODE" == "restore" ]]; then
  stop_old
  echo "stopped ai-crm"
  exit 0
fi

if [[ "$MODE" != "headless" ]]; then
  echo "Use --headless for detached local serving (required in this workspace)."
  exit 1
fi

stop_old
: >"$LOG_FILE"

if [[ -n "${AI_CRM_ENV_FILE:-}" && -f "${AI_CRM_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "${AI_CRM_ENV_FILE}"
  set +a
elif [[ -f "${HOME}/.config/etorrefranca4-chart/env" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "${HOME}/.config/etorrefranca4-chart/env"
  set +a
fi
export AI_CRM_MODEL="${AI_CRM_MODEL:-composer-2.5}"

if [[ ! -d "$VENV" ]]; then
  (cd "$BACKEND" && uv venv .venv) >>"$LOG_FILE" 2>&1
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
uv pip install -r "$BACKEND/requirements.txt" >>"$LOG_FILE" 2>&1

if [[ ! -d "$ROOT/client/node_modules" ]]; then
  (cd "$ROOT/client" && npm install) >>"$LOG_FILE" 2>&1
fi

(cd "$ROOT/client" && npm run build) >>"$LOG_FILE" 2>&1

mkdir -p "$BACKEND/sandbox"

nohup sh -c "cd \"$BACKEND\" && AI_CRM_MODEL=\"${AI_CRM_MODEL}\" \"$VENV/bin/uvicorn\" app.main:app --host 127.0.0.1 --port $PORT 2>&1 | tr -d '\\000' | stdbuf -oL strings -n 1 >> \"$LOG_FILE\"" >/dev/null 2>&1 &
echo $! >"$PID_FILE"

sleep 5
if is_up; then
  echo "ai-crm ready on http://127.0.0.1:${PORT}/sample/ai-crm/"
else
  echo "ai-crm failed to start; see debug.log" >&2
  tail -n 40 "$LOG_FILE" >&2 || true
  exit 1
fi

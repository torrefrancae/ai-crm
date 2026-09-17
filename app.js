'use strict';
const http = require('http');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = __dirname;
const PORT = Number(process.env.AI_CRM_UPSTREAM_PORT || 13096);
const PREFIX = '/api/ai-crm';
const UPSTREAM = `http://127.0.0.1:${PORT}`;
const PID_FILE = path.join(ROOT, 'tmp', 'uvicorn.pid');
const LOG_FILE = path.join(ROOT, 'tmp', 'uvicorn.log');
const LOCK_FILE = path.join(ROOT, 'tmp', 'uvicorn.lock');
let lastSpawnAt = 0;

function pidAlive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function rewritePath(urlPath) {
  if (urlPath === PREFIX || urlPath.startsWith(`${PREFIX}/`) || urlPath.startsWith(`${PREFIX}?`)) {
    const rest = urlPath.slice(PREFIX.length);
    return rest.startsWith('/') || rest.startsWith('?') || rest === '' ? rest || '/' : `/${rest}`;
  }
  return urlPath;
}

function isUp(cb) {
  const req = http.get(`${UPSTREAM}/health`, (res) => {
    res.resume();
    cb(res.statusCode === 200);
  });
  req.on('error', () => cb(false));
  req.setTimeout(1500, () => {
    req.destroy();
    cb(false);
  });
}

function ensureUpstream() {
  const now = Date.now();
  if (now - lastSpawnAt < 8000) return;
  fs.mkdirSync(path.join(ROOT, 'tmp'), { recursive: true });
  try {
    if (fs.existsSync(PID_FILE)) {
      const old = Number(fs.readFileSync(PID_FILE, 'utf8').trim());
      if (Number.isFinite(old) && pidAlive(old)) return;
    }
  } catch {
    /* ignore */
  }

  let lockFd;
  try {
    lockFd = fs.openSync(LOCK_FILE, 'wx');
  } catch {
    return;
  }

  lastSpawnAt = now;
  try {
    const out = fs.openSync(LOG_FILE, 'a');
    const child = spawn(
      path.join(ROOT, '.venv', 'bin', 'uvicorn'),
      ['app.main:api', '--host', '127.0.0.1', '--port', String(PORT), '--workers', '1'],
      {
        cwd: path.join(ROOT, 'backend'),
        env: {
          ...process.env,
          AI_CRM_PASSENGER: '1',
          AI_CRM_TRUST_PROXY: '1',
          AI_CRM_MODEL: process.env.AI_CRM_MODEL || 'auto',
          PATH: `${path.join(ROOT, '.venv', 'bin')}:${process.env.PATH || ''}`,
        },
        detached: true,
        stdio: ['ignore', out, out],
      }
    );
    fs.writeFileSync(PID_FILE, String(child.pid));
    child.unref();
  } finally {
    try {
      fs.closeSync(lockFd);
      fs.unlinkSync(LOCK_FILE);
    } catch {
      /* ignore */
    }
  }
}

function proxy(req, res) {
  const opts = {
    hostname: '127.0.0.1',
    port: PORT,
    path: rewritePath(req.url || '/'),
    method: req.method,
    headers: { ...req.headers, host: `127.0.0.1:${PORT}` },
  };
  const upstream = http.request(opts, (upRes) => {
    res.writeHead(upRes.statusCode || 502, upRes.headers);
    upRes.pipe(res);
  });
  upstream.on('error', () => {
    if (!res.headersSent) res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'AI-CRM API warming up. Retry in a moment.' }));
    ensureUpstream();
  });
  req.pipe(upstream);
}

ensureUpstream();
const server = http.createServer((req, res) => {
  isUp((ok) => {
    if (!ok) {
      ensureUpstream();
      setTimeout(() => proxy(req, res), 1200);
      return;
    }
    proxy(req, res);
  });
});

server.listen();

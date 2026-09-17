import { useTheme } from "@src/hooks/useTheme";

export function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="panel-grid">
      <div className="card stack">
        <div className="panel-title">
          <h3>Workspace</h3>
        </div>
        <div className="list-row">
          <div>
            <strong>Product</strong>
            <span>AI-CRM local demo</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Backend</strong>
            <span>FastAPI + SQLAlchemy + SQLite</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Frontend</strong>
            <span>React + Vite + TypeScript</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Base path</strong>
            <span>/sample/ai-crm/</span>
          </div>
        </div>
      </div>
      <div className="card stack">
        <div className="panel-title">
          <h3>Appearance</h3>
        </div>
        <div className="list-row">
          <div>
            <strong>Theme</strong>
            <span>Light is the default; choice is saved in this browser</span>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              type="button"
              className={`btn ${theme === "light" ? "primary" : ""}`}
              onClick={() => setTheme("light")}
            >
              Light
            </button>
            <button
              type="button"
              className={`btn ${theme === "dark" ? "primary" : ""}`}
              onClick={() => setTheme("dark")}
            >
              Dark
            </button>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Currency</strong>
            <span>USD display formatting</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>Seed data</strong>
            <span>Auto-loads on first API boot</span>
          </div>
        </div>
        <div className="list-row">
          <div>
            <strong>AI Analyst</strong>
            <span>Deterministic analytics over live tables</span>
          </div>
        </div>
      </div>
    </div>
  );
}

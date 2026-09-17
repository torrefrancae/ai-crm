export function SettingsPage() {
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
          <h3>Demo defaults</h3>
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

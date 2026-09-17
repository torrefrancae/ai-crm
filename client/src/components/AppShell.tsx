import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  Activity,
  Building2,
  ChartColumn,
  Inbox,
  LayoutDashboard,
  Moon,
  Sparkles,
  Sun,
  Target,
  UserRound,
  CheckSquare,
  Settings,
  ContactRound,
} from "lucide-react";
import { useTheme } from "@src/hooks/useTheme";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/pipeline", label: "Pipeline", icon: Target },
  { to: "/contacts", label: "Contacts", icon: ContactRound },
  { to: "/companies", label: "Companies", icon: Building2 },
  { to: "/leads", label: "Leads", icon: UserRound },
  { to: "/tasks", label: "Tasks", icon: CheckSquare },
  { to: "/activities", label: "Activities", icon: Activity },
  { to: "/inbox", label: "Inbox", icon: Inbox },
  { to: "/ai", label: "AI Analyst", icon: Sparkles },
  { to: "/reports", label: "Reports", icon: ChartColumn },
  { to: "/settings", label: "Settings", icon: Settings },
];

const titles: Record<string, { title: string; blurb: string }> = {
  "/": {
    title: "Dashboard",
    blurb: "Pipeline health, forecast, and the work that needs attention today.",
  },
  "/pipeline": {
    title: "Pipeline",
    blurb: "Drag deals across stages or advance them with one click.",
  },
  "/contacts": {
    title: "Contacts",
    blurb: "People across accounts, owners, and recent touchpoints.",
  },
  "/companies": {
    title: "Companies",
    blurb: "Account health, industry mix, and revenue footprint.",
  },
  "/leads": {
    title: "Leads",
    blurb: "Inbound and outbound prospects ranked by intent score.",
  },
  "/tasks": {
    title: "Tasks",
    blurb: "Follow-ups and blockers tied to live opportunities.",
  },
  "/activities": {
    title: "Activities",
    blurb: "Calls, emails, meetings, and notes across the team.",
  },
  "/inbox": {
    title: "Inbox",
    blurb: "Customer threads that need a reply or a handoff.",
  },
  "/ai": {
    title: "AI Analyst",
    blurb: "Ask about forecast, risk, leads, and team performance.",
  },
  "/reports": {
    title: "Reports",
    blurb: "Stage mix, owner contribution, and account health signals.",
  },
  "/settings": {
    title: "Settings",
    blurb: "Workspace preferences for this local demo environment.",
  },
};

export function AppShell() {
  const { pathname } = useLocation();
  const meta = titles[pathname] ?? titles["/"];
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span className="brand-orb" aria-hidden />
            <div>
              <h1>AI-CRM</h1>
              <p>Revenue workspace</p>
            </div>
          </div>
        </div>
        <nav className="nav">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          Local FastAPI workspace with seeded B2B accounts. AI Analyst reads live CRM
          metrics, not generic chat fluff.
        </div>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <h2>{meta.title}</h2>
            <p>{meta.blurb}</p>
          </div>
          <div className="theme-toggle">
            <button
              type="button"
              className="btn"
              onClick={toggleTheme}
              aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
            >
              {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
              {theme === "light" ? "Dark" : "Light"}
            </button>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}

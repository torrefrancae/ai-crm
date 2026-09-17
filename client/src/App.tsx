import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@src/components/AppShell";
import { DashboardPage } from "@src/pages/DashboardPage";
import { PipelinePage } from "@src/pages/PipelinePage";
import { ContactsPage } from "@src/pages/ContactsPage";
import { CompaniesPage } from "@src/pages/CompaniesPage";
import { LeadsPage } from "@src/pages/LeadsPage";
import { TasksPage } from "@src/pages/TasksPage";
import { ActivitiesPage } from "@src/pages/ActivitiesPage";
import { InboxPage } from "@src/pages/InboxPage";
import { AiAnalystPage } from "@src/pages/AiAnalystPage";
import { ReportsPage } from "@src/pages/ReportsPage";
import { SettingsPage } from "@src/pages/SettingsPage";

export default function App() {
  return (
    <BrowserRouter basename="/sample/ai-crm">
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="pipeline" element={<PipelinePage />} />
          <Route path="contacts" element={<ContactsPage />} />
          <Route path="companies" element={<CompaniesPage />} />
          <Route path="leads" element={<LeadsPage />} />
          <Route path="tasks" element={<TasksPage />} />
          <Route path="activities" element={<ActivitiesPage />} />
          <Route path="inbox" element={<InboxPage />} />
          <Route path="ai" element={<AiAnalystPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

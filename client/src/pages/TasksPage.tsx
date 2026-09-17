import { useEffect, useState } from "react";
import { api, shortDate } from "@src/lib/api";
import type { TaskItem } from "@src/types/crm";
import { LoadingState } from "@src/components/LoadingState";

export function TasksPage() {
  const [rows, setRows] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () =>
    api
      .tasks()
      .then(setRows)
      .finally(() => setLoading(false));

  useEffect(() => {
    void load();
  }, []);

  async function toggleDone(task: TaskItem) {
    const next = task.status === "done" ? "todo" : "done";
    const updated = await api.updateTask(task.id, {
      title: task.title,
      description: task.description,
      status: next,
      priority: task.priority,
      due_date: task.due_date,
      owner: task.owner,
      related_type: task.related_type,
      related_id: task.related_id,
    });
    setRows((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
  }

  if (loading) return <LoadingState label="Loading tasks..." />;

  return (
    <div className="stack">
      {rows.map((task) => (
        <div className="list-row card" key={task.id}>
          <div>
            <strong style={{ textDecoration: task.status === "done" ? "line-through" : "none" }}>
              {task.title}
            </strong>
            <span>
              {task.owner} · due {shortDate(task.due_date)} · {task.description}
            </span>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span
              className={`badge ${
                task.priority === "high" ? "danger" : task.priority === "medium" ? "warn" : "accent"
              }`}
            >
              {task.priority}
            </span>
            <button className="btn" onClick={() => void toggleDone(task)}>
              {task.status === "done" ? "Reopen" : "Complete"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

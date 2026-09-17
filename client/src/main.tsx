import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "@src/App";
import { applyTheme, getStoredTheme } from "@src/lib/theme";
import "@src/styles/app.css";

applyTheme(getStoredTheme());

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

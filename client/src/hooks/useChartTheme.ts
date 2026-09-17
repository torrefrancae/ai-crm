import { useSyncExternalStore } from "react";
import { readCssVar } from "@src/lib/theme";

function subscribe(onStoreChange: () => void) {
  const observer = new MutationObserver(onStoreChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
  return () => observer.disconnect();
}

function getThemeSnapshot() {
  return document.documentElement.getAttribute("data-theme") ?? "light";
}

export function useChartTheme() {
  const theme = useSyncExternalStore(subscribe, getThemeSnapshot, () => "light");

  return {
    theme,
    muted: readCssVar("--chart-muted", "#5f7385"),
    accent: readCssVar("--accent", "#1f9a86"),
    accent2: readCssVar("--accent-2", "#c98a12"),
    grid: readCssVar("--line", "rgba(20, 36, 48, 0.1)"),
    tooltip: {
      background: readCssVar("--chart-tooltip-bg", "#ffffff"),
      border: `1px solid ${readCssVar("--chart-tooltip-border", "rgba(20, 36, 48, 0.12)")}`,
      borderRadius: 12,
      color: readCssVar("--text", "#15202b"),
    },
  };
}

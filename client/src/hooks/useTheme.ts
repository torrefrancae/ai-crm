import { useEffect, useState } from "react";
import {
  applyTheme,
  getStoredTheme,
  persistTheme,
  type ThemeMode,
} from "@src/lib/theme";

export function useTheme() {
  const [theme, setTheme] = useState<ThemeMode>(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
    persistTheme(theme);
  }, [theme]);

  function toggleTheme() {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  }

  return { theme, setTheme, toggleTheme };
}

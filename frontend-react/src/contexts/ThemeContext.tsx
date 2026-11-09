"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export type Theme = "dark" | "light";
export type AccentColor = "teal" | "purple" | "blue" | "amber" | "rose";

export const ACCENT_COLORS: AccentColor[] = [
  "teal",
  "purple",
  "blue",
  "amber",
  "rose",
];

const THEME_STORAGE_KEY = "aso-theme";
const COLOR_STORAGE_KEY = "aso-color";

interface ThemeContextValue {
  theme: Theme;
  color: AccentColor;
  accentColor: AccentColor;
  setTheme: (theme: Theme) => void;
  setColor: (color: AccentColor) => void;
  setAccentColor: (color: AccentColor) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function isTheme(value: string | null): value is Theme {
  return value === "dark" || value === "light";
}

function isAccent(value: string | null): value is AccentColor {
  return value !== null && ACCENT_COLORS.includes(value as AccentColor);
}

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark");
}

function applyColor(color: AccentColor) {
  const root = document.documentElement;
  root.setAttribute("data-theme", color);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");
  const [color, setColorState] = useState<AccentColor>("teal");

  useEffect(() => {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const storedColor = localStorage.getItem(COLOR_STORAGE_KEY) || localStorage.getItem("aso-accent");
    const nextTheme: Theme = isTheme(storedTheme) ? storedTheme : "dark";
    const nextColor: AccentColor = isAccent(storedColor) ? storedColor : "teal";
    setThemeState(nextTheme);
    setColorState(nextColor);
    applyTheme(nextTheme);
    applyColor(nextColor);
  }, []);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    applyTheme(next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
  }, []);

  const setColor = useCallback((next: AccentColor) => {
    setColorState(next);
    applyColor(next);
    localStorage.setItem(COLOR_STORAGE_KEY, next);
    localStorage.setItem("aso-accent", next);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      const next: Theme = prev === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(THEME_STORAGE_KEY, next);
      return next;
    });
  }, []);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      color,
      accentColor: color,
      setTheme,
      setColor,
      setAccentColor: setColor,
      toggleTheme,
    }),
    [theme, color, setTheme, setColor, toggleTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

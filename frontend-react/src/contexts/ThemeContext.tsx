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
const ACCENT_STORAGE_KEY = "aso-accent";

interface ThemeContextValue {
  theme: Theme;
  accentColor: AccentColor;
  setTheme: (theme: Theme) => void;
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
  root.setAttribute("data-theme", theme);
  root.classList.toggle("dark", theme === "dark");
}

function applyAccent(color: AccentColor) {
  document.documentElement.setAttribute("data-accent", color);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");
  const [accentColor, setAccentState] = useState<AccentColor>("teal");

  // Hydrate from localStorage after mount (client-only) and sync the DOM.
  useEffect(() => {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const storedAccent = localStorage.getItem(ACCENT_STORAGE_KEY);
    const nextTheme: Theme = isTheme(storedTheme) ? storedTheme : "dark";
    const nextAccent: AccentColor = isAccent(storedAccent) ? storedAccent : "teal";
    setThemeState(nextTheme);
    setAccentState(nextAccent);
    applyTheme(nextTheme);
    applyAccent(nextAccent);
  }, []);

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next);
    applyTheme(next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
  }, []);

  const setAccentColor = useCallback((next: AccentColor) => {
    setAccentState(next);
    applyAccent(next);
    localStorage.setItem(ACCENT_STORAGE_KEY, next);
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
    () => ({ theme, accentColor, setTheme, setAccentColor, toggleTheme }),
    [theme, accentColor, setTheme, setAccentColor, toggleTheme]
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

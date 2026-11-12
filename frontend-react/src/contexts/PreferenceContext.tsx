"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useTheme as useNextTheme } from "next-themes";
import api from "@/lib/api";

export type ThemeMode = "light" | "dark" | "system";
export type Palette = "teal" | "rose" | "blue" | "purple" | "amber";
export type FontSize = "small" | "medium" | "large";

export const PALETTES: Palette[] = ["teal", "rose", "blue", "purple", "amber"];
export const FONT_SIZES: FontSize[] = ["small", "medium", "large"];

interface PreferenceContextValue {
  themeMode: ThemeMode;
  palette: Palette;
  fontSize: FontSize;
  enabled_features: string[];
  setThemeMode: (mode: ThemeMode) => void;
  setPalette: (palette: Palette) => void;
  setFontSize: (size: FontSize) => void;
  setEnabledFeatures: (features: string[]) => void;
  loading: boolean;
}

const PreferenceContext = createContext<PreferenceContextValue | null>(null);

function applyPalette(palette: Palette) {
  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-palette", palette);
  }
}

function applyFontSize(size: FontSize) {
  if (typeof document !== "undefined") {
    document.documentElement.classList.remove("font-small", "font-medium", "font-large");
    document.documentElement.classList.add(`font-${size}`);
  }
}

export function PreferenceProvider({ children }: { children: React.ReactNode }) {
  const { setTheme: setNextTheme } = useNextTheme();
  const [themeMode, setThemeModeState] = useState<ThemeMode>("system");
  const [palette, setPaletteState] = useState<Palette>("teal");
  const [fontSize, setFontSizeState] = useState<FontSize>("medium");
  const [enabledFeatures, setEnabledFeaturesState] = useState<string[]>([
    "chat",
    "dashboard",
    "calendar",
    "shop",
    "social",
    "jobs",
    "inventory",
    "settings",
    "profile",
    "health",
    "home",
    "integrations",
    "vault",
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api
        .get("/preferences")
        .then((res) => {
          const data = res.data;
          if (data) {
            if (data.theme_mode) {
              setThemeModeState(data.theme_mode);
              setNextTheme(data.theme_mode);
            }
            if (data.theme_palette) {
              setPaletteState(data.theme_palette);
              applyPalette(data.theme_palette);
            }
            if (data.font_size) {
              setFontSizeState(data.font_size);
              applyFontSize(data.font_size);
            }
            if (data.enabled_features) {
              setEnabledFeaturesState(data.enabled_features);
            }
          }
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [setNextTheme]);

  const patchPrefs = useCallback(async (updates: Record<string, any>) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    try {
      await api.patch("/preferences", updates);
    } catch {}
  }, []);

  const setThemeMode = useCallback(
    (mode: ThemeMode) => {
      setThemeModeState(mode);
      setNextTheme(mode);
      patchPrefs({ theme_mode: mode });
    },
    [setNextTheme, patchPrefs]
  );

  const setPalette = useCallback(
    (p: Palette) => {
      setPaletteState(p);
      applyPalette(p);
      patchPrefs({ theme_palette: p });
    },
    [patchPrefs]
  );

  const setFontSize = useCallback(
    (fs: FontSize) => {
      setFontSizeState(fs);
      applyFontSize(fs);
      patchPrefs({ font_size: fs });
    },
    [patchPrefs]
  );

  const setEnabledFeatures = useCallback(
    (features: string[]) => {
      setEnabledFeaturesState(features);
      patchPrefs({ enabled_features: features });
    },
    [patchPrefs]
  );

  const value = useMemo(
    () => ({
      themeMode,
      palette,
      fontSize,
      enabled_features: enabledFeatures,
      setThemeMode,
      setPalette,
      setFontSize,
      setEnabledFeatures,
      loading,
    }),
    [themeMode, palette, fontSize, enabledFeatures, setThemeMode, setPalette, setFontSize, setEnabledFeatures, loading]
  );

  return (
    <PreferenceContext.Provider value={value}>
      {children}
    </PreferenceContext.Provider>
  );
}

export function usePreferences(): PreferenceContextValue {
  const context = useContext(PreferenceContext);
  if (!context) {
    throw new Error("usePreferences must be used within a PreferenceProvider");
  }
  return context;
}

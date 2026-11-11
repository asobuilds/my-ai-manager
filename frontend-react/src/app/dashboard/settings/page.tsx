"use client";

import { useState } from "react";
import { Check, Lock, Moon, Palette, X, Plus, Minus } from "lucide-react";
import { usePreferences, Palette as PaletteType } from "@/contexts/PreferenceContext";

interface PasswordForm {
  current: string;
  next: string;
  confirm: string;
}

const EMPTY_PASSWORD_FORM: PasswordForm = { current: "", next: "", confirm: "" };

export default function SettingsPage() {
  const {
    themeMode,
    palette,
    fontSize,
    setThemeMode,
    setPalette,
    setFontSize,
    enabled_features,
    setEnabledFeatures,
    loading: prefsLoading,
  } = usePreferences();

  const FEATURES = [
    { label: "Dashboard", value: "dashboard" },
    { label: "AI Chat", value: "chat" },
    { label: "Data Inventory", value: "inventory" },
    { label: "Shop Manager", value: "shop" },
    { label: "Social Media", value: "social" },
    { label: "Job Tracker", value: "jobs" },
    { label: "Calendar", value: "calendar" },
    { label: "Health", value: "health" },
    { label: "Home Management", value: "home" },
    { label: "Integrations", value: "integrations" },
  ];

  function toggleFeature(value: string) {
    if (prefsLoading) return;
    const next = enabled_features.includes(value)
      ? enabled_features.filter((f) => f !== value)
      : [...enabled_features, value];
    setEnabledFeatures(next);
  }

  const [passwordForm, setPasswordForm] = useState<PasswordForm>(EMPTY_PASSWORD_FORM);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  function showToast(msg: string, type: "ok" | "err") {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }

  function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!passwordForm.current) {
      showToast("Enter your current password", "err");
      return;
    }
    if (passwordForm.next.length < 8) {
      showToast("New password must be at least 8 characters", "err");
      return;
    }
    if (passwordForm.next !== passwordForm.confirm) {
      showToast("Passwords do not match", "err");
      return;
    }
    setPasswordForm(EMPTY_PASSWORD_FORM);
    showToast("Password change will be enabled soon", "ok");
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* ── Header ── */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--foreground)]">⚙️ Settings</h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Manage your account security and personalize your workspace.
        </p>
      </div>

      {/* ── Toast ── */}
      {toast && (
        <div
          className="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl border text-sm"
          style={{
            background: toast.type === "ok" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
            borderColor: toast.type === "ok" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)",
            color: toast.type === "ok" ? "#34d399" : "#f87171",
          }}
        >
          {toast.type === "ok" ? <Check size={14} /> : <X size={14} />}
          {toast.msg}
        </div>
      )}

      <div className="space-y-6">
        {/* ── Password ── */}
        <section
          className="glass-card glass-card-transition p-6 border"
          style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Lock size={16} style={{ color: "#2dd4bf" }} />
            <h2 className="text-base font-semibold text-[var(--foreground)]">Change Password</h2>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mb-5">
            Choose a strong password with at least 8 characters.
          </p>

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                Current Password
              </label>
              <input
                type="password"
                value={passwordForm.current}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, current: e.target.value })
                }
                placeholder="••••••••"
                className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordForm.next}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, next: e.target.value })
                  }
                  placeholder="••••••••"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordForm.confirm}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, confirm: e.target.value })
                  }
                  placeholder="••••••••"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>
            </div>

            <div className="pt-1">
              <button
                type="submit"
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.98]"
                style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
              >
                Update Password
              </button>
            </div>
          </form>
        </section>

        {/* ── Appearance ── */}
        <section
          className="glass-card glass-card-transition p-6 border"
          style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Palette size={16} style={{ color: "#a78bfa" }} />
            <h2 className="text-base font-semibold text-[var(--foreground)]">Appearance</h2>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mb-5">
            Personalize your workspace theme, palette, and font size.
          </p>

          {/* Theme Mode toggle */}
          <div className="flex items-center justify-between py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <div className="flex items-center gap-3">
              <Moon size={16} className="text-[var(--muted-foreground)]" />
              <div>
                <p className="text-sm font-medium text-[var(--foreground)]">Theme Mode</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Choose light, dark, or system mode
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 bg-[var(--muted)] p-1 rounded-xl">
              {(["light", "dark", "system"] as const).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setThemeMode(mode)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                    themeMode === mode
                      ? "bg-[var(--primary)] text-[var(--primary-foreground)] shadow-sm"
                      : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          {/* Palette / Color dropdown */}
          <div className="flex items-center justify-between py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <div className="flex items-center gap-3">
              <Palette size={16} className="text-[var(--muted-foreground)]" />
              <div>
                <p className="text-sm font-medium text-[var(--foreground)]">Theme Palette</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Primary accent color for buttons and active states
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={palette}
                onChange={(e) => setPalette(e.target.value as PaletteType)}
                className="rounded-lg border px-3 py-2 text-sm bg-transparent focus:outline-none"
                style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
              >
                {[
                  { label: "Teal", value: "teal" },
                  { label: "Blue", value: "blue" },
                  { label: "Purple", value: "purple" },
                  { label: "Amber", value: "amber" },
                  { label: "Rose", value: "rose" },
                ].map((option) => (
                  <option key={option.value} value={option.value} style={{ background: "#1a1a2e", color: "#f0f0f5" }}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Font Size selector */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <span className="text-base">🔤</span>
              <div>
                <p className="text-sm font-medium text-[var(--foreground)]">Font Size</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Adjust interface text scale
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 bg-[var(--muted)] p-1 rounded-xl">
              {(["small", "medium", "large"] as const).map((size) => (
                <button
                  key={size}
                  type="button"
                  onClick={() => setFontSize(size)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                    fontSize === size
                      ? "bg-[var(--primary)] text-[var(--primary-foreground)] shadow-sm"
                      : "text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ── System Features ── */}
        <section
          className="glass-card glass-card-transition p-6 border"
          style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Plus size={16} style={{ color: "#a78bfa" }} />
            <h2 className="text-base font-semibold text-[var(--foreground)]">System Features</h2>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mb-5">
            Enable or disable workspace modules. Changes are saved to your account.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {FEATURES.map((feature) => {
              const enabled = enabled_features.includes(feature.value);
              return (
                <label
                  key={feature.value}
                  className="glass-card-transition flex items-center gap-3 p-3 border cursor-pointer"
                  style={{
                    borderColor: enabled
                      ? "rgba(45,212,191,0.4)"
                      : "rgba(255,255,255,0.06)",
                    background: enabled ? "rgba(45,212,191,0.08)" : "transparent",
                  }}
                  onClick={() => toggleFeature(feature.value)}
                >
                  <input
                    type="checkbox"
                    checked={enabled}
                    className="rounded border-[var(--border)] text-[var(--primary)] focus:ring-[var(--primary)] bg-transparent"
                    readOnly
                  />
                  {enabled ? (
                    <Minus size={14} className="text-[var(--primary)] shrink-0" />
                  ) : (
                    <Plus size={14} className="text-[var(--muted-foreground)] shrink-0" />
                  )}
                  <span className="text-sm text-[var(--foreground)]">{feature.label}</span>
                </label>
              );
            })}
          </div>
          {prefsLoading && (
            <p className="text-xs text-[var(--muted-foreground)] mt-3">
              Saving…
            </p>
          )}
        </section>
      </div>
    </div>
  );
}

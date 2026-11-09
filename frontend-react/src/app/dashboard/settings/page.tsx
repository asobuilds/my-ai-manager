"use client";

import { useState } from "react";
import { Check, Lock, Moon, Palette, X } from "lucide-react";
import { useTheme, AccentColor } from "@/contexts/ThemeContext";

const ACCENT_OPTIONS: { label: string; value: AccentColor; color: string }[] = [
  { label: "Teal", value: "teal", color: "#2dd4bf" },
  { label: "Blue", value: "blue", color: "#3b82f6" },
  { label: "Purple", value: "purple", color: "#a78bfa" },
  { label: "Amber", value: "amber", color: "#f59e0b" },
  { label: "Rose", value: "rose", color: "#f43f5e" },
];

interface PasswordForm {
  current: string;
  next: string;
  confirm: string;
}

const EMPTY_PASSWORD_FORM: PasswordForm = { current: "", next: "", confirm: "" };

export default function SettingsPage() {
  const { theme, accentColor, setTheme, setAccentColor } = useTheme();
  const darkMode = theme === "dark";
  const currentAccentColorObj = ACCENT_OPTIONS.find((o) => o.value === accentColor) || ACCENT_OPTIONS[0];

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
          className="rounded-2xl border p-6"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.06)" }}
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
          className="rounded-2xl border p-6"
          style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Palette size={16} style={{ color: "#a78bfa" }} />
            <h2 className="text-base font-semibold text-[var(--foreground)]">Appearance</h2>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mb-5">
            Personalize how your workspace looks. These preferences are preview-only for now.
          </p>

          {/* Dark mode toggle */}
          <div className="flex items-center justify-between py-3 border-b" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <div className="flex items-center gap-3">
              <Moon size={16} className="text-[var(--muted-foreground)]" />
              <div>
                <p className="text-sm font-medium text-[var(--foreground)]">Dark Mode</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Use the dark theme across the dashboard
                </p>
              </div>
            </div>
            <button
              type="button"
              role="switch"
              aria-checked={darkMode}
              onClick={() => setTheme(darkMode ? "light" : "dark")}
              className="relative w-11 h-6 rounded-full transition-colors shrink-0"
              style={{ background: darkMode ? "var(--primary)" : "rgba(15,23,42,0.2)" }}
            >
              <span
                className="absolute top-0.5 w-5 h-5 rounded-full bg-white transition-all shadow-sm"
                style={{ left: darkMode ? "22px" : "2px" }}
              />
            </button>
          </div>

          {/* Accent color */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Palette size={16} className="text-[var(--muted-foreground)]" />
              <div>
                <p className="text-sm font-medium text-[var(--foreground)]">Theme Accent Color</p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  Highlight color used for buttons and active states
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span
                className="w-4 h-4 rounded-full border shadow-sm"
                style={{ background: currentAccentColorObj.color, borderColor: "rgba(255,255,255,0.2)" }}
              />
              <select
                value={accentColor}
                onChange={(e) => setAccentColor(e.target.value as AccentColor)}
                className="rounded-lg border px-3 py-2 text-sm bg-transparent focus:outline-none"
                style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
              >
                {ACCENT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value} style={{ background: theme === "dark" ? "#1a1a2e" : "#ffffff", color: theme === "dark" ? "#f0f0f5" : "#0f172a" }}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

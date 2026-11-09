"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, Loader2, User, X } from "lucide-react";
import api from "@/lib/api";

interface Me {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  phone: string | null;
  location: string | null;
  bio: string | null;
  resume_text: string | null;
  is_active: boolean;
  created_at: string;
}

interface ProfileForm {
  full_name: string;
  phone: string;
  bio: string;
}

function initials(name: string | null, email: string): string {
  const source = (name || email || "").trim();
  if (!source) return "?";
  const parts = source.split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return source.slice(0, 2).toUpperCase();
}

export default function ProfilePage() {
  const [me, setMe] = useState<Me | null>(null);
  const [form, setForm] = useState<ProfileForm>({ full_name: "", phone: "", bio: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const loadProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<Me>("/auth/me");
      setMe(res.data);
      setForm({
        full_name: res.data.full_name ?? "",
        phone: res.data.phone ?? "",
        bio: res.data.bio ?? "",
      });
    } catch {
      setError("Failed to load your profile. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put<Me>("/profile", {
        full_name: form.full_name.trim() || null,
        phone: form.phone.trim() || null,
        bio: form.bio.trim() || null,
      });
      // Backend currently persists phone/bio; keep the edited name in the
      // optimistic UI as well.
      setMe((prev) =>
        prev ? { ...prev, ...res.data, full_name: form.full_name.trim() || null } : res.data
      );
      showToast("Profile updated", "ok");
    } catch {
      showToast("Failed to update profile", "err");
    } finally {
      setSaving(false);
    }
  }

  const roleLabel = me?.role === "owner" ? "Owner" : "Staff";
  const roleStyle =
    me?.role === "owner"
      ? { background: "rgba(45,212,191,0.15)", color: "#2dd4bf" }
      : { background: "rgba(59,130,246,0.15)", color: "#60a5fa" };

  return (
    <div className="max-w-3xl mx-auto">
      {/* ── Header ── */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--foreground)]">👤 Profile</h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Manage your account details and personal information.
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

      {loading ? (
        <div className="space-y-4">
          <div
            className="rounded-2xl border p-6 animate-pulse"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.06)" }}
          >
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-[var(--muted)]" />
              <div className="space-y-2">
                <div className="h-4 w-40 rounded bg-[var(--muted)]" />
                <div className="h-3 w-56 rounded bg-[var(--muted)]" />
              </div>
            </div>
          </div>
          <div className="h-64 rounded-2xl bg-[var(--muted)] animate-pulse" />
        </div>
      ) : error ? (
        <div
          className="rounded-xl border flex flex-col items-center justify-center py-16 text-center gap-3"
          style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)" }}
        >
          <p className="text-sm text-red-400">{error}</p>
          <button
            onClick={loadProfile}
            className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
            style={{ borderColor: "rgba(239,68,68,0.3)", color: "#f87171" }}
          >
            Retry
          </button>
        </div>
      ) : me ? (
        <div className="space-y-6">
          {/* ── Identity card ── */}
          <section
            className="rounded-2xl border p-6"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.06)" }}
          >
            <div className="flex flex-col sm:flex-row sm:items-center gap-5">
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold shrink-0"
                style={{
                  background: "linear-gradient(135deg, #2dd4bf, #a78bfa)",
                  color: "#0a0a0f",
                }}
              >
                {initials(me.full_name, me.email)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="text-lg font-semibold text-[var(--foreground)] truncate">
                    {me.full_name || "Unnamed user"}
                  </p>
                  <span
                    className="text-[10px] px-2 py-0.5 rounded-full font-medium uppercase tracking-wide"
                    style={roleStyle}
                  >
                    {roleLabel}
                  </span>
                </div>
                <p className="text-sm text-[var(--muted-foreground)] mt-0.5 truncate">
                  {me.email}
                </p>
              </div>
              <button
                type="button"
                onClick={() => showToast("Avatar upload coming soon", "ok")}
                className="shrink-0 px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
                style={{ borderColor: "rgba(255,255,255,0.1)", color: "var(--muted-foreground)" }}
              >
                Change Photo
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6 pt-5 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                  Email
                </p>
                <p className="text-sm text-[var(--foreground)] mt-1 truncate">{me.email}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                  Full Name
                </p>
                <p className="text-sm text-[var(--foreground)] mt-1 truncate">
                  {me.full_name || "—"}
                </p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)]">
                  Role
                </p>
                <p className="text-sm text-[var(--foreground)] mt-1">{roleLabel}</p>
              </div>
            </div>
          </section>

          {/* ── Edit form ── */}
          <section
            className="rounded-2xl border p-6"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.06)" }}
          >
            <div className="flex items-center gap-2 mb-5">
              <User size={16} style={{ color: "#2dd4bf" }} />
              <h2 className="text-base font-semibold text-[var(--foreground)]">Edit Profile</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Full Name
                </label>
                <input
                  type="text"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  placeholder="Your name"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Phone
                </label>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  placeholder="+1 555 000 0000"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Bio
                </label>
                <textarea
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  placeholder="Tell us a little about yourself…"
                  rows={3}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none resize-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>

              <div className="pt-1">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-40 hover:opacity-90 active:scale-[0.98]"
                  style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
                >
                  {saving ? (
                    <span className="flex items-center gap-2">
                      <Loader2 size={14} className="animate-spin" />
                      Saving…
                    </span>
                  ) : (
                    "Save Changes"
                  )}
                </button>
              </div>
            </form>
          </section>
        </div>
      ) : null}
    </div>
  );
}

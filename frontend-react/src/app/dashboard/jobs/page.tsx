"use client";

import { useEffect, useState } from "react";
import {
  Plus,
  Briefcase,
  Building2,
  User,
  Calendar,
  X,
  Check,
  Loader2,
} from "lucide-react";
import api from "@/lib/api";

interface Job {
  id: string;
  company_name: string;
  job_title: string;
  status: string;
  notes: string;
  applied_date: string | null;
}

const STATUS_ORDER = ["applied", "interviewing", "offered", "rejected"] as const;
const STATUS_LABELS: Record<string, string> = {
  applied: "Applied",
  interviewing: "Interviewing",
  offered: "Offered",
  rejected: "Rejected",
};

const STATUS_COLORS: Record<string, string> = {
  applied: "#3b82f6",
  interviewing: "#f59e0b",
  offered: "#10b981",
  rejected: "#ef4444",
};

const COLUMN_BG: Record<string, string> = {
  applied: "rgba(59,130,246,0.06)",
  interviewing: "rgba(245,158,11,0.06)",
  offered: "rgba(16,185,129,0.06)",
  rejected: "rgba(239,68,68,0.06)",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ company_name: "", job_title: "", notes: "" });
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  useEffect(() => {
    api
      .get("/jobs")
      .then((r) => setJobs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function setStatus(jobId: string, status: string) {
    api
      .patch(`/jobs/${jobId}`, { status })
      .then(() => {
        setJobs((prev) =>
          prev.map((j) => (j.id === jobId ? { ...j, status } : j))
        );
        showToast("Status updated", "ok");
      })
      .catch(() => showToast("Failed to update", "err"));
  }

  function showToast(msg: string, type: "ok" | "err") {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.company_name.trim() || !form.job_title.trim()) return;
    setSubmitting(true);
    try {
      const r = await api.post("/jobs", {
        company_name: form.company_name,
        job_title: form.job_title,
        notes: form.notes || null,
        status: "applied",
      });
      setJobs((prev) => [...prev, r.data]);
      setShowModal(false);
      setForm({ company_name: "", job_title: "", notes: "" });
      showToast("Application added!", "ok");
    } catch {
      showToast("Failed to add application", "err");
    } finally {
      setSubmitting(false);
    }
  }

  const grouped = Object.fromEntries(
    STATUS_ORDER.map((s) => [s, jobs.filter((j) => j.status === s)])
  ) as Record<string, Job[]>;

  return (
    <div className="max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--foreground)]">💼 Job Tracker</h1>
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Manage your career pipeline. Track applications across stages and never miss a follow-up.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.97]"
          style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
        >
          <Plus size={16} />
          New Application
        </button>
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

      {/* ── Kanban Board ── */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-2xl border p-4 space-y-3 animate-pulse" style={{ background: "var(--card)", borderColor: "rgba(255,255,255,0.06)" }}>
              <div className="h-4 w-24 rounded bg-[var(--muted)]" />
              {[1, 2, 3].map((j) => (
                <div key={j} className="h-20 rounded-xl bg-[var(--muted)]" />
              ))}
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {STATUS_ORDER.map((status) => (
            <div
              key={status}
              className="rounded-2xl border p-4 min-h-[400px] bg-white/5 backdrop-blur-md border-white/10"
            >
              {/* Column header */}
              <div className="flex items-center gap-2 mb-4">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ background: STATUS_COLORS[status] }}
                />
                <h2 className="text-sm font-semibold text-[var(--foreground)]">
                  {STATUS_LABELS[status]}
                </h2>
                <span
                  className="ml-auto text-xs font-mono px-2 py-0.5 rounded-full"
                  style={{
                    background: "rgba(255,255,255,0.06)",
                    color: "var(--muted-foreground)",
                  }}
                >
                  {grouped[status].length}
                </span>
              </div>

              {/* Cards */}
              <div className="space-y-3">
                {grouped[status].map((job) => (
                  <div
                    key={job.id}
                    className="rounded-xl border p-3 transition-all hover:border-[var(--primary)]/30 bg-white/5 backdrop-blur-sm border-white/10"
                  >
                    <div className="flex items-start gap-2">
                      <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                        style={{ background: `${STATUS_COLORS[job.status]}20` }}
                      >
                        <Briefcase size={14} style={{ color: STATUS_COLORS[job.status] }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-[var(--foreground)] truncate">
                          {job.company_name}
                        </p>
                        <p className="text-xs text-[var(--muted-foreground)] truncate">
                          {job.job_title}
                        </p>
                      </div>
                    </div>

                    {job.notes && (
                      <p className="text-xs text-[var(--muted-foreground)] mt-2 line-clamp-2">
                        {job.notes}
                      </p>
                    )}

                    {/* Status selector */}
                    <select
                      value={job.status}
                      onChange={(e) => setStatus(job.id, e.target.value)}
                      className="mt-3 w-full text-xs rounded-lg border px-2 py-1.5 bg-transparent focus:outline-none"
                      style={{
                        borderColor: "rgba(255,255,255,0.1)",
                        color: "var(--foreground)",
                      }}
                    >
                      {STATUS_ORDER.map((s) => (
                        <option key={s} value={s} style={{ background: "#1a1a2e" }}>
                          {STATUS_LABELS[s]}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>

              {grouped[status].length === 0 && (
                <p className="text-xs text-[var(--muted-foreground)] text-center mt-8 opacity-50">
                  No applications
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── New Application Modal ── */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
          onClick={() => setShowModal(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl border overflow-hidden"
            style={{
              background: "#0d0d14",
              borderColor: "rgba(255,255,255,0.1)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.5)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <h2 className="text-base font-semibold text-[var(--foreground)]">
                ➕ New Application
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Company Name *
                </label>
                <input
                  type="text"
                  value={form.company_name}
                  onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                  placeholder="e.g. Google"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                  required
                />
              </div>
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Job Title *
                </label>
                <input
                  type="text"
                  value={form.job_title}
                  onChange={(e) => setForm({ ...form, job_title: e.target.value })}
                  placeholder="e.g. Software Engineer"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                  required
                />
              </div>
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Notes
                </label>
                <textarea
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Salary, location, referral info…"
                  rows={3}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none resize-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 rounded-xl text-sm font-medium border transition-colors hover:bg-[var(--accent)]"
                  style={{ borderColor: "rgba(255,255,255,0.1)", color: "var(--muted-foreground)" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !form.company_name.trim() || !form.job_title.trim()}
                  className="flex-1 py-2.5 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-40 hover:opacity-90"
                  style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
                >
                  {submitting ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 size={14} className="animate-spin" />
                      Adding…
                    </span>
                  ) : (
                    "Add Application"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

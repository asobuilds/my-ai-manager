"use client";

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowUp,
  CheckCircle2,
  Inbox,
  Loader2,
  Search,
  X,
  Send,
} from "lucide-react";
import api from "@/lib/api";

interface Message {
  id: string;
  platform: string;
  sender: string;
  subject: string;
  content: string;
  priority_score: number;
  category: string;
  status: string;
  received_at: string | null;
}

const PLATFORM_EMOJI: Record<string, string> = {
  gmail: "📧",
  linkedin: "💼",
  whatsapp: "💬",
  facebook: "📘",
  twitter: "🐦",
};

const CATEGORY_COLORS: Record<string, string> = {
  work: "rgba(59,130,246,0.15)",
  job: "rgba(167,139,250,0.15)",
  personal: "rgba(45,212,191,0.15)",
  newsletter: "rgba(245,158,11,0.15)",
  urgent: "rgba(239,68,68,0.15)",
};

const CATEGORY_TEXT_COLORS: Record<string, string> = {
  work: "#3b82f6",
  job: "#a78bfa",
  personal: "#2dd4bf",
  newsletter: "#f59e0b",
  urgent: "#ef4444",
};

export default function InventoryPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalMsg, setModalMsg] = useState<Message | null>(null);
  const [draft, setDraft] = useState("");
  const [drafting, setDrafting] = useState(false);
  const [draftDone, setDraftDone] = useState(false);
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");

  useEffect(() => {
    api
      .get("/messages")
      .then((r) => setMessages(r.data))
      .catch(() => setError("Failed to load messages."))
      .finally(() => setLoading(false));
  }, []);

  const critical = messages.filter((m) => m.priority_score >= 9).length;
  const action = messages.filter((m) => m.priority_score >= 7 && m.priority_score <= 8).length;
  const low = messages.filter((m) => m.priority_score < 7).length;

  const categories = useMemo(() => {
    const set = new Set<string>();
    messages.forEach((m) => {
      if (m.category) set.add(m.category.toLowerCase());
    });
    return ["all", ...Array.from(set)];
  }, [messages]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return messages.filter((m) => {
      const matchesCategory =
        activeCategory === "all" || m.category?.toLowerCase() === activeCategory;
      const matchesQuery =
        !q ||
        [m.sender, m.subject, m.content, m.platform].some((value) =>
          (value || "").toLowerCase().includes(q)
        );
      return matchesCategory && matchesQuery;
    });
  }, [messages, query, activeCategory]);

  function openModal(msg: Message) {
    setModalMsg(msg);
    setDraft("");
    setDraftDone(false);
  }

  async function handleDraft() {
    if (!modalMsg) return;
    setDrafting(true);
    try {
      const r = await api.post("/messages/draft", { message_id: modalMsg.id });
      setDraft(r.data.draft);
      setDraftDone(true);
    } catch {
      setDraft("Failed to generate draft. Try again.");
    } finally {
      setDrafting(false);
    }
  }

  const kpiCards = [
    {
      label: "Critical",
      value: critical,
      sub: "Needs immediate attention",
      icon: ArrowUp,
      color: "#ef4444",
      bg: "rgba(239,68,68,0.08)",
      border: "rgba(239,68,68,0.2)",
    },
    {
      label: "Action Needed",
      value: action,
      sub: "Follow up within 48 hrs",
      icon: AlertTriangle,
      color: "#f59e0b",
      bg: "rgba(245,158,11,0.08)",
      border: "rgba(245,158,11,0.2)",
    },
    {
      label: "Low Priority",
      value: low,
      sub: "Review when convenient",
      icon: CheckCircle2,
      color: "#2dd4bf",
      bg: "rgba(45,212,191,0.08)",
      border: "rgba(45,212,191,0.2)",
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--foreground)]">📦 Data Inventory</h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Your central command center. Aso filters your connected data by priority so you can focus on what matters.
        </p>
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {kpiCards.map((k) => (
          <div
            key={k.label}
            className="rounded-xl p-5 border bg-white/5 backdrop-blur-md border-white/10"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
                {k.label}
              </span>
              <k.icon size={16} style={{ color: k.color }} />
            </div>
            {loading ? (
              <div className="h-9 w-12 rounded bg-[var(--muted)] animate-pulse" />
            ) : (
              <p className="text-4xl font-bold leading-none" style={{ color: k.color }}>
                {k.value}
              </p>
            )}
            <p className="text-xs text-[var(--muted-foreground)] mt-2">{k.sub}</p>
          </div>
        ))}
      </div>

      {/* ── Messages ── */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <h2 className="text-base font-semibold text-[var(--foreground)]">
            All Messages
            <span className="ml-2 text-xs font-normal text-[var(--muted-foreground)]">
              {filtered.length} of {messages.length}
            </span>
          </h2>
          <div className="relative sm:w-64">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)]"
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search messages…"
              className="w-full rounded-lg border pl-9 pr-3 py-2 text-sm bg-transparent text-[var(--foreground)] focus:outline-none"
              style={{ borderColor: "rgba(255,255,255,0.08)" }}
              onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
              onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
            />
          </div>
        </div>

        {/* Filter tabs */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          {categories.map((cat) => {
            const active = activeCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className="px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-colors"
                style={
                  active
                    ? { background: "rgba(45,212,191,0.15)", color: "#2dd4bf" }
                    : {
                        background: "rgba(255,255,255,0.04)",
                        color: "var(--muted-foreground)",
                      }
                }
              >
                {cat === "all" ? "All" : cat}
              </button>
            );
          })}
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="rounded-xl border border-[var(--border)] p-4 animate-pulse"
                style={{ background: "var(--card)" }}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-[var(--muted)] shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 w-24 rounded bg-[var(--muted)]" />
                    <div className="h-4 w-3/4 rounded bg-[var(--muted)]" />
                    <div className="h-3 w-full rounded bg-[var(--muted)]" />
                  </div>
                  <div className="h-8 w-20 rounded-lg bg-[var(--muted)]" />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div
            className="rounded-xl border flex flex-col items-center justify-center py-16 text-center"
            style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)" }}
          >
            <p className="text-sm text-red-400">{error}</p>
          </div>
        ) : filtered.length === 0 ? (
          <div
            className="rounded-xl border border-dashed flex flex-col items-center justify-center py-20 text-center"
            style={{ borderColor: "rgba(255,255,255,0.08)" }}
          >
            <Inbox size={32} className="text-[var(--muted-foreground)] mb-3 opacity-50" />
            <p className="text-sm text-[var(--muted-foreground)]">
              {messages.length === 0
                ? "No messages yet. Connect Gmail and sync to get started."
                : "No messages match your search or filter."}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {[...filtered]
              .sort((a, b) => b.priority_score - a.priority_score)
              .map((msg) => {
                const priorityColor =
                  msg.priority_score >= 9
                    ? "#ef4444"
                    : msg.priority_score >= 7
                      ? "#f59e0b"
                      : "#2dd4bf";
                const priorityBg =
                  msg.priority_score >= 9
                    ? "rgba(239,68,68,0.12)"
                    : msg.priority_score >= 7
                      ? "rgba(245,158,11,0.12)"
                      : "rgba(45,212,191,0.12)";
                const catColor =
                  CATEGORY_TEXT_COLORS[msg.category?.toLowerCase()] ?? "#94a3b8";
                const catBg =
                  CATEGORY_COLORS[msg.category?.toLowerCase()] ?? "rgba(255,255,255,0.05)";
                const emoji = PLATFORM_EMOJI[msg.platform] ?? "📩";

                return (
                  <div
                    key={msg.id}
                    className="rounded-xl border p-4 flex flex-col sm:flex-row items-start sm:items-center gap-4 hover:bg-white/10 transition-colors bg-white/5 backdrop-blur-md border-white/10"
                  >
                    {/* Priority badge */}
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
                      style={{ background: priorityBg, color: priorityColor }}
                    >
                      {msg.priority_score}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-base">{emoji}</span>
                        <span className="text-xs font-mono text-[var(--muted-foreground)] uppercase">
                          {msg.platform}
                        </span>
                        <span className="text-xs text-[var(--muted-foreground)]">·</span>
                        <span className="text-sm text-[var(--foreground)] font-medium truncate">
                          {msg.sender || "Unknown"}
                        </span>
                        {msg.category && (
                          <>
                            <span className="text-xs text-[var(--muted-foreground)]">·</span>
                            <span
                              className="text-xs px-2 py-0.5 rounded-full font-medium"
                              style={{ background: catBg, color: catColor }}
                            >
                              {msg.category}
                            </span>
                          </>
                        )}
                      </div>
                      <p className="text-sm text-[var(--foreground)] font-medium mt-0.5 truncate">
                        {msg.subject || "(no subject)"}
                      </p>
                      <p className="text-xs text-[var(--muted-foreground)] mt-1 line-clamp-2">
                        {msg.content || "(no content)"}
                      </p>
                    </div>

                    {/* Action */}
                    <button
                      onClick={() => openModal(msg)}
                      className="shrink-0 px-4 py-2 rounded-lg text-sm font-medium border transition-colors hover:bg-[var(--accent)]"
                      style={{
                        borderColor: "rgba(45,212,191,0.3)",
                        color: "#2dd4bf",
                      }}
                    >
                      Draft Reply
                    </button>
                  </div>
                );
              })}
          </div>
        )}
      </div>

      {/* ── Draft Modal ── */}
      {modalMsg && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
          onClick={() => setModalMsg(null)}
        >
          <div
            className="w-full max-w-2xl rounded-2xl border overflow-hidden"
            style={{
              background: "#0d0d14",
              borderColor: "rgba(255,255,255,0.1)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.5)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <div>
                <p className="text-sm font-semibold text-[var(--foreground)]">
                  Draft Reply
                </p>
                <p className="text-xs text-[var(--muted-foreground)] mt-0.5">
                  {modalMsg.sender} · {modalMsg.subject || "(no subject)"}
                </p>
              </div>
              <button
                onClick={() => setModalMsg(null)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            {/* Original message */}
            <div className="px-6 py-4 border-b" style={{ borderColor: "rgba(255,255,255,0.04)" }}>
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)] mb-2">
                Original Message
              </p>
              <p className="text-sm text-[var(--foreground)] leading-relaxed">
                {modalMsg.content || "(no content)"}
              </p>
            </div>

            {/* Draft area */}
            <div className="px-6 py-4 space-y-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)] mb-2">
                  AI Draft
                </p>
                {drafting ? (
                  <div
                    className="rounded-xl border flex items-center justify-center py-8"
                    style={{ borderColor: "rgba(255,255,255,0.06)" }}
                  >
                    <Loader2 size={20} className="animate-spin text-[var(--primary)]" />
                    <span className="ml-3 text-sm text-[var(--muted-foreground)]">
                      Generating draft…
                    </span>
                  </div>
                ) : (
                  <textarea
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    placeholder="Draft reply will appear here…"
                    className="w-full rounded-xl border px-4 py-3 text-sm bg-transparent text-[var(--foreground)] placeholder-[var(--muted-foreground)] resize-none focus:outline-none focus:ring-2"
                    style={{
                      borderColor: "rgba(255,255,255,0.08)",
                      height: 140,
                    }}
                    onFocus={(e) =>
                      (e.currentTarget.style.boxShadow = "0 0 0 2px rgba(45,212,191,0.2)")
                    }
                    onBlur={(e) => (e.currentTarget.style.boxShadow = "none")}
                  />
                )}
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleDraft}
                  disabled={drafting}
                  className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors disabled:opacity-50"
                  style={{
                    borderColor: "rgba(255,255,255,0.1)",
                    color: "var(--foreground)",
                    background: "var(--muted)",
                  }}
                >
                  {drafting ? (
                    <span className="flex items-center gap-2">
                      <Loader2 size={14} className="animate-spin" />
                      Generating…
                    </span>
                  ) : draftDone ? (
                    "Regenerate"
                  ) : (
                    "Generate Draft"
                  )}
                </button>
                <button
                  className="px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                  style={{
                    background: "linear-gradient(135deg, #2dd4bf, #0ea5e9)",
                    color: "#0a0a0f",
                    border: "none",
                  }}
                  disabled={!draft || drafting}
                  onClick={() => {
                    alert("Send wired up in next phase.");
                    setModalMsg(null);
                  }}
                >
                  <Send size={14} />
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

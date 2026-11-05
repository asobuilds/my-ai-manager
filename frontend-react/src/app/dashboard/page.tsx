"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, ArrowDown, ArrowUp, Inbox } from "lucide-react";
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
}

export default function DashboardPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [greeting, setGreeting] = useState("afternoon");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const h = new Date().getHours();
    setGreeting(h < 12 ? "morning" : h < 18 ? "afternoon" : "evening");
  }, []);

  useEffect(() => {
    api
      .get("/messages")
      .then((r) => setMessages(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const critical = messages.filter((m) => m.priority_score >= 9).length;
  const action   = messages.filter((m) => m.priority_score >= 7 && m.priority_score <= 8).length;
  const low      = messages.filter((m) => m.priority_score < 7).length;
  const recent   = [...messages].sort((a, b) => b.priority_score - a.priority_score).slice(0, 5);

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
      {/* ── Welcome ── */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--foreground)]">
          Good {greeting}, ready to get things done?
        </h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Here&apos;s what Aso found across your connected accounts.
        </p>
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {kpiCards.map((k) => (
          <div
            key={k.label}
            className="rounded-xl p-5 border"
            style={{
              background: k.bg,
              borderColor: k.border,
            }}
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
              <p
                className="text-4xl font-bold leading-none"
                style={{ color: k.color }}
              >
                {k.value}
              </p>
            )}
            <p className="text-xs text-[var(--muted-foreground)] mt-2">{k.sub}</p>
          </div>
        ))}
      </div>

      {/* ── Recent Messages ── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[var(--foreground)]">Recent Messages</h2>
          <a href="/dashboard/inventory" className="text-xs text-[var(--primary)] hover:opacity-80">
            View all
          </a>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 rounded-xl bg-[var(--muted)] animate-pulse"
              />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div
            className="rounded-xl border border-dashed flex flex-col items-center justify-center py-16 text-center"
            style={{ borderColor: "rgba(255,255,255,0.08)" }}
          >
            <Inbox size={32} className="text-[var(--muted-foreground)] mb-3" />
            <p className="text-sm text-[var(--muted-foreground)]">
              No messages yet. Connect Gmail and sync to get started.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {recent.map((msg) => (
              <div
                key={msg.id}
                className="rounded-xl border p-4 flex items-center gap-4 hover:bg-[var(--accent)] transition-colors cursor-pointer"
                style={{ borderColor: "rgba(255,255,255,0.06)" }}
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-sm shrink-0"
                  style={{
                    background:
                      msg.priority_score >= 9
                        ? "rgba(239,68,68,0.12)"
                        : msg.priority_score >= 7
                          ? "rgba(245,158,11,0.12)"
                          : "rgba(45,212,191,0.12)",
                    color:
                      msg.priority_score >= 9
                        ? "#ef4444"
                        : msg.priority_score >= 7
                          ? "#f59e0b"
                          : "#2dd4bf",
                  }}
                >
                  {msg.priority_score}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-[var(--muted-foreground)] uppercase">
                      {msg.platform}
                    </span>
                    <span className="text-xs text-[var(--muted-foreground)]">·</span>
                    <span className="text-xs text-[var(--muted-foreground)] truncate">
                      {msg.sender}
                    </span>
                  </div>
                  <p className="text-sm text-[var(--foreground)] font-medium truncate mt-0.5">
                    {msg.subject || "(no subject)"}
                  </p>
                </div>
                <a
                  href="/dashboard/inventory"
                  className="text-xs px-3 py-1.5 rounded-lg border shrink-0 hover:bg-[var(--accent)] transition-colors"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--muted-foreground)" }}
                >
                  View
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

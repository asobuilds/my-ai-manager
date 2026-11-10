"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  ArrowUp,
  CalendarDays,
  CheckCircle2,
  Inbox,
  Megaphone,
  Package,
  PenLine,
} from "lucide-react";
import api from "@/lib/api";
import { WeatherWidget } from "@/components/weather-widget";

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

const quickActions = [
  {
    label: "Schedule Meeting",
    description: "Plan your next event",
    href: "/dashboard/calendar",
    icon: CalendarDays,
    color: "#2dd4bf",
    bg: "rgba(45,212,191,0.12)",
  },
  {
    label: "Draft Email",
    description: "Reply with AI assistance",
    href: "/dashboard/inventory",
    icon: PenLine,
    color: "#3b82f6",
    bg: "rgba(59,130,246,0.12)",
  },
  {
    label: "Check Stock",
    description: "Review inventory levels",
    href: "/dashboard/shop",
    icon: Package,
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.12)",
  },
  {
    label: "Create Post",
    description: "Generate a promo post",
    href: "/dashboard/social",
    icon: Megaphone,
    color: "#a78bfa",
    bg: "rgba(167,139,250,0.12)",
  },
];

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
  const action = messages.filter((m) => m.priority_score >= 7 && m.priority_score <= 8).length;
  const low = messages.filter((m) => m.priority_score < 7).length;
  const recent = [...messages].sort((a, b) => b.priority_score - a.priority_score).slice(0, 3);

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
          Here&apos;s a high-level overview of what Aso found across your accounts.
        </p>
      </div>

      {/* ── Weather ── */}
      <WeatherWidget />

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {kpiCards.map((k) => (
          <div
            key={k.label}
            className="rounded-xl p-5 border"
            style={{ background: k.bg, borderColor: k.border }}
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

      {/* ── Quick Actions ── */}
      <div>
        <h2 className="text-base font-semibold text-[var(--foreground)] mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="group rounded-xl border p-4 transition-all hover:-translate-y-0.5 hover:shadow-lg"
              style={{
                background: "rgba(255,255,255,0.03)",
                borderColor: "rgba(255,255,255,0.06)",
              }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                style={{ background: item.bg }}
              >
                <item.icon size={18} style={{ color: item.color }} />
              </div>
              <p className="text-sm font-semibold text-[var(--foreground)] flex items-center gap-1">
                {item.label}
                <ArrowRight
                  size={13}
                  className="opacity-0 -translate-x-1 transition-all group-hover:opacity-100 group-hover:translate-x-0"
                  style={{ color: item.color }}
                />
              </p>
              <p className="text-xs text-[var(--muted-foreground)] mt-1">{item.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* ── Recent Activity ── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[var(--foreground)]">Recent Activity</h2>
          <Link href="/dashboard/inventory" className="text-xs text-[var(--primary)] hover:opacity-80">
            View all
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 rounded-xl bg-[var(--muted)] animate-pulse" />
            ))}
          </div>
        ) : recent.length === 0 ? (
          <div
            className="rounded-xl border border-dashed flex flex-col items-center justify-center py-16 text-center"
            style={{ borderColor: "rgba(255,255,255,0.08)" }}
          >
            <Inbox size={32} className="text-[var(--muted-foreground)] mb-3" />
            <p className="text-sm text-[var(--muted-foreground)]">
              No activity yet. Connect Gmail and sync to get started.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {recent.map((msg) => (
              <Link
                key={msg.id}
                href="/dashboard/inventory"
                className="rounded-xl border p-4 flex items-center gap-4 hover:bg-[var(--accent)] transition-colors"
                style={{ borderColor: "rgba(255,255,255,0.06)" }}
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold shrink-0"
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
                <ArrowRight size={14} className="shrink-0 text-[var(--muted-foreground)]" />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

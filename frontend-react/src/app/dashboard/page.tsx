"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  ArrowUp,
  CalendarDays,
  CheckCircle2,
  Clock,
  Inbox,
  Megaphone,
  Package,
  PenLine,
  MessageSquare,
  CloudSun,
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
}

const quickActions = [
  {
    label: "Schedule",
    description: "Meeting",
    href: "/dashboard/calendar",
    icon: CalendarDays,
    iconColor: "text-blue-400",
    bgColor: "bg-blue-500/10",
  },
  {
    label: "Draft",
    description: "Email",
    href: "/dashboard/inventory",
    icon: PenLine,
    iconColor: "text-teal-400",
    bgColor: "bg-teal-500/10",
  },
  {
    label: "Stock",
    description: "Check",
    href: "/dashboard/shop",
    icon: Package,
    iconColor: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
  },
  {
    label: "Post",
    description: "Create",
    href: "/dashboard/social",
    icon: Megaphone,
    iconColor: "text-pink-400",
    bgColor: "bg-pink-500/10",
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
      .then((r) => {
        setMessages(r.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const critical = messages.filter((m) => m.priority_score >= 9).length;
  const action = messages.filter((m) => m.priority_score >= 7 && m.priority_score <= 8).length;
  const low = messages.filter((m) => m.priority_score < 7).length;
  const recent = [...messages].sort((a, b) => b.priority_score - a.priority_score).slice(0, 3);
  const tasksDue = messages.filter((m) => m.status === "pending").length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-5xl mx-auto px-6 py-6 space-y-6">
        {/* ── Header Row ── */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-[var(--foreground)]">
              Good {greeting}, ready to get things done?
            </h1>
            <p className="text-sm text-[var(--muted-foreground)] mt-1">
              Here&apos;s a high-level overview of what Aso found across your accounts.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0 pt-1">
            <div className="glass-card flex items-center gap-2 px-3 py-1.5 text-xs text-[var(--muted-foreground)]">
              <Clock size={12} />
              <span>Last sync: active</span>
            </div>
            <div className="glass-card flex items-center gap-2 px-3 py-1.5 text-xs text-[var(--muted-foreground)]">
              <CloudSun size={12} className="text-yellow-400" />
              <span>28°C Lagos</span>
            </div>
          </div>
        </div>

        {/* ── KPI Cards ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: "Critical", value: critical, sub: "Needs immediate attention", colorClass: "text-red-400", borderClass: "border-red-500/20", bgClass: "bg-red-500/5", icon: ArrowUp, iconColor: "#ef4444" },
            { label: "Action Needed", value: action, sub: "Follow up within 48 hrs", colorClass: "text-amber-400", borderClass: "border-amber-500/20", bgClass: "bg-amber-500/5", icon: AlertTriangle, iconColor: "#f59e0b" },
            { label: "Low Priority", value: low, sub: "Review when convenient", colorClass: "text-emerald-400", borderClass: "border-emerald-500/20", bgClass: "bg-emerald-500/5", icon: CheckCircle2, iconColor: "#2dd4bf" },
          ].map((k) => (
            <div key={k.label} className={`glass-card glass-card-transition p-5 ${k.borderClass} ${k.bgClass}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
                  {k.label}
                </span>
                <k.icon size={16} style={{ color: k.iconColor }} />
              </div>
              {loading ? (
                <div className="h-9 w-12 rounded bg-[var(--muted)] animate-pulse" />
              ) : (
                <p className={`text-4xl font-bold leading-none ${k.colorClass}`}>{k.value}</p>
              )}
              <p className="text-xs text-[var(--muted-foreground)] mt-2">{k.sub}</p>
            </div>
          ))}
        </div>

        {/* ── Quick Actions Toolbar ── */}
        <div>
          <h2 className="text-base font-semibold text-[var(--foreground)] mb-3">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-3">
            {quickActions.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="glass-card glass-card-transition group flex flex-col items-center gap-2 p-3 text-center hover:bg-white/10"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${item.bgColor}`}>
                  <item.icon size={18} className={item.iconColor} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--foreground)]">{item.label}</p>
                  <p className="text-[10px] text-[var(--muted-foreground)]">{item.description}</p>
                </div>
                <ArrowRight
                  size={12}
                  className={`opacity-0 -translate-x-1 transition-all group-hover:opacity-100 group-hover:translate-x-0 ${item.iconColor}`}
                />
              </Link>
            ))}
          </div>
        </div>

        {/* ── Recent Activity Summary ── */}
        <div>
          <div className="flex items-center justify-between mb-3">
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
          ) : messages.length === 0 ? (
            <div className="glass-card border border-dashed flex flex-col items-center justify-center py-12 text-center"
              style={{ borderColor: "rgba(255,255,255,0.08)" }}
            >
              <Inbox size={32} className="text-[var(--muted-foreground)] mb-3" />
              <p className="text-sm text-[var(--muted-foreground)]">
                No activity yet. Connect Gmail and sync to get started.
              </p>
            </div>
          ) : (
            <>
              {/* Summary Card */}
              <div className="glass-card p-4 mb-4 flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <MessageSquare size={16} className="text-blue-400" />
                  <span className="text-sm text-[var(--muted-foreground)]">Total messages: <span className="text-[var(--foreground)] font-semibold">{messages.length}</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle size={16} className="text-amber-400" />
                  <span className="text-sm text-[var(--muted-foreground)]">Tasks due: <span className="text-[var(--foreground)] font-semibold">{tasksDue}</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-emerald-400" />
                  <span className="text-sm text-[var(--muted-foreground)]">Last sync: <span className="text-[var(--foreground)] font-semibold">active</span></span>
                </div>
              </div>

              {/* Recent Items */}
              {recent.length > 0 && (
                <div className="space-y-2">
                  {recent.map((msg) => (
                    <Link
                      key={msg.id}
                      href="/dashboard/inventory"
                      className="rounded-xl border p-4 flex items-center gap-4 hover:bg-white/5 transition-colors"
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
                          <span className="text-xs font-mono text-[var(--muted-foreground)] uppercase">{msg.platform}</span>
                          <span className="text-xs text-[var(--muted-foreground)]">·</span>
                          <span className="text-xs text-[var(--muted-foreground)] truncate">{msg.sender}</span>
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
            </>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  Check,
  Clock,
  Loader2,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import api from "@/lib/api";

interface CalendarEvent {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  event_type: string;
  created_at: string;
  updated_at: string | null;
}

interface EventForm {
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  event_type: string;
}

const EMPTY_FORM: EventForm = {
  title: "",
  description: "",
  start_time: "",
  end_time: "",
  event_type: "meeting",
};

const EVENT_TYPES = ["meeting", "reminder", "holiday"] as const;

const TYPE_COLORS: Record<string, string> = {
  meeting: "#3b82f6",
  reminder: "#f59e0b",
  holiday: "#10b981",
};

const TYPE_BG: Record<string, string> = {
  meeting: "rgba(59,130,246,0.12)",
  reminder: "rgba(245,158,11,0.12)",
  holiday: "rgba(16,185,129,0.12)",
};

function formatDateHeading(dateKey: string): string {
  const date = new Date(`${dateKey}T00:00:00`);
  return date.toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<EventForm>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<CalendarEvent[]>("/calendar/events");
      setEvents(res.data);
    } catch {
      setError("Failed to load calendar events. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const grouped = useMemo(() => {
    const groups: Record<string, CalendarEvent[]> = {};
    for (const event of events) {
      const key = event.start_time.slice(0, 10);
      if (!groups[key]) groups[key] = [];
      groups[key].push(event);
    }
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
  }, [events]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title.trim() || !form.start_time || !form.end_time) return;
    setSubmitting(true);
    try {
      await api.post("/calendar/events", {
        title: form.title.trim(),
        description: form.description.trim() || null,
        start_time: form.start_time,
        end_time: form.end_time,
        event_type: form.event_type,
      });
      setShowModal(false);
      setForm(EMPTY_FORM);
      showToast("Event created", "ok");
      await loadEvents();
    } catch (err) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      showToast(detail || "Failed to create event", "err");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(eventId: string) {
    setDeletingId(eventId);
    try {
      await api.delete(`/calendar/events/${eventId}`);
      setEvents((prev) => prev.filter((ev) => ev.id !== eventId));
      showToast("Event deleted", "ok");
    } catch {
      showToast("Failed to delete event", "err");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--foreground)]">📅 Calendar</h1>
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Keep track of meetings, reminders, and holidays in one place.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.97]"
          style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
        >
          <Plus size={16} />
          New Event
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

      {/* ── Event list ── */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="rounded-xl border p-4 animate-pulse"
              style={{ background: "var(--card)", borderColor: "rgba(255,255,255,0.06)" }}
            >
              <div className="h-3 w-40 rounded bg-[var(--muted)] mb-3" />
              <div className="h-16 rounded-xl bg-[var(--muted)]" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div
          className="rounded-xl border flex flex-col items-center justify-center py-16 text-center gap-3"
          style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)" }}
        >
          <p className="text-sm text-red-400">{error}</p>
          <button
            onClick={loadEvents}
            className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
            style={{ borderColor: "rgba(239,68,68,0.3)", color: "#f87171" }}
          >
            Retry
          </button>
        </div>
      ) : grouped.length === 0 ? (
        <div
          className="rounded-xl border border-dashed flex flex-col items-center justify-center py-20 text-center"
          style={{ borderColor: "rgba(255,255,255,0.08)" }}
        >
          <CalendarDays size={32} className="text-[var(--muted-foreground)] mb-3 opacity-50" />
          <p className="text-sm text-[var(--muted-foreground)]">
            No events yet. Create one, or ask Aso to schedule something.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {grouped.map(([dateKey, dayEvents]) => (
            <div key={dateKey}>
              <h2 className="text-sm font-semibold text-[var(--foreground)] mb-3">
                {formatDateHeading(dateKey)}
                <span className="ml-2 text-xs font-normal text-[var(--muted-foreground)]">
                  {dayEvents.length}
                </span>
              </h2>
              <div className="space-y-3">
                {dayEvents.map((event) => {
                  const color = TYPE_COLORS[event.event_type] ?? "#94a3b8";
                  const bg = TYPE_BG[event.event_type] ?? "rgba(255,255,255,0.05)";
                  return (
                    <div
                      key={event.id}
                      className="rounded-xl border p-4 flex items-start gap-4"
                      style={{
                        background: "rgba(255,255,255,0.03)",
                        borderColor: "rgba(255,255,255,0.06)",
                      }}
                    >
                      <div
                        className="w-1 self-stretch rounded-full shrink-0"
                        style={{ background: color }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-[var(--foreground)]">
                            {event.title}
                          </span>
                          <span
                            className="text-[10px] px-2 py-0.5 rounded-full font-medium capitalize"
                            style={{ background: bg, color }}
                          >
                            {event.event_type}
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)] mt-1">
                          <Clock size={12} />
                          {formatTime(event.start_time)} – {formatTime(event.end_time)}
                        </div>
                        {event.description && (
                          <p className="text-xs text-[var(--muted-foreground)] mt-2 line-clamp-2">
                            {event.description}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleDelete(event.id)}
                        disabled={deletingId === event.id}
                        className="shrink-0 rounded-lg p-2 text-[var(--muted-foreground)] hover:text-red-400 hover:bg-[var(--accent)] transition-colors disabled:opacity-40"
                        aria-label="Delete event"
                      >
                        {deletingId === event.id ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Trash2 size={15} />
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── New Event Modal ── */}
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
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <h2 className="text-base font-semibold text-[var(--foreground)]">➕ New Event</h2>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Title *
                </label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="e.g. Team standup"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                  required
                />
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Description
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Optional details…"
                  rows={2}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none resize-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
                  onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    Starts *
                  </label>
                  <input
                    type="datetime-local"
                    value={form.start_time}
                    onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    Ends *
                  </label>
                  <input
                    type="datetime-local"
                    value={form.end_time}
                    onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Type
                </label>
                <select
                  value={form.event_type}
                  onChange={(e) => setForm({ ...form, event_type: e.target.value })}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none capitalize"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                >
                  {EVENT_TYPES.map((type) => (
                    <option key={type} value={type} style={{ background: "#1a1a2e" }}>
                      {type}
                    </option>
                  ))}
                </select>
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
                  disabled={
                    submitting ||
                    !form.title.trim() ||
                    !form.start_time ||
                    !form.end_time
                  }
                  className="flex-1 py-2.5 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-40 hover:opacity-90"
                  style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
                >
                  {submitting ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 size={14} className="animate-spin" />
                      Creating…
                    </span>
                  ) : (
                    "Create Event"
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

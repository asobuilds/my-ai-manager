"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Check,
  Loader2,
  Megaphone,
  RefreshCw,
  Send,
  Sparkles,
  X,
} from "lucide-react";
import api from "@/lib/api";

interface SocialPost {
  id: string;
  user_id: string;
  platform: string;
  content: string;
  status: string;
  scheduled_time: string | null;
  created_at: string;
}

const PLATFORMS = ["X", "Instagram", "WhatsApp"] as const;

const PLATFORM_EMOJI: Record<string, string> = {
  X: "𝕏",
  Instagram: "📸",
  WhatsApp: "💬",
};

const STATUS_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  draft: { bg: "rgba(148,163,184,0.15)", color: "#94a3b8", label: "Draft" },
  scheduled: { bg: "rgba(59,130,246,0.15)", color: "#60a5fa", label: "Scheduled" },
  published: { bg: "rgba(16,185,129,0.15)", color: "#34d399", label: "Published" },
};

function formatScheduled(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function SocialPage() {
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ownerOnly, setOwnerOnly] = useState(false);

  const [platform, setPlatform] = useState<string>("X");
  const [productName, setProductName] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState<string | null>(null);
  const [savingDraft, setSavingDraft] = useState(false);

  const [publishingId, setPublishingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const loadPosts = useCallback(async () => {
    setLoading(true);
    setError(null);
    setOwnerOnly(false);
    try {
      const res = await api.get<SocialPost[]>("/social/posts");
      setPosts(res.data);
    } catch (err) {
      if ((err as { response?: { status?: number } })?.response?.status === 403) {
        setOwnerOnly(true);
      } else {
        setError("Failed to load social posts. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!productName.trim()) return;
    setGenerating(true);
    setGenerated(null);
    try {
      const res = await api.post<{ content: string }>("/social/generate", {
        product_name: productName.trim(),
        platform,
      });
      setGenerated(res.data.content);
    } catch {
      showToast("Failed to generate post", "err");
    } finally {
      setGenerating(false);
    }
  }

  async function handleSaveDraft() {
    if (!generated) return;
    setSavingDraft(true);
    try {
      const res = await api.post<SocialPost>("/social/posts", {
        platform,
        content: generated,
        status: "draft",
      });
      setPosts((prev) => [res.data, ...prev]);
      setGenerated(null);
      setProductName("");
      showToast("Saved as draft", "ok");
    } catch {
      showToast("Failed to save draft", "err");
    } finally {
      setSavingDraft(false);
    }
  }

  async function handlePublish(post: SocialPost) {
    setPublishingId(post.id);
    try {
      const res = await api.patch<SocialPost>(`/social/posts/${post.id}`, {
        status: "published",
      });
      setPosts((prev) => prev.map((p) => (p.id === post.id ? res.data : p)));
      showToast("Post published", "ok");
    } catch {
      showToast("Failed to publish post", "err");
    } finally {
      setPublishingId(null);
    }
  }

  if (ownerOnly) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-[var(--foreground)] mb-2">📣 Social Media</h1>
        <div
          className="rounded-xl border flex flex-col items-center justify-center py-20 text-center"
          style={{ borderColor: "rgba(255,255,255,0.08)" }}
        >
          <Megaphone size={32} className="text-[var(--muted-foreground)] mb-3 opacity-50" />
          <p className="text-sm text-[var(--muted-foreground)]">
            Social media management is available to owner accounts only.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* ── Header ── */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--foreground)]">📣 Social Media</h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Generate promotional posts with AI and manage your publishing queue.
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

      {/* ── AI Generator ── */}
      <div
        className="rounded-2xl border p-6 mb-8"
        style={{
          background: "rgba(255,255,255,0.03)",
          borderColor: "rgba(45,212,191,0.18)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.25)",
        }}
      >
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={16} style={{ color: "#2dd4bf" }} />
          <h2 className="text-base font-semibold text-[var(--foreground)]">AI Post Generator</h2>
        </div>

        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-3">
          <div className="sm:w-44 shrink-0">
            <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
              Platform
            </label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
            >
              {PLATFORMS.map((p) => (
                <option key={p} value={p} style={{ background: "#1a1a2e" }}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
              Product Name
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g. Organic Avocados"
              className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
              onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(45,212,191,0.4)")}
              onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={generating || !productName.trim()}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all disabled:opacity-40 hover:opacity-90 active:scale-[0.98]"
              style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
            >
              {generating ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Sparkles size={15} />
                  Generate Post
                </>
              )}
            </button>
          </div>
        </form>

        {/* Preview */}
        {generated && (
          <div
            className="mt-5 rounded-xl border p-4"
            style={{
              background: "rgba(45,212,191,0.05)",
              borderColor: "rgba(45,212,191,0.2)",
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
                Preview · {platform}
              </p>
              <span className="text-xs text-[var(--muted-foreground)]">
                {generated.length} chars
              </span>
            </div>
            <p className="text-sm text-[var(--foreground)] leading-relaxed whitespace-pre-wrap">
              {generated}
            </p>
            <div className="flex items-center gap-3 mt-4">
              <button
                onClick={handleSaveDraft}
                disabled={savingDraft}
                className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)] disabled:opacity-40"
                style={{ borderColor: "rgba(45,212,191,0.3)", color: "#2dd4bf" }}
              >
                {savingDraft ? "Saving…" : "Save as Draft"}
              </button>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)] disabled:opacity-40"
                style={{ borderColor: "rgba(255,255,255,0.1)", color: "var(--muted-foreground)" }}
              >
                Regenerate
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Posts ── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[var(--foreground)]">
            Posts
            <span className="ml-2 text-xs font-normal text-[var(--muted-foreground)]">
              {posts.length}
            </span>
          </h2>
          {!loading && !error && (
            <button
              onClick={loadPosts}
              className="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
            >
              <RefreshCw size={12} />
              Refresh
            </button>
          )}
        </div>

        {loading ? (
          <div
            className="rounded-xl border overflow-hidden"
            style={{ borderColor: "rgba(255,255,255,0.06)" }}
          >
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="flex items-center gap-4 px-5 py-4 animate-pulse border-b last:border-b-0"
                style={{ borderColor: "rgba(255,255,255,0.04)" }}
              >
                <div className="h-4 w-24 rounded bg-[var(--muted)]" />
                <div className="h-4 flex-1 rounded bg-[var(--muted)]" />
                <div className="h-4 w-20 rounded bg-[var(--muted)]" />
                <div className="h-8 w-24 rounded-lg bg-[var(--muted)]" />
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
              onClick={loadPosts}
              className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
              style={{ borderColor: "rgba(239,68,68,0.3)", color: "#f87171" }}
            >
              Retry
            </button>
          </div>
        ) : posts.length === 0 ? (
          <div
            className="rounded-xl border border-dashed flex flex-col items-center justify-center py-20 text-center"
            style={{ borderColor: "rgba(255,255,255,0.08)" }}
          >
            <Megaphone size={32} className="text-[var(--muted-foreground)] mb-3 opacity-50" />
            <p className="text-sm text-[var(--muted-foreground)]">
              No posts yet. Generate one above and save it as a draft.
            </p>
          </div>
        ) : (
          <div
            className="rounded-xl border overflow-x-auto"
            style={{ borderColor: "rgba(255,255,255,0.06)" }}
          >
            <table className="w-full text-sm">
              <thead>
                <tr
                  className="text-left text-xs uppercase tracking-wider text-[var(--muted-foreground)]"
                  style={{ background: "rgba(255,255,255,0.03)" }}
                >
                  <th className="px-5 py-3 font-medium">Platform</th>
                  <th className="px-5 py-3 font-medium">Content</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Scheduled</th>
                  <th className="px-5 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {posts.map((post) => {
                  const status = STATUS_STYLES[post.status] ?? STATUS_STYLES.draft;
                  return (
                    <tr
                      key={post.id}
                      className="border-t"
                      style={{ borderColor: "rgba(255,255,255,0.04)" }}
                    >
                      <td className="px-5 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <span className="text-base">
                            {PLATFORM_EMOJI[post.platform] ?? "📣"}
                          </span>
                          <span className="text-[var(--foreground)] font-medium">
                            {post.platform}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3 max-w-xs">
                        <p className="text-xs text-[var(--muted-foreground)] line-clamp-2">
                          {post.content}
                        </p>
                      </td>
                      <td className="px-5 py-3 whitespace-nowrap">
                        <span
                          className="text-[11px] px-2.5 py-1 rounded-full font-medium"
                          style={{ background: status.bg, color: status.color }}
                        >
                          {status.label}
                        </span>
                      </td>
                      <td className="px-5 py-3 whitespace-nowrap text-xs text-[var(--muted-foreground)]">
                        {formatScheduled(post.scheduled_time)}
                      </td>
                      <td className="px-5 py-3 text-right whitespace-nowrap">
                        {post.status === "published" ? (
                          <span className="text-xs text-[var(--muted-foreground)]">Published</span>
                        ) : (
                          <button
                            onClick={() => handlePublish(post)}
                            disabled={publishingId === post.id}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)] disabled:opacity-40"
                            style={{ borderColor: "rgba(45,212,191,0.3)", color: "#2dd4bf" }}
                          >
                            {publishingId === post.id ? (
                              <Loader2 size={12} className="animate-spin" />
                            ) : (
                              <Send size={12} />
                            )}
                            Publish Now
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

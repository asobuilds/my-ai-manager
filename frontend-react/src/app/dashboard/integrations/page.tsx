"use client";

import { useEffect, useState } from "react";
import {
  Mail,
  MessageCircle,
  Briefcase,
  MessageSquare,
  Icon as TwitterIcon,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import api from "@/lib/api";

interface ConnectionStatus {
  gmail_connected: boolean;
  authorization_url: string | null;
}

interface Platform {
  name: string;
  emoji: string;
  icon: React.ReactNode;
  description: string;
  provider: string;
  comingSoon?: boolean;
}

const PLATFORMS: Platform[] = [
  {
    name: "Gmail",
    emoji: "📧",
    icon: <Mail size={20} />,
    description: "Sync your Gmail to ingest emails, draft replies, and prioritize inbox.",
    provider: "gmail",
  },
  {
    name: "WhatsApp Business",
    emoji: "💬",
    icon: <MessageCircle size={20} />,
    description: "Connect WhatsApp Business to track customer messages and leads.",
    provider: "whatsapp",
    comingSoon: true,
  },
  {
    name: "LinkedIn",
    emoji: "💼",
    icon: <Briefcase size={20} />,
    description: "Sync your LinkedIn network and job recommendations.",
    provider: "linkedin",
    comingSoon: true,
  },
  {
    name: "Facebook Messenger",
    emoji: "📘",
    icon: <MessageSquare size={20} />,
    description: "Connect Facebook Messenger for unified customer communication.",
    provider: "facebook",
    comingSoon: true,
  },
  {
    name: "Twitter / X",
    emoji: "🐦",
    icon: <span className="text-lg">🐦</span>,
    description: "Monitor your Twitter mentions and DMs in one place.",
    provider: "twitter",
    comingSoon: true,
  },
];

export default function IntegrationsPage() {
  const [status, setStatus] = useState<ConnectionStatus>({
    gmail_connected: false,
    authorization_url: null,
  });
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    api
      .get("/me/connections/status")
      .then((r) => setStatus(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function handleConnect(platform: Platform) {
    if (platform.comingSoon) {
      setToast(`${platform.name} coming soon!`);
      setTimeout(() => setToast(null), 3000);
      return;
    }
    if (platform.provider === "gmail" && status.authorization_url) {
      window.open(status.authorization_url, "_blank");
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* ── Header ── */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--foreground)]">🔌 Integrations</h1>
        <p className="text-sm text-[var(--muted-foreground)] mt-1">
          Connect your platforms. Once connected, Aso will automatically ingest, filter, and prioritize your data.
        </p>
      </div>

      {/* ── Toast ── */}
      {toast && (
        <div
          className="fixed top-4 right-4 z-50 px-4 py-3 rounded-xl border text-sm"
          style={{
            background: "rgba(45,212,191,0.12)",
            borderColor: "rgba(45,212,191,0.3)",
            color: "#2dd4bf",
          }}
        >
          {toast}
        </div>
      )}

      {/* ── Platform Grid ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
        {PLATFORMS.map((p) => {
          const connected = p.provider === "gmail" && status.gmail_connected;

          return (
            <div
              key={p.provider}
              className="rounded-2xl border p-5 transition-all hover:border-[var(--primary)]/30 bg-white/5 backdrop-blur-md border-white/10 group"
            >
              <div className="flex items-start gap-4">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                  style={{
                    background: connected
                      ? "rgba(16,185,129,0.15)"
                      : "rgba(255,255,255,0.05)",
                    color: connected ? "#10b981" : "var(--muted-foreground)",
                  }}
                >
                  {connected ? (
                    <CheckCircle2 size={22} />
                  ) : (
                    <span className="text-xl">{p.emoji}</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold text-[var(--foreground)]">
                      {p.name}
                    </h3>
                    {connected && (
                      <span
                        className="text-xs px-2 py-0.5 rounded-full font-medium"
                        style={{
                          background: "rgba(16,185,129,0.15)",
                          color: "#34d399",
                        }}
                      >
                        Connected
                      </span>
                    )}
                    {p.comingSoon && !connected && (
                      <span
                        className="text-xs px-2 py-0.5 rounded-full font-medium"
                        style={{
                          background: "rgba(255,255,255,0.05)",
                          color: "var(--muted-foreground)",
                        }}
                      >
                        Soon
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-[var(--muted-foreground)] mt-1 leading-relaxed">
                    {p.description}
                  </p>
                </div>
              </div>

              <div className="mt-5">
                {loading ? (
                  <div
                    className="w-full py-2.5 rounded-xl text-center text-sm flex items-center justify-center gap-2"
                    style={{ background: "rgba(255,255,255,0.05)", color: "var(--muted-foreground)" }}
                  >
                    <Loader2 size={14} className="animate-spin" />
                    Checking…
                  </div>
                ) : connected ? (
                  <button
                    disabled
                    className="w-full py-2.5 rounded-xl text-sm font-medium cursor-not-allowed"
                    style={{
                      background: "rgba(16,185,129,0.12)",
                      color: "#34d399",
                      border: "1px solid rgba(16,185,129,0.2)",
                    }}
                  >
                    ✅ Connected
                  </button>
                ) : p.comingSoon ? (
                  <button
                    onClick={() => handleConnect(p)}
                    className="w-full py-2.5 rounded-xl text-sm font-medium border transition-colors hover:bg-[var(--accent)]"
                    style={{
                      borderColor: "rgba(255,255,255,0.08)",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    Coming Soon
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(p)}
                    className="w-full py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.98]"
                    style={{
                      background: "linear-gradient(135deg, #2dd4bf, #3b82f6)",
                    }}
                  >
                    {status.authorization_url ? "Connect with Google" : "Connect Gmail"}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

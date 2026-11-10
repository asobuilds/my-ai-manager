"use client";

import { useState } from "react";
import { Mail, Lock, Bot, Eye, EyeOff } from "lucide-react";
import api from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const resp = await api.post("/auth/login", { email, password });
      localStorage.setItem("access_token", resp.data.access_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        // FastAPI validation error array
        setError(detail.map((d: any) => d.msg || "Validation error").join(", "));
      } else if (typeof detail === "string") {
        // Standard string error
        setError(detail);
      } else {
        setError("Invalid email or password.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* ── Left: Branding ── */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            background: "linear-gradient(135deg, #0f1a2e 0%, #1e1a4e 50%, #0f2e2a 100%)",
          }}
        />
        {/* Animated orbs */}
        <div
          className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full opacity-20 blur-3xl animate-pulse"
          style={{ background: "#3b82f6" }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-72 h-72 rounded-full opacity-15 blur-3xl animate-pulse"
          style={{ background: "#8b5cf6", animationDelay: "1s" }}
        />
        <div
          className="absolute top-1/2 left-1/2 w-48 h-48 rounded-full opacity-10 blur-3xl animate-pulse"
          style={{ background: "#10b981", animationDelay: "2s" }}
        />

        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl" style={{ background: "rgba(255,255,255,0.15)" }}>
              🤖
            </div>
            <span className="text-2xl font-bold tracking-tight">Aso</span>
          </div>
          <h1 className="text-5xl font-bold leading-tight mb-6">
            Your AI-powered
            <br />
            <span style={{ color: "#3b82f6" }}>data assistant</span>
          </h1>
          <p className="text-lg text-slate-300 leading-relaxed max-w-md">
            Manage your emails, track job applications, and organize your data — all in one
            beautifully intelligent dashboard.
          </p>
          <div className="mt-12 flex flex-wrap gap-3">
            {["📧 Email", "💼 Jobs", "📁 Files", "💬 Chat"].map((tag) => (
              <span
                key={tag}
                className="px-4 py-2 rounded-full text-sm font-medium backdrop-blur-md border"
                style={{
                  background: "rgba(255,255,255,0.08)",
                  borderColor: "rgba(255,255,255,0.15)",
                  color: "#e2e8f0",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right: Login Form ── */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
              style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" }}
            >
              🤖
            </div>
            <span className="text-xl font-bold text-slate-900 dark:text-white">Aso</span>
          </div>

          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Welcome back
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mb-8">
            Sign in to continue to your dashboard
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Email
              </label>
              <div className="relative">
                <Mail
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  size={18}
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border text-sm bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all"
                  style={{
                    borderColor: "rgba(0,0,0,0.1)",
                    outline: "none",
                  }}
                  onFocus={(e) =>
                    (e.currentTarget.style.boxShadow = "0 0 0 3px rgba(59,130,246,0.15)")
                  }
                  onBlur={(e) => (e.currentTarget.style.boxShadow = "none")}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                  size={18}
                />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl border text-sm bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all"
                  style={{
                    borderColor: "rgba(0,0,0,0.1)",
                    outline: "none",
                  }}
                  onFocus={(e) =>
                    (e.currentTarget.style.boxShadow = "0 0 0 3px rgba(59,130,246,0.15)")
                  }
                  onBlur={(e) => (e.currentTarget.style.boxShadow = "none")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && (
              <div
                className="text-sm text-red-500 flex items-center gap-2"
                role="alert"
              >
                <span>⚠</span> {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90 active:scale-[0.98] disabled:opacity-60"
              style={{
                background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
                boxShadow: "0 4px 14px rgba(59,130,246,0.35)",
              }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg
                    className="animate-spin h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    />
                  </svg>
                  Signing in…
                </span>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400 dark:text-slate-500">
            Don&apos;t have an account?{" "}
            <a href="/signup" className="font-medium hover:underline" style={{ color: "#3b82f6" }}>
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

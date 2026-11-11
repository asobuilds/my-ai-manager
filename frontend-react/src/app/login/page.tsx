"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Bot,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
  User,
} from "lucide-react";
import api from "@/lib/api";

type Mode = "signin" | "signup";

interface ApiErrorDetail {
  msg?: string;
}

function extractError(err: unknown, mode: Mode): string {
  const detail = (
    err as { response?: { data?: { detail?: string | ApiErrorDetail[] } } }
  )?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || "Validation error").join(", ");
  }
  if (typeof detail === "string") {
    return detail;
  }
  return mode === "signin"
    ? "Invalid email or password."
    : "Could not create your account. Please try again.";
}

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("signin");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      router.replace("/dashboard");
    }
  }, [router]);

  function switchMode(next: Mode) {
    setMode(next);
    setError("");
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "signup") {
        await api.post("/auth/register", {
          full_name: fullName,
          email,
          password,
        });
      }

      const resp = await api.post("/auth/login", { email, password });
      localStorage.setItem("access_token", resp.data.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(extractError(err, mode));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 lg:grid lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-black lg:flex lg:flex-col lg:justify-between lg:p-14">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-24 left-1/4 h-80 w-80 rounded-full bg-blue-500/20 blur-3xl" />
          <div className="absolute bottom-10 right-1/4 h-80 w-80 rounded-full bg-purple-500/20 blur-3xl" />
          <div className="absolute left-1/2 top-1/2 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl" />
        </div>

        <Link href="/" className="relative z-10 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/25">
            <Bot size={22} className="text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-white">Aso</span>
        </Link>

        <div className="relative z-10 max-w-md">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 backdrop-blur-md">
            <Sparkles size={16} className="text-blue-400" />
            Your AI Personal &amp; Business Assistant
          </div>
          <h1 className="text-4xl font-bold leading-tight tracking-tight text-white xl:text-5xl">
            Welcome back to Aso.
          </h1>
          <p className="mt-5 text-lg leading-relaxed text-slate-300">
            Sign in to manage your shop, inbox, calendar, and social media from one
            intelligent dashboard.
          </p>

          <div className="mt-10 space-y-4">
            {[
              "AI-powered inbox and calendar management",
              "Real-time shop and inventory tracking",
              "Health, home, and business insights in one place",
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 text-sm text-slate-300">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-500/15">
                  <ShieldCheck size={15} className="text-emerald-400" />
                </div>
                {item}
              </div>
            ))}
          </div>
        </div>

        <p className="relative z-10 text-xs text-slate-500">
          &copy; Aso. All rights reserved.
        </p>
      </aside>

      <main className="flex min-h-screen items-center justify-center px-6 py-16">
        <div className="w-full max-w-md">
          <Link href="/" className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
              <Bot size={20} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">Aso</span>
          </Link>

          <div className="glass-card rounded-3xl border border-white/10 p-8 shadow-2xl backdrop-blur-xl">
            <div className="mb-6 grid grid-cols-2 gap-1 rounded-xl border border-white/10 bg-white/5 p-1">
              <button
                type="button"
                onClick={() => switchMode("signin")}
                className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors ${
                  mode === "signin"
                    ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => switchMode("signup")}
                className={`rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors ${
                  mode === "signup"
                    ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Sign Up
              </button>
            </div>

            <h2 className="text-2xl font-bold text-white">
              {mode === "signin" ? "Welcome back" : "Create your account"}
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              {mode === "signin"
                ? "Sign in to continue to your dashboard."
                : "Start using Aso in less than a minute."}
            </p>

            {error && (
              <div
                role="alert"
                className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300 backdrop-blur-md"
              >
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              {mode === "signup" && (
                <div>
                  <label
                    htmlFor="full-name"
                    className="mb-1.5 block text-sm font-medium text-slate-300"
                  >
                    Full Name
                  </label>
                  <div className="relative">
                    <User
                      size={18}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                    />
                    <input
                      id="full-name"
                      type="text"
                      value={fullName}
                      onChange={(event) => setFullName(event.target.value)}
                      required
                      autoComplete="name"
                      placeholder="Jane Doe"
                      className="w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10"
                    />
                  </div>
                </div>
              )}

              <div>
                <label
                  htmlFor="email"
                  className="mb-1.5 block text-sm font-medium text-slate-300"
                >
                  Email
                </label>
                <div className="relative">
                  <Mail
                    size={18}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                    autoComplete="email"
                    placeholder="you@example.com"
                    className="w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="mb-1.5 block text-sm font-medium text-slate-300"
                >
                  Password
                </label>
                <div className="relative">
                  <Lock
                    size={18}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
                  />
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    minLength={mode === "signup" ? 8 : undefined}
                    autoComplete={
                      mode === "signin" ? "current-password" : "new-password"
                    }
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-white/10 bg-white/5 py-2.5 pl-10 pr-10 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blue-500/50 focus:bg-white/10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((value) => !value)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 transition-colors hover:text-slate-300"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                {mode === "signup" && (
                  <p className="mt-1.5 text-xs text-slate-500">
                    Must be at least 8 characters.
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    {mode === "signin" ? "Signing in..." : "Creating account..."}
                  </>
                ) : (
                  <>
                    {mode === "signin" ? "Login" : "Create Account"}
                    <ArrowRight
                      size={18}
                      className="transition-transform group-hover:translate-x-0.5"
                    />
                  </>
                )}
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-slate-500">
              By continuing you agree to Aso&apos;s terms and privacy policy.
            </p>
          </div>

          <p className="mt-6 text-center text-sm text-slate-400">
            <Link href="/" className="font-medium text-blue-400 hover:text-blue-300">
              Back to landing page
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}

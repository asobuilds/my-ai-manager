import Link from "next/link";
import { ArrowRight, Bot, MessageSquare, ShoppingBag, Sparkles, Star } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-black">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-1/4 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl animate-pulse" />
        <div
          className="absolute bottom-0 right-1/4 h-96 w-96 rounded-full bg-purple-500/20 blur-3xl animate-pulse"
          style={{ animationDelay: "1.5s" }}
        />
        <div
          className="absolute left-1/2 top-1/2 h-72 w-72 rounded-full bg-emerald-500/10 blur-3xl animate-pulse"
          style={{ animationDelay: "3s" }}
        />
      </div>

      <div className="relative z-10 mx-auto grid min-h-screen max-w-7xl grid-cols-1 items-center gap-16 px-6 py-24 lg:grid-cols-2 lg:px-8">
        <div className="text-center lg:text-left">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-slate-300 backdrop-blur-md">
            <Sparkles size={16} className="text-blue-400" />
            Meet Aso, your everyday AI
          </div>

          <h1 className="text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
            Your AI Personal &amp; Business Assistant.
          </h1>

          <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-slate-300 lg:mx-0">
            Manage your shop, emails, calendar, and social media — all from one intelligent
            dashboard.
          </p>

          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row lg:justify-start">
            <Link
              href="/dashboard"
              className="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition-all hover:opacity-90 active:scale-[0.98] sm:w-auto"
            >
              Get Started
              <ArrowRight
                size={18}
                className="transition-transform group-hover:translate-x-1"
              />
            </Link>
            <a
              href="#capabilities"
              className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/15 bg-white/5 px-7 py-3.5 text-sm font-semibold text-white backdrop-blur-md transition-colors hover:bg-white/10 sm:w-auto"
            >
              Learn More
            </a>
          </div>

          <div className="mt-10 flex items-center justify-center gap-6 text-sm text-slate-400 lg:justify-start">
            <div className="flex items-center gap-1.5">
              <Star size={16} className="fill-amber-400 text-amber-400" />
              <span>4.9 average rating</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Bot size={16} className="text-blue-400" />
              <span>Always on</span>
            </div>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-md">
          <div className="absolute inset-0 -z-10 rounded-full bg-gradient-to-tr from-blue-500/30 via-purple-500/20 to-emerald-500/20 blur-3xl" />

          <div className="glass-card relative rounded-3xl border border-white/10 p-5 shadow-2xl backdrop-blur-xl">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
                  <Bot size={20} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Aso Assistant</p>
                  <p className="flex items-center gap-1.5 text-xs text-emerald-400">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    Online
                  </p>
                </div>
              </div>
              <MessageSquare size={18} className="text-slate-400" />
            </div>

            <div className="space-y-3">
              <div className="flex justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-blue-500 px-4 py-2.5 text-sm text-white">
                  Add my new sneakers to the shop and post them on Instagram.
                </div>
              </div>
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-white/10 px-4 py-2.5 text-sm text-slate-200">
                  Done! I&apos;ve listed the product and scheduled your post for 6 PM today.
                </div>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-4">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400/30 to-blue-500/30">
                  <ShoppingBag size={26} className="text-emerald-300" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-white">
                    Cloud Runner Sneakers
                  </p>
                  <p className="mt-0.5 text-xs text-slate-400">In stock · 24 units</p>
                  <p className="mt-1 text-sm font-bold text-emerald-400">$129.00</p>
                </div>
                <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-medium text-emerald-300">
                  Live
                </span>
              </div>
            </div>
          </div>

          <div className="glass-card absolute -bottom-6 -left-6 hidden rounded-2xl border border-white/10 px-4 py-3 shadow-xl sm:flex sm:items-center sm:gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-purple-500/20">
              <Sparkles size={18} className="text-purple-300" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Tasks automated</p>
              <p className="text-sm font-semibold text-white">1,284 this week</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

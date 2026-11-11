"use client";

import { useRef, useState } from "react";
import {
  Bot,
  Calendar,
  ChevronLeft,
  ChevronRight,
  Share2,
  ShoppingBag,
} from "lucide-react";

const FEATURES = [
  {
    title: "AI Chat",
    description:
      "Ask anything in natural language and let Aso handle the busywork across your tools.",
    icon: Bot,
    iconClass: "text-blue-400",
    iconBg: "bg-blue-500/15",
  },
  {
    title: "Shop Manager",
    description:
      "Track inventory, add products, and monitor sales from a single intelligent storefront.",
    icon: ShoppingBag,
    iconClass: "text-emerald-400",
    iconBg: "bg-emerald-500/15",
  },
  {
    title: "Calendar",
    description:
      "Schedule meetings and reminders automatically, with smart suggestions for your day.",
    icon: Calendar,
    iconClass: "text-purple-400",
    iconBg: "bg-purple-500/15",
  },
  {
    title: "Social Media",
    description:
      "Draft, schedule, and publish posts across your channels without switching tabs.",
    icon: Share2,
    iconClass: "text-pink-400",
    iconBg: "bg-pink-500/15",
  },
];

export function CapabilitiesSection() {
  const trackRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  function goTo(index: number) {
    const clamped = Math.max(0, Math.min(FEATURES.length - 1, index));
    setActiveIndex(clamped);
    const track = trackRef.current;
    const card = track?.children[clamped] as HTMLElement | undefined;
    if (track && card) {
      track.scrollTo({ left: card.offsetLeft, behavior: "smooth" });
    }
  }

  return (
    <section id="capabilities" className="bg-black py-24">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
              Capabilities
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
              One assistant. Everything you run.
            </h2>
            <p className="mt-3 max-w-2xl text-slate-400">
              Aso connects the pieces of your personal and business life so you can focus on
              what matters.
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              aria-label="Previous capability"
              onClick={() => goTo(activeIndex - 1)}
              disabled={activeIndex === 0}
              className="flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-white/5 text-white backdrop-blur-md transition-colors hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft size={20} />
            </button>
            <button
              type="button"
              aria-label="Next capability"
              onClick={() => goTo(activeIndex + 1)}
              disabled={activeIndex === FEATURES.length - 1}
              className="flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-white/5 text-white backdrop-blur-md transition-colors hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>

        <div
          ref={trackRef}
          className="mt-12 flex snap-x snap-mandatory gap-6 overflow-x-auto scroll-smooth pb-4 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        >
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="glass-card glass-card-transition w-[85%] shrink-0 snap-start rounded-2xl border border-white/10 p-8 sm:w-[45%] lg:w-[31%]"
              >
                <div
                  className={`flex h-14 w-14 items-center justify-center rounded-2xl ${feature.iconBg}`}
                >
                  <Icon size={28} className={feature.iconClass} />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">{feature.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate-400">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        <div className="mt-4 flex justify-center gap-2">
          {FEATURES.map((feature, index) => (
            <button
              key={feature.title}
              type="button"
              aria-label={`Go to ${feature.title}`}
              onClick={() => goTo(index)}
              className={`h-2 rounded-full transition-all ${
                index === activeIndex ? "w-8 bg-blue-400" : "w-2 bg-white/20"
              }`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

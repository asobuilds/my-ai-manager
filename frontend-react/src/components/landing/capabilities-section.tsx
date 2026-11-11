"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Bot,
  ShoppingBag,
  Calendar,
  Share2,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  Heart,
} from "lucide-react";

interface Slide {
  id: string;
  title: string;
  description: string;
  gradient: string;
  badge: string;
  badgeColor: string;
  icon: any;
  mockComponent: React.ReactNode;
}

export function CapabilitiesSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const slides: Slide[] = [
    {
      id: "ai-chat",
      title: "Your AI Assistant.",
      description:
        "Chat with Aso in natural language to draft emails, summarize unread messages, schedule meetings, and query your data effortlessly.",
      gradient: "linear-gradient(135deg, #091a2e 0%, #172554 50%, #0f172a 100%)",
      badge: "AI Chat & Ingestion",
      badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
      icon: Bot,
      mockComponent: (
        <div className="w-full max-w-md rounded-2xl border border-white/15 bg-slate-900 p-6 shadow-2xl">
          <div className="flex items-center gap-3 pb-4 border-b border-white/10 mb-4">
            <div className="w-9 h-9 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
              <Bot size={20} />
            </div>
            <div>
              <p className="font-semibold text-white text-sm">Aso Intelligence</p>
              <p className="text-xs text-slate-400">Online & ready</p>
            </div>
          </div>
          <div className="space-y-3 text-sm">
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-[85%] font-medium">
                Summarize my unread emails and draft a reply to Marcus.
              </div>
            </div>
            <div className="flex justify-start">
              <div className="bg-slate-800 text-slate-100 px-4 py-2.5 rounded-2xl rounded-tl-sm max-w-[85%] border border-white/10 space-y-2">
                <p>Found 14 unread messages. 3 flagged as high priority.</p>
                <div className="p-2.5 rounded-lg bg-blue-500/15 border border-blue-500/30 text-xs text-blue-300 flex items-center gap-2 font-medium">
                  <Sparkles size={14} /> Drafting reply to Marcus Vance...
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "shop-manager",
      title: "Manage Your Shop.",
      description:
        "Track inventory levels in real-time, get low-stock alerts, and let Aso automatically reorder supplies from your preferred vendors.",
      gradient: "linear-gradient(135deg, #022c22 0%, #064e3b 50%, #022c22 100%)",
      badge: "Shop & Inventory",
      badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
      icon: ShoppingBag,
      mockComponent: (
        <div className="w-full max-w-md rounded-2xl border border-emerald-500/30 bg-slate-900 p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ShoppingBag size={18} />
              </div>
              <span className="font-semibold text-white text-sm">Inventory Status</span>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-medium">
              Live Sync
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 border border-white/10 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center text-emerald-400 font-bold">
                  📦
                </div>
                <div>
                  <p className="font-medium text-white text-sm">Organic Cotton Tote</p>
                  <p className="text-xs text-slate-400">SKU: TOTE-882</p>
                </div>
              </div>
              <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium">
                12 left (Low)
              </span>
            </div>
            <div className="pt-2 border-t border-white/10 flex items-center justify-between text-xs text-slate-300 font-medium">
              <span>Auto-reorder enabled</span>
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 size={12} /> Supplier notified
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "calendar-health",
      title: "Plan Your Life.",
      description:
        "Schedule calendar events seamlessly, track your health vitals and daily steps, and receive intelligent reminders tailored to your routine.",
      gradient: "linear-gradient(135deg, #3b0764 0%, #581c87 50%, #2e1065 100%)",
      badge: "Calendar & Health",
      badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
      icon: Calendar,
      mockComponent: (
        <div className="w-full max-w-md rounded-2xl border border-purple-500/30 bg-slate-900 p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400">
                <Heart size={18} className="text-red-400" />
              </div>
              <span className="font-semibold text-white text-sm">Vitals & Schedule</span>
            </div>
            <span className="text-xs text-purple-300 font-medium">Today</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-800/80 border border-white/10 space-y-1">
              <p className="text-[10px] uppercase text-slate-400 font-medium">Blood Pressure</p>
              <p className="text-lg font-bold text-emerald-400">118/78 <span className="text-xs font-normal text-slate-400">mmHg</span></p>
              <span className="text-[10px] text-emerald-300 bg-emerald-500/15 px-2 py-0.5 rounded font-medium">Normal</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-800/80 border border-white/10 space-y-1">
              <p className="text-[10px] uppercase text-slate-400 font-medium">Daily Steps</p>
              <p className="text-lg font-bold text-purple-300">8,420</p>
              <span className="text-[10px] text-purple-300 bg-purple-500/15 px-2 py-0.5 rounded font-medium">Goal: 10k</span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "social-media",
      title: "Grow Your Brand.",
      description:
        "Generate high-converting promotional posts, schedule campaigns, and manage your social presence across platforms from one central hub.",
      gradient: "linear-gradient(135deg, #500724 0%, #831843 50%, #4c0519 100%)",
      badge: "Social Media Generator",
      badgeColor: "bg-pink-500/20 text-pink-300 border-pink-500/30",
      icon: Share2,
      mockComponent: (
        <div className="w-full max-w-md rounded-2xl border border-pink-500/30 bg-slate-900 p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-pink-500/20 flex items-center justify-center text-pink-400">
                <Share2 size={18} />
              </div>
              <span className="font-semibold text-white text-sm">Campaign Generator</span>
            </div>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-pink-500/15 text-pink-300 border border-pink-500/30 font-medium">
              AI Ready
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/80 border border-white/10 space-y-3 text-sm">
            <p className="text-slate-100 font-medium leading-relaxed">
              🚀 Exciting news! Our new autumn collection is officially live. Grab yours today before stock runs out! 🛍️✨ #AsoShop #NewRelease
            </p>
            <div className="flex items-center justify-between pt-2 border-t border-white/10 text-xs text-slate-300 font-medium">
              <span>Optimized for Twitter & LinkedIn</span>
              <span className="text-pink-400">Scheduled 10:00 AM</span>
            </div>
          </div>
        </div>
      ),
    },
  ];

  const scrollToSlide = (index: number) => {
    const clamped = Math.max(0, Math.min(slides.length - 1, index));
    setCurrentIndex(clamped);
    const container = containerRef.current;
    if (container) {
      const slideElement = container.children[clamped] as HTMLElement;
      if (slideElement) {
        container.scrollTo({
          left: slideElement.offsetLeft,
          behavior: "smooth",
        });
      }
    }
  };

  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) return;
    const scrollPosition = container.scrollLeft;
    const slideWidth = container.clientWidth;
    const newIndex = Math.round(scrollPosition / slideWidth);
    if (newIndex !== currentIndex && newIndex >= 0 && newIndex < slides.length) {
      setCurrentIndex(newIndex);
    }
  };

  return (
    <section id="capabilities" className="relative bg-slate-950 text-white py-24 overflow-hidden">
      {/* Section Header */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 mb-16 text-center">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-400 mb-3">
          Capabilities
        </p>
        <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-4">
          One assistant. Everything you run.
        </h2>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Explore how Aso unifies your workflows across chat, shop management, health, and social media.
        </p>
      </div>

      {/* Horizontal Scroll Container */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex overflow-x-auto snap-x snap-mandatory scroll-smooth w-full [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        style={{ scrollSnapType: "x mandatory" }}
      >
        {slides.map((slide, index) => {
          const Icon = slide.icon;

          return (
            <div
              key={slide.id}
              className="w-full shrink-0 snap-center px-6 lg:px-16 py-16 flex items-center justify-center relative"
              style={{ background: slide.gradient, minHeight: "520px" }}
            >
              <div className="absolute inset-0 bg-black/15 pointer-events-none" />

              <div className="max-w-6xl w-full mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10">
                {/* Left: Content */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                  className="space-y-6"
                >
                  <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${slide.badgeColor}`}>
                    <Icon size={14} /> {slide.badge}
                  </div>
                  <h3 className="text-3xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
                    {slide.title}
                  </h3>
                  <p className="text-slate-200 text-base md:text-lg leading-relaxed max-w-xl font-normal">
                    {slide.description}
                  </p>
                  <div className="flex items-center gap-4 pt-2">
                    <span className="text-xs text-slate-300 font-mono tracking-wider">
                      0{index + 1} / 0{slides.length}
                    </span>
                  </div>
                </motion.div>

                {/* Right: Mock UI */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="flex justify-center"
                >
                  {slide.mockComponent}
                </motion.div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation Controls at Bottom Center */}
      <div className="mt-12 flex flex-col items-center gap-4">
        <div className="flex items-center gap-6 bg-slate-900/90 backdrop-blur-md px-6 py-3 rounded-full border border-white/15 shadow-2xl">
          {/* Left Arrow */}
          <button
            onClick={() => scrollToSlide(currentIndex - 1)}
            disabled={currentIndex === 0}
            className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed border border-white/15"
            aria-label="Previous slide"
          >
            <ChevronLeft size={20} />
          </button>

          {/* Dots */}
          <div className="flex items-center gap-2">
            {slides.map((_, i) => (
              <button
                key={i}
                onClick={() => scrollToSlide(i)}
                className={`h-2 rounded-full transition-all ${
                  currentIndex === i ? "w-8 bg-white" : "w-2 bg-white/30 hover:bg-white/50"
                }`}
                aria-label={`Go to slide ${i + 1}`}
              />
            ))}
          </div>

          {/* Right Arrow */}
          <button
            onClick={() => scrollToSlide(currentIndex + 1)}
            disabled={currentIndex === slides.length - 1}
            className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed border border-white/15"
            aria-label="Next slide"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </section>
  );
}

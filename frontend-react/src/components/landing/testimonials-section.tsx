"use client";

import { Star, MessageSquareQuote } from "lucide-react";

interface Testimonial {
  quote: string;
  name: string;
  role: string;
  initials: string;
  gradient: string;
}

const testimonials: Testimonial[] = [
  {
    quote: "Aso saved me 10 hours a week on shop management and inventory tracking. The automated workflows are incredible.",
    name: "Sarah Jenkins",
    role: "Boutique Shop Owner",
    initials: "SJ",
    gradient: "from-blue-500 to-indigo-500",
  },
  {
    quote: "The Gmail integration and AI priority engine completely transformed how I handle customer emails and inquiries. Absolute lifesaver.",
    name: "Marcus Vance",
    role: "Operations Director",
    initials: "MV",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    quote: "Clean interface, lightning fast, and our team picked it up in minutes. Highly recommend Aso to any growing business.",
    name: "Elena Rostova",
    role: "Founder & CEO",
    initials: "ER",
    gradient: "from-emerald-500 to-teal-500",
  },
];

export default function TestimonialsSection() {
  return (
    <section className="py-24 px-6 relative overflow-hidden bg-slate-950 text-white">
      {/* Background glow effects */}
      <div
        className="absolute top-1/4 right-1/4 w-72 h-72 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "#8b5cf6" }}
      />
      <div
        className="absolute bottom-1/4 left-1/4 w-80 h-80 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "#3b82f6" }}
      />

      <div className="max-w-6xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <div
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider mb-4 border"
            style={{
              background: "rgba(59, 130, 246, 0.1)",
              borderColor: "rgba(59, 130, 246, 0.25)",
              color: "#60a5fa",
            }}
          >
            <MessageSquareQuote size={14} /> Testimonials
          </div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Loved by shop owners & professionals
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            See how Aso is helping businesses save time, streamline operations, and scale with confidence.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, index) => (
            <div
              key={index}
              className="relative p-8 rounded-2xl border transition-all duration-300 hover:-translate-y-1 hover:border-slate-700 flex flex-col justify-between"
              style={{
                background: "rgba(255, 255, 255, 0.03)",
                backdropFilter: "blur(16px)",
                borderColor: "rgba(255, 255, 255, 0.08)",
                boxShadow: "0 20px 40px -15px rgba(0, 0, 0, 0.5)",
              }}
            >
              <div>
                {/* Rating Stars */}
                <div className="flex items-center gap-1 mb-6 text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={16} fill="currentColor" />
                  ))}
                </div>

                {/* Quote */}
                <p className="text-slate-300 text-base leading-relaxed mb-8 italic">
                  &ldquo;{t.quote}&rdquo;
                </p>
              </div>

              {/* Author Info */}
              <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white text-sm bg-gradient-to-br ${t.gradient} shadow-md`}
                >
                  {t.initials}
                </div>
                <div>
                  <h3 className="font-semibold text-white text-base">{t.name}</h3>
                  <p className="text-xs text-slate-400">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

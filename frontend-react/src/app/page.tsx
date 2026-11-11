"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bot } from "lucide-react";
import { HeroSection } from "@/components/landing/hero-section";
import { CapabilitiesSection } from "@/components/landing/capabilities-section";
import TestimonialsSection from "@/components/landing/testimonials-section";
import FaqSection from "@/components/landing/faq-section";
import Footer from "@/components/landing/footer";

const reveal = {
  initial: { opacity: 0, y: 50 },
  whileInView: { opacity: 1, y: 0 },
  transition: { duration: 0.6 },
  viewport: { once: true },
};

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-x-clip bg-slate-950">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg shadow-blue-500/20">
              <Bot size={20} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">Aso</span>
          </Link>

          <Link
            href="/dashboard"
            className="group inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-sm font-semibold text-white backdrop-blur-md transition-colors hover:bg-white/15"
          >
            Go to Dashboard
            <ArrowRight
              size={16}
              className="transition-transform group-hover:translate-x-0.5"
            />
          </Link>
        </nav>
      </header>

      <main>
        <motion.div
          className="bg-slate-950"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <HeroSection />
        </motion.div>

        <motion.div className="bg-slate-900" {...reveal}>
          <CapabilitiesSection />
        </motion.div>

        <motion.div className="bg-slate-950" {...reveal}>
          <TestimonialsSection />
        </motion.div>

        <motion.div className="bg-slate-900" {...reveal}>
          <FaqSection />
        </motion.div>

        <motion.div className="bg-slate-950" {...reveal}>
          <Footer />
        </motion.div>
      </main>
    </div>
  );
}

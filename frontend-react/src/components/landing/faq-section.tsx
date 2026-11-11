"use client";

import { useState } from "react";
import { ChevronDown, HelpCircle } from "lucide-react";

interface FaqItem {
  question: string;
  answer: string;
}

const faqs: FaqItem[] = [
  {
    question: "What is Aso?",
    answer:
      "Aso is your intelligent AI assistant designed to streamline workflows, manage shop inventory, track job applications, and organize communications in one unified workspace.",
  },
  {
    question: "Can I use it for my shop?",
    answer:
      "Yes! Aso features a robust shop and inventory management module that allows you to track products, monitor stock levels, manage orders, and analyze sales effortlessly.",
  },
  {
    question: "Is my data safe?",
    answer:
      "Absolutely. We employ enterprise-grade encryption in transit and at rest, alongside strict privacy controls, ensuring your business and personal data remain confidential and secure.",
  },
  {
    question: "Does it connect to Gmail?",
    answer:
      "Yes, Aso integrates seamlessly with Gmail to automatically summarize incoming emails, prioritize important messages, and assist you in drafting professional replies instantly.",
  },
  {
    question: "Can my staff use it?",
    answer:
      "Yes, you can invite team members and staff with customizable role-based access controls to collaborate securely across inventory, orders, and shared calendars.",
  },
];

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section
      className="py-24 px-6 relative overflow-hidden"
      style={{
        background: "linear-gradient(135deg, #091c1b 0%, #0d2828 50%, #061515 100%)",
      }}
    >
      {/* Background glow accents */}
      <div
        className="absolute top-1/2 left-10 w-80 h-80 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "#10b981" }}
      />
      <div
        className="absolute bottom-10 right-10 w-96 h-96 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: "#3b82f6" }}
      />

      <div className="max-w-4xl mx-auto relative z-10">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider mb-4 border"
            style={{
              background: "rgba(16, 185, 129, 0.1)",
              borderColor: "rgba(16, 185, 129, 0.25)",
              color: "#34d399",
            }}
          >
            <HelpCircle size={14} /> FAQ
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-slate-300 text-lg max-w-2xl mx-auto">
            Got questions about Aso? We&apos;ve got answers. Everything you need to know about the platform and features.
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div
                key={index}
                className="rounded-2xl border transition-all duration-300 overflow-hidden"
                style={{
                  background: isOpen ? "rgba(255, 255, 255, 0.06)" : "rgba(255, 255, 255, 0.03)",
                  borderColor: isOpen ? "rgba(52, 211, 153, 0.3)" : "rgba(255, 255, 255, 0.08)",
                  backdropFilter: "blur(12px)",
                }}
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full px-6 py-5 text-left flex items-center justify-between gap-4 font-semibold text-white focus:outline-none transition-colors"
                >
                  <span className="text-lg">{faq.question}</span>
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-transform duration-300"
                    style={{
                      background: isOpen ? "rgba(52, 211, 153, 0.2)" : "rgba(255, 255, 255, 0.06)",
                      color: isOpen ? "#34d399" : "#94a3b8",
                      transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
                    }}
                  >
                    <ChevronDown size={18} />
                  </div>
                </button>

                <div
                  className="transition-all duration-300 ease-in-out overflow-hidden"
                  style={{
                    maxHeight: isOpen ? "300px" : "0px",
                    opacity: isOpen ? 1 : 0,
                  }}
                >
                  <div className="px-6 pb-6 pt-1 text-slate-300 leading-relaxed text-base border-t border-white/5">
                    {faq.answer}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

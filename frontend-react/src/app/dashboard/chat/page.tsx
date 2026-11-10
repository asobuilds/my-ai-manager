"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { Send, Bot, User as UserIcon, Loader2 } from "lucide-react";
import api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await api.post("/chat", {
        message: input.trim(),
        conversation_id: null,
      });
      const assistantMsg: Message = { role: "assistant", content: response.data.response || "" };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Failed to get a response from Aso.";
      setMessages((prev) => [...prev, { role: "assistant", content: errorMsg }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Message History */}
      <div className="flex-1 overflow-y-auto px-4 pt-4 pb-2">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mx-auto mb-4">
              <Bot size={28} className="text-blue-400" />
            </div>
            <h2 className="text-lg font-semibold text-[var(--foreground)] mb-2">
              Hello, I'm Aso!
            </h2>
            <p className="text-sm text-[var(--muted-foreground)] max-w-md mx-auto">
              I'm your personal AI assistant. Ask me about your emails, calendar, inventory, or anything else!
            </p>
            <div className="mt-6 flex gap-2 justify-center flex-wrap">
              {[
                "Check my low stock items",
                "Schedule a meeting tomorrow",
                "What emails need attention?",
                "Show me my calendar",
              ].map((hint) => (
                <button
                  key={hint}
                  onClick={() => setInput(hint)}
                  className="px-3 py-1.5 text-xs rounded-lg border text-[var(--muted-foreground)] hover:bg-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                  style={{ borderColor: "rgba(255,255,255,0.08)" }}
                >
                  {hint}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] px-4 py-3 rounded-2xl transition-all ${
                    msg.role === "user"
                      ? "bg-blue-500/15 text-[var(--foreground)] text-sm"
                      : "glass-card glass-card-transition text-sm"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {msg.role === "assistant" && (
                      <div className="w-6 h-6 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Bot size={14} className="text-blue-400" />
                      </div>
                    )}
                    <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                    {msg.role === "user" && (
                      <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                        <UserIcon size={14} className="text-white" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="glass-card px-4 py-3 rounded-2xl">
                  <div className="flex items-center gap-2">
                    <Bot size={14} className="text-blue-400" />
                    <div className="flex space-x-1">
                      <Loader2 size={16} className="animate-spin text-blue-400" />
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-border glass-card-transition">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Aso anything..."
            className="flex-1 px-4 py-2.5 rounded-xl border bg-transparent text-sm focus:outline-none"
            style={{
              borderColor: "rgba(255,255,255,0.08)",
              color: "var(--foreground)",
            }}
            onFocus={(e) => (e.currentTarget.style.borderColor = "rgba(59,130,246,0.4)")}
            onBlur={(e) => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)")}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex items-center justify-center w-10 h-10 rounded-xl text-blue-400 hover:bg-blue-500/10 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
}
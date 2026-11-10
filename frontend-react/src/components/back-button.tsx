"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

export function BackButton() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.back()}
      className="glass-link-transition flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm text-muted-foreground hover:text-foreground transition-colors"
    >
      <ArrowLeft size={16} className="text-blue-400" />
      <span>Back</span>
    </button>
  );
}
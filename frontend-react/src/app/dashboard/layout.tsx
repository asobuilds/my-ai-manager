"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard-layout";

export default function DashboardRouteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = () =>
      setAuthenticated(Boolean(localStorage.getItem("access_token")));
    const handleUnauthorized = () => setAuthenticated(false);

    checkAuth();
    window.addEventListener("aso:unauthorized", handleUnauthorized);
    window.addEventListener("storage", checkAuth);
    return () => {
      window.removeEventListener("aso:unauthorized", handleUnauthorized);
      window.removeEventListener("storage", checkAuth);
    };
  }, []);

  return (
    <DashboardLayout>
      {authenticated === false && (
        <div className="mb-6 flex flex-col gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200 sm:flex-row sm:items-center sm:justify-between">
          <span className="flex items-center gap-2">
            <AlertTriangle size={16} />
            You&apos;re not signed in. Showing a preview with no personal data.
          </span>
          <Link
            href="/"
            className="font-semibold text-amber-100 underline underline-offset-4 hover:text-white"
          >
            Back to home
          </Link>
        </div>
      )}
      {children}
    </DashboardLayout>
  );
}

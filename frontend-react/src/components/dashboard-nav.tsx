"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageCircle,
  CalendarDays,
  Inbox,
  Briefcase,
  Megaphone,
  Package,
  Plug,
  Settings,
  User,
  Heart,
  Home,
  Lock,
} from "lucide-react";

const navItems = [
  { label: "Chat", href: "/dashboard", icon: MessageCircle },
  { label: "Calendar", href: "/dashboard/calendar", icon: CalendarDays },
  { label: "Home", href: "/dashboard/home", icon: Home, iconClass: "text-orange-400" },
  { label: "Data Inventory", href: "/dashboard/inventory", icon: Inbox },
  { label: "Shop Manager", href: "/dashboard/shop", icon: Package },
  { label: "Social Media", href: "/dashboard/social", icon: Megaphone },
  { label: "Job Tracker", href: "/dashboard/jobs", icon: Briefcase },
  { label: "Health", href: "/dashboard/health", icon: Heart, iconClass: "text-red-400" },
  { label: "Vault", href: "/dashboard/vault", icon: Lock, iconClass: "text-yellow-400" },
  { label: "Integrations", href: "/dashboard/integrations", icon: Plug },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
  { label: "Profile", href: "/dashboard/profile", icon: User },
];

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <nav className="px-2 py-3 space-y-0.5">
      {navItems.map((item) => {
        const active = pathname === item.href || pathname.startsWith(item.href + "/");
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              active
                ? "text-white"
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
            style={active ? { background: "linear-gradient(135deg, #3b82f6, #8b5cf6)" } : undefined}
          >
            <item.icon size={18} className={item.iconClass || ""} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

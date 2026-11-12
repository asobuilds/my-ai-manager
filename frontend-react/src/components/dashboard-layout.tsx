"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
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
  LogOut,
  MessageSquare,
  Heart,
  Home,
  Lock,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { BackButton } from "@/components/back-button";
import { usePreferences } from "@/contexts/PreferenceContext";

const navItems = [
  { label: "Chat", href: "/dashboard/chat", icon: MessageSquare, feature: "chat", iconColor: "text-blue-400" },
  { label: "Dashboard", href: "/dashboard", icon: MessageCircle, feature: "dashboard", iconColor: "text-blue-400" },
  { label: "Calendar", href: "/dashboard/calendar", icon: CalendarDays, feature: "calendar", iconColor: "text-purple-400" },
  { label: "Data Inventory", href: "/dashboard/inventory", icon: Inbox, feature: "inventory", iconColor: "text-cyan-400" },
  { label: "Shop Manager", href: "/dashboard/shop", icon: Package, feature: "shop", iconColor: "text-emerald-400" },
  { label: "Social Media", href: "/dashboard/social", icon: Megaphone, feature: "social", iconColor: "text-pink-400" },
  { label: "Job Tracker", href: "/dashboard/jobs", icon: Briefcase, feature: "jobs", iconColor: "text-amber-400" },
  { label: "Health", href: "/dashboard/health", icon: Heart, feature: "health", iconColor: "text-red-400" },
  { label: "Home", href: "/dashboard/home", icon: Home, feature: "home", iconColor: "text-orange-400" },
  { label: "Vault", href: "/dashboard/vault", icon: Lock, feature: "vault", iconColor: "text-yellow-400" },
  { label: "Integrations", href: "/dashboard/integrations", icon: Plug, feature: "integrations", iconColor: "text-indigo-400" },
  { label: "Settings", href: "/dashboard/settings", icon: Settings, feature: "settings", iconColor: "text-green-400" },
  { label: "Profile", href: "/dashboard/profile", icon: User, feature: "profile", iconColor: "text-violet-400" },
];

function SidebarContentInner() {
  const pathname = usePathname();
  const router = useRouter();
  const { state } = useSidebar();
  const { enabled_features } = usePreferences();

  const visibleItems = navItems.filter(
    (item) => item.label === "Chat" || !item.feature || enabled_features.includes(item.feature)
  );

  function handleLogout() {
    localStorage.removeItem("access_token");
    router.push("/");
  }

  return (
    <>
      <SidebarHeader className="flex items-center gap-3 px-4 py-5 border-b border-border">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0 bg-gradient-to-br from-blue-500 to-purple-600 text-white font-bold">
          🤖
        </div>
        {state !== "collapsed" && (
          <div>
            <p className="text-sm font-bold text-foreground leading-none">Aso</p>
            <p className="text-[10px] text-muted-foreground mt-0.5 leading-none">Data Assistant</p>
          </div>
        )}
      </SidebarHeader>

      <SidebarContent>
        <SidebarMenu>
          {visibleItems.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            return (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  tooltip={item.label}
                  className={
                    active
                      ? "glass-link-active text-blue-400 font-semibold bg-blue-500/10"
                      : "glass-link text-muted-foreground"
                  }
                >
                  <Link href={item.href} className="flex items-center gap-3 w-full">
                    <item.icon size={16} className={item.iconColor} />
                    <span>{item.label}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="border-t border-border p-3">
        <button
          onClick={handleLogout}
          className="glass-link flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm text-muted-foreground hover:text-destructive transition-colors"
        >
          <LogOut size={16} />
          {state !== "collapsed" && <span>Log Out</span>}
        </button>
      </SidebarFooter>
    </>
  );
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showBackButton = pathname !== "/dashboard";

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full bg-background text-foreground">
        <Sidebar collapsible="icon" variant="inset" className="border-r border-white/5 bg-slate-900/80 backdrop-blur-md">
          <SidebarContentInner />
          <SidebarRail />
        </Sidebar>
        <main className="flex-1 flex flex-col min-w-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-foreground">
          <header className="h-14 border-b border-white/10 flex items-center px-4 gap-3 shrink-0 bg-slate-900/50 backdrop-blur-sm">
            {showBackButton && <BackButton />}
            <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
            <span className="text-xs text-muted-foreground ml-1">
              Aso Data Assistant
            </span>
          </header>
          <div className="flex-1 overflow-auto p-6">{children}</div>
        </main>
      </div>
    </SidebarProvider>
  );
}

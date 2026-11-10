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
} from "lucide-react";
import { useRouter } from "next/navigation";
import { usePreferences } from "@/contexts/PreferenceContext";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: MessageCircle, feature: "dashboard" },
  { label: "Calendar", href: "/dashboard/calendar", icon: CalendarDays, feature: "calendar" },
  { label: "Data Inventory", href: "/dashboard/inventory", icon: Inbox, feature: "inventory" },
  { label: "Shop Manager", href: "/dashboard/shop", icon: Package, feature: "shop" },
  { label: "Social Media", href: "/dashboard/social", icon: Megaphone, feature: "social" },
  { label: "Job Tracker", href: "/dashboard/jobs", icon: Briefcase, feature: "jobs" },
  { label: "Integrations", href: "/dashboard/integrations", icon: Plug },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
  { label: "Profile", href: "/dashboard/profile", icon: User },
];

function SidebarContentInner() {
  const pathname = usePathname();
  const router = useRouter();
  const { state } = useSidebar();
  const { enabled_features } = usePreferences();

  const visibleItems = navItems.filter(
    (item) => !item.feature || enabled_features.includes(item.feature)
  );

  function handleLogout() {
    localStorage.removeItem("access_token");
    router.push("/");
  }

  return (
    <>
      <SidebarHeader className="flex items-center gap-3 px-4 py-5 border-b border-border">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0 bg-primary text-primary-foreground font-bold">
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
                      ? "glass-link-active text-primary font-semibold"
                      : "glass-link text-muted-foreground"
                  }
                >
                  <Link href={item.href} className="flex items-center gap-3 w-full">
                    <item.icon size={16} />
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
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full bg-background text-foreground">
        <Sidebar collapsible="icon" variant="inset" className="border-r sidebar-glass">
          <SidebarContentInner />
          <SidebarRail />
        </Sidebar>
        <main className="flex-1 flex flex-col min-w-0 bg-background text-foreground">
          <header className="h-14 border-b border-border flex items-center px-4 gap-3 shrink-0 bg-muted/20">
            <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
            <span className="text-xs text-muted-foreground ml-1">
              Aso Data Assistant
            </span>
          </header>
          <div className="flex-1 overflow-auto p-6 bg-background text-foreground">{children}</div>
        </main>
      </div>
    </SidebarProvider>
  );
}

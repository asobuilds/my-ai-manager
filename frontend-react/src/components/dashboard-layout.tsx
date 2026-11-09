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

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: MessageCircle },
  { label: "Calendar", href: "/dashboard/calendar", icon: CalendarDays },
  { label: "Data Inventory", href: "/dashboard/inventory", icon: Inbox },
  { label: "Shop Manager", href: "/dashboard/shop", icon: Package },
  { label: "Social Media", href: "/dashboard/social", icon: Megaphone },
  { label: "Job Tracker", href: "/dashboard/jobs", icon: Briefcase },
  { label: "Integrations", href: "/dashboard/integrations", icon: Plug },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
  { label: "Profile", href: "/dashboard/profile", icon: User },
];

function SidebarContentInner() {
  const pathname = usePathname();
  const router = useRouter();
  const { state } = useSidebar();

  function handleLogout() {
    localStorage.removeItem("access_token");
    router.push("/");
  }

  return (
    <>
      <SidebarHeader className="flex items-center gap-3 px-4 py-5 border-b border-[var(--border)]">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0"
          style={{ background: "linear-gradient(135deg, #2dd4bf, #a78bfa)" }}
        >
          🤖
        </div>
        {state !== "collapsed" && (
          <div>
            <p className="text-sm font-bold text-[var(--foreground)] leading-none">Aso</p>
            <p className="text-[10px] text-[var(--muted-foreground)] mt-0.5 leading-none">Data Assistant</p>
          </div>
        )}
      </SidebarHeader>

      <SidebarContent>
        <SidebarMenu>
          {navItems.map((item) => {
            const active =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const btnStyle = active
              ? { background: "rgba(45,212,191,0.12)", color: "#2dd4bf" }
              : undefined;
            return (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton tooltip={item.label} style={btnStyle}>
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

      <SidebarFooter className="border-t border-[var(--border)] p-3">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-[var(--muted-foreground)] hover:text-red-400 hover:bg-red-500/10 transition-colors"
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
      <div className="flex min-h-screen w-full" style={{ background: "#0a0a0f" }}>
        <Sidebar collapsible="icon" variant="inset" className="border-r border-[var(--border)]">
          <SidebarContentInner />
          <SidebarRail />
        </Sidebar>
        <main className="flex-1 flex flex-col min-w-0">
          <header
            className="h-14 border-b border-[var(--border)] flex items-center px-4 gap-3 shrink-0"
            style={{ background: "rgba(255,255,255,0.02)" }}
          >
            <SidebarTrigger className="text-[var(--muted-foreground)] hover:text-[var(--foreground)]" />
            <span className="text-xs text-[var(--muted-foreground)] ml-1">
              Aso Data Assistant
            </span>
          </header>
          <div className="flex-1 overflow-auto p-6">{children}</div>
        </main>
      </div>
    </SidebarProvider>
  );
}

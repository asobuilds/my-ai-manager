export default function DashboardPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
        Welcome to your Dashboard
      </h1>
      <p className="text-slate-500 dark:text-slate-400 mb-8">
        Your AI-powered data assistant is ready. Use the sidebar to navigate between sections.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { title: "💬 Chat", desc: "Talk to Aso about your data", href: "/dashboard" },
          { title: "📦 Data Inventory", desc: "Browse and manage synced messages", href: "/dashboard/inventory" },
          { title: "💼 Job Tracker", desc: "Track your applications", href: "/dashboard/jobs" },
          { title: "🔌 Integrations", desc: "Connect your accounts", href: "/dashboard/integrations" },
          { title: "⚙️ Settings", desc: "Customize your experience", href: "/dashboard/settings" },
          { title: "👤 Profile", desc: "Manage your account", href: "/dashboard/profile" },
        ].map((card) => (
          <a
            key={card.href}
            href={card.href}
            className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-md transition-shadow group"
          >
            <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-blue-500 transition-colors">
              {card.title}
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              {card.desc}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}

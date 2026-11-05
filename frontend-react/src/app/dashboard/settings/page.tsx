export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">⚙️ Settings</h1>
      <p className="text-sm text-[var(--muted-foreground)] mb-8">
        Customize your dashboard. Theme, layout, and notification preferences.
      </p>
      <div
        className="rounded-xl border border-dashed flex flex-col items-center justify-center py-24 text-center"
        style={{ borderColor: "rgba(255,255,255,0.08)" }}
      >
        <p className="text-sm text-[var(--muted-foreground)]">Settings panel coming soon.</p>
      </div>
    </div>
  );
}

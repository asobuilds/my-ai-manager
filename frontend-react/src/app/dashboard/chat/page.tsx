export default function ChatPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">💬 Chat</h1>
      <p className="text-sm text-[var(--muted-foreground)] mb-8">
        Talk to Aso. Ask questions about your inbox, draft emails, or manage your schedule.
      </p>
      <div
        className="rounded-xl border border-dashed flex flex-col items-center justify-center py-24 text-center"
        style={{ borderColor: "rgba(255,255,255,0.08)" }}
      >
        <p className="text-sm text-[var(--muted-foreground)]">Chat interface coming soon.</p>
      </div>
    </div>
  );
}

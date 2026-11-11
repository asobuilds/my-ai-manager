"use client";

import { useCallback, useEffect, useState } from "react";
import { Home as HomeIcon, Wrench, Plus, CheckCircle2, Clock, ShieldCheck, Tag, Loader2, X, AlertCircle } from "lucide-react";
import api from "@/lib/api";

interface HomeAsset {
  id?: string;
  name: string;
  category: string;
  serial_number?: string;
  purchase_date?: string;
  warranty_expiry: string;
}

interface MaintenanceTask {
  id?: string;
  title: string;
  description?: string;
  due_date: string;
  asset_id?: string;
  asset_name?: string;
  recurring: boolean;
  completed: boolean;
}

export default function HomeManagementPage() {
  const [assets, setAssets] = useState<HomeAsset[]>([
    { id: "1", name: "Smart HVAC System", category: "Climate Control", serial_number: "HVAC-9081-X", purchase_date: "2024-05-12", warranty_expiry: "2027-05-12" },
    { id: "2", name: "Solar Inverter & Battery", category: "Power & Energy", serial_number: "SOL-INV-442", purchase_date: "2023-08-20", warranty_expiry: "2028-08-20" },
    { id: "3", name: "Smart Refrigerator", category: "Kitchen Appliances", serial_number: "REF-LG-771", purchase_date: "2024-01-15", warranty_expiry: "2026-01-15" },
  ]);

  const [tasks, setTasks] = useState<MaintenanceTask[]>([
    { id: "1", title: "Replace HVAC Air Filters", description: "Change high-efficiency MERV 13 filters in main hallway unit.", due_date: "2026-12-01", asset_id: "1", asset_name: "Smart HVAC System", recurring: true, completed: false },
    { id: "2", title: "Inverter Annual Checkup", description: "Inspect terminal connections and dust solar panels.", due_date: "2026-11-25", asset_id: "2", asset_name: "Solar Inverter & Battery", recurring: true, completed: false },
    { id: "3", title: "Clean Refrigerator Coils", description: "Vacuum dust buildup underneath and behind the fridge.", due_date: "2026-11-18", asset_id: "3", asset_name: "Smart Refrigerator", recurring: false, completed: true },
  ]);

  const [loadingAssets, setLoadingAssets] = useState(true);
  const [loadingTasks, setLoadingTasks] = useState(true);

  // Modals state
  const [isAssetModalOpen, setIsAssetModalOpen] = useState(false);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [savingAsset, setSavingAsset] = useState(false);
  const [savingTask, setSavingTask] = useState(false);

  // Asset form state
  const [assetForm, setAssetForm] = useState({
    name: "",
    category: "Appliances",
    serial_number: "",
    purchase_date: "",
    warranty_expiry: "",
  });

  // Task form state
  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    due_date: "",
    asset_id: "",
    recurring: false,
  });

  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const fetchData = useCallback(async () => {
    setLoadingAssets(true);
    setLoadingTasks(true);

    try {
      const res = await api.get<HomeAsset[]>("/home/assets");
      if (Array.isArray(res.data) && res.data.length > 0) {
        setAssets(res.data);
      }
    } catch {
      // Keep mock assets
    } finally {
      setLoadingAssets(false);
    }

    try {
      const res = await api.get<MaintenanceTask[]>("/home/maintenance");
      if (Array.isArray(res.data) && res.data.length > 0) {
        setTasks(res.data);
      }
    } catch {
      // Keep mock tasks
    } finally {
      setLoadingTasks(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleAddAsset(e: React.FormEvent) {
    e.preventDefault();
    setSavingAsset(true);
    const newAsset: HomeAsset = {
      name: assetForm.name.trim(),
      category: assetForm.category.trim(),
      serial_number: assetForm.serial_number.trim() || undefined,
      purchase_date: assetForm.purchase_date || undefined,
      warranty_expiry: assetForm.warranty_expiry || new Date().toISOString().split("T")[0],
    };

    try {
      const res = await api.post<HomeAsset>("/home/assets", newAsset);
      setAssets((prev) => [res.data || { ...newAsset, id: Math.random().toString() }, ...prev]);
      showToast("Home asset added successfully", "ok");
      setIsAssetModalOpen(false);
      setAssetForm({ name: "", category: "Appliances", serial_number: "", purchase_date: "", warranty_expiry: "" });
    } catch {
      setAssets((prev) => [{ ...newAsset, id: Math.random().toString() }, ...prev]);
      showToast("Home asset added locally", "ok");
      setIsAssetModalOpen(false);
      setAssetForm({ name: "", category: "Appliances", serial_number: "", purchase_date: "", warranty_expiry: "" });
    } finally {
      setSavingAsset(false);
    }
  }

  async function handleAddTask(e: React.FormEvent) {
    e.preventDefault();
    setSavingTask(true);
    const selectedAsset = assets.find((a) => a.id === taskForm.asset_id);
    const newTask: MaintenanceTask = {
      title: taskForm.title.trim(),
      description: taskForm.description.trim() || undefined,
      due_date: taskForm.due_date || new Date().toISOString().split("T")[0],
      asset_id: taskForm.asset_id || undefined,
      asset_name: selectedAsset?.name,
      recurring: taskForm.recurring,
      completed: false,
    };

    try {
      const res = await api.post<MaintenanceTask>("/home/maintenance", newTask);
      setTasks((prev) => [res.data || { ...newTask, id: Math.random().toString() }, ...prev]);
      showToast("Maintenance task scheduled", "ok");
      setIsTaskModalOpen(false);
      setTaskForm({ title: "", description: "", due_date: "", asset_id: "", recurring: false });
    } catch {
      setTasks((prev) => [{ ...newTask, id: Math.random().toString() }, ...prev]);
      showToast("Maintenance task scheduled locally", "ok");
      setIsTaskModalOpen(false);
      setTaskForm({ title: "", description: "", due_date: "", asset_id: "", recurring: false });
    } finally {
      setSavingTask(false);
    }
  }

  async function handleCompleteTask(taskId?: string) {
    if (!taskId) return;
    try {
      await api.patch(`/home/maintenance/${taskId}/complete`, { completed: true });
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, completed: true } : t))
      );
      showToast("Maintenance task marked complete", "ok");
    } catch {
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, completed: true } : t))
      );
      showToast("Task marked complete locally", "ok");
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-12 pb-16">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <HomeIcon className="text-orange-400" size={26} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Home Management</h1>
          </div>
          <p className="text-sm text-slate-400">
            Track household assets, manage warranties, and stay on top of scheduled maintenance tasks.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAssetModalOpen(true)}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-white transition-all shadow-lg hover:opacity-90 flex items-center gap-2"
            style={{ background: "linear-gradient(135deg, #f97316, #fb923c)", boxShadow: "0 4px 14px rgba(249,115,22,0.3)" }}
          >
            <Plus size={16} /> Add Asset
          </button>
          <button
            onClick={() => setIsTaskModalOpen(true)}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-white transition-all shadow-lg hover:opacity-90 flex items-center gap-2"
            style={{ background: "linear-gradient(135deg, #3b82f6, #6366f1)", boxShadow: "0 4px 14px rgba(59,130,246,0.3)" }}
          >
            <Plus size={16} /> Add Task
          </button>
        </div>
      </div>

      {/* ── Toast Notification ── */}
      {toast && (
        <div
          className="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl border text-sm shadow-xl"
          style={{
            background: toast.type === "ok" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
            borderColor: toast.type === "ok" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)",
            color: toast.type === "ok" ? "#34d399" : "#f87171",
            backdropFilter: "blur(12px)",
          }}
        >
          {toast.type === "ok" ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          {toast.msg}
        </div>
      )}

      {/* ── Section 1: Home Assets ── */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldCheck size={18} className="text-orange-400" /> Home Assets & Warranties
          </h2>
          <span className="text-xs text-slate-400">{assets.length} registered assets</span>
        </div>

        {loadingAssets ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-44 rounded-2xl bg-white/5 animate-pulse border border-white/10" />
            ))}
          </div>
        ) : assets.length === 0 ? (
          <div className="p-12 rounded-2xl border border-white/10 text-center text-slate-400 text-sm bg-white/[0.02]">
            No home assets added yet. Click &quot;Add Asset&quot; to register your first appliance or device.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {assets.map((asset, idx) => (
              <div
                key={asset.id || idx}
                className="p-6 rounded-2xl border transition-all duration-300 hover:border-orange-500/40 flex flex-col justify-between"
                style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-orange-500/10 text-orange-300 font-medium border border-orange-500/20 flex items-center gap-1">
                      <Tag size={12} /> {asset.category}
                    </span>
                    {asset.serial_number && (
                      <span className="text-xs text-slate-400 font-mono">S/N: {asset.serial_number}</span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{asset.name}</h3>
                  {asset.purchase_date && (
                    <p className="text-xs text-slate-400 mb-1">Purchased: {asset.purchase_date}</p>
                  )}
                </div>

                <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Warranty Expiry</span>
                  <span className="font-semibold text-emerald-400 flex items-center gap-1">
                    <ShieldCheck size={14} /> {asset.warranty_expiry}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Section 2: Maintenance Schedule ── */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Wrench size={18} className="text-blue-400" /> Maintenance Schedule
          </h2>
          <span className="text-xs text-slate-400">
            {tasks.filter((t) => !t.completed).length} pending tasks
          </span>
        </div>

        {loadingTasks ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 rounded-2xl bg-white/5 animate-pulse border border-white/10" />
            ))}
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-12 rounded-2xl border border-white/10 text-center text-slate-400 text-sm bg-white/[0.02]">
            No maintenance tasks scheduled. Click &quot;Add Task&quot; to create one.
          </div>
        ) : (
          <div className="space-y-4">
            {tasks.map((task, idx) => (
              <div
                key={task.id || idx}
                className={`p-6 rounded-2xl border transition-all duration-300 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 ${
                  task.completed ? "opacity-60 bg-white/[0.01]" : "bg-white/[0.03]"
                }`}
                style={{ backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap">
                    <h3 className={`text-base font-semibold text-white ${task.completed ? "line-through text-slate-400" : ""}`}>
                      {task.title}
                    </h3>
                    {task.recurring && (
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 font-medium border border-blue-500/20">
                        Recurring
                      </span>
                    )}
                    {task.asset_name && (
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-orange-500/10 text-orange-300 font-medium border border-orange-500/20">
                        {task.asset_name}
                      </span>
                    )}
                  </div>
                  {task.description && (
                    <p className="text-xs text-slate-400 leading-relaxed">{task.description}</p>
                  )}
                  <div className="flex items-center gap-2 text-xs text-slate-400 pt-1">
                    <Clock size={14} className="text-slate-400" /> Due: <span className="text-slate-300 font-medium">{task.due_date}</span>
                  </div>
                </div>

                <div className="shrink-0 flex items-center gap-3">
                  {task.completed ? (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
                      <CheckCircle2 size={14} /> Completed
                    </span>
                  ) : (
                    <button
                      onClick={() => handleCompleteTask(task.id)}
                      className="px-4 py-2 rounded-xl text-xs font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98] flex items-center gap-1.5 shadow-md"
                      style={{ background: "linear-gradient(135deg, #10b981, #059669)" }}
                    >
                      <CheckCircle2 size={14} /> Complete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Add Asset Modal ── */}
      {isAssetModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div
            className="w-full max-w-lg rounded-2xl border p-6 shadow-2xl relative"
            style={{ background: "#0b1329", borderColor: "rgba(255,255,255,0.12)" }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck size={18} className="text-orange-400" /> Add Home Asset
              </h3>
              <button onClick={() => setIsAssetModalOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleAddAsset} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-300 mb-1 block">Asset Name *</label>
                <input
                  type="text"
                  value={assetForm.name}
                  onChange={(e) => setAssetForm({ ...assetForm, name: e.target.value })}
                  placeholder="e.g. Smart Water Heater"
                  className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-orange-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Category</label>
                  <input
                    type="text"
                    value={assetForm.category}
                    onChange={(e) => setAssetForm({ ...assetForm, category: e.target.value })}
                    placeholder="e.g. Climate Control"
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-orange-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Serial Number</label>
                  <input
                    type="text"
                    value={assetForm.serial_number}
                    onChange={(e) => setAssetForm({ ...assetForm, serial_number: e.target.value })}
                    placeholder="e.g. SN-9982"
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-orange-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Purchase Date</label>
                  <input
                    type="date"
                    value={assetForm.purchase_date}
                    onChange={(e) => setAssetForm({ ...assetForm, purchase_date: e.target.value })}
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-orange-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Warranty Expiry *</label>
                  <input
                    type="date"
                    value={assetForm.warranty_expiry}
                    onChange={(e) => setAssetForm({ ...assetForm, warranty_expiry: e.target.value })}
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-orange-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsAssetModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium border border-white/10 text-slate-300 hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingAsset}
                  className="px-5 py-2 rounded-xl text-xs font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50"
                  style={{ background: "linear-gradient(135deg, #f97316, #fb923c)" }}
                >
                  {savingAsset ? "Saving…" : "Save Asset"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Add Task Modal ── */}
      {isTaskModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div
            className="w-full max-w-lg rounded-2xl border p-6 shadow-2xl relative"
            style={{ background: "#0b1329", borderColor: "rgba(255,255,255,0.12)" }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Wrench size={18} className="text-blue-400" /> Schedule Maintenance Task
              </h3>
              <button onClick={() => setIsTaskModalOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleAddTask} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-300 mb-1 block">Task Title *</label>
                <input
                  type="text"
                  value={taskForm.title}
                  onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                  placeholder="e.g. Flush water heater tank"
                  className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-blue-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 mb-1 block">Description</label>
                <textarea
                  value={taskForm.description}
                  onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                  placeholder="Provide instructions or details…"
                  rows={2}
                  className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-blue-400 resize-none"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Due Date *</label>
                  <input
                    type="date"
                    value={taskForm.due_date}
                    onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-blue-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Related Asset</label>
                  <select
                    value={taskForm.asset_id}
                    onChange={(e) => setTaskForm({ ...taskForm, asset_id: e.target.value })}
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-blue-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  >
                    <option value="">None (General Home Task)</option>
                    {assets.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <input
                  type="checkbox"
                  id="recurring"
                  checked={taskForm.recurring}
                  onChange={(e) => setTaskForm({ ...taskForm, recurring: e.target.checked })}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-blue-500 focus:ring-0"
                />
                <label htmlFor="recurring" className="text-xs font-medium text-slate-300 cursor-pointer">
                  Recurring task (repeats automatically)
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsTaskModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium border border-white/10 text-slate-300 hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingTask}
                  className="px-5 py-2 rounded-xl text-xs font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50"
                  style={{ background: "linear-gradient(135deg, #3b82f6, #6366f1)" }}
                >
                  {savingTask ? "Scheduling…" : "Schedule Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

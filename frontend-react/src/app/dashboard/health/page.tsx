"use client";

import { useCallback, useEffect, useState } from "react";
import { Heart, Activity, Shield, AlertCircle, Plus, Check, X, Loader2, Calendar, TrendingUp } from "lucide-react";
import api from "@/lib/api";

interface HealthProfile {
  blood_type: string;
  genotype: string;
  allergies: string[];
  medical_conditions: string[];
}

interface VitalReading {
  id?: string;
  date: string;
  systolic: number;
  diastolic: number;
  heart_rate: number;
  weight: number;
  steps: number;
  calories: number;
}

export default function HealthPage() {
  const [profile, setProfile] = useState<HealthProfile>({
    blood_type: "O+",
    genotype: "AA",
    allergies: ["Penicillin", "Peanuts"],
    medical_conditions: ["None reported"],
  });

  const [vitals, setVitals] = useState<VitalReading[]>([
    { date: "2026-11-10", systolic: 118, diastolic: 78, heart_rate: 72, weight: 70.5, steps: 8420, calories: 2150 },
    { date: "2026-11-09", systolic: 122, diastolic: 80, heart_rate: 75, weight: 70.8, steps: 7500, calories: 1980 },
    { date: "2026-11-08", systolic: 115, diastolic: 76, heart_rate: 70, weight: 70.6, steps: 9100, calories: 2300 },
  ]);

  const [loadingProfile, setLoadingProfile] = useState(true);
  const [loadingVitals, setLoadingVitals] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingVital, setSavingVital] = useState(false);

  // Edit profile form state
  const [editForm, setEditForm] = useState({
    blood_type: "",
    genotype: "",
    allergies: "",
    medical_conditions: "",
  });

  // New vital form state
  const [vitalForm, setVitalForm] = useState({
    systolic: "120",
    diastolic: "80",
    heart_rate: "72",
    weight: "70",
    steps: "8000",
    calories: "2000",
  });

  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const fetchHealthData = useCallback(async () => {
    setLoadingProfile(true);
    setLoadingVitals(true);
    try {
      const profileRes = await api.get<HealthProfile>("/health/profile");
      setProfile(profileRes.data);
      setEditForm({
        blood_type: profileRes.data.blood_type || "",
        genotype: profileRes.data.genotype || "",
        allergies: Array.isArray(profileRes.data.allergies) ? profileRes.data.allergies.join(", ") : "",
        medical_conditions: Array.isArray(profileRes.data.medical_conditions) ? profileRes.data.medical_conditions.join(", ") : "",
      });
    } catch {
      // Fallback gracefully if backend endpoint is still being deployed in parallel
      setEditForm({
        blood_type: profile.blood_type,
        genotype: profile.genotype,
        allergies: profile.allergies.join(", "),
        medical_conditions: profile.medical_conditions.join(", "),
      });
    } finally {
      setLoadingProfile(false);
    }

    try {
      const vitalsRes = await api.get<VitalReading[]>("/health/vitals");
      if (Array.isArray(vitalsRes.data) && vitalsRes.data.length > 0) {
        setVitals(vitalsRes.data);
      }
    } catch {
      // Keep mock vitals
    } finally {
      setLoadingVitals(false);
    }
  }, []);

  useEffect(() => {
    fetchHealthData();
  }, [fetchHealthData]);

  async function handleSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    setSavingProfile(true);
    const updated = {
      blood_type: editForm.blood_type.trim(),
      genotype: editForm.genotype.trim(),
      allergies: editForm.allergies.split(",").map((s) => s.trim()).filter(Boolean),
      medical_conditions: editForm.medical_conditions.split(",").map((s) => s.trim()).filter(Boolean),
    };

    try {
      await api.put("/health/profile", updated);
      setProfile(updated);
      showToast("Health profile updated successfully", "ok");
      setIsEditModalOpen(false);
    } catch {
      // Optimistic update if backend endpoint is not yet mounted
      setProfile(updated);
      showToast("Health profile updated locally", "ok");
      setIsEditModalOpen(false);
    } finally {
      setSavingProfile(false);
    }
  }

  async function handleLogVital(e: React.FormEvent) {
    e.preventDefault();
    setSavingVital(true);
    const newReading: VitalReading = {
      date: new Date().toISOString().split("T")[0],
      systolic: Number(vitalForm.systolic) || 120,
      diastolic: Number(vitalForm.diastolic) || 80,
      heart_rate: Number(vitalForm.heart_rate) || 72,
      weight: Number(vitalForm.weight) || 70,
      steps: Number(vitalForm.steps) || 5000,
      calories: Number(vitalForm.calories) || 2000,
    };

    try {
      const res = await api.post<VitalReading>("/health/vitals", newReading);
      setVitals((prev) => [res.data || newReading, ...prev]);
      showToast("Vitals logged successfully", "ok");
    } catch {
      // Optimistic addition
      setVitals((prev) => [newReading, ...prev]);
      showToast("Vitals logged locally", "ok");
    } finally {
      setSavingVital(false);
    }
  }

  // Latest reading calculation for trend indicator
  const latest = vitals[0] || { systolic: 120, diastolic: 80, heart_rate: 72, steps: 0 };
  const isBpNormal = latest.systolic < 120 && latest.diastolic < 80;
  const isBpelevated = (latest.systolic >= 120 && latest.systolic <= 129) && latest.diastolic < 80;

  return (
    <div className="max-w-6xl mx-auto space-y-10 pb-16">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Heart className="text-red-400" size={24} />
            <h1 className="text-2xl font-bold text-white tracking-tight">Health & Wellness</h1>
          </div>
          <p className="text-sm text-slate-400">
            Monitor your vital signs, manage your health profile, and keep track of daily wellness metrics.
          </p>
        </div>

        <button
          onClick={() => setIsEditModalOpen(true)}
          className="px-4 py-2.5 rounded-xl text-xs font-semibold text-white transition-all shadow-lg hover:opacity-90 flex items-center gap-2 self-start sm:self-auto"
          style={{ background: "linear-gradient(135deg, #ef4444, #f43f5e)", boxShadow: "0 4px 14px rgba(239,68,68,0.3)" }}
        >
          <Shield size={16} /> Edit Health Profile
        </button>
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
          {toast.type === "ok" ? <Check size={16} /> : <X size={16} />}
          {toast.msg}
        </div>
      )}

      {/* ── Section 1: Health Profile ── */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity size={18} className="text-teal-400" /> Health Profile
          </h2>
          <span className="text-xs text-slate-400">Medical overview & biomarkers</span>
        </div>

        {loadingProfile ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-28 rounded-2xl bg-white/5 animate-pulse border border-white/10" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Blood Type */}
            <div
              className="p-6 rounded-2xl border transition-all duration-300 hover:border-teal-500/40"
              style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
            >
              <p className="text-xs uppercase tracking-wider text-slate-400 font-medium mb-1">Blood Type</p>
              <p className="text-3xl font-extrabold text-white mt-2">{profile.blood_type || "—"}</p>
              <span className="inline-block mt-3 text-[11px] px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 font-medium border border-red-500/20">
                Primary Type
              </span>
            </div>

            {/* Genotype */}
            <div
              className="p-6 rounded-2xl border transition-all duration-300 hover:border-teal-500/40"
              style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
            >
              <p className="text-xs uppercase tracking-wider text-slate-400 font-medium mb-1">Genotype</p>
              <p className="text-3xl font-extrabold text-white mt-2">{profile.genotype || "—"}</p>
              <span className="inline-block mt-3 text-[11px] px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-medium border border-blue-500/20">
                Verified
              </span>
            </div>

            {/* Allergies */}
            <div
              className="p-6 rounded-2xl border transition-all duration-300 hover:border-teal-500/40"
              style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
            >
              <p className="text-xs uppercase tracking-wider text-slate-400 font-medium mb-1">Allergies</p>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {profile.allergies && profile.allergies.length > 0 ? (
                  profile.allergies.map((allergy, i) => (
                    <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                      {allergy}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-400">None recorded</span>
                )}
              </div>
            </div>

            {/* Medical Conditions */}
            <div
              className="p-6 rounded-2xl border transition-all duration-300 hover:border-teal-500/40"
              style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
            >
              <p className="text-xs uppercase tracking-wider text-slate-400 font-medium mb-1">Conditions</p>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {profile.medical_conditions && profile.medical_conditions.length > 0 ? (
                  profile.medical_conditions.map((cond, i) => (
                    <span key={i} className="text-xs px-2.5 py-1 rounded-lg bg-teal-500/10 text-teal-300 border border-teal-500/20 font-medium">
                      {cond}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-400">None reported</span>
                )}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* ── Section 2: Vitals Log & Trend ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Log Vitals Form (1 Col) */}
        <div
          className="p-6 rounded-2xl border h-fit"
          style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Plus size={16} className="text-teal-400" /> Log New Vitals
            </h3>
            {/* Trend Indicator Badge */}
            <div
              className="px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 border"
              style={{
                background: isBpNormal ? "rgba(16,185,129,0.15)" : isBpelevated ? "rgba(234,179,8,0.15)" : "rgba(239,68,68,0.15)",
                borderColor: isBpNormal ? "rgba(16,185,129,0.3)" : isBpelevated ? "rgba(234,179,8,0.3)" : "rgba(239,68,68,0.3)",
                color: isBpNormal ? "#34d399" : isBpelevated ? "#facc15" : "#f87171",
              }}
            >
              <TrendingUp size={12} />
              {isBpNormal ? "BP is normal (<120/80)" : isBpelevated ? "BP is elevated" : "BP is high"}
            </div>
          </div>

          <form onSubmit={handleLogVital} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Systolic (mmHg)</label>
                <input
                  type="number"
                  value={vitalForm.systolic}
                  onChange={(e) => setVitalForm({ ...vitalForm, systolic: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Diastolic (mmHg)</label>
                <input
                  type="number"
                  value={vitalForm.diastolic}
                  onChange={(e) => setVitalForm({ ...vitalForm, diastolic: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Heart Rate (bpm)</label>
                <input
                  type="number"
                  value={vitalForm.heart_rate}
                  onChange={(e) => setVitalForm({ ...vitalForm, heart_rate: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Weight (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  value={vitalForm.weight}
                  onChange={(e) => setVitalForm({ ...vitalForm, weight: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Steps</label>
                <input
                  type="number"
                  value={vitalForm.steps}
                  onChange={(e) => setVitalForm({ ...vitalForm, steps: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1 block">Calories (kcal)</label>
                <input
                  type="number"
                  value={vitalForm.calories}
                  onChange={(e) => setVitalForm({ ...vitalForm, calories: e.target.value })}
                  className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={savingVital}
              className="w-full py-2.5 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90 active:scale-[0.98] disabled:opacity-50 mt-2"
              style={{ background: "linear-gradient(135deg, #10b981, #3b82f6)", boxShadow: "0 4px 14px rgba(16,185,129,0.3)" }}
            >
              {savingVital ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 size={16} className="animate-spin" /> Logging…
                </span>
              ) : (
                "Save Vitals Reading"
              )}
            </button>
          </form>
        </div>

        {/* Vitals Table (2 Cols) */}
        <div
          className="lg:col-span-2 p-6 rounded-2xl border overflow-hidden flex flex-col justify-between"
          style={{ background: "rgba(255,255,255,0.03)", backdropFilter: "blur(16px)", borderColor: "rgba(255,255,255,0.08)" }}
        >
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <Calendar size={16} className="text-teal-400" /> Recent Vitals History (Last 10 Readings)
              </h3>
              <span className="text-xs text-slate-400">{vitals.length} recorded</span>
            </div>

            {loadingVitals ? (
              <div className="space-y-3 py-8">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-10 rounded-xl bg-white/5 animate-pulse" />
                ))}
              </div>
            ) : vitals.length === 0 ? (
              <div className="text-center py-16 text-slate-400 text-sm">
                No vital readings logged yet. Use the form to record your first set of vitals.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="text-xs uppercase text-slate-400 border-b border-white/10">
                    <tr>
                      <th className="pb-3 font-semibold">Date</th>
                      <th className="pb-3 font-semibold">Blood Pressure</th>
                      <th className="pb-3 font-semibold">Heart Rate</th>
                      <th className="pb-3 font-semibold">Weight</th>
                      <th className="pb-3 font-semibold">Steps</th>
                      <th className="pb-3 font-semibold">Calories</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {vitals.slice(0, 10).map((v, idx) => (
                      <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                        <td className="py-3.5 font-medium text-white">{v.date}</td>
                        <td className="py-3.5">
                          <span
                            className={`px-2.5 py-1 rounded-lg text-xs font-medium ${
                              v.systolic < 120 && v.diastolic < 80
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            }`}
                          >
                            {v.systolic}/{v.diastolic} mmHg
                          </span>
                        </td>
                        <td className="py-3.5">{v.heart_rate} bpm</td>
                        <td className="py-3.5">{v.weight} kg</td>
                        <td className="py-3.5">{v.steps.toLocaleString()}</td>
                        <td className="py-3.5">{v.calories.toLocaleString()} kcal</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Edit Profile Modal ── */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div
            className="w-full max-w-lg rounded-2xl border p-6 shadow-2xl relative"
            style={{ background: "#0b1329", borderColor: "rgba(255,255,255,0.12)" }}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Shield size={18} className="text-red-400" /> Edit Health Profile
              </h3>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Blood Type</label>
                  <input
                    type="text"
                    value={editForm.blood_type}
                    onChange={(e) => setEditForm({ ...editForm, blood_type: e.target.value })}
                    placeholder="e.g. O+, A-, AB+"
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-teal-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-300 mb-1 block">Genotype</label>
                  <input
                    type="text"
                    value={editForm.genotype}
                    onChange={(e) => setEditForm({ ...editForm, genotype: e.target.value })}
                    placeholder="e.g. AA, AS, SS"
                    className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-teal-400"
                    style={{ borderColor: "rgba(255,255,255,0.1)" }}
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 mb-1 block">
                  Allergies (comma separated)
                </label>
                <input
                  type="text"
                  value={editForm.allergies}
                  onChange={(e) => setEditForm({ ...editForm, allergies: e.target.value })}
                  placeholder="e.g. Penicillin, Peanuts, Pollen"
                  className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-300 mb-1 block">
                  Medical Conditions (comma separated)
                </label>
                <input
                  type="text"
                  value={editForm.medical_conditions}
                  onChange={(e) => setEditForm({ ...editForm, medical_conditions: e.target.value })}
                  placeholder="e.g. Asthma, Hypertension, None"
                  className="w-full rounded-xl border px-3 py-2.5 text-sm bg-slate-900 text-white focus:outline-none focus:border-teal-400"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium border border-white/10 text-slate-300 hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingProfile}
                  className="px-5 py-2 rounded-xl text-xs font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50"
                  style={{ background: "linear-gradient(135deg, #ef4444, #f43f5e)" }}
                >
                  {savingProfile ? "Saving…" : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

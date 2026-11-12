"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  Lock,
  Upload,
  KeyRound,
  FileText,
  Download,
  X,
  Check,
  Loader2,
  AlertCircle,
} from "lucide-react";
import api from "@/lib/api";

interface VaultFile {
  id: string;
  filename: string;
  created_at: string;
}

export default function VaultPage() {
  const [files, setFiles] = useState<VaultFile[]>([]);
  const [loadingFiles, setLoadingFiles] = useState(true);

  // Upload form
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadPassword, setUploadPassword] = useState("");
  const [uploading, setUploading] = useState(false);

  // Download modal
  const [downloadTarget, setDownloadTarget] = useState<VaultFile | null>(null);
  const [downloadPassword, setDownloadPassword] = useState("");
  const [downloading, setDownloading] = useState(false);

  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);
  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const fetchFiles = useCallback(async () => {
    setLoadingFiles(true);
    try {
      const res = await api.get<VaultFile[]>("/vault/files");
      setFiles(Array.isArray(res.data) ? res.data : []);
    } catch {
      setFiles([]);
    } finally {
      setLoadingFiles(false);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      showToast("Please choose a file to upload.", "err");
      return;
    }
    if (!uploadPassword) {
      showToast("Please set a password to protect this file.", "err");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("password", uploadPassword);
      await api.post("/vault/upload", formData);
      showToast("File encrypted and stored in your vault.", "ok");
      setUploadPassword("");
      if (fileInputRef.current) fileInputRef.current.value = "";
      await fetchFiles();
    } catch {
      showToast("Upload failed. Please try again.", "err");
    } finally {
      setUploading(false);
    }
  }

  function openDownload(file: VaultFile) {
    setDownloadTarget(file);
    setDownloadPassword("");
  }

  async function handleDownloadSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!downloadTarget) return;
    setDownloading(true);
    try {
      const res = await api.post<Blob>(
        `/vault/download/${downloadTarget.id}`,
        { password: downloadPassword },
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = downloadTarget.filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showToast("File decrypted and downloaded.", "ok");
      setDownloadTarget(null);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      showToast(status === 400 ? "Incorrect password." : "Download failed.", "err");
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 min-h-screen">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Lock className="text-yellow-400" size={24} />
          <h1 className="text-2xl font-bold text-white tracking-tight">Secure Vault</h1>
        </div>
        <p className="text-sm text-slate-400">
          Store private documents, audio, and video. Files are encrypted with a password you choose.
        </p>
      </div>

      {/* Toast */}
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
          {toast.type === "ok" ? <Check size={16} /> : <AlertCircle size={16} />}
          {toast.msg}
        </div>
      )}

      {/* Upload card */}
      <section
        className="p-6 rounded-2xl border bg-white/5 backdrop-blur-md border-white/10"
      >
        <h2 className="text-base font-semibold text-white flex items-center gap-2 mb-4">
          <Upload size={16} className="text-yellow-400" /> Upload to Vault
        </h2>
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-400 mb-1.5 block">File</label>
            <input
              ref={fileInputRef}
              type="file"
              className="w-full text-sm text-slate-300 file:mr-3 file:px-3 file:py-1.5 file:rounded-lg file:border-0 file:bg-yellow-400/10 file:text-yellow-300 file:text-xs file:font-medium hover:file:bg-yellow-400/20 file:cursor-pointer"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-400 mb-1.5 block">
              Vault Password
            </label>
            <div className="relative">
              <KeyRound
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <input
                type="password"
                value={uploadPassword}
                onChange={(e) => setUploadPassword(e.target.value)}
                placeholder="Protect this file"
                className="w-full rounded-xl border pl-9 pr-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-yellow-400"
                style={{ borderColor: "rgba(255,255,255,0.1)" }}
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1.5">
              You&apos;ll need this exact password to decrypt and download the file later.
            </p>
          </div>
          <button
            type="submit"
            disabled={uploading}
            className="w-full py-2.5 rounded-xl text-white font-medium text-sm transition-all hover:opacity-90 active:scale-[0.98] disabled:opacity-50"
            style={{
              background: "linear-gradient(135deg, #f59e0b, #eab308)",
              color: "#0f172a",
            }}
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 size={16} className="animate-spin" /> Encrypting & Uploading…
              </span>
            ) : (
              "Encrypt & Store"
            )}
          </button>
        </form>
      </section>

      {/* File list */}
      <section
        className="p-6 rounded-2xl border bg-white/5 backdrop-blur-md border-white/10"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <FileText size={16} className="text-yellow-400" /> Stored Files
          </h2>
          <span className="text-xs text-slate-400">{files.length} encrypted</span>
        </div>

        {loadingFiles ? (
          <div className="space-y-3">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-12 rounded-xl bg-white/5 animate-pulse" />
            ))}
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-sm">
            No files in your vault yet. Upload your first encrypted file above.
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {files.map((f) => (
              <div key={f.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText size={18} className="text-slate-400 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-white truncate">{f.filename}</p>
                    <p className="text-[11px] text-slate-500">
                      {new Date(f.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => openDownload(f)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-yellow-400/10 text-yellow-300 border border-yellow-400/20 hover:bg-yellow-400/20 transition-colors shrink-0"
                >
                  <Download size={13} /> Download
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Download password modal */}
      {downloadTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div
            className="w-full max-w-sm rounded-2xl border p-6 shadow-2xl"
            style={{ background: "#0b1329", borderColor: "rgba(255,255,255,0.12)" }}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <KeyRound size={16} className="text-yellow-400" /> Decrypt File
              </h3>
              <button
                onClick={() => setDownloadTarget(null)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X size={18} />
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-4 break-words">
              Enter the password to download{" "}
              <span className="text-slate-200 font-medium">{downloadTarget.filename}</span>.
            </p>
            <form onSubmit={handleDownloadSubmit} className="space-y-4">
              <input
                autoFocus
                type="password"
                value={downloadPassword}
                onChange={(e) => setDownloadPassword(e.target.value)}
                placeholder="Vault password"
                className="w-full rounded-xl border px-3 py-2 text-sm bg-slate-900/50 text-white focus:outline-none focus:border-yellow-400"
                style={{ borderColor: "rgba(255,255,255,0.1)" }}
              />
              <div className="flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setDownloadTarget(null)}
                  className="px-4 py-2 rounded-xl text-xs font-medium border border-white/10 text-slate-300 hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={downloading || !downloadPassword}
                  className="px-5 py-2 rounded-xl text-xs font-semibold transition-all hover:opacity-90 disabled:opacity-50"
                  style={{
                    background: "linear-gradient(135deg, #f59e0b, #eab308)",
                    color: "#0f172a",
                  }}
                >
                  {downloading ? "Decrypting…" : "Download"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

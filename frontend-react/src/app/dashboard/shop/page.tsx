"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  Boxes,
  Check,
  Loader2,
  Package,
  Plus,
  RefreshCw,
  X,
  ShoppingCart,
  Mail,
  Building2,
} from "lucide-react";
import api from "@/lib/api";

interface Supplier {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
}

interface Product {
  id: string;
  user_id: string;
  sku: string;
  name: string;
  category: string | null;
  price: number;
  stock_quantity: number;
  reorder_level: number;
  supplier_id: string | null;
  created_at: string;
  updated_at: string | null;
}

interface ProductForm {
  name: string;
  sku: string;
  price: string;
  category: string;
  stock_quantity: string;
  reorder_level: string;
  supplier_id: string;
}

interface StockForm {
  movement_type: "in" | "out";
  quantity: string;
}

const EMPTY_PRODUCT_FORM: ProductForm = {
  name: "",
  sku: "",
  price: "",
  category: "",
  stock_quantity: "0",
  reorder_level: "5",
  supplier_id: "",
};

function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export default function ShopPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [alerts, setAlerts] = useState<Product[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [supplierForm, setSupplierForm] = useState({ name: "", email: "" });
  const [submittingSupplier, setSubmittingSupplier] = useState(false);

  const [showAddModal, setShowAddModal] = useState(false);
  const [productForm, setProductForm] = useState<ProductForm>(EMPTY_PRODUCT_FORM);
  const [submittingProduct, setSubmittingProduct] = useState(false);

  const [stockTarget, setStockTarget] = useState<Product | null>(null);
  const [stockForm, setStockForm] = useState<StockForm>({ movement_type: "in", quantity: "" });
  const [submittingStock, setSubmittingStock] = useState(false);

  // Reorder Modal State
  const [reorderLoadingId, setReorderLoadingId] = useState<string | null>(null);
  const [reorderModalData, setReorderModalData] = useState<{
    productName: string;
    supplierEmail: string;
    draft: string;
  } | null>(null);

  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);

  const isStaff = role === "staff";
  const canModify = role !== null && !isStaff;

  const showToast = useCallback((msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [productsRes, alertsRes, meRes, suppliersRes] = await Promise.all([
        api.get<Product[]>("/shop/products"),
        api.get<Product[]>("/shop/alerts/low-stock"),
        api.get<{ role: string }>("/auth/me"),
        api.get<Supplier[]>("/suppliers"),
      ]);
      setProducts(productsRes.data);
      setAlerts(alertsRes.data);
      setRole(meRes.data.role);
      setSuppliers(suppliersRes.data);
    } catch {
      setError("Failed to load inventory. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleAddSupplier(e: React.FormEvent) {
    e.preventDefault();
    if (!supplierForm.name.trim() || !supplierForm.email.trim()) return;
    setSubmittingSupplier(true);
    try {
      const res = await api.post<Supplier>("/suppliers", {
        name: supplierForm.name.trim(),
        email: supplierForm.email.trim(),
      });
      setSuppliers((prev) => [res.data, ...prev]);
      setSupplierForm({ name: "", email: "" });
      showToast("Supplier added successfully", "ok");
    } catch {
      showToast("Failed to add supplier", "err");
    } finally {
      setSubmittingSupplier(false);
    }
  }

  async function handleAddProduct(e: React.FormEvent) {
    e.preventDefault();
    if (!productForm.name.trim() || !productForm.sku.trim() || !productForm.price.trim()) return;
    setSubmittingProduct(true);
    try {
      await api.post("/shop/products", {
        name: productForm.name.trim(),
        sku: productForm.sku.trim(),
        price: Math.round(Number(productForm.price) * 100),
        category: productForm.category.trim() || null,
        stock_quantity: Number(productForm.stock_quantity) || 0,
        reorder_level: Number(productForm.reorder_level) || 0,
        supplier_id: productForm.supplier_id ? productForm.supplier_id : null,
      });
      setShowAddModal(false);
      setProductForm(EMPTY_PRODUCT_FORM);
      showToast("Product added", "ok");
      await loadData();
    } catch (err) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      showToast(detail || "Failed to add product", "err");
    } finally {
      setSubmittingProduct(false);
    }
  }

  async function handleStockMovement(e: React.FormEvent) {
    e.preventDefault();
    if (!stockTarget || !stockForm.quantity.trim()) return;
    setSubmittingStock(true);
    try {
      await api.post(`/shop/products/${stockTarget.id}/stock`, {
        movement_type: stockForm.movement_type,
        quantity: Number(stockForm.quantity),
      });
      setStockTarget(null);
      setStockForm({ movement_type: "in", quantity: "" });
      showToast("Stock updated", "ok");
      await loadData();
    } catch (err) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      showToast(detail || "Failed to update stock", "err");
    } finally {
      setSubmittingStock(false);
    }
  }

  async function handleReorder(product: Product) {
    setReorderLoadingId(product.id);
    try {
      const res = await api.post<{ draft: string; supplier_email: string; product_name: string }>(
        `/shop/reorder/${product.id}`
      );
      setReorderModalData({
        productName: res.data.product_name || product.name,
        supplierEmail: res.data.supplier_email || "No supplier email",
        draft: res.data.draft || "",
      });
    } catch (err) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      showToast(detail || "Failed to generate reorder draft", "err");
    } finally {
      setReorderLoadingId(null);
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[var(--foreground)]">📦 Shop Manager</h1>
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Track products, monitor stock levels, and restock before you run out.
          </p>
        </div>
        {canModify && (
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 active:scale-[0.97]"
            style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
          >
            <Plus size={16} />
            Add Product
          </button>
        )}
      </div>

      {/* ── Toast ── */}
      {toast && (
        <div
          className="fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-3 rounded-xl border text-sm"
          style={{
            background: toast.type === "ok" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
            borderColor: toast.type === "ok" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)",
            color: toast.type === "ok" ? "#34d399" : "#f87171",
          }}
        >
          {toast.type === "ok" ? <Check size={14} /> : <X size={14} />}
          {toast.msg}
        </div>
      )}

      {/* ── Add Supplier Form (if suppliers list is empty) ── */}
      {!loading && suppliers.length === 0 && canModify && (
        <div
          className="glass-card border p-6 mb-8 rounded-2xl"
          style={{ background: "rgba(45,212,191,0.04)", borderColor: "rgba(45,212,191,0.2)" }}
        >
          <div className="flex items-center gap-2 mb-2">
            <Building2 size={18} style={{ color: "#2dd4bf" }} />
            <h2 className="text-base font-semibold text-[var(--foreground)]">Add Your First Supplier</h2>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mb-4">
            You need at least one supplier before assigning them to products for automated reordering.
          </p>
          <form onSubmit={handleAddSupplier} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="Supplier Name (e.g. FreshProduce Co)"
              value={supplierForm.name}
              onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
              className="flex-1 rounded-xl border px-4 py-2 text-sm bg-transparent focus:outline-none"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
              required
            />
            <input
              type="email"
              placeholder="Supplier Email (e.g. orders@freshproduce.com)"
              value={supplierForm.email}
              onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
              className="flex-1 rounded-xl border px-4 py-2 text-sm bg-transparent focus:outline-none"
              style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
              required
            />
            <button
              type="submit"
              disabled={submittingSupplier}
              className="px-5 py-2 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 shrink-0 flex items-center justify-center gap-2"
              style={{ background: "#2dd4bf" }}
            >
              {submittingSupplier && <Loader2 size={14} className="animate-spin" />}
              Save Supplier
            </button>
          </form>
        </div>
      )}

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div
          className="glass-card glass-card-transition p-5 border bg-white/5 backdrop-blur-md border-white/10"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
              Needs Restocking
            </span>
            <AlertTriangle size={16} style={{ color: "#ef4444" }} />
          </div>
          {loading ? (
            <div className="h-9 w-12 rounded bg-[var(--muted)] animate-pulse" />
          ) : (
            <p className="text-4xl font-bold leading-none" style={{ color: "#ef4444" }}>
              {alerts.length}
            </p>
          )}
          <p className="text-xs text-[var(--muted-foreground)] mt-2">
            Items at or below reorder level
          </p>
        </div>

        <div
          className="glass-card glass-card-transition p-5 border bg-white/5 backdrop-blur-md border-white/10"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
              Products
            </span>
            <Package size={16} style={{ color: "#2dd4bf" }} />
          </div>
          {loading ? (
            <div className="h-9 w-12 rounded bg-[var(--muted)] animate-pulse" />
          ) : (
            <p className="text-4xl font-bold leading-none" style={{ color: "#2dd4bf" }}>
              {products.length}
            </p>
          )}
          <p className="text-xs text-[var(--muted-foreground)] mt-2">Total tracked SKUs</p>
        </div>

        <div
          className="glass-card glass-card-transition p-5 border bg-white/5 backdrop-blur-md border-white/10"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--muted-foreground)]">
              Total Units
            </span>
            <Boxes size={16} style={{ color: "#3b82f6" }} />
          </div>
          {loading ? (
            <div className="h-9 w-12 rounded bg-[var(--muted)] animate-pulse" />
          ) : (
            <p className="text-4xl font-bold leading-none" style={{ color: "#3b82f6" }}>
              {products.reduce((sum, p) => sum + p.stock_quantity, 0)}
            </p>
          )}
          <p className="text-xs text-[var(--muted-foreground)] mt-2">Across all products</p>
        </div>
      </div>

      {/* ── Product Table ── */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-[var(--foreground)]">Inventory</h2>
          {!loading && !error && (
            <button
              onClick={loadData}
              className="flex items-center gap-1.5 text-xs text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
            >
              <RefreshCw size={12} />
              Refresh
            </button>
          )}
        </div>

        {loading ? (
          <div
            className="glass-card border overflow-hidden"
            style={{ borderColor: "rgba(255,255,255,0.06)" }}
          >
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="flex items-center gap-4 px-5 py-4 animate-pulse border-b last:border-b-0"
                style={{ borderColor: "rgba(255,255,255,0.04)" }}
              >
                <div className="h-4 flex-1 rounded bg-[var(--muted)]" />
                <div className="h-4 w-20 rounded bg-[var(--muted)]" />
                <div className="h-4 w-16 rounded bg-[var(--muted)]" />
                <div className="h-4 w-16 rounded bg-[var(--muted)]" />
                <div className="h-8 w-24 rounded-lg bg-[var(--muted)]" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div
            className="glass-card border flex flex-col items-center justify-center py-16 text-center gap-3"
            style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.05)" }}
          >
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={loadData}
              className="px-4 py-2 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
              style={{ borderColor: "rgba(239,68,68,0.3)", color: "#f87171" }}
            >
              Retry
            </button>
          </div>
        ) : products.length === 0 ? (
          <div
            className="glass-card border border-dashed flex flex-col items-center justify-center py-20 text-center"
            style={{ borderColor: "rgba(255,255,255,0.08)" }}
          >
            <Package size={32} className="text-[var(--muted-foreground)] mb-3 opacity-50" />
            <p className="text-sm text-[var(--muted-foreground)]">
              No products yet.{canModify ? " Add your first product to get started." : ""}
            </p>
          </div>
        ) : (
          <div
            className="glass-card border overflow-x-auto bg-white/5 backdrop-blur-md border-white/10"
          >
            <table className="w-full text-sm">
              <thead>
                <tr
                  className="text-left text-xs uppercase tracking-wider text-[var(--muted-foreground)] bg-white/5"
                >
                  <th className="px-5 py-3 font-medium">Product Name</th>
                  <th className="px-5 py-3 font-medium">SKU</th>
                  <th className="px-5 py-3 font-medium text-right">Price</th>
                  <th className="px-5 py-3 font-medium text-right">Stock</th>
                  <th className="px-5 py-3 font-medium text-right">Reorder Level</th>
                  {canModify && <th className="px-5 py-3 font-medium text-right">Actions</th>}
                </tr>
              </thead>
              <tbody>
                {products.map((product) => {
                  const low = product.stock_quantity <= product.reorder_level;
                  const isReordering = reorderLoadingId === product.id;
                  return (
                    <tr
                      key={product.id}
                      className="border-t"
                      style={{
                        borderColor: "rgba(255,255,255,0.04)",
                        background: low ? "rgba(239,68,68,0.06)" : "transparent",
                      }}
                    >
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-[var(--foreground)] font-medium">
                            {product.name}
                          </span>
                          {product.category && (
                            <span
                              className="text-[10px] px-2 py-0.5 rounded-full"
                              style={{
                                background: "rgba(255,255,255,0.06)",
                                color: "var(--muted-foreground)",
                              }}
                            >
                              {product.category}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3 font-mono text-xs text-[var(--muted-foreground)]">
                        {product.sku}
                      </td>
                      <td className="px-5 py-3 text-right text-[var(--foreground)]">
                        {formatPrice(product.price)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <span
                          className="font-medium"
                          style={{ color: low ? "#f87171" : "var(--foreground)" }}
                        >
                          {product.stock_quantity}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-right text-[var(--muted-foreground)]">
                        {product.reorder_level}
                      </td>
                      {canModify && (
                        <td className="px-5 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {low && (
                              <button
                                onClick={() => handleReorder(product)}
                                disabled={isReordering}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors hover:opacity-90"
                                style={{
                                  borderColor: "rgba(245,158,11,0.4)",
                                  background: "rgba(245,158,11,0.15)",
                                  color: "#f59e0b",
                                }}
                                title="AI Reorder Draft"
                              >
                                {isReordering ? (
                                  <Loader2 size={12} className="animate-spin" />
                                ) : (
                                  <ShoppingCart size={12} />
                                )}
                                Reorder
                              </button>
                            )}
                            <button
                              onClick={() => {
                                setStockTarget(product);
                                setStockForm({ movement_type: "in", quantity: "" });
                              }}
                              className="px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors hover:bg-[var(--accent)]"
                              style={{ borderColor: "rgba(45,212,191,0.3)", color: "#2dd4bf" }}
                            >
                              Update Stock
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Add Product Modal ── */}
      {showAddModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
          onClick={() => setShowAddModal(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl border overflow-hidden"
            style={{
              background: "#0d0d14",
              borderColor: "rgba(255,255,255,0.1)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.5)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <h2 className="text-base font-semibold text-[var(--foreground)]">➕ Add Product</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleAddProduct} className="px-6 py-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Name *
                </label>
                <input
                  type="text"
                  value={productForm.name}
                  onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                  placeholder="e.g. Wireless Mouse"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    SKU *
                  </label>
                  <input
                    type="text"
                    value={productForm.sku}
                    onChange={(e) => setProductForm({ ...productForm, sku: e.target.value })}
                    placeholder="WM-001"
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    Price (USD) *
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={productForm.price}
                    onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                    placeholder="19.99"
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Category
                </label>
                <input
                  type="text"
                  value={productForm.category}
                  onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                  placeholder="e.g. Electronics"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Supplier
                </label>
                <select
                  value={productForm.supplier_id}
                  onChange={(e) => setProductForm({ ...productForm, supplier_id: e.target.value })}
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                >
                  <option value="" style={{ background: "#1a1a2e", color: "#fff" }}>
                    -- Select Supplier --
                  </option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id} style={{ background: "#1a1a2e", color: "#fff" }}>
                      {s.name} ({s.email || "no email"})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    Initial Stock
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={productForm.stock_quantity}
                    onChange={(e) => setProductForm({ ...productForm, stock_quantity: e.target.value })}
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                    Reorder Level
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={productForm.reorder_level}
                    onChange={(e) => setProductForm({ ...productForm, reorder_level: e.target.value })}
                    className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                    style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium border text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
                  style={{ borderColor: "rgba(255,255,255,0.08)" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingProduct}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 flex items-center gap-2"
                  style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
                >
                  {submittingProduct && <Loader2 size={14} className="animate-spin" />}
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Update Stock Modal ── */}
      {stockTarget && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
          onClick={() => setStockTarget(null)}
        >
          <div
            className="w-full max-w-sm rounded-2xl border overflow-hidden"
            style={{
              background: "#0d0d14",
              borderColor: "rgba(255,255,255,0.1)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.5)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <h2 className="text-base font-semibold text-[var(--foreground)]">
                📦 Update Stock: {stockTarget.name}
              </h2>
              <button
                onClick={() => setStockTarget(null)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleStockMovement} className="px-6 py-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Movement Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setStockForm({ ...stockForm, movement_type: "in" })}
                    className="py-2 rounded-xl text-xs font-medium border transition-colors"
                    style={{
                      borderColor:
                        stockForm.movement_type === "in"
                          ? "rgba(16,185,129,0.5)"
                          : "rgba(255,255,255,0.08)",
                      background:
                        stockForm.movement_type === "in"
                          ? "rgba(16,185,129,0.15)"
                          : "transparent",
                      color: stockForm.movement_type === "in" ? "#34d399" : "var(--muted-foreground)",
                    }}
                  >
                    Stock In (+)
                  </button>
                  <button
                    type="button"
                    onClick={() => setStockForm({ ...stockForm, movement_type: "out" })}
                    className="py-2 rounded-xl text-xs font-medium border transition-colors"
                    style={{
                      borderColor:
                        stockForm.movement_type === "out"
                          ? "rgba(239,68,68,0.5)"
                          : "rgba(255,255,255,0.08)",
                      background:
                        stockForm.movement_type === "out"
                          ? "rgba(239,68,68,0.15)"
                          : "transparent",
                      color: stockForm.movement_type === "out" ? "#f87171" : "var(--muted-foreground)",
                    }}
                  >
                    Stock Out (-)
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Quantity *
                </label>
                <input
                  type="number"
                  min="1"
                  value={stockForm.quantity}
                  onChange={(e) => setStockForm({ ...stockForm, quantity: e.target.value })}
                  placeholder="10"
                  className="w-full rounded-xl border px-4 py-2.5 text-sm bg-transparent focus:outline-none"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                <button
                  type="button"
                  onClick={() => setStockTarget(null)}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium border text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
                  style={{ borderColor: "rgba(255,255,255,0.08)" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingStock}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 flex items-center gap-2"
                  style={{ background: "linear-gradient(135deg, #2dd4bf, #3b82f6)" }}
                >
                  {submittingStock && <Loader2 size={14} className="animate-spin" />}
                  Confirm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Reorder Modal ── */}
      {reorderModalData && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
          onClick={() => setReorderModalData(null)}
        >
          <div
            className="w-full max-w-lg rounded-2xl border overflow-hidden"
            style={{
              background: "#0d0d14",
              borderColor: "rgba(255,255,255,0.1)",
              boxShadow: "0 24px 48px rgba(0,0,0,0.5)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              className="flex items-center justify-between px-6 py-4 border-b"
              style={{ borderColor: "rgba(255,255,255,0.06)" }}
            >
              <div className="flex items-center gap-2">
                <Mail size={18} style={{ color: "#f59e0b" }} />
                <h2 className="text-base font-semibold text-[var(--foreground)]">
                  AI Reorder Draft: {reorderModalData.productName}
                </h2>
              </div>
              <button
                onClick={() => setReorderModalData(null)}
                className="rounded-lg p-1.5 hover:bg-[var(--accent)] transition-colors text-[var(--muted-foreground)]"
              >
                <X size={16} />
              </button>
            </div>

            <div className="px-6 py-5 space-y-4">
              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1 block">
                  Supplier Email
                </label>
                <p className="text-sm font-mono text-[var(--foreground)] bg-black/30 px-3 py-2 rounded-xl border" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                  {reorderModalData.supplierEmail}
                </p>
              </div>

              <div>
                <label className="text-xs font-medium text-[var(--muted-foreground)] mb-1.5 block">
                  Email Draft (Editable)
                </label>
                <textarea
                  value={reorderModalData.draft}
                  onChange={(e) =>
                    setReorderModalData({ ...reorderModalData, draft: e.target.value })
                  }
                  rows={8}
                  className="w-full rounded-xl border p-3 text-sm bg-transparent focus:outline-none font-mono"
                  style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--foreground)" }}
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(reorderModalData.draft);
                    showToast("Copied draft to clipboard", "ok");
                  }}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium border text-[var(--foreground)] hover:bg-[var(--accent)] transition-colors flex items-center gap-2"
                  style={{ borderColor: "rgba(255,255,255,0.1)" }}
                >
                  Copy to Clipboard
                </button>
                <button
                  type="button"
                  onClick={() => {
                    showToast(`Simulated sending reorder email to ${reorderModalData.supplierEmail}!`, "ok");
                    setReorderModalData(null);
                  }}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-white transition-all hover:opacity-90 flex items-center gap-2"
                  style={{ background: "linear-gradient(135deg, #f59e0b, #ef4444)" }}
                >
                  Simulate Send
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

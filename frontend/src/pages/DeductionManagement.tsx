import { Pause, Pencil, Play, Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { createDeduction, deleteDeduction, listDeductions, updateDeduction } from "../api/deductions";
import { listEmployees } from "../api/employees";
import type { DeductionType, Employee, EmployeeDeduction } from "../api/types";
import { DEDUCTION_LABELS, DEDUCTION_TYPES, formatPeso } from "../lib/format";
import { todayIso } from "../lib/dates";


interface FormState {
  employee_id: number | "";
  deduction_type: DeductionType;
  total_amount: string;
  amount_per_cutoff: string;
  remaining_balance: string;
  start_date: string;
  is_active: boolean;
}

const emptyForm: FormState = {
  employee_id: "",
  deduction_type: "SSS_LOAN",
  total_amount: "",
  amount_per_cutoff: "",
  remaining_balance: "",
  start_date: todayIso(),
  is_active: true,
};

const errorMessage = (err: unknown, fallback: string): string =>
  err && typeof err === "object" && "response" in err
    ? // @ts-expect-error axios error shape
      err.response?.data?.detail ?? fallback
    : fallback;

const isPaidOff = (d: EmployeeDeduction) => d.remaining_balance !== null && parseFloat(d.remaining_balance) <= 0;

export default function DeductionManagement() {
  const [deductions, setDeductions] = useState<EmployeeDeduction[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [saving, setSaving] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      const [rows, emps] = await Promise.all([listDeductions(), listEmployees()]);
      setDeductions(rows);
      setEmployees(emps);
      setError(null);
    } catch {
      setError("Failed to load data. Is the backend running on http://127.0.0.1:8000?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const employeeName = (id: number) => {
    const e = employees.find((emp) => emp.id === id);
    return e ? `${e.first_name} ${e.last_name}` : `#${id}`;
  };

  const openCreate = () => {
    setEditingId(null);
    setForm({ ...emptyForm, start_date: todayIso() });
    setShowForm(true);
  };

  const openEdit = (d: EmployeeDeduction) => {
    setEditingId(d.id);
    setForm({
      employee_id: d.employee_id,
      deduction_type: d.deduction_type,
      total_amount: d.total_amount ?? "",
      amount_per_cutoff: d.amount_per_cutoff,
      remaining_balance: d.remaining_balance ?? "",
      start_date: d.start_date,
      is_active: d.is_active,
    });
    setShowForm(true);
  };

  const isMp2 = form.deduction_type === "MP2";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.employee_id === "") return;
    setSaving(true);
    try {
      if (editingId !== null) {
        await updateDeduction(editingId, {
          amount_per_cutoff: form.amount_per_cutoff,
          start_date: form.start_date,
          is_active: form.is_active,
          ...(isMp2 ? {} : { remaining_balance: form.remaining_balance }),
        });
      } else {
        await createDeduction({
          employee_id: form.employee_id,
          deduction_type: form.deduction_type,
          total_amount: isMp2 ? null : form.total_amount,
          amount_per_cutoff: form.amount_per_cutoff,
          start_date: form.start_date,
          is_active: true,
        });
      }
      setShowForm(false);
      await refresh();
    } catch (err: unknown) {
      alert(errorMessage(err, "Failed to save deduction"));
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (d: EmployeeDeduction) => {
    try {
      await updateDeduction(d.id, { is_active: !d.is_active });
      await refresh();
    } catch (err: unknown) {
      alert(errorMessage(err, "Failed to update deduction"));
    }
  };

  const handleDelete = async (d: EmployeeDeduction) => {
    if (!confirm(`Delete this ${DEDUCTION_LABELS[d.deduction_type]} for ${employeeName(d.employee_id)}?`)) return;
    try {
      await deleteDeduction(d.id);
      await refresh();
    } catch (err: unknown) {
      alert(errorMessage(err, "Failed to delete deduction"));
    }
  };

  const statusOf = (d: EmployeeDeduction) => {
    if (d.is_active) return { label: "Active", className: "bg-green-100 text-green-800" };
    if (isPaidOff(d)) return { label: "Paid off", className: "bg-slate-200 text-slate-600" };
    return { label: "Paused", className: "bg-slate-200 text-slate-600" };
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Loans &amp; Deductions</h1>
          <p className="text-sm text-slate-500">
            SSS, Pag-IBIG and calamity loans, MP2 savings, and petty cash advances. Each payroll run deducts the
            per-cutoff amount and reduces the balance until it is paid off.
          </p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 rounded-lg bg-green-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-800"
        >
          <Plus size={16} /> Add Deduction
        </button>
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Employee</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Total</th>
              <th className="px-3 py-2">Per Cutoff</th>
              <th className="px-3 py-2">Remaining</th>
              <th className="px-3 py-2">Starts</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-3 py-4 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : deductions.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-3 py-4 text-center text-slate-400">
                  No loans or deductions yet.
                </td>
              </tr>
            ) : (
              deductions.map((d) => {
                const status = statusOf(d);
                return (
                  <tr key={d.id} className="hover:bg-slate-50">
                    <td className="px-3 py-2 font-medium text-slate-900">{employeeName(d.employee_id)}</td>
                    <td className="px-3 py-2">
                      <span className="rounded-full bg-slate-100 px-1.5 py-0.5 text-xs font-medium text-slate-700">
                        {DEDUCTION_LABELS[d.deduction_type]}
                      </span>
                    </td>
                    <td className="px-3 py-2">{d.total_amount !== null ? formatPeso(d.total_amount) : "—"}</td>
                    <td className="px-3 py-2">{formatPeso(d.amount_per_cutoff)}</td>
                    <td className="px-3 py-2">
                      {d.remaining_balance !== null ? formatPeso(d.remaining_balance) : "Ongoing"}
                    </td>
                    <td className="px-3 py-2 text-slate-600">{d.start_date}</td>
                    <td className="px-3 py-2">
                      <span className={`rounded-full px-1.5 py-0.5 text-xs font-medium ${status.className}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEdit(d)}
                          title="Edit"
                          className="rounded p-1.5 text-slate-500 hover:bg-slate-100"
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          onClick={() => handleToggleActive(d)}
                          disabled={isPaidOff(d)}
                          title={isPaidOff(d) ? "Paid off. Edit the balance to reopen it" : d.is_active ? "Pause" : "Resume"}
                          className={
                            d.is_active
                              ? "rounded p-1.5 text-amber-600 hover:bg-amber-50"
                              : "rounded p-1.5 text-green-600 hover:bg-green-50 disabled:cursor-not-allowed disabled:text-slate-300 disabled:hover:bg-transparent"
                          }
                        >
                          {d.is_active ? <Pause size={16} /> : <Play size={16} />}
                        </button>
                        <button
                          onClick={() => handleDelete(d)}
                          title="Delete"
                          className="rounded p-1.5 text-red-500 hover:bg-red-50"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 p-3">
          <div className="w-full max-w-md rounded-xl bg-white p-4 shadow-lg">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">
                {editingId !== null ? "Edit Deduction" : "Add Deduction"}
              </h2>
              <button onClick={() => setShowForm(false)} className="rounded p-1 text-slate-400 hover:bg-slate-100">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">Employee</label>
                  <select
                    required
                    disabled={editingId !== null}
                    value={form.employee_id}
                    onChange={(e) => setForm({ ...form, employee_id: e.target.value === "" ? "" : Number(e.target.value) })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm disabled:bg-slate-100"
                  >
                    <option value="">Select employee</option>
                    {employees.map((emp) => (
                      <option key={emp.id} value={emp.id}>
                        {emp.first_name} {emp.last_name}
                        {emp.is_active ? "" : " (inactive)"}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">Type</label>
                  <select
                    disabled={editingId !== null}
                    value={form.deduction_type}
                    onChange={(e) => setForm({ ...form, deduction_type: e.target.value as DeductionType })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm disabled:bg-slate-100"
                  >
                    {DEDUCTION_TYPES.map((t) => (
                      <option key={t} value={t}>
                        {DEDUCTION_LABELS[t]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {isMp2 ? (
                <p className="rounded-lg bg-slate-50 px-2.5 py-1.5 text-xs text-slate-500">
                  MP2 is a voluntary savings contribution: it has no total or balance and is deducted every cutoff
                  until you pause it.
                </p>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="mb-1 block text-xs font-medium text-slate-600">
                      {editingId !== null ? "Original Total (PHP)" : "Total Amount (PHP)"}
                    </label>
                    <input
                      required
                      disabled={editingId !== null}
                      type="number"
                      min="0.01"
                      step="0.01"
                      value={form.total_amount}
                      onChange={(e) => setForm({ ...form, total_amount: e.target.value })}
                      className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm disabled:bg-slate-100"
                    />
                  </div>
                  {editingId !== null && (
                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-600">Remaining Balance (PHP)</label>
                      <input
                        required
                        type="number"
                        min="0"
                        step="0.01"
                        value={form.remaining_balance}
                        onChange={(e) => setForm({ ...form, remaining_balance: e.target.value })}
                        className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                      />
                    </div>
                  )}
                </div>
              )}

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">Amount per Cutoff (PHP)</label>
                  <input
                    required
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={form.amount_per_cutoff}
                    onChange={(e) => setForm({ ...form, amount_per_cutoff: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">Starts On</label>
                  <input
                    required
                    type="date"
                    value={form.start_date}
                    onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                  />
                </div>
              </div>

              {editingId !== null && (
                <label className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  />
                  Active (deducted on each payroll run)
                </label>
              )}

              <div className="mt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-lg bg-green-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

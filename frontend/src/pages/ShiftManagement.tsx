import { Pencil, Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";
import { createShift, deleteShift, listShifts, updateShift } from "../api/shifts";
import type { Shift } from "../api/types";

type ShiftInput = Omit<Shift, "id">;

const emptyForm: ShiftInput = {
  name: "",
  start_time: "08:00:00",
  end_time: "17:00:00",
  grace_period_minutes: 10,
};

export default function ShiftManagement() {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<ShiftInput>(emptyForm);
  const [saving, setSaving] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      setShifts(await listShifts());
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

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setShowForm(true);
  };

  const openEdit = (shift: Shift) => {
    setEditingId(shift.id);
    setForm({
      name: shift.name,
      start_time: shift.start_time,
      end_time: shift.end_time,
      grace_period_minutes: shift.grace_period_minutes,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingId !== null) {
        await updateShift(editingId, form);
      } else {
        await createShift(form);
      }
      setShowForm(false);
      await refresh();
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to save shift"
          : "Failed to save shift";
      alert(message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this shift? Employees using it as their default will be unassigned.")) return;
    try {
      await deleteShift(id);
      await refresh();
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to delete shift"
          : "Failed to delete shift";
      alert(message);
    }
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Shifts</h1>
          <p className="text-sm text-slate-500">
            Define work shifts and assign them to employees to enable lateness, undertime, and night shift
            differential tracking.
          </p>
        </div>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 rounded-lg bg-green-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-800"
        >
          <Plus size={16} /> Add Shift
        </button>
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Start Time</th>
              <th className="px-3 py-2">End Time</th>
              <th className="px-3 py-2">Grace Period</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : shifts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-4 text-center text-slate-400">
                  No shifts yet. Add one, then assign it to an employee as their Default Shift.
                </td>
              </tr>
            ) : (
              shifts.map((shift) => (
                <tr key={shift.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2 font-medium text-slate-900">{shift.name}</td>
                  <td className="px-3 py-2">{shift.start_time.slice(0, 5)}</td>
                  <td className="px-3 py-2">{shift.end_time.slice(0, 5)}</td>
                  <td className="px-3 py-2">{shift.grace_period_minutes} min</td>
                  <td className="px-3 py-2">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => openEdit(shift)}
                        className="rounded p-1.5 text-slate-500 hover:bg-slate-100"
                      >
                        <Pencil size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(shift.id)}
                        title="Delete"
                        className="rounded p-1.5 text-red-500 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 p-3">
          <div className="w-full max-w-sm rounded-xl bg-white p-4 shadow-lg">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">{editingId !== null ? "Edit Shift" : "Add Shift"}</h2>
              <button onClick={() => setShowForm(false)} className="rounded p-1 text-slate-400 hover:bg-slate-100">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Shift Name</label>
                <input
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Day Shift, Night Shift"
                  className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">Start Time</label>
                  <input
                    required
                    type="time"
                    value={form.start_time.slice(0, 5)}
                    onChange={(e) => setForm({ ...form, start_time: `${e.target.value}:00` })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-slate-600">End Time</label>
                  <input
                    required
                    type="time"
                    value={form.end_time.slice(0, 5)}
                    onChange={(e) => setForm({ ...form, end_time: `${e.target.value}:00` })}
                    className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Grace Period (minutes)</label>
                <input
                  required
                  type="number"
                  min="0"
                  step="1"
                  value={form.grace_period_minutes}
                  onChange={(e) => setForm({ ...form, grace_period_minutes: Number(e.target.value) })}
                  className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                />
                <p className="mt-1 text-xs text-slate-400">
                  Minutes after start time before an employee is marked late.
                </p>
              </div>
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

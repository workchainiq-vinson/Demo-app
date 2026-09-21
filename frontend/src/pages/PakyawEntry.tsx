import { Plus, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { createGroupPakyawLog, createIndividualPakyawLog, listPakyawCatalog, listPakyawLogs } from "../api/pakyaw";
import { listEmployees } from "../api/employees";
import type { Employee, PakyawCatalogItem, PakyawLog } from "../api/types";
import { formatPeso } from "../lib/format";

const todayIso = () => new Date().toISOString().slice(0, 10);

export default function PakyawEntry() {
  const [mode, setMode] = useState<"individual" | "group">("individual");
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [catalog, setCatalog] = useState<PakyawCatalogItem[]>([]);
  const [logs, setLogs] = useState<PakyawLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [taskId, setTaskId] = useState<number | "">("");
  const [date, setDate] = useState(todayIso());

  // individual mode
  const [employeeId, setEmployeeId] = useState<number | "">("");
  const [units, setUnits] = useState("");

  // group mode
  const [groupEmployeeIds, setGroupEmployeeIds] = useState<number[]>([]);
  const [totalUnits, setTotalUnits] = useState("");

  const refresh = async () => {
    setLoading(true);
    const [emps, cat, logRows] = await Promise.all([listEmployees(), listPakyawCatalog(), listPakyawLogs()]);
    setEmployees(emps);
    setCatalog(cat);
    setLogs(logRows);
    setLoading(false);
  };

  useEffect(() => {
    refresh();
  }, []);

  const employeeName = (id: number) => {
    const e = employees.find((emp) => emp.id === id);
    return e ? `${e.first_name} ${e.last_name}` : `#${id}`;
  };

  const taskName = (id: number) => catalog.find((t) => t.id === id)?.task_name ?? `#${id}`;

  const toggleGroupEmployee = (id: number) => {
    setGroupEmployeeIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskId) return;
    setSaving(true);
    try {
      if (mode === "individual") {
        if (!employeeId || !units) return;
        await createIndividualPakyawLog({
          employee_id: employeeId,
          pakyaw_catalog_id: taskId,
          date,
          units_completed: units,
        });
        setUnits("");
      } else {
        if (groupEmployeeIds.length === 0 || !totalUnits) return;
        await createGroupPakyawLog({
          employee_ids: groupEmployeeIds,
          pakyaw_catalog_id: taskId,
          date,
          total_units: totalUnits,
        });
        setGroupEmployeeIds([]);
        setTotalUnits("");
      }
      await refresh();
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to log pakyaw output"
          : "Failed to log pakyaw output";
      alert(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="mb-4">
        <h1 className="text-xl font-semibold text-slate-900">Pakyaw Data Entry</h1>
        <p className="text-sm text-slate-500">
          Log piece-rate output individually, or split a team's total output equally with Group Entry.
        </p>
      </div>

      <div className="mb-3 inline-flex rounded-lg border border-slate-300 bg-white p-1">
        <button
          onClick={() => setMode("individual")}
          className={`rounded-md px-3 py-1.5 text-sm font-medium ${
            mode === "individual" ? "bg-green-700 text-white" : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          Individual
        </button>
        <button
          onClick={() => setMode("group")}
          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium ${
            mode === "group" ? "bg-green-700 text-white" : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Users size={14} /> Group Entry
        </button>
      </div>

      <form onSubmit={handleSubmit} className="mb-4 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Task</label>
            <select
              required
              value={taskId}
              onChange={(e) => setTaskId(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
            >
              <option value="">Select task</option>
              {catalog.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.task_name} ({formatPeso(t.rate_per_unit)}/{t.unit_of_measure})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Date</label>
            <input
              type="date"
              required
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
            />
          </div>

          {mode === "individual" ? (
            <>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Employee</label>
                <select
                  required
                  value={employeeId}
                  onChange={(e) => setEmployeeId(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                >
                  <option value="">Select employee</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Units Completed</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  value={units}
                  onChange={(e) => setUnits(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                />
              </div>
            </>
          ) : (
            <>
              <div className="col-span-2">
                <label className="mb-1 block text-xs font-medium text-slate-600">
                  Team Members ({groupEmployeeIds.length} selected)
                </label>
                <div className="flex max-h-24 flex-wrap gap-1.5 overflow-y-auto rounded-lg border border-slate-300 p-1.5">
                  {employees.map((emp) => (
                    <button
                      type="button"
                      key={emp.id}
                      onClick={() => toggleGroupEmployee(emp.id)}
                      className={`rounded-full px-1.5.5 py-1 text-xs font-medium ${
                        groupEmployeeIds.includes(emp.id)
                          ? "bg-green-700 text-white"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      {emp.first_name} {emp.last_name}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">Total Units</label>
                <input
                  required
                  type="number"
                  step="0.01"
                  value={totalUnits}
                  onChange={(e) => setTotalUnits(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm"
                />
                {groupEmployeeIds.length > 0 && totalUnits && (
                  <p className="mt-1 text-xs text-slate-500">
                    {formatPeso((parseFloat(totalUnits) / groupEmployeeIds.length).toFixed(2))} worth of units each
                    (approx.)
                  </p>
                )}
              </div>
            </>
          )}
        </div>
        <div className="mt-2 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 rounded-lg bg-green-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
          >
            <Plus size={16} /> {saving ? "Saving..." : "Log Output"}
          </button>
        </div>
      </form>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-3 py-2">Employee</th>
              <th className="px-3 py-2">Task</th>
              <th className="px-3 py-2">Date</th>
              <th className="px-3 py-2">Units</th>
              <th className="px-3 py-2">Group Batch</th>
              <th className="px-3 py-2">Computed Pay</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-3 py-4 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-3 py-4 text-center text-slate-400">
                  No pakyaw logs yet.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50">
                  <td className="px-3 py-2 font-medium text-slate-900">{employeeName(log.employee_id)}</td>
                  <td className="px-3 py-2">{taskName(log.pakyaw_catalog_id)}</td>
                  <td className="px-3 py-2">{log.date}</td>
                  <td className="px-3 py-2">{log.units_completed}</td>
                  <td className="px-3 py-2 font-mono text-xs text-slate-400">
                    {log.group_batch_id ? log.group_batch_id.slice(0, 8) : "—"}
                  </td>
                  <td className="px-3 py-2 font-medium">{formatPeso(log.computed_pay)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

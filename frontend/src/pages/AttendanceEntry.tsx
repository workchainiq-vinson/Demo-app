import { Check, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { approveOvertime, createAttendance, listAttendance } from "../api/attendance";
import { listEmployees } from "../api/employees";
import { listHolidays } from "../api/holidays";
import type { Attendance, Employee, Holiday } from "../api/types";

const todayIso = () => new Date().toISOString().slice(0, 10);

export default function AttendanceEntry() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [records, setRecords] = useState<Attendance[]>([]);
  const [loading, setLoading] = useState(true);

  const [employeeId, setEmployeeId] = useState<number | "">("");
  const [date, setDate] = useState(todayIso());
  const [timeIn, setTimeIn] = useState("22:00");
  const [timeOut, setTimeOut] = useState("06:00");
  const [nextDayOut, setNextDayOut] = useState(true);
  const [isRestDayWorked, setIsRestDayWorked] = useState(false);
  const [holidayId, setHolidayId] = useState<number | "">("");
  const [saving, setSaving] = useState(false);

  const refresh = async () => {
    setLoading(true);
    const [emps, hols, atts] = await Promise.all([listEmployees(), listHolidays(), listAttendance()]);
    setEmployees(emps);
    setHolidays(hols);
    setRecords(atts);
    setLoading(false);
  };

  useEffect(() => {
    refresh();
  }, []);

  const employeeName = (id: number) => {
    const e = employees.find((emp) => emp.id === id);
    return e ? `${e.first_name} ${e.last_name}` : `#${id}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employeeId) return;
    setSaving(true);
    try {
      const outDate = nextDayOut ? addDays(date, 1) : date;
      await createAttendance({
        employee_id: employeeId,
        date,
        time_in: `${date}T${timeIn}:00`,
        time_out: `${outDate}T${timeOut}:00`,
        is_rest_day_worked: isRestDayWorked,
        holiday_id: holidayId === "" ? null : holidayId,
      });
      setIsRestDayWorked(false);
      setHolidayId("");
      await refresh();
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to log attendance"
          : "Failed to log attendance";
      alert(message);
    } finally {
      setSaving(false);
    }
  };

  const handleApproveOt = async (att: Attendance) => {
    const input = prompt("Approved OT minutes:", String(att.actual_ot_minutes));
    if (input === null) return;
    const minutes = Number(input);
    if (Number.isNaN(minutes) || minutes < 0) return;
    try {
      await approveOvertime(att.id, minutes);
      await refresh();
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to approve overtime"
          : "Failed to approve overtime";
      alert(message);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Attendance</h1>
        <p className="text-sm text-slate-500">
          Log daily punches. Lateness, undertime, and NSD minutes are computed automatically from the
          employee's assigned shift.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mb-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-6">
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-medium text-slate-600">Employee</label>
            <select
              required
              value={employeeId}
              onChange={(e) => setEmployeeId(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
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
            <label className="mb-1 block text-xs font-medium text-slate-600">Date</label>
            <input
              type="date"
              required
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Time In</label>
            <input
              type="time"
              required
              value={timeIn}
              onChange={(e) => setTimeIn(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Time Out</label>
            <input
              type="time"
              required
              value={timeOut}
              onChange={(e) => setTimeOut(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-600">Holiday</label>
            <select
              value={holidayId}
              onChange={(e) => setHolidayId(e.target.value === "" ? "" : Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">None</option>
              {holidays.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.date} - {h.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-6">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={nextDayOut} onChange={(e) => setNextDayOut(e.target.checked)} />
            Time Out is next calendar day (overnight shift)
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={isRestDayWorked}
              onChange={(e) => setIsRestDayWorked(e.target.checked)}
            />
            Worked on rest day
          </label>
          <button
            type="submit"
            disabled={saving}
            className="ml-auto flex items-center gap-2 rounded-lg bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
          >
            <Plus size={16} /> {saving ? "Saving..." : "Log Attendance"}
          </button>
        </div>
      </form>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Employee</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Time In</th>
              <th className="px-4 py-3">Time Out</th>
              <th className="px-4 py-3">Late</th>
              <th className="px-4 py-3">Undertime</th>
              <th className="px-4 py-3">NSD</th>
              <th className="px-4 py-3">Actual OT</th>
              <th className="px-4 py-3">Approved OT</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={10} className="px-4 py-6 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : records.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-6 text-center text-slate-400">
                  No attendance records yet.
                </td>
              </tr>
            ) : (
              records.map((att) => (
                <tr key={att.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{employeeName(att.employee_id)}</td>
                  <td className="px-4 py-3">{att.date}</td>
                  <td className="px-4 py-3">{att.time_in?.slice(11, 16) ?? "—"}</td>
                  <td className="px-4 py-3">{att.time_out?.slice(11, 16) ?? "—"}</td>
                  <td className="px-4 py-3">{att.late_minutes}m</td>
                  <td className="px-4 py-3">{att.undertime_minutes}m</td>
                  <td className="px-4 py-3">{att.nsd_minutes}m</td>
                  <td className="px-4 py-3">{att.actual_ot_minutes}m</td>
                  <td className="px-4 py-3 font-medium text-green-700">{att.approved_ot_minutes}m</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleApproveOt(att)}
                      className="inline-flex items-center gap-1 rounded-lg border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                    >
                      <Check size={14} /> Approve OT
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function addDays(iso: string, days: number): string {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

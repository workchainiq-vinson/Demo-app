import { CalendarDays, ClipboardList, Download, FileText, Sprout, Users, Wallet } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDashboardSummary } from "../api/dashboard";
import { listEmployees } from "../api/employees";
import { listPayrollRuns } from "../api/payroll";
import {
  getAttendanceCsvUrl,
  getDtrSummaryPdfUrl,
  getEmployeesCsvUrl,
  getPakyawCsvUrl,
  getPayrollSummaryCsvUrl,
  getPayrollSummaryPdfUrl,
} from "../api/reports";
import type { DashboardSummary, Employee, PayrollRun } from "../api/types";
import { formatPeso } from "../lib/format";

const todayIso = () => new Date().toISOString().slice(0, 10);
const firstOfMonthIso = () => {
  const d = new Date();
  d.setDate(1);
  return d.toISOString().slice(0, 10);
};

function KpiCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: typeof Users;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="mb-1.5 flex items-center gap-2 text-slate-500">
        <Icon size={16} />
        <p className="text-xs font-semibold uppercase tracking-wider">{label}</p>
      </div>
      <p className="text-2xl font-semibold text-slate-900">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | "">("");
  const [attendanceFrom, setAttendanceFrom] = useState(firstOfMonthIso());
  const [attendanceTo, setAttendanceTo] = useState(todayIso());
  const [pakyawFrom, setPakyawFrom] = useState(firstOfMonthIso());
  const [pakyawTo, setPakyawTo] = useState(todayIso());
  const [dtrFrom, setDtrFrom] = useState(firstOfMonthIso());
  const [dtrTo, setDtrTo] = useState(todayIso());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [s, emps, r] = await Promise.all([getDashboardSummary(), listEmployees(), listPayrollRuns()]);
        setSummary(s);
        setEmployees(emps);
        setRuns(r);
        if (r.length > 0) setSelectedRunId(r[0].id);
        setError(null);
      } catch {
        setError("Failed to load dashboard. Is the backend running on http://127.0.0.1:8000?");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading dashboard...</p>;
  }

  if (error || !summary) {
    return <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error ?? "No data available."}</div>;
  }

  const chartData = summary.payroll_trend.map((point) => ({
    name: point.cutoff_end,
    Gross: point.gross_pay,
    Net: point.net_pay,
  }));

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">Overview of headcount, attendance, production, and payroll.</p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          icon={Users}
          label="Active Employees"
          value={String(summary.employee_counts.active)}
          sub={`${summary.employee_counts.by_type.REGULAR} Regular · ${summary.employee_counts.by_type.PAKYAW} Pakyaw · ${summary.employee_counts.by_type.MIXED} Mixed`}
        />
        <KpiCard
          icon={Wallet}
          label="Latest Payroll Run"
          value={summary.latest_payroll_run ? formatPeso(summary.latest_payroll_run.net_pay) : "—"}
          sub={
            summary.latest_payroll_run
              ? `Net pay · ${summary.latest_payroll_run.cutoff_start} to ${summary.latest_payroll_run.cutoff_end}`
              : "No payroll runs yet"
          }
        />
        <KpiCard
          icon={CalendarDays}
          label="Attendance This Month"
          value={`${summary.attendance_summary_this_month.days_logged} days logged`}
          sub={`${summary.attendance_summary_this_month.late_minutes}m late · ${summary.attendance_summary_this_month.approved_ot_minutes}m OT · ${summary.attendance_summary_this_month.nsd_minutes}m NSD`}
        />
        <KpiCard
          icon={Sprout}
          label="Pakyaw Output This Month"
          value={formatPeso(summary.pakyaw_summary_this_month.total_pay)}
          sub={`${summary.pakyaw_summary_this_month.total_units} units completed`}
        />
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm lg:col-span-2">
          <p className="mb-2 text-sm font-semibold text-slate-700">Payroll Trend (Gross vs Net)</p>
          {chartData.length === 0 ? (
            <p className="py-6 text-center text-sm text-slate-400">No payroll runs yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(value) => formatPeso(typeof value === "number" ? value : 0)} />
                <Legend />
                <Bar dataKey="Gross" fill="#45640a" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Net" fill="#00a83c" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
          <p className="mb-2 text-sm font-semibold text-slate-700">Upcoming Holidays</p>
          {summary.upcoming_holidays.length === 0 ? (
            <p className="text-sm text-slate-400">No upcoming holidays.</p>
          ) : (
            <ul className="space-y-2">
              {summary.upcoming_holidays.map((h) => (
                <li key={h.id} className="flex items-center justify-between text-sm">
                  <span className="text-slate-700">{h.name}</span>
                  <span className="text-xs text-slate-400">{h.date}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <div className="mb-2 flex items-center gap-2">
          <FileText size={16} className="text-slate-500" />
          <p className="text-sm font-semibold text-slate-700">Downloadable Reports</p>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          <div className="rounded-lg border border-slate-100 p-2.5">
            <p className="mb-1.5 text-xs font-medium text-slate-600">Payroll Summary</p>
            <select
              value={selectedRunId}
              onChange={(e) => setSelectedRunId(e.target.value === "" ? "" : Number(e.target.value))}
              className="mb-1.5 w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
            >
              <option value="">Select run</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  #{r.id} · {r.cutoff_start} to {r.cutoff_end}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <a
                href={selectedRunId ? getPayrollSummaryPdfUrl(selectedRunId) : undefined}
                target="_blank"
                rel="noreferrer"
                aria-disabled={!selectedRunId}
                className={`flex flex-1 items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium ${
                  selectedRunId ? "text-slate-600 hover:bg-slate-100" : "pointer-events-none text-slate-300"
                }`}
              >
                <Download size={12} /> PDF
              </a>
              <a
                href={selectedRunId ? getPayrollSummaryCsvUrl(selectedRunId) : undefined}
                target="_blank"
                rel="noreferrer"
                aria-disabled={!selectedRunId}
                className={`flex flex-1 items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium ${
                  selectedRunId ? "text-slate-600 hover:bg-slate-100" : "pointer-events-none text-slate-300"
                }`}
              >
                <Download size={12} /> CSV
              </a>
            </div>
          </div>

          <div className="rounded-lg border border-slate-100 p-2.5">
            <p className="mb-1.5 text-xs font-medium text-slate-600">Attendance Report</p>
            <div className="mb-1.5 flex gap-1">
              <input
                type="date"
                value={attendanceFrom}
                onChange={(e) => setAttendanceFrom(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
              <input
                type="date"
                value={attendanceTo}
                onChange={(e) => setAttendanceTo(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
            </div>
            <a
              href={getAttendanceCsvUrl({ date_from: attendanceFrom, date_to: attendanceTo })}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100"
            >
              <Download size={12} /> CSV
            </a>
          </div>

          <div className="rounded-lg border border-slate-100 p-2.5">
            <p className="mb-1.5 text-xs font-medium text-slate-600">Pakyaw Production Report</p>
            <div className="mb-1.5 flex gap-1">
              <input
                type="date"
                value={pakyawFrom}
                onChange={(e) => setPakyawFrom(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
              <input
                type="date"
                value={pakyawTo}
                onChange={(e) => setPakyawTo(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
            </div>
            <a
              href={getPakyawCsvUrl({ date_from: pakyawFrom, date_to: pakyawTo })}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100"
            >
              <Download size={12} /> CSV
            </a>
          </div>

          <div className="rounded-lg border border-slate-100 p-2.5">
            <p className="mb-1.5 text-xs font-medium text-slate-600">DTR Summary Report</p>
            <div className="mb-1.5 flex gap-1">
              <input
                type="date"
                value={dtrFrom}
                onChange={(e) => setDtrFrom(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
              <input
                type="date"
                value={dtrTo}
                onChange={(e) => setDtrTo(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs"
              />
            </div>
            <a
              href={getDtrSummaryPdfUrl({ date_from: dtrFrom, date_to: dtrTo })}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100"
            >
              <ClipboardList size={12} /> PDF
            </a>
          </div>

          <div className="rounded-lg border border-slate-100 p-2.5">
            <p className="mb-1.5 text-xs font-medium text-slate-600">Employee Directory</p>
            <p className="mb-1.5 text-xs text-slate-400">{employees.length} employees on record</p>
            <a
              href={getEmployeesCsvUrl()}
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 rounded-lg border border-slate-300 px-1.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100"
            >
              <Download size={12} /> CSV
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

import { Download, PlayCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { generatePayroll, getPayslipPdfUrl, listPayrollRuns } from "../api/payroll";
import type { PayrollRun } from "../api/types";
import { formatPeso } from "../lib/format";

const todayIso = () => new Date().toISOString().slice(0, 10);
const firstOfMonthIso = () => {
  const d = new Date();
  d.setDate(1);
  return d.toISOString().slice(0, 10);
};

export default function PayrollGeneration() {
  const [cutoffStart, setCutoffStart] = useState(firstOfMonthIso());
  const [cutoffEnd, setCutoffEnd] = useState(todayIso());
  const [applyStatutory, setApplyStatutory] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [runs, setRuns] = useState<PayrollRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    const data = await listPayrollRuns();
    setRuns(data);
    if (data.length > 0 && selectedRunId === null) {
      setSelectedRunId(data[0].id);
    }
    setLoading(false);
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const run = await generatePayroll({
        cutoff_start: cutoffStart,
        cutoff_end: cutoffEnd,
        apply_statutory_deductions: applyStatutory,
      });
      setRuns((prev) => [run, ...prev]);
      setSelectedRunId(run.id);
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? // @ts-expect-error axios error shape
            err.response?.data?.detail ?? "Failed to generate payroll"
          : "Failed to generate payroll";
      alert(message);
    } finally {
      setGenerating(false);
    }
  };

  const selectedRun = runs.find((r) => r.id === selectedRunId) ?? null;

  const totals = selectedRun?.payslips.reduce(
    (acc, p) => ({
      gross: acc.gross + parseFloat(p.gross_pay),
      deductions: acc.deductions + parseFloat(p.total_deductions),
      net: acc.net + parseFloat(p.net_pay),
    }),
    { gross: 0, deductions: 0, net: 0 },
  );

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Payroll Generation</h1>
        <p className="text-sm text-slate-500">Generate a payroll run for a cutoff period across all active employees.</p>
      </div>

      <form onSubmit={handleGenerate} className="mb-6 flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-600">Cutoff Start</label>
          <input
            type="date"
            required
            value={cutoffStart}
            onChange={(e) => setCutoffStart(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-600">Cutoff End</label>
          <input
            type="date"
            required
            value={cutoffEnd}
            onChange={(e) => setCutoffEnd(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <label className="mb-2 flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" checked={applyStatutory} onChange={(e) => setApplyStatutory(e.target.checked)} />
          Apply Statutory Deductions
        </label>
        <button
          type="submit"
          disabled={generating}
          className="ml-auto flex items-center gap-2 rounded-lg bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
        >
          <PlayCircle size={16} /> {generating ? "Generating..." : "Generate Payroll"}
        </button>
      </form>

      {runs.length > 0 && (
        <div className="mb-4 flex items-center gap-2">
          <label className="text-xs font-medium text-slate-600">View Run:</label>
          <select
            value={selectedRunId ?? ""}
            onChange={(e) => setSelectedRunId(Number(e.target.value))}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
          >
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                #{r.id} &middot; {r.cutoff_start} to {r.cutoff_end}
                {r.apply_statutory_deductions ? "" : " (no deductions)"}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Employee</th>
              <th className="px-4 py-3">Gross Pay</th>
              <th className="px-4 py-3">SSS</th>
              <th className="px-4 py-3">PhilHealth</th>
              <th className="px-4 py-3">Pag-IBIG</th>
              <th className="px-4 py-3">Total Deductions</th>
              <th className="px-4 py-3">Net Pay</th>
              <th className="px-4 py-3 text-right">Payslip</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-4 py-6 text-center text-slate-400">
                  Loading...
                </td>
              </tr>
            ) : !selectedRun || selectedRun.payslips.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-6 text-center text-slate-400">
                  No payroll runs yet. Generate one above.
                </td>
              </tr>
            ) : (
              selectedRun.payslips.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-900">{p.employee_name}</td>
                  <td className="px-4 py-3">{formatPeso(p.gross_pay)}</td>
                  <td className="px-4 py-3">{formatPeso(p.sss_deduction)}</td>
                  <td className="px-4 py-3">{formatPeso(p.philhealth_deduction)}</td>
                  <td className="px-4 py-3">{formatPeso(p.pagibig_deduction)}</td>
                  <td className="px-4 py-3">{formatPeso(p.total_deductions)}</td>
                  <td className="px-4 py-3 font-semibold text-green-700">{formatPeso(p.net_pay)}</td>
                  <td className="px-4 py-3 text-right">
                    <a
                      href={getPayslipPdfUrl(p.id)}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 rounded-lg border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                    >
                      <Download size={14} /> Download PDF
                    </a>
                  </td>
                </tr>
              ))
            )}
          </tbody>
          {selectedRun && selectedRun.payslips.length > 0 && totals && (
            <tfoot className="bg-slate-50 font-semibold">
              <tr>
                <td className="px-4 py-3">Totals</td>
                <td className="px-4 py-3">{formatPeso(totals.gross)}</td>
                <td className="px-4 py-3" colSpan={3}></td>
                <td className="px-4 py-3">{formatPeso(totals.deductions)}</td>
                <td className="px-4 py-3 text-green-700">{formatPeso(totals.net)}</td>
                <td className="px-4 py-3"></td>
              </tr>
            </tfoot>
          )}
        </table>
      </div>
    </div>
  );
}

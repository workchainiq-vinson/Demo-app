import { API_BASE_URL } from "./client";

export const getPayrollSummaryCsvUrl = (runId: number): string =>
  `${API_BASE_URL}/reports/payroll-summary/${runId}/csv`;

export const getPayrollSummaryPdfUrl = (runId: number): string =>
  `${API_BASE_URL}/reports/payroll-summary/${runId}/pdf`;

export const getAttendanceCsvUrl = (params: { date_from?: string; date_to?: string }): string => {
  const query = new URLSearchParams();
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  const qs = query.toString();
  return `${API_BASE_URL}/reports/attendance/csv${qs ? `?${qs}` : ""}`;
};

export const getPakyawCsvUrl = (params: { date_from?: string; date_to?: string }): string => {
  const query = new URLSearchParams();
  if (params.date_from) query.set("date_from", params.date_from);
  if (params.date_to) query.set("date_to", params.date_to);
  const qs = query.toString();
  return `${API_BASE_URL}/reports/pakyaw/csv${qs ? `?${qs}` : ""}`;
};

export const getEmployeesCsvUrl = (): string => `${API_BASE_URL}/reports/employees/csv`;

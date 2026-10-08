import { API_BASE_URL } from "./client";
import type { EmploymentStatus } from "./types";

const withStatus = (url: string, employmentStatus?: EmploymentStatus | ""): string =>
  employmentStatus ? `${url}${url.includes("?") ? "&" : "?"}employment_status=${employmentStatus}` : url;

export const getPayrollSummaryCsvUrl = (runId: number, employmentStatus?: EmploymentStatus | ""): string =>
  withStatus(`${API_BASE_URL}/reports/payroll-summary/${runId}/csv`, employmentStatus);

export const getPayrollSummaryPdfUrl = (runId: number, employmentStatus?: EmploymentStatus | ""): string =>
  withStatus(`${API_BASE_URL}/reports/payroll-summary/${runId}/pdf`, employmentStatus);

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

export const getDtrSummaryPdfUrl = (params: {
  date_from: string;
  date_to: string;
  department?: string;
  employment_status?: EmploymentStatus | "";
}): string => {
  const query = new URLSearchParams({ date_from: params.date_from, date_to: params.date_to });
  if (params.department) query.set("department", params.department);
  if (params.employment_status) query.set("employment_status", params.employment_status);
  return `${API_BASE_URL}/reports/dtr-summary/pdf?${query.toString()}`;
};

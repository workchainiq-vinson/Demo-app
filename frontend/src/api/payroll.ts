import { API_BASE_URL, api } from "./client";
import type { PayrollRun } from "./types";

export const generatePayroll = async (payload: {
  cutoff_start: string;
  cutoff_end: string;
  apply_statutory_deductions: boolean;
  employee_ids?: number[] | null;
}): Promise<PayrollRun> => {
  const { data } = await api.post<PayrollRun>("/payroll/generate", payload);
  return data;
};

export const listPayrollRuns = async (): Promise<PayrollRun[]> => {
  const { data } = await api.get<PayrollRun[]>("/payroll/runs");
  return data;
};

export const getPayslipPdfUrl = (payslipId: number): string => {
  return `${API_BASE_URL}/payroll/payslips/${payslipId}/pdf`;
};

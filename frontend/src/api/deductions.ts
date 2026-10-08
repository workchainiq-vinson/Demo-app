import { api } from "./client";
import type { EmployeeDeduction, EmployeeDeductionInput } from "./types";

export const listDeductions = async (): Promise<EmployeeDeduction[]> => {
  const { data } = await api.get<EmployeeDeduction[]>("/deductions");
  return data;
};

export const createDeduction = async (payload: EmployeeDeductionInput): Promise<EmployeeDeduction> => {
  const { data } = await api.post<EmployeeDeduction>("/deductions", payload);
  return data;
};

export const updateDeduction = async (
  id: number,
  payload: Partial<{
    total_amount: string | null;
    amount_per_cutoff: string;
    remaining_balance: string | null;
    start_date: string;
    is_active: boolean;
  }>,
): Promise<EmployeeDeduction> => {
  const { data } = await api.put<EmployeeDeduction>(`/deductions/${id}`, payload);
  return data;
};

export const deleteDeduction = async (id: number): Promise<void> => {
  await api.delete(`/deductions/${id}`);
};

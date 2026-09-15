import { api } from "./client";
import type { Employee, EmployeeInput } from "./types";

export const listEmployees = async (): Promise<Employee[]> => {
  const { data } = await api.get<Employee[]>("/employees");
  return data;
};

export const createEmployee = async (payload: EmployeeInput): Promise<Employee> => {
  const { data } = await api.post<Employee>("/employees", payload);
  return data;
};

export const updateEmployee = async (id: number, payload: Partial<EmployeeInput>): Promise<Employee> => {
  const { data } = await api.put<Employee>(`/employees/${id}`, payload);
  return data;
};

export const deleteEmployee = async (id: number): Promise<void> => {
  await api.delete(`/employees/${id}`);
};

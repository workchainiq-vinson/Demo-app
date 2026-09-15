import { api } from "./client";
import type { Attendance, AttendanceInput } from "./types";

export const listAttendance = async (params?: {
  employee_id?: number;
  date_from?: string;
  date_to?: string;
}): Promise<Attendance[]> => {
  const { data } = await api.get<Attendance[]>("/attendance", { params });
  return data;
};

export const createAttendance = async (payload: AttendanceInput): Promise<Attendance> => {
  const { data } = await api.post<Attendance>("/attendance", payload);
  return data;
};

export const approveOvertime = async (id: number, approved_ot_minutes: number): Promise<Attendance> => {
  const { data } = await api.put<Attendance>(`/attendance/${id}/approve-ot`, { approved_ot_minutes });
  return data;
};

export const deleteAttendance = async (id: number): Promise<void> => {
  await api.delete(`/attendance/${id}`);
};

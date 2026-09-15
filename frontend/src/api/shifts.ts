import { api } from "./client";
import type { Shift } from "./types";

export const listShifts = async (): Promise<Shift[]> => {
  const { data } = await api.get<Shift[]>("/shifts");
  return data;
};

export const createShift = async (payload: Omit<Shift, "id">): Promise<Shift> => {
  const { data } = await api.post<Shift>("/shifts", payload);
  return data;
};

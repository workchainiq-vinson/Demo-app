import { api } from "./client";
import type { Holiday } from "./types";

export const listHolidays = async (): Promise<Holiday[]> => {
  const { data } = await api.get<Holiday[]>("/holidays");
  return data;
};

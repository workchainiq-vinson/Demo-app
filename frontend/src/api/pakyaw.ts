import { api } from "./client";
import type { PakyawCatalogItem, PakyawLog } from "./types";

export const listPakyawCatalog = async (): Promise<PakyawCatalogItem[]> => {
  const { data } = await api.get<PakyawCatalogItem[]>("/pakyaw/catalog");
  return data;
};

export const listPakyawLogs = async (params?: {
  employee_id?: number;
  date_from?: string;
  date_to?: string;
}): Promise<PakyawLog[]> => {
  const { data } = await api.get<PakyawLog[]>("/pakyaw/logs", { params });
  return data;
};

export const createIndividualPakyawLog = async (payload: {
  employee_id: number;
  pakyaw_catalog_id: number;
  date: string;
  units_completed: string;
}): Promise<PakyawLog> => {
  const { data } = await api.post<PakyawLog>("/pakyaw/logs", payload);
  return data;
};

export const createGroupPakyawLog = async (payload: {
  employee_ids: number[];
  pakyaw_catalog_id: number;
  date: string;
  total_units: string;
}): Promise<PakyawLog[]> => {
  const { data } = await api.post<PakyawLog[]>("/pakyaw/logs/group", payload);
  return data;
};

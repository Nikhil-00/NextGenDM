import api from "./api";
import type { Automation, AutomationCreate, AutomationUpdate } from "@/types";

export const automationService = {
  async list(): Promise<Automation[]> {
    const { data } = await api.get("/api/v1/automations/");
    return data;
  },

  async create(payload: AutomationCreate): Promise<Automation> {
    const { data } = await api.post("/api/v1/automations/", payload);
    return data;
  },

  async get(id: string): Promise<Automation> {
    const { data } = await api.get(`/api/v1/automations/${id}`);
    return data;
  },

  async update(id: string, payload: AutomationUpdate): Promise<Automation> {
    const { data } = await api.put(`/api/v1/automations/${id}`, payload);
    return data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/api/v1/automations/${id}`);
  },

  async toggle(id: string): Promise<Automation> {
    const { data } = await api.patch(`/api/v1/automations/${id}/toggle`);
    return data;
  },
};

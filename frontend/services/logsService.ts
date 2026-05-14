import api from "./api";
import type { PaginatedLogs, DashboardStats } from "@/types";

export const logsService = {
  async getLogs(page = 1, perPage = 20): Promise<PaginatedLogs> {
    const { data } = await api.get(`/api/v1/logs/?page=${page}&per_page=${perPage}`);
    return data;
  },
};

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await api.get("/api/v1/dashboard/stats");
    return data;
  },
};

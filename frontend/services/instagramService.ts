import api from "./api";
import type { InstagramAccount, InstagramMedia } from "@/types";

export const instagramService = {
  async getConnectUrl(): Promise<string> {
    const { data } = await api.get("/api/v1/instagram/connect");
    return data.oauth_url;
  },

  async listAccounts(): Promise<InstagramAccount[]> {
    const { data } = await api.get("/api/v1/instagram/accounts");
    return data;
  },

  async disconnect(accountId: string): Promise<void> {
    await api.delete(`/api/v1/instagram/accounts/${accountId}`);
  },

  async connectManual(accessToken: string): Promise<InstagramAccount> {
    const { data } = await api.post("/api/v1/instagram/connect/manual", {
      access_token: accessToken,
    });
    return data;
  },

  async getAccountMedia(accountId: string): Promise<InstagramMedia[]> {
    const { data } = await api.get(`/api/v1/instagram/accounts/${accountId}/media`);
    return data;
  },
};

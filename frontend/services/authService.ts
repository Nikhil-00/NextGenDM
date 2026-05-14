import api from "./api";
import type { TokenResponse, User } from "@/types";

export const authService = {
  async signup(email: string, password: string, full_name?: string): Promise<TokenResponse> {
    const { data } = await api.post("/api/v1/auth/signup", { email, password, full_name });
    return data;
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const { data } = await api.post("/api/v1/auth/login", { email, password });
    return data;
  },

  async logout(): Promise<void> {
    await api.post("/api/v1/auth/logout");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  async getMe(): Promise<User> {
    const { data } = await api.get("/api/v1/auth/me");
    return data;
  },

  saveTokens(tokens: TokenResponse) {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
  },

  clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  isLoggedIn(): boolean {
    if (typeof window === "undefined") return false;
    return !!localStorage.getItem("access_token");
  },
};

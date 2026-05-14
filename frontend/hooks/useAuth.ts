"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { authService } from "@/services/authService";

export function useAuth() {
  const { user, isLoading, setUser, setLoading, logout } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!authService.isLoggedIn()) {
      setLoading(false);
      return;
    }
    authService
      .getMe()
      .then(setUser)
      .catch(() => {
        logout();
      })
      .finally(() => setLoading(false));
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch {}
    logout();
    router.push("/login");
  };

  return { user, isLoading, logout: handleLogout };
}

export function useRequireAuth() {
  const { user, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user && !authService.isLoggedIn()) {
      router.push("/login");
    }
  }, [user, isLoading]);

  return { user, isLoading };
}

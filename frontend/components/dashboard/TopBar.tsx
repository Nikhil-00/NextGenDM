"use client";

import { Bell, User } from "lucide-react";
import { useAuthStore } from "@/store/authStore";

interface TopBarProps {
  title: string;
}

export function TopBar({ title }: TopBarProps) {
  const { user } = useAuthStore();

  return (
    <header className="flex items-center justify-between h-16 px-6 border-b border-border bg-background shrink-0">
      <h1 className="text-xl font-semibold">{title}</h1>
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted">
          <User className="w-4 h-4 text-muted-foreground" />
        </div>
        <span className="text-sm text-muted-foreground hidden sm:block">
          {user?.full_name || user?.email || "User"}
        </span>
      </div>
    </header>
  );
}

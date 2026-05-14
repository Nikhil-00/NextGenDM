"use client";

import { useQuery } from "@tanstack/react-query";
import { Zap, Instagram, MessageSquare, Activity } from "lucide-react";
import { TopBar } from "@/components/dashboard/TopBar";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { dashboardService } from "@/services/logsService";
import { logsService } from "@/services/logsService";
import { LogsTable } from "@/components/logs/LogsTable";

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: dashboardService.getStats,
  });

  const { data: recentLogs, isLoading: logsLoading } = useQuery({
    queryKey: ["logs", 1],
    queryFn: () => logsService.getLogs(1, 5),
  });

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Dashboard" />
      <div className="flex-1 p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Automations"
            value={stats?.total_automations ?? 0}
            icon={Zap}
            isLoading={statsLoading}
          />
          <StatsCard
            title="Active Automations"
            value={stats?.active_automations ?? 0}
            icon={Activity}
            isLoading={statsLoading}
          />
          <StatsCard
            title="Connected Accounts"
            value={stats?.connected_accounts ?? 0}
            icon={Instagram}
            isLoading={statsLoading}
          />
          <StatsCard
            title="Messages Sent"
            value={stats?.messages_sent ?? 0}
            icon={MessageSquare}
            description="Total DMs sent"
            isLoading={statsLoading}
          />
        </div>

        <div>
          <h2 className="text-base font-semibold mb-3">Recent Activity</h2>
          <LogsTable logs={recentLogs?.items ?? []} isLoading={logsLoading} />
        </div>
      </div>
    </div>
  );
}

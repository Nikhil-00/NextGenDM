"use client";

import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { AutomationLog, LogStatus } from "@/types";
import { formatDate } from "@/lib/utils";

const statusConfig: Record<LogStatus, { label: string; variant: "success" | "destructive" | "secondary" | "warning" }> = {
  success: { label: "Sent", variant: "success" },
  failed: { label: "Failed", variant: "destructive" },
  pending: { label: "Pending", variant: "secondary" },
  follow_required: { label: "Follow Required", variant: "warning" },
};

interface LogsTableProps {
  logs: AutomationLog[];
  isLoading?: boolean;
}

export function LogsTable({ logs, isLoading }: LogsTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p className="text-sm">No activity yet. Automations will log events here.</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/50">
            <th className="text-left px-4 py-3 font-medium text-muted-foreground">Time</th>
            <th className="text-left px-4 py-3 font-medium text-muted-foreground">Trigger</th>
            <th className="text-left px-4 py-3 font-medium text-muted-foreground">Keyword</th>
            <th className="text-left px-4 py-3 font-medium text-muted-foreground">Sender</th>
            <th className="text-left px-4 py-3 font-medium text-muted-foreground">Status</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => {
            const status = statusConfig[log.status] || { label: log.status, variant: "secondary" as const };
            return (
              <tr
                key={log.id}
                className={`border-b border-border last:border-0 hover:bg-muted/30 transition-colors ${i % 2 === 0 ? "" : "bg-muted/10"}`}
              >
                <td className="px-4 py-3 text-muted-foreground text-xs whitespace-nowrap">
                  {formatDate(log.created_at)}
                </td>
                <td className="px-4 py-3 text-xs capitalize">
                  {log.trigger_type?.replace("_", " ") || "—"}
                </td>
                <td className="px-4 py-3">
                  {log.trigger_keyword ? (
                    <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                      {log.trigger_keyword}
                    </span>
                  ) : "—"}
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground">
                  {log.sender_instagram_id || "—"}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={status.variant as any} className="text-xs">
                    {status.label}
                  </Badge>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TopBar } from "@/components/dashboard/TopBar";
import { LogsTable } from "@/components/logs/LogsTable";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { logsService } from "@/services/logsService";

export default function LogsPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["logs", page],
    queryFn: () => logsService.getLogs(page, 20),
  });

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Activity Logs" />
      <div className="flex-1 p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-muted-foreground">
            {data ? `${data.total} total events` : "Loading…"}
          </p>
        </div>

        <LogsTable logs={data?.items ?? []} isLoading={isLoading} />

        {data && data.pages > 1 && (
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-muted-foreground">
              Page {data.page} of {data.pages}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

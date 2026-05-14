"use client";

import { useQuery } from "@tanstack/react-query";
import { TopBar } from "@/components/dashboard/TopBar";
import { AutomationForm } from "@/components/automations/AutomationForm";
import { instagramService } from "@/services/instagramService";
import { Skeleton } from "@/components/ui/skeleton";

export default function NewAutomationPage() {
  const { data: accounts, isLoading } = useQuery({
    queryKey: ["instagram-accounts"],
    queryFn: instagramService.listAccounts,
  });

  return (
    <div className="flex flex-col h-full">
      <TopBar title="New Automation" />
      <div className="flex-1 p-6">
        {isLoading ? (
          <div className="space-y-4 max-w-2xl">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        ) : (
          <AutomationForm accounts={accounts ?? []} mode="create" />
        )}
      </div>
    </div>
  );
}

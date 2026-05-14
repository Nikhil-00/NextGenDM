"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { TopBar } from "@/components/dashboard/TopBar";
import { AutomationForm } from "@/components/automations/AutomationForm";
import { automationService } from "@/services/automationService";
import { instagramService } from "@/services/instagramService";
import { Skeleton } from "@/components/ui/skeleton";

export default function EditAutomationPage() {
  const { id } = useParams<{ id: string }>();

  const { data: automation, isLoading: autoLoading } = useQuery({
    queryKey: ["automation", id],
    queryFn: () => automationService.get(id),
    enabled: !!id,
  });

  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ["instagram-accounts"],
    queryFn: instagramService.listAccounts,
  });

  const isLoading = autoLoading || accountsLoading;

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Edit Automation" />
      <div className="flex-1 p-6">
        {isLoading ? (
          <div className="space-y-4 max-w-2xl">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        ) : automation ? (
          <AutomationForm accounts={accounts ?? []} initialData={automation} mode="edit" />
        ) : (
          <p className="text-muted-foreground">Automation not found.</p>
        )}
      </div>
    </div>
  );
}

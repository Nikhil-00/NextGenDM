"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Zap } from "lucide-react";
import { toast } from "sonner";
import { TopBar } from "@/components/dashboard/TopBar";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AutomationCard } from "@/components/automations/AutomationCard";
import { automationService } from "@/services/automationService";

export default function AutomationsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: automations, isLoading } = useQuery({
    queryKey: ["automations"],
    queryFn: automationService.list,
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) => automationService.toggle(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["automations"] }),
    onError: () => toast.error("Failed to toggle automation."),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => automationService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["automations"] });
      toast.success("Automation deleted.");
    },
    onError: () => toast.error("Failed to delete automation."),
  });

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Automations" />
      <div className="flex-1 p-6">
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">
            {automations?.length ?? 0} automation{automations?.length !== 1 ? "s" : ""}
          </p>
          <Link href="/automations/new">
            <Button className="gap-2">
              <Plus className="w-4 h-4" /> New Automation
            </Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-48" />)}
          </div>
        ) : automations?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
              <Zap className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="font-semibold text-lg mb-2">No automations yet</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-sm">
              Create your first automation to start sending DMs automatically when someone comments a keyword.
            </p>
            <Link href="/automations/new">
              <Button className="gap-2"><Plus className="w-4 h-4" /> Create Automation</Button>
            </Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {automations?.map((automation) => (
              <AutomationCard
                key={automation.id}
                automation={automation}
                onToggle={(id) => toggleMutation.mutate(id)}
                onEdit={(id) => router.push(`/automations/${id}`)}
                onDelete={(id) => deleteMutation.mutate(id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

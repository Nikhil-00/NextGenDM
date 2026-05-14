"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Instagram, Plus, AlertCircle, Key } from "lucide-react";
import { TopBar } from "@/components/dashboard/TopBar";
import { Button } from "@/components/ui/button";
import { AccountCard } from "@/components/instagram/AccountCard";
import { Skeleton } from "@/components/ui/skeleton";
import { instagramService } from "@/services/instagramService";

function InstagramPageInner() {
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const [showTokenInput, setShowTokenInput] = useState(false);
  const [tokenValue, setTokenValue] = useState("");

  const { data: accounts, isLoading } = useQuery({
    queryKey: ["instagram-accounts"],
    queryFn: instagramService.listAccounts,
  });

  const disconnectMutation = useMutation({
    mutationFn: (id: string) => instagramService.disconnect(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["instagram-accounts"] });
      toast.success("Account disconnected.");
    },
    onError: () => toast.error("Failed to disconnect account."),
  });

  const manualConnectMutation = useMutation({
    mutationFn: (token: string) => instagramService.connectManual(token),
    onSuccess: (account) => {
      queryClient.invalidateQueries({ queryKey: ["instagram-accounts"] });
      toast.success(`@${account.username} connected successfully!`);
      setShowTokenInput(false);
      setTokenValue("");
    },
    onError: () => toast.error("Invalid token. Make sure it's a valid Instagram access token."),
  });

  useEffect(() => {
    if (searchParams.get("connected") === "true") {
      const username = searchParams.get("username");
      toast.success(`@${username} connected successfully!`);
      queryClient.invalidateQueries({ queryKey: ["instagram-accounts"] });
    }
  }, [searchParams]);

  const handleConnect = async () => {
    try {
      const url = await instagramService.getConnectUrl();
      window.location.href = url;
    } catch {
      toast.error("Failed to initiate Instagram connection.");
    }
  };

  return (
    <div className="flex flex-col h-full">
      <TopBar title="Instagram Accounts" />
      <div className="flex-1 p-6">
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">
            {accounts?.length ?? 0} account{accounts?.length !== 1 ? "s" : ""} connected
          </p>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2" onClick={() => setShowTokenInput(!showTokenInput)}>
              <Key className="w-4 h-4" /> Dev: Paste Token
            </Button>
            <Button className="gap-2" onClick={handleConnect}>
              <Plus className="w-4 h-4" /> Connect Account
            </Button>
          </div>
        </div>

        {showTokenInput && (
          <div className="mb-6 p-4 rounded-lg border border-blue-500/30 bg-blue-500/10">
            <p className="text-xs text-blue-300 mb-3 font-medium">
              Development: Paste your Instagram access token from the Meta App Dashboard
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={tokenValue}
                onChange={(e) => setTokenValue(e.target.value)}
                placeholder="Paste Instagram access token here..."
                className="flex-1 px-3 py-2 text-sm rounded-md bg-background border border-input focus:outline-none focus:ring-1 focus:ring-ring"
              />
              <Button
                size="sm"
                onClick={() => manualConnectMutation.mutate(tokenValue)}
                disabled={!tokenValue.trim() || manualConnectMutation.isPending}
              >
                {manualConnectMutation.isPending ? "Connecting..." : "Connect"}
              </Button>
            </div>
          </div>
        )}

        <div className="mb-6 p-4 rounded-lg border border-amber-500/30 bg-amber-500/10 flex gap-3">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-300 leading-relaxed">
            <strong>Requirements:</strong> Your Instagram must be a <strong>Business or Creator account</strong> connected
            to a Facebook Page. Personal Instagram accounts are not supported by Meta's API.
          </p>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
        ) : accounts?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-pink-500/20 to-purple-600/20 mb-4">
              <Instagram className="w-8 h-8 text-pink-400" />
            </div>
            <h3 className="font-semibold text-lg mb-2">No accounts connected</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-sm">
              Connect your Instagram Business account to start creating automations.
            </p>
            <Button className="gap-2" onClick={handleConnect}>
              <Plus className="w-4 h-4" /> Connect Instagram
            </Button>
          </div>
        ) : (
          <div className="space-y-3 max-w-lg">
            {accounts?.map((account) => (
              <AccountCard
                key={account.id}
                account={account}
                onDisconnect={(id) => disconnectMutation.mutate(id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function InstagramPage() {
  return (
    <Suspense>
      <InstagramPageInner />
    </Suspense>
  );
}

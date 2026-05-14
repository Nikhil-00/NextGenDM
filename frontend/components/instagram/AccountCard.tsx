"use client";

import Image from "next/image";
import { Instagram, Trash2, CheckCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { InstagramAccount } from "@/types";

interface AccountCardProps {
  account: InstagramAccount;
  onDisconnect: (id: string) => void;
}

export function AccountCard({ account, onDisconnect }: AccountCardProps) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center gap-4">
          <div className="relative">
            {account.profile_picture_url ? (
              <Image
                src={account.profile_picture_url}
                alt={account.username}
                width={48}
                height={48}
                className="rounded-full"
              />
            ) : (
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-pink-500 to-purple-600">
                <Instagram className="w-6 h-6 text-white" />
              </div>
            )}
            <div className="absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full bg-green-500 border-2 border-card" />
          </div>

          <div className="flex-1 min-w-0">
            <p className="font-semibold">@{account.username}</p>
            {account.page_name && (
              <p className="text-xs text-muted-foreground mt-0.5">{account.page_name}</p>
            )}
            <div className="flex items-center gap-1.5 mt-1.5">
              <Badge variant="success" className="text-xs gap-1">
                <CheckCircle className="w-3 h-3" /> Connected
              </Badge>
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="hover:text-destructive hover:bg-destructive/10 shrink-0"
            onClick={() => onDisconnect(account.id)}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

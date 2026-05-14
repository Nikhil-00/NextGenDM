"use client";

import { useState } from "react";
import { Zap, MessageSquare, Link2, Users, Pencil, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import type { Automation } from "@/types";
import { formatDate } from "@/lib/utils";

interface AutomationCardProps {
  automation: Automation;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function AutomationCard({ automation, onToggle, onEdit, onDelete }: AutomationCardProps) {
  const [toggling, setToggling] = useState(false);

  const handleToggle = async () => {
    setToggling(true);
    await onToggle(automation.id);
    setToggling(false);
  };

  return (
    <Card className="hover:border-primary/50 transition-colors">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 shrink-0">
              <Zap className="w-4 h-4 text-primary" />
            </div>
            <div className="min-w-0">
              <p className="font-semibold truncate">{automation.name}</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Keyword: <span className="text-foreground font-medium">"{automation.trigger_keyword}"</span>
              </p>
            </div>
          </div>
          <Switch
            checked={automation.is_active}
            onCheckedChange={handleToggle}
            disabled={toggling}
            className="shrink-0"
          />
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="outline" className="text-xs gap-1">
            {automation.trigger_type === "comment_keyword" ? (
              <><MessageSquare className="w-3 h-3" /> Comment</>
            ) : (
              <><MessageSquare className="w-3 h-3" /> DM</>
            )}
          </Badge>
          {automation.response_link && (
            <Badge variant="outline" className="text-xs gap-1">
              <Link2 className="w-3 h-3" /> Has Link
            </Badge>
          )}
          {automation.require_follow && (
            <Badge variant="secondary" className="text-xs gap-1">
              <Users className="w-3 h-3" /> Follow-to-Unlock
            </Badge>
          )}
          <Badge variant={automation.is_active ? "success" : "outline"} className="text-xs">
            {automation.is_active ? "Active" : "Paused"}
          </Badge>
        </div>

        <div className="mt-4 p-3 rounded-lg bg-muted/50 text-xs text-muted-foreground line-clamp-2">
          {automation.response_message}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{formatDate(automation.created_at)}</span>
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onEdit(automation.id)}>
              <Pencil className="w-3.5 h-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 hover:text-destructive hover:bg-destructive/10"
              onClick={() => onDelete(automation.id)}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

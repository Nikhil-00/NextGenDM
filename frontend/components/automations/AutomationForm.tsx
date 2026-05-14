"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, Film, Image as ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { automationService } from "@/services/automationService";
import { instagramService } from "@/services/instagramService";
import type { Automation, AutomationCreate, InstagramAccount, InstagramMedia } from "@/types";

interface AutomationFormProps {
  accounts: InstagramAccount[];
  initialData?: Automation;
  mode: "create" | "edit";
}

export function AutomationForm({ accounts, initialData, mode }: AutomationFormProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    instagram_account_id: initialData?.instagram_account_id || accounts[0]?.id || "",
    name: initialData?.name || "",
    trigger_type: initialData?.trigger_type || "comment_keyword",
    trigger_keyword: initialData?.trigger_keyword || "",
    action_type: initialData?.action_type || "send_dm",
    response_message: initialData?.response_message || "",
    response_link: initialData?.response_link || "",
    require_follow: initialData?.require_follow || false,
    follow_required_message: initialData?.follow_required_message || "Please follow our account first to receive this content!",
    media_id: initialData?.media_id || "",
    media_url: initialData?.media_url || "",
  });

  const { data: mediaList, isLoading: mediaLoading } = useQuery<InstagramMedia[]>({
    queryKey: ["instagram-media", form.instagram_account_id],
    queryFn: () => instagramService.getAccountMedia(form.instagram_account_id),
    enabled: !!form.instagram_account_id && form.trigger_type === "comment_keyword",
  });

  const set = (field: string, value: unknown) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.instagram_account_id) return toast.error("Please connect an Instagram account first.");
    if (!form.name.trim()) return toast.error("Automation name is required.");
    if (!form.trigger_keyword.trim()) return toast.error("Trigger keyword is required.");
    if (!form.response_message.trim()) return toast.error("Response message is required.");

    setLoading(true);
    try {
      const payload: AutomationCreate = {
        ...form,
        response_link: form.response_link || undefined,
        media_id: form.media_id || undefined,
        media_url: form.media_url || undefined,
      };

      if (mode === "create") {
        await automationService.create(payload);
        toast.success("Automation created!");
      } else if (initialData) {
        await automationService.update(initialData.id, payload);
        toast.success("Automation updated!");
      }
      router.push("/automations");
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Basic Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Automation Name</Label>
            <Input
              placeholder="e.g. Free Guide Campaign"
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Instagram Account</Label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              value={form.instagram_account_id}
              onChange={(e) => set("instagram_account_id", e.target.value)}
            >
              {accounts.length === 0 && <option value="">No accounts connected</option>}
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>@{a.username}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Trigger</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Trigger Type</Label>
            <div className="flex gap-3">
              {[
                { value: "comment_keyword", label: "Comment Keyword" },
                { value: "dm_keyword", label: "DM Keyword" },
              ].map((opt) => (
                <button
                  type="button"
                  key={opt.value}
                  onClick={() => set("trigger_type", opt.value)}
                  className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-colors ${
                    form.trigger_type === opt.value
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-background text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Keyword</Label>
            <Input
              placeholder='e.g. "guide" or "freebie"'
              value={form.trigger_keyword}
              onChange={(e) => set("trigger_keyword", e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              When someone {form.trigger_type === "comment_keyword" ? "comments" : "messages"} this keyword, the automation fires.
            </p>
          </div>
        </CardContent>
      </Card>

      {form.trigger_type === "comment_keyword" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Target Post / Reel</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground mb-3">
              Select the post or reel this automation applies to. Leave blank to apply to all posts.
            </p>
            {mediaLoading ? (
              <p className="text-xs text-muted-foreground">Loading your posts...</p>
            ) : !mediaList?.length ? (
              <p className="text-xs text-muted-foreground">No posts found for this account.</p>
            ) : (
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                <button
                  type="button"
                  onClick={() => { set("media_id", ""); set("media_url", ""); }}
                  className={`relative aspect-square rounded-lg border-2 flex items-center justify-center text-xs font-medium transition-colors ${
                    !form.media_id ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground hover:border-primary/50"
                  }`}
                >
                  All Posts
                </button>
                {mediaList.map((media) => {
                  const thumb = media.thumbnail_url || media.media_url;
                  const selected = form.media_id === media.id;
                  return (
                    <button
                      type="button"
                      key={media.id}
                      onClick={() => { set("media_id", media.id); set("media_url", thumb || ""); }}
                      className={`relative aspect-square rounded-lg border-2 overflow-hidden transition-all ${
                        selected ? "border-primary ring-2 ring-primary/30" : "border-border hover:border-primary/50"
                      }`}
                    >
                      {thumb ? (
                        <img src={thumb} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full bg-muted flex items-center justify-center">
                          {media.media_type === "VIDEO" ? <Film className="w-5 h-5 text-muted-foreground" /> : <ImageIcon className="w-5 h-5 text-muted-foreground" />}
                        </div>
                      )}
                      {selected && (
                        <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                          <CheckCircle2 className="w-6 h-6 text-primary" />
                        </div>
                      )}
                      {media.media_type === "VIDEO" && (
                        <div className="absolute top-1 right-1 bg-black/60 rounded px-1">
                          <Film className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Response</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Response Message</Label>
            <Textarea
              placeholder="Hey! Here's your free guide..."
              value={form.response_message}
              onChange={(e) => set("response_message", e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label>Link (optional)</Label>
            <Input
              placeholder="https://example.com/your-guide.pdf"
              value={form.response_link}
              onChange={(e) => set("response_link", e.target.value)}
            />
            <p className="text-xs text-muted-foreground">This link will be appended to the message.</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Follow-to-Unlock</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Require Follow</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Only send the response if the user follows your account.
              </p>
            </div>
            <Switch
              checked={form.require_follow}
              onCheckedChange={(v) => set("require_follow", v)}
            />
          </div>

          {form.require_follow && (
            <div className="space-y-2">
              <Label>Message if NOT following</Label>
              <Textarea
                value={form.follow_required_message}
                onChange={(e) => set("follow_required_message", e.target.value)}
                rows={2}
              />
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Button type="submit" disabled={loading}>
          {loading ? "Saving…" : mode === "create" ? "Create Automation" : "Save Changes"}
        </Button>
        <Button type="button" variant="outline" onClick={() => router.push("/automations")}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

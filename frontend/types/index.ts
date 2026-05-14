export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface InstagramAccount {
  id: string;
  instagram_user_id: string;
  username: string;
  profile_picture_url: string | null;
  page_id: string | null;
  page_name: string | null;
  is_active: boolean;
  created_at: string;
}

export type TriggerType = "comment_keyword" | "dm_keyword";
export type ActionType = "send_dm" | "send_link";
export type LogStatus = "success" | "failed" | "pending" | "follow_required";

export interface Automation {
  id: string;
  instagram_account_id: string;
  name: string;
  trigger_type: TriggerType;
  trigger_keyword: string;
  action_type: ActionType;
  response_message: string;
  response_link: string | null;
  require_follow: boolean;
  follow_required_message: string;
  media_id: string | null;
  media_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InstagramMedia {
  id: string;
  caption?: string;
  media_type: "IMAGE" | "VIDEO" | "CAROUSEL_ALBUM";
  media_url?: string;
  thumbnail_url?: string;
  permalink: string;
  timestamp: string;
}

export interface AutomationCreate {
  instagram_account_id: string;
  name: string;
  trigger_type: TriggerType;
  trigger_keyword: string;
  action_type: ActionType;
  response_message: string;
  response_link?: string;
  require_follow?: boolean;
  follow_required_message?: string;
  media_id?: string;
  media_url?: string;
}

export interface AutomationUpdate {
  name?: string;
  trigger_keyword?: string;
  response_message?: string;
  response_link?: string;
  require_follow?: boolean;
  follow_required_message?: string;
  is_active?: boolean;
}

export interface AutomationLog {
  id: string;
  automation_id: string | null;
  trigger_type: string | null;
  trigger_keyword: string | null;
  sender_instagram_id: string | null;
  sender_username: string | null;
  action_taken: string | null;
  status: LogStatus;
  error_message: string | null;
  created_at: string;
}

export interface PaginatedLogs {
  items: AutomationLog[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface DashboardStats {
  total_automations: number;
  active_automations: number;
  connected_accounts: number;
  messages_sent: number;
}

export interface UploadedFile {
  id: string;
  filename: string;
  original_filename: string;
  file_url: string;
  file_size: number | null;
  mime_type: string | null;
  created_at: string;
}

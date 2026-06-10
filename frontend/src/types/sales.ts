import type { components, paths } from "./generated/openapi";

export type OpportunityPayload = components["schemas"]["OpportunityCreate"];
export type OpportunityUpdatePayload = components["schemas"]["OpportunityUpdate"];
export type FollowUpPayload = components["schemas"]["FollowUpCreate"];
export type FollowUpUpdatePayload = components["schemas"]["FollowUpUpdate"];
export type OpportunityListParams =
  NonNullable<paths["/api/v1/opportunities"]["get"]["parameters"]["query"]>;

export type OpportunityStage =
  | "NEW"
  | "PACKAGE_SENT"
  | "INTERESTED"
  | "NEED_FOLLOW_UP"
  | "THINKING"
  | "BOOKED"
  | "LOST";
export type OpportunityType = "MATERNITY" | "NEWBORN" | "FAMILY" | "MILESTONE" | "CAKE_SMASH";
export type FollowUpType = "CALL" | "WHATSAPP" | "INSTAGRAM_DM" | "EMAIL" | "OTHER";
export type FollowUpStatus = "PENDING" | "COMPLETED" | "MISSED";

export interface FamilySummary {
  id: string;
  family_code: string;
  primary_contact_name: string;
  primary_contact_phone: string;
  primary_contact_email?: string | null;
  city?: string | null;
}

export interface UserSummary {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface LostReason {
  id: string;
  name: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FollowUp {
  id: string;
  opportunity_id: string;
  assigned_to_user_id: string;
  followup_type: FollowUpType;
  due_date: string;
  completed_at?: string | null;
  status: FollowUpStatus;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  assigned_to_user?: UserSummary | null;
}

export interface OpportunityNote {
  id: string;
  opportunity_id: string;
  created_by_user_id: string;
  note: string;
  created_at: string;
  created_by_user?: UserSummary | null;
}

export interface OpportunityStageHistory {
  id: string;
  opportunity_id: string;
  from_stage?: OpportunityStage | null;
  to_stage: OpportunityStage;
  changed_by_user_id: string;
  notes?: string | null;
  created_at: string;
  changed_by_user?: UserSummary | null;
}

export interface Opportunity {
  id: string;
  organization_id: string;
  branch_id: string;
  family_id: string;
  assigned_to_user_id: string;
  opportunity_type: OpportunityType;
  current_stage: OpportunityStage;
  estimated_value: string;
  probability: number;
  expected_booking_date?: string | null;
  lost_reason_id?: string | null;
  notes?: string | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  family?: FamilySummary | null;
  assigned_to_user?: UserSummary | null;
  lost_reason?: LostReason | null;
  followups: FollowUp[];
  opportunity_notes: OpportunityNote[];
  stage_history: OpportunityStageHistory[];
}

export type Pipeline = Record<OpportunityStage, Opportunity[]>;

export interface SalesMetrics {
  open_opportunities: number;
  booked_opportunities: number;
  lost_opportunities: number;
  conversion_rate: number;
  pending_followups: number;
  missed_followups: number;
  follow_up_compliance: number;
  average_opportunity_value: number;
}

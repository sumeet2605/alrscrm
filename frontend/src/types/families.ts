import type { components, paths } from "./generated/openapi";

export type FamilyPayload = components["schemas"]["FamilyCreate"];
export type FamilyUpdatePayload = components["schemas"]["FamilyUpdate"];
export type FamilyListParams =
  NonNullable<paths["/api/v1/families"]["get"]["parameters"]["query"]>;
export type FamilySearchParams =
  NonNullable<paths["/api/v1/families/search"]["get"]["parameters"]["query"]>;

export type FamilyStatus = components["schemas"]["FamilyStatus"];
export type LeadSource = components["schemas"]["LeadSource"];
export type Gender = components["schemas"]["Gender"];
export type Relationship = components["schemas"]["Relationship"];
export type ServiceType = components["schemas"]["ServiceType"];

export interface FamilyMember {
  id: string;
  name: string;
  relationship: Relationship;
  date_of_birth?: string | null;
  gender?: Gender | null;
  created_at: string;
  updated_at: string;
}

export interface FamilyAddress {
  id: string;
  address_line_1: string;
  address_line_2?: string | null;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceInterest {
  id: string;
  service_type: ServiceType;
  priority: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Family {
  id: string;
  organization_id: string;
  branch_id: string;
  family_code: string;
  primary_contact_name: string;
  primary_contact_phone: string;
  primary_contact_email?: string | null;
  partner_name?: string | null;
  partner_phone?: string | null;
  partner_email?: string | null;
  city?: string | null;
  expected_delivery_date?: string | null;
  source: LeadSource;
  notes?: string | null;
  status: FamilyStatus;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  members: FamilyMember[];
  address?: FamilyAddress | null;
  service_interests: ServiceInterest[];
}

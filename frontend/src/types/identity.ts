import type { components, paths } from "./generated/openapi";

export interface Permission {
  id: string;
  code: string;
  name: string;
  description?: string | null;
}

export interface Role {
  id: string;
  name: string;
  description?: string | null;
  is_platform: boolean;
  priority: number;
  permissions: Permission[];
}

export interface Organization {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationSettings {
  id: string;
  organization_id: string;
  studio_name: string;
  logo_url?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  website?: string | null;
  address?: string | null;
  timezone: string;
  currency: string;
  delivery_expiry_default: number;
  gallery_selection_default_limit: number;
  created_at: string;
  updated_at: string;
}

export interface OrganizationOnboardingPayload {
  organization: {
    name: string;
    code: string;
    timezone: string;
    email?: string | null;
    phone?: string | null;
  };
  branch: {
    name: string;
  };
  owner: {
    name: string;
    email: string;
    phone?: string | null;
  };
}

export interface OrganizationOnboardingResult {
  organization: Organization;
  settings: OrganizationSettings;
  branch_id: string;
  owner_id: string;
  owner_temporary_password: string;
}

export interface Branch {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  city: string;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  organization_id: string;
  branch_id?: string | null;
  username?: string | null;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  is_active: boolean;
  password_reset_required?: boolean;
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export type BranchPayload = components["schemas"]["BranchCreate"];
export type BranchUpdatePayload = components["schemas"]["BranchUpdate"];
export type BranchListParams =
  NonNullable<paths["/api/v1/branches"]["get"]["parameters"]["query"]>;

export type UserPayload = components["schemas"]["UserCreate"];
export type UserUpdatePayload = components["schemas"]["UserUpdate"];
export type UserListParams =
  NonNullable<paths["/api/v1/users"]["get"]["parameters"]["query"]>;

export type OrganizationPayload = Pick<Organization, "name" | "code" | "is_active">;
export type OrganizationUpdatePayload = Partial<OrganizationPayload>;
export type OrganizationSettingsUpdatePayload = Partial<
  Omit<OrganizationSettings, "id" | "organization_id" | "created_at" | "updated_at">
>;
export interface OrganizationListParams {
  page?: number;
  page_size?: number;
}

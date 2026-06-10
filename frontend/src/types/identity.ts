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
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export interface BranchPayload {
  organization_id: string;
  name: string;
  code: string;
  city: string;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  is_active: boolean;
}

export interface UserPayload {
  organization_id: string;
  branch_id?: string | null;
  username?: string | null;
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  is_active: boolean;
  role_ids: string[];
}

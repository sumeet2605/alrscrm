/* eslint-disable */
/* tslint:disable */
// This file is generated from the backend OpenAPI schema.
// Run npm run generate:api-types from frontend/ to regenerate.

export interface components {
  schemas: {
    "APIResponse": {
      "data": unknown;
      "message": string;
      "meta"?: Record<string, unknown> | null;
      "success": boolean;
    };
    "BranchCreate": {
      "address"?: string | null;
      "city": string;
      "code": string;
      "email"?: string | null;
      "is_active"?: boolean;
      "name": string;
      "organization_id": string;
      "phone"?: string | null;
    };
    "BranchUpdate": {
      "address"?: string | null;
      "city"?: string | null;
      "code"?: string | null;
      "email"?: string | null;
      "is_active"?: boolean | null;
      "name"?: string | null;
      "organization_id"?: string | null;
      "phone"?: string | null;
    };
    "FamilyAddressCreate": {
      "address_line_1": string;
      "address_line_2"?: string | null;
      "city": string;
      "country": string;
      "postal_code": string;
      "state": string;
    };
    "FamilyCreate": {
      "address"?: components["schemas"]["FamilyAddressCreate"] | null;
      "branch_id": string;
      "city"?: string | null;
      "expected_delivery_date"?: string | null;
      "members"?: components["schemas"]["FamilyMemberCreate"][];
      "notes"?: string | null;
      "organization_id": string;
      "partner_email"?: string | null;
      "partner_name"?: string | null;
      "partner_phone"?: string | null;
      "primary_contact_email"?: string | null;
      "primary_contact_name": string;
      "primary_contact_phone": string;
      "service_interests"?: components["schemas"]["ServiceInterestCreate"][];
      "source"?: components["schemas"]["LeadSource"];
      "status"?: components["schemas"]["FamilyStatus"];
    };
    "FamilyMemberCreate": {
      "date_of_birth"?: string | null;
      "gender"?: components["schemas"]["Gender"] | null;
      "name": string;
      "relationship": components["schemas"]["Relationship"];
    };
    "FamilyStatus": string;
    "FamilyUpdate": {
      "address"?: components["schemas"]["FamilyAddressCreate"] | null;
      "branch_id"?: string | null;
      "city"?: string | null;
      "expected_delivery_date"?: string | null;
      "members"?: components["schemas"]["FamilyMemberCreate"][] | null;
      "notes"?: string | null;
      "partner_email"?: string | null;
      "partner_name"?: string | null;
      "partner_phone"?: string | null;
      "primary_contact_email"?: string | null;
      "primary_contact_name"?: string | null;
      "primary_contact_phone"?: string | null;
      "service_interests"?: components["schemas"]["ServiceInterestCreate"][] | null;
      "source"?: components["schemas"]["LeadSource"] | null;
      "status"?: components["schemas"]["FamilyStatus"] | null;
    };
    "Gender": string;
    "HTTPValidationError": {
      "detail"?: components["schemas"]["ValidationError"][];
    };
    "LeadSource": string;
    "LoginRequest": {
      "email": string;
      "password": string;
    };
    "OrganizationCreate": {
      "code": string;
      "is_active"?: boolean;
      "name": string;
    };
    "OrganizationUpdate": {
      "code"?: string | null;
      "is_active"?: boolean | null;
      "name"?: string | null;
    };
    "RefreshRequest": {
      "refresh_token": string;
    };
    "Relationship": string;
    "ServiceInterestCreate": {
      "notes"?: string | null;
      "priority"?: number;
      "service_type": components["schemas"]["ServiceType"];
    };
    "ServiceType": string;
    "UserCreate": {
      "branch_id"?: string | null;
      "email": string;
      "first_name": string;
      "is_active"?: boolean;
      "last_name": string;
      "organization_id": string;
      "password": string;
      "phone"?: string | null;
      "role_ids"?: string[];
      "username"?: string | null;
    };
    "UserUpdate": {
      "branch_id"?: string | null;
      "email"?: string | null;
      "first_name"?: string | null;
      "is_active"?: boolean | null;
      "last_name"?: string | null;
      "organization_id"?: string | null;
      "password"?: string | null;
      "phone"?: string | null;
      "role_ids"?: string[] | null;
      "username"?: string | null;
    };
    "ValidationError": {
      "ctx"?: {

    };
      "input"?: unknown;
      "loc": (string | number)[];
      "msg": string;
      "type": string;
    };
  };
}

export interface paths {
  "/api/v1/auth/login": {
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["LoginRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/auth/logout": {
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["RefreshRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/auth/me": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/auth/refresh": {
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["RefreshRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/branches": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["BranchCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/branches/{branch_id}": {
    get: {
      parameters: {
      path: {
        "branch_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    patch: {
      parameters: {
      path: {
        "branch_id": string;
      };
    };
      requestBody: components["schemas"]["BranchUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "branch_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/families": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "search"?: string | null;
        "status"?: components["schemas"]["FamilyStatus"] | null;
        "source"?: components["schemas"]["LeadSource"] | null;
        "branch_id"?: string | null;
        "edd_from"?: string | null;
        "edd_to"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["FamilyCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/families/search": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "name"?: string | null;
        "phone"?: string | null;
        "email"?: string | null;
        "family_code"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/families/{family_id}": {
    get: {
      parameters: {
      path: {
        "family_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    put: {
      parameters: {
      path: {
        "family_id": string;
      };
    };
      requestBody: components["schemas"]["FamilyUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "family_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/organizations": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["OrganizationCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/organizations/{organization_id}": {
    get: {
      parameters: {
      path: {
        "organization_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    patch: {
      parameters: {
      path: {
        "organization_id": string;
      };
    };
      requestBody: components["schemas"]["OrganizationUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "organization_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/permissions": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/roles": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/users": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["UserCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/users/{user_id}": {
    get: {
      parameters: {
      path: {
        "user_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    patch: {
      parameters: {
      path: {
        "user_id": string;
      };
    };
      requestBody: components["schemas"]["UserUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "user_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/health": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": unknown;
      };
    };
  };
}

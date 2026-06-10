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
    "HTTPValidationError": {
      "detail"?: components["schemas"]["ValidationError"][];
    };
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

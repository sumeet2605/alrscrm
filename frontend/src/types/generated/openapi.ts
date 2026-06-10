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
    "AssignmentRole": "LEAD_PHOTOGRAPHER" | "SECOND_PHOTOGRAPHER" | "ASSISTANT";
    "BookingCreate": {
      "advance_received"?: number | string;
      "booking_date": string;
      "booking_status"?: components["schemas"]["BookingStatus"];
      "branch_id": string;
      "family_id": string;
      "items": components["schemas"]["BookingItemCreate"][];
      "notes"?: string | null;
      "opportunity_id": string;
      "organization_id": string;
    };
    "BookingItemAddonCreate": {
      "addon_id": string;
    };
    "BookingItemCreate": {
      "addons"?: components["schemas"]["BookingItemAddonCreate"][];
      "discount"?: number | string;
      "package_id": string;
      "service_type": components["schemas"]["ServiceType"];
    };
    "BookingStatus": "PENDING_ADVANCE" | "CONFIRMED" | "SCHEDULED" | "COMPLETED" | "CANCELLED";
    "BookingUpdate": {
      "advance_received"?: number | string | null;
      "booking_date"?: string | null;
      "booking_status"?: components["schemas"]["BookingStatus"] | null;
      "items"?: components["schemas"]["BookingItemCreate"][] | null;
      "notes"?: string | null;
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
    "FamilyStatus": "INQUIRY" | "INTERESTED" | "BOOKED" | "ACTIVE" | "INACTIVE";
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
    "FollowUpCreate": {
      "assigned_to_user_id": string;
      "completed_at"?: string | null;
      "due_date": string;
      "followup_type"?: components["schemas"]["FollowUpType"];
      "notes"?: string | null;
      "opportunity_id": string;
      "status"?: components["schemas"]["FollowUpStatus"];
    };
    "FollowUpStatus": "PENDING" | "COMPLETED" | "MISSED";
    "FollowUpType": "CALL" | "WHATSAPP" | "INSTAGRAM_DM" | "EMAIL" | "OTHER";
    "FollowUpUpdate": {
      "assigned_to_user_id"?: string | null;
      "completed_at"?: string | null;
      "due_date"?: string | null;
      "followup_type"?: components["schemas"]["FollowUpType"] | null;
      "notes"?: string | null;
      "status"?: components["schemas"]["FollowUpStatus"] | null;
    };
    "Gender": "MALE" | "FEMALE" | "OTHER";
    "HTTPValidationError": {
      "detail"?: components["schemas"]["ValidationError"][];
    };
    "LeadSource": "INSTAGRAM" | "WHATSAPP" | "GOOGLE" | "REFERRAL" | "WEBSITE" | "WALKIN" | "OTHER";
    "LoginRequest": {
      "email": string;
      "password": string;
    };
    "OpportunityCreate": {
      "assigned_to_user_id": string;
      "branch_id": string;
      "current_stage"?: components["schemas"]["OpportunityStage"];
      "estimated_value"?: number | string;
      "expected_booking_date"?: string | null;
      "family_id": string;
      "lost_reason_id"?: string | null;
      "notes"?: string | null;
      "opportunity_type": components["schemas"]["OpportunityType"];
      "organization_id": string;
      "probability"?: number;
    };
    "OpportunityNoteCreate": {
      "note": string;
    };
    "OpportunityStage": "NEW" | "PACKAGE_SENT" | "INTERESTED" | "NEED_FOLLOW_UP" | "THINKING" | "BOOKED" | "LOST";
    "OpportunityType": "MATERNITY" | "NEWBORN" | "FAMILY" | "MILESTONE" | "CAKE_SMASH";
    "OpportunityUpdate": {
      "assigned_to_user_id"?: string | null;
      "branch_id"?: string | null;
      "current_stage"?: components["schemas"]["OpportunityStage"] | null;
      "estimated_value"?: number | string | null;
      "expected_booking_date"?: string | null;
      "family_id"?: string | null;
      "lost_reason_id"?: string | null;
      "notes"?: string | null;
      "opportunity_type"?: components["schemas"]["OpportunityType"] | null;
      "probability"?: number | null;
      "stage_change_notes"?: string | null;
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
    "PackageAddonCreate": {
      "branch_id": string;
      "description"?: string | null;
      "is_active"?: boolean;
      "name": string;
      "organization_id": string;
      "price": number | string;
    };
    "PackageAddonUpdate": {
      "branch_id"?: string | null;
      "description"?: string | null;
      "is_active"?: boolean | null;
      "name"?: string | null;
      "price"?: number | string | null;
    };
    "PackageCreate": {
      "branch_id": string;
      "description"?: string | null;
      "is_active"?: boolean;
      "name": string;
      "organization_id": string;
      "price": number | string;
      "service_type": components["schemas"]["ServiceType"];
    };
    "PackageUpdate": {
      "branch_id"?: string | null;
      "description"?: string | null;
      "is_active"?: boolean | null;
      "name"?: string | null;
      "price"?: number | string | null;
      "service_type"?: components["schemas"]["ServiceType"] | null;
    };
    "PhotographerAssignmentCreate": {
      "role": components["schemas"]["AssignmentRole"];
      "shoot_schedule_id": string;
      "user_id": string;
    };
    "RefreshRequest": {
      "refresh_token": string;
    };
    "Relationship": "MOTHER" | "FATHER" | "BABY" | "GRANDPARENT" | "SIBLING" | "OTHER";
    "ServiceInterestCreate": {
      "notes"?: string | null;
      "priority"?: number;
      "service_type": components["schemas"]["ServiceType"];
    };
    "ServiceType": "MATERNITY" | "NEWBORN" | "FAMILY" | "MILESTONE" | "CAKE_SMASH";
    "ShootScheduleCreate": {
      "booking_id": string;
      "booking_item_id": string;
      "location": string;
      "notes"?: string | null;
      "scheduled_end": string;
      "scheduled_start": string;
      "shoot_status"?: components["schemas"]["ShootStatus"];
    };
    "ShootScheduleUpdate": {
      "location"?: string | null;
      "notes"?: string | null;
      "scheduled_end"?: string | null;
      "scheduled_start"?: string | null;
      "shoot_status"?: components["schemas"]["ShootStatus"] | null;
    };
    "ShootStatus": "NOT_SCHEDULED" | "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "RESCHEDULED" | "CANCELLED";
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
  "/api/v1/addons": {
    get: {
      parameters: {
      query: {
        "branch_id"?: string | null;
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
      requestBody: components["schemas"]["PackageAddonCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/addons/{addon_id}": {
    put: {
      parameters: {
      path: {
        "addon_id": string;
      };
    };
      requestBody: components["schemas"]["PackageAddonUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/assignments": {
    get: {
      parameters: {
      query: {
        "photographer_id"?: string | null;
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
      requestBody: components["schemas"]["PhotographerAssignmentCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/assignments/{assignment_id}": {
    delete: {
      parameters: {
      path: {
        "assignment_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
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
  "/api/v1/bookings": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "search"?: string | null;
        "booking_status"?: components["schemas"]["BookingStatus"] | null;
        "service_type"?: components["schemas"]["ServiceType"] | null;
        "photographer_id"?: string | null;
        "booking_from"?: string | null;
        "booking_to"?: string | null;
        "branch_id"?: string | null;
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
      requestBody: components["schemas"]["BookingCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/bookings/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/bookings/{booking_id}": {
    get: {
      parameters: {
      path: {
        "booking_id": string;
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
        "booking_id": string;
      };
    };
      requestBody: components["schemas"]["BookingUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "booking_id": string;
      };
    };
      requestBody: never;
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
  "/api/v1/followups": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "branch_id"?: string | null;
        "assigned_to_user_id"?: string | null;
        "status"?: components["schemas"]["FollowUpStatus"] | null;
        "due_from"?: string | null;
        "due_to"?: string | null;
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
      requestBody: components["schemas"]["FollowUpCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/followups/{followup_id}": {
    put: {
      parameters: {
      path: {
        "followup_id": string;
      };
    };
      requestBody: components["schemas"]["FollowUpUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/lost-reasons": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/opportunities": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "search"?: string | null;
        "stage"?: components["schemas"]["OpportunityStage"] | null;
        "assigned_to_user_id"?: string | null;
        "opportunity_type"?: components["schemas"]["OpportunityType"] | null;
        "lost_reason_id"?: string | null;
        "branch_id"?: string | null;
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
      requestBody: components["schemas"]["OpportunityCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/opportunities/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/opportunities/pipeline": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/opportunities/{opportunity_id}": {
    get: {
      parameters: {
      path: {
        "opportunity_id": string;
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
        "opportunity_id": string;
      };
    };
      requestBody: components["schemas"]["OpportunityUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    delete: {
      parameters: {
      path: {
        "opportunity_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/opportunities/{opportunity_id}/history": {
    get: {
      parameters: {
      path: {
        "opportunity_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/opportunities/{opportunity_id}/notes": {
    get: {
      parameters: {
      path: {
        "opportunity_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
    post: {
      parameters: {
      path: {
        "opportunity_id": string;
      };
    };
      requestBody: components["schemas"]["OpportunityNoteCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
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
  "/api/v1/packages": {
    get: {
      parameters: {
      query: {
        "branch_id"?: string | null;
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
      requestBody: components["schemas"]["PackageCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/packages/{package_id}": {
    get: {
      parameters: {
      path: {
        "package_id": string;
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
        "package_id": string;
      };
    };
      requestBody: components["schemas"]["PackageUpdate"];
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
  "/api/v1/schedules": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "shoot_status"?: components["schemas"]["ShootStatus"] | null;
        "photographer_id"?: string | null;
        "scheduled_from"?: string | null;
        "scheduled_to"?: string | null;
        "branch_id"?: string | null;
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
      requestBody: components["schemas"]["ShootScheduleCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/schedules/{schedule_id}": {
    get: {
      parameters: {
      path: {
        "schedule_id": string;
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
        "schedule_id": string;
      };
    };
      requestBody: components["schemas"]["ShootScheduleUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
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

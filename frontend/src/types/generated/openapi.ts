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
    "Body_upload_gallery_photo_api_v1_galleries__gallery_id__photos_upload_post": {
      "file": string;
      "image_height"?: number;
      "image_width"?: number;
      "sort_order"?: number;
    };
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
    "DeliveryAuthenticateRequest": {
      "password"?: string | null;
      "token": string;
    };
    "DeliveryJobCreate": {
      "allow_re_download"?: boolean;
      "delivery_notes"?: string | null;
      "editing_job_id": string;
      "max_downloads"?: number;
      "original_download_enabled"?: boolean;
      "password"?: string | null;
      "re_download_fee"?: number | string;
      "watermark_enabled"?: boolean;
    };
    "DeliveryJobUpdate": {
      "allow_re_download"?: boolean | null;
      "delivery_link"?: string | null;
      "delivery_notes"?: string | null;
      "expiry_date"?: string | null;
      "max_downloads"?: number | null;
      "original_download_enabled"?: boolean | null;
      "password"?: string | null;
      "re_download_fee"?: number | string | null;
      "watermark_enabled"?: boolean | null;
    };
    "DeliveryReopenRequest": {
      "reason": string;
      "requested_by_email": string;
      "requested_by_name": string;
    };
    "DeliveryStatus": "PENDING" | "ZIP_GENERATING" | "READY" | "SENT" | "DELIVERED" | "EXPIRED" | "REOPEN_REQUESTED" | "REOPENED" | "CLOSED";
    "EditingAssignEditor": {
      "assigned_editor_id": string;
      "due_date"?: string | null;
    };
    "EditingJobCreate": {
      "assigned_editor_id"?: string | null;
      "due_date"?: string | null;
      "gallery_id": string;
      "notes"?: string | null;
      "priority"?: components["schemas"]["EditingPriority"];
    };
    "EditingJobUpdate": {
      "completed_photo_count"?: number | null;
      "due_date"?: string | null;
      "editing_status"?: components["schemas"]["EditingStatus"] | null;
      "notes"?: string | null;
      "priority"?: components["schemas"]["EditingPriority"] | null;
    };
    "EditingPriority": "LOW" | "NORMAL" | "HIGH" | "URGENT";
    "EditingReviewCreate": {
      "review_notes"?: string | null;
    };
    "EditingStatus": "PENDING" | "ASSIGNED" | "IN_PROGRESS" | "READY_FOR_REVIEW" | "APPROVED" | "REJECTED" | "READY_FOR_DELIVERY";
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
    "FavoriteSelectionCreate": {
      "gallery_photo_id": string;
      "selected_by_email"?: string | null;
      "selected_by_name": string;
    };
    "FinanceSettingsUpdate": {
      "auto_create_booking_invoice"?: boolean | null;
      "billing_address"?: string | null;
      "billing_state"?: string | null;
      "billing_state_code"?: string | null;
      "branch_id"?: string | null;
      "default_currency"?: string | null;
      "default_due_days"?: number | null;
      "gstin"?: string | null;
      "invoice_prefix"?: string | null;
      "legal_name"?: string | null;
      "registration_type"?: components["schemas"]["GSTRegistrationType"] | null;
      "require_payment_before_delivery"?: boolean | null;
      "trade_name"?: string | null;
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
    "GSTRegistrationType": "REGULAR" | "COMPOSITION" | "EXEMPT" | "UNREGISTERED";
    "GalleryAuthenticateRequest": {
      "password": string;
    };
    "GalleryCreate": {
      "allow_download"?: boolean;
      "allow_watermark"?: boolean;
      "booking_id": string;
      "booking_item_id": string;
      "expires_at"?: string | null;
      "gallery_name": string;
      "gallery_status"?: components["schemas"]["GalleryStatus"];
      "password"?: string | null;
      "selection_deadline"?: string | null;
      "selection_limit"?: number;
    };
    "GalleryPhotoCreate": {
      "file_name": string;
      "file_size": number;
      "image_height": number;
      "image_width": number;
      "is_active"?: boolean;
      "sort_order"?: number;
      "storage_path": string;
      "thumbnail_path"?: string | null;
    };
    "GalleryStatus": "DRAFT" | "UPLOADED" | "SELECTION_OPEN" | "SELECTION_SUBMITTED" | "SELECTION_REOPENED" | "SELECTION_CLOSED";
    "GalleryUpdate": {
      "allow_download"?: boolean | null;
      "allow_watermark"?: boolean | null;
      "expires_at"?: string | null;
      "gallery_name"?: string | null;
      "gallery_status"?: components["schemas"]["GalleryStatus"] | null;
      "password"?: string | null;
      "selection_deadline"?: string | null;
      "selection_limit"?: number | null;
    };
    "GalleryUpgradeRequestCreate": {
      "notes"?: string | null;
      "price_per_photo": number;
      "requested_limit": number;
    };
    "Gender": "MALE" | "FEMALE" | "OTHER";
    "HTTPValidationError": {
      "detail"?: components["schemas"]["ValidationError"][];
    };
    "InvoiceCreate": {
      "booking_id": string;
      "branch_id": string;
      "buyer_billing_address"?: string | null;
      "buyer_billing_name"?: string | null;
      "buyer_gstin"?: string | null;
      "buyer_state_code"?: string | null;
      "currency"?: string;
      "due_date": string;
      "family_id": string;
      "gst_registration_type"?: components["schemas"]["GSTRegistrationType"];
      "line_items": components["schemas"]["InvoiceLineItemCreate"][];
      "notes"?: string | null;
      "organization_id": string;
      "place_of_supply_state_code"?: string | null;
      "reverse_charge_applicable"?: boolean;
      "seller_address"?: string | null;
      "seller_gstin"?: string | null;
      "seller_legal_name"?: string | null;
      "seller_state_code"?: string | null;
      "seller_trade_name"?: string | null;
      "supply_type"?: components["schemas"]["SupplyType"];
    };
    "InvoiceLineItemCreate": {
      "cgst_amount"?: number | string;
      "cgst_rate"?: number | string;
      "description": string;
      "discount_amount"?: number | string;
      "igst_amount"?: number | string;
      "igst_rate"?: number | string;
      "quantity": number | string;
      "sac_code"?: string | null;
      "service_type": string;
      "sgst_amount"?: number | string;
      "sgst_rate"?: number | string;
      "tax_rate"?: number | string;
      "unit_price": number | string;
    };
    "InvoiceStatus": "DRAFT" | "ISSUED" | "PARTIALLY_PAID" | "PAID" | "VOID" | "OVERDUE";
    "InvoiceUpdate": {
      "buyer_billing_address"?: string | null;
      "buyer_billing_name"?: string | null;
      "buyer_gstin"?: string | null;
      "buyer_state_code"?: string | null;
      "currency"?: string | null;
      "due_date"?: string | null;
      "gst_registration_type"?: components["schemas"]["GSTRegistrationType"] | null;
      "line_items"?: components["schemas"]["InvoiceLineItemCreate"][] | null;
      "notes"?: string | null;
      "place_of_supply_state_code"?: string | null;
      "reverse_charge_applicable"?: boolean | null;
      "seller_address"?: string | null;
      "seller_gstin"?: string | null;
      "seller_legal_name"?: string | null;
      "seller_state_code"?: string | null;
      "seller_trade_name"?: string | null;
      "supply_type"?: components["schemas"]["SupplyType"] | null;
    };
    "LeadSource": "INSTAGRAM" | "WHATSAPP" | "GOOGLE" | "REFERRAL" | "WEBSITE" | "WALKIN" | "OTHER";
    "LoginRequest": {
      "email": string;
      "organization_code": string;
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
    "OrganizationOnboardingBranch": {
      "name"?: string;
    };
    "OrganizationOnboardingCreate": {
      "branch": components["schemas"]["OrganizationOnboardingBranch"];
      "organization": components["schemas"]["OrganizationOnboardingDetails"];
      "owner": components["schemas"]["OrganizationOnboardingOwner"];
    };
    "OrganizationOnboardingDetails": {
      "code": string;
      "email"?: string | null;
      "name": string;
      "phone"?: string | null;
      "timezone"?: string;
    };
    "OrganizationOnboardingOwner": {
      "email": string;
      "name": string;
      "phone"?: string | null;
    };
    "OrganizationSettingsUpdate": {
      "address"?: string | null;
      "contact_email"?: string | null;
      "contact_phone"?: string | null;
      "currency"?: string | null;
      "delivery_expiry_default"?: number | null;
      "gallery_selection_default_limit"?: number | null;
      "logo_url"?: string | null;
      "studio_name"?: string | null;
      "timezone"?: string | null;
      "website"?: string | null;
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
    "PaymentCreate": {
      "amount": number | string;
      "invoice_id": string;
      "notes"?: string | null;
      "payment_method": components["schemas"]["PaymentMethod"];
      "payment_status"?: components["schemas"]["PaymentStatus"];
      "received_date"?: string;
      "transaction_reference"?: string | null;
    };
    "PaymentMethod": "CASH" | "UPI" | "BANK_TRANSFER" | "CARD" | "CHEQUE" | "OTHER";
    "PaymentStatus": "PENDING" | "COMPLETED" | "FAILED" | "REFUNDED";
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
    "SupplyType": "INTRA_STATE" | "INTER_STATE" | "NON_GST";
    "UserCreate": {
      "branch_id"?: string | null;
      "email": string;
      "first_name": string;
      "is_active"?: boolean;
      "last_name": string;
      "organization_id": string;
      "password": string;
      "password_reset_required"?: boolean;
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
      "password_reset_required"?: boolean | null;
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
  "/api/v1/delivery/client/{token}": {
    get: {
      parameters: {
      path: {
        "token": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/client/{token}/download": {
    post: {
      parameters: {
      path: {
        "token": string;
      };
      header: {
        "authorization"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/client/{token}/reopen-request": {
    post: {
      parameters: {
      path: {
        "token": string;
      };
    };
      requestBody: components["schemas"]["DeliveryReopenRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "branch_id"?: string | null;
        "status"?: components["schemas"]["DeliveryStatus"] | null;
        "search"?: string | null;
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
      requestBody: components["schemas"]["DeliveryJobCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}": {
    get: {
      parameters: {
      path: {
        "job_id": string;
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
        "job_id": string;
      };
    };
      requestBody: components["schemas"]["DeliveryJobUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/access-token/revoke": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/access-token/rotate": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/approve-reopen": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/close": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/downloads": {
    get: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/generate-zip": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/jobs/{job_id}/send": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/delivery/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/delivery/public/authenticate": {
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["DeliveryAuthenticateRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "status"?: components["schemas"]["EditingStatus"] | null;
        "priority"?: components["schemas"]["EditingPriority"] | null;
        "assigned_editor_id"?: string | null;
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
      requestBody: components["schemas"]["EditingJobCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}": {
    get: {
      parameters: {
      path: {
        "job_id": string;
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
        "job_id": string;
      };
    };
      requestBody: components["schemas"]["EditingJobUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/approve": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: components["schemas"]["EditingReviewCreate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/assign-editor": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: components["schemas"]["EditingAssignEditor"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/ready-for-delivery": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/reject": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: components["schemas"]["EditingReviewCreate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/start": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/jobs/{job_id}/submit-review": {
    post: {
      parameters: {
      path: {
        "job_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/editing/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/editing/my-work": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
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
  "/api/v1/finance/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/finance/settings": {
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
    patch: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["FinanceSettingsUpdate"];
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
  "/api/v1/galleries": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "branch_id"?: string | null;
        "gallery_status"?: components["schemas"]["GalleryStatus"] | null;
        "search"?: string | null;
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
      requestBody: components["schemas"]["GalleryCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/client/{access_token}": {
    get: {
      parameters: {
      path: {
        "access_token": string;
      };
      header: {
        "authorization"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/client/{access_token}/authenticate": {
    post: {
      parameters: {
      path: {
        "access_token": string;
      };
    };
      requestBody: components["schemas"]["GalleryAuthenticateRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/client/{access_token}/favorites": {
    post: {
      parameters: {
      path: {
        "access_token": string;
      };
    };
      requestBody: components["schemas"]["FavoriteSelectionCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/client/{access_token}/favorites/{favorite_id}": {
    delete: {
      parameters: {
      path: {
        "access_token": string;
        "favorite_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/client/{access_token}/submit-selection": {
    post: {
      parameters: {
      path: {
        "access_token": string;
      };
      header: {
        "authorization"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/metrics": {
    get: {
      parameters: Record<string, never>;
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      };
    };
  };
  "/api/v1/galleries/public/{gallery_id}/authenticate": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["GalleryAuthenticateRequest"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/upgrade-requests/{request_id}/approve": {
    put: {
      parameters: {
      path: {
        "request_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/upgrade-requests/{request_id}/mark-paid": {
    put: {
      parameters: {
      path: {
        "request_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/upgrade-requests/{request_id}/reject": {
    put: {
      parameters: {
      path: {
        "request_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}": {
    get: {
      parameters: {
      path: {
        "gallery_id": string;
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
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["GalleryUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/access-token/revoke": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/access-token/rotate": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/favorites": {
    get: {
      parameters: {
      path: {
        "gallery_id": string;
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
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["FavoriteSelectionCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/favorites/{favorite_id}": {
    delete: {
      parameters: {
      path: {
        "gallery_id": string;
        "favorite_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/photos": {
    get: {
      parameters: {
      path: {
        "gallery_id": string;
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
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["GalleryPhotoCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/photos/upload": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/photos/{photo_id}": {
    delete: {
      parameters: {
      path: {
        "gallery_id": string;
        "photo_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/public": {
    get: {
      parameters: {
      path: {
        "gallery_id": string;
      };
      header: {
        "authorization"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/public/favorites": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["FavoriteSelectionCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/public/favorites/{favorite_id}": {
    delete: {
      parameters: {
      path: {
        "gallery_id": string;
        "favorite_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/public/submit-selection": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
      header: {
        "authorization"?: string | null;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/reopen-selection": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/submit-selection": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/upgrade-request": {
    post: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: components["schemas"]["GalleryUpgradeRequestCreate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/galleries/{gallery_id}/upgrade-requests": {
    get: {
      parameters: {
      path: {
        "gallery_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/invoices": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "branch_id"?: string | null;
        "invoice_status"?: components["schemas"]["InvoiceStatus"] | null;
        "booking_id"?: string | null;
        "family_id"?: string | null;
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
      requestBody: components["schemas"]["InvoiceCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/invoices/{invoice_id}": {
    get: {
      parameters: {
      path: {
        "invoice_id": string;
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
        "invoice_id": string;
      };
    };
      requestBody: components["schemas"]["InvoiceUpdate"];
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/invoices/{invoice_id}/issue": {
    post: {
      parameters: {
      path: {
        "invoice_id": string;
      };
    };
      requestBody: never;
      responses: {
      "200": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/invoices/{invoice_id}/void": {
    post: {
      parameters: {
      path: {
        "invoice_id": string;
      };
    };
      requestBody: never;
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
  "/api/v1/organizations/onboard": {
    post: {
      parameters: Record<string, never>;
      requestBody: components["schemas"]["OrganizationOnboardingCreate"];
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
  "/api/v1/organizations/{organization_id}/activate": {
    post: {
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
  "/api/v1/organizations/{organization_id}/deactivate": {
    post: {
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
  "/api/v1/organizations/{organization_id}/settings": {
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
      requestBody: components["schemas"]["OrganizationSettingsUpdate"];
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
  "/api/v1/payments": {
    get: {
      parameters: {
      query: {
        "page"?: number;
        "page_size"?: number;
        "branch_id"?: string | null;
        "payment_status"?: components["schemas"]["PaymentStatus"] | null;
        "payment_method"?: components["schemas"]["PaymentMethod"] | null;
        "invoice_id"?: string | null;
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
      requestBody: components["schemas"]["PaymentCreate"];
      responses: {
      "201": components["schemas"]["APIResponse"];
      "422": components["schemas"]["HTTPValidationError"];
      };
    };
  };
  "/api/v1/payments/{payment_id}": {
    get: {
      parameters: {
      path: {
        "payment_id": string;
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

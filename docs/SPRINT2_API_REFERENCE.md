# Sprint 2 API Reference

All endpoints use the existing `/api/v1` prefix and response envelope.

## Families

### POST `/api/v1/families`

Creates a family.

Required permission: `families:write`

Body: `FamilyCreate`

Returns: created family.

### GET `/api/v1/families`

Lists families with pagination, search, and filters.

Required permission: `families:read`

Query params:

- `page`
- `page_size`
- `search`
- `status`
- `source`
- `branch_id`
- `edd_from`
- `edd_to`

Returns: family list plus pagination metadata.

### GET `/api/v1/families/search`

Searches families by one of the supported lookup fields.

Required permission: `families:read`

Query params:

- `name`
- `phone`
- `email`
- `family_code`
- `page`
- `page_size`

### GET `/api/v1/families/{family_id}`

Returns a single family aggregate.

Required permission: `families:read`

### PUT `/api/v1/families/{family_id}`

Updates a family profile and owned child collections.

Required permission: `families:write`

Body: `FamilyUpdate`

### DELETE `/api/v1/families/{family_id}`

Soft-deletes a family.

Required permission: `families:delete`

## Generated Frontend Types

OpenAPI generation writes to:

- `frontend/src/types/generated/openapi.ts`
- `frontend/src/types/generated/openapi-schema.json`

Family request payloads use generated schemas:

- `FamilyCreate`
- `FamilyUpdate`
- `FamilyAddressCreate`
- `FamilyMemberCreate`
- `ServiceInterestCreate`

# Sprint 2 Database Design

## Tables

### families

Stores the family CRM aggregate root.

Key fields:

- `id`
- `organization_id`
- `branch_id`
- `family_code`
- `primary_contact_name`
- `primary_contact_phone`
- `primary_contact_email`
- `partner_name`
- `partner_phone`
- `partner_email`
- `city`
- `expected_delivery_date`
- `source`
- `status`
- `notes`
- `deleted_at`
- `created_at`
- `updated_at`

Constraints:

- Unique `family_code`
- Unique `primary_contact_phone`
- Composite FK from `(branch_id, organization_id)` to `(branches.id, branches.organization_id)`

Indexes:

- `family_code`
- `primary_contact_phone`
- `primary_contact_email`
- `status`
- `source`
- `expected_delivery_date`
- `created_at`
- `branch_id`

### family_members

Owned child records for people connected to a family.

### family_addresses

One address per family, enforced by a unique `family_id`.

### family_tags

Reusable tags for future segmentation.

### family_tag_mappings

Many-to-many mapping between families and tags.

### service_interests

Owned child records for requested services such as maternity, newborn, milestone, and family shoots.

## Migrations

Sprint 2 adds:

- `backend/alembic/versions/202606100004_create_family_domain.py`

PostgreSQL deployments also create `family_code_seq`, used by the backend to allocate monotonic family codes.

## Modeling Notes

The current phone uniqueness rule is global because the product requirement states no duplicate families. If multi-country duplicate phone formats become valid later, replace this with normalized E.164 storage and a scoped uniqueness policy.

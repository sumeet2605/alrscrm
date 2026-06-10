# Domain Model Review

Reviewed documents:

- `docs/Family_Aggregate_Diagram.md`
- `docs/Domain_Event_Map.md`

Note: these exact filenames were not present at review start. The closest
existing document was `docs/FAMILY_AGGREGATE_AND_EVENTS.md`; the requested
canonical files were created and validated against the implementation.

Validated against:

- Sprint 1 Identity and Access implementation
- Sprint 2 Family implementation
- Alembic migrations through `202606100004`
- Current `/api/v1` route contracts
- Current SQLAlchemy models and service-layer audit calls

## Critical Findings

1. The previous combined diagram treated several future domain events as if they were implemented. The current code only writes audit events to `audit_logs`; there is no domain event outbox or event bus.
2. `FamilyTag` was visually close to the Family aggregate but does not belong inside it. It is a reusable taxonomy entity with its own table and should remain outside the Family aggregate boundary.
3. Sprint 1 aggregates were missing from the event map. Authentication, Organization, Branch, and User services already emit audit events and must be represented when reviewing event ownership.
4. Family child collection changes are not independently observable. Member, address, service interest, status, and EDD changes are currently collapsed into `family.updated`.
5. API contracts use a generic `APIResponse`, so generated frontend OpenAPI read types do not fully represent the response payloads. This is a contract documentation and tooling limitation, not a separate domain requirement.

## Recommended Changes

- Keep `Family`, `FamilyMember`, `FamilyAddress`, and `ServiceInterest` inside the Family aggregate.
- Keep `Organization`, `Branch`, `User`, `Role`, `Permission`, `RefreshTokenSession`, `AuditLog`, and `FamilyTag` outside the Family aggregate.
- Use `docs/Family_Aggregate_Diagram.md` as the canonical aggregate diagram.
- Use `docs/Domain_Event_Map.md` as the canonical implementation-accurate event map.
- Label current events as audit events until an outbox or message bus exists.
- Avoid documenting unimplemented granular events as current behavior.
- If granular event tracking is later implemented, derive it from actual aggregate mutations rather than adding separate child-resource APIs prematurely.

## Aggregate Boundaries

| Aggregate Or Entity | Current Boundary | Validation |
| --- | --- | --- |
| `Organization` | Identity aggregate | Sprint 1 model, routes, service, and audit events exist. |
| `Branch` | Identity aggregate | Sprint 1 model, routes, service, and branch scoping exist. |
| `User` | Identity aggregate | Sprint 1 model, routes, service, roles, and deactivation exist. |
| `Role` | Identity aggregate/reference | Read API exists; permissions assigned through seed/service behavior. |
| `Permission` | Identity reference | Read API exists; seeded permission catalog. |
| `RefreshTokenSession` | Authentication aggregate/entity | Token rotation and revocation implemented. |
| `AuditLog` | Audit entity | Shared audit persistence, not a business aggregate. |
| `Family` | Family aggregate root | Sprint 2 model, routes, service, RBAC, and migration exist. |
| `FamilyMember` | Family-owned entity | Child collection owned by Family. |
| `FamilyAddress` | Family-owned entity | One address per Family. |
| `ServiceInterest` | Family-owned entity | Child collection owned by Family. |
| `FamilyTag` | Separate taxonomy entity | Table exists, but no API or lifecycle service exists yet. |
| `FamilyTagMapping` | Association | Join table between Family and reusable tags. |

## Event Ownership

| Owner | Implemented Events |
| --- | --- |
| Authentication | `auth.login_failed`, `auth.login_succeeded`, `auth.refresh_rotated`, `auth.logout` |
| Identity: Organization | `organization.created`, `organization.updated`, `organization.deactivated` |
| Identity: Branch | `branch.created`, `branch.updated`, `branch.deactivated` |
| Identity: User | `user.created`, `user.updated`, `user.deactivated` |
| Family | `family.created`, `family.updated`, `family.deleted` |

Not currently implemented as discrete events:

- `FamilyMemberAdded`
- `FamilyAddressUpdated`
- `ServiceInterestAdded`
- `FamilyStatusChanged`
- `ExpectedDeliveryDateChanged`
- `FamilyTagAssigned`

## Missing Aggregates

The reviewed diagram was missing implemented Sprint 1 boundaries:

- Authentication session/token boundary through `RefreshTokenSession`.
- Identity boundaries for `Organization`, `Branch`, `User`, `Role`, and `Permission`.
- Audit boundary through `AuditLog`.

No booking, session, invoice, gallery, editing, or delivery aggregate exists in the current implementation.

## Missing Domain Events

Against the current implementation, the missing documented events were the Sprint 1 audit events listed above. Against the desired finer-grained Family domain, there are also no discrete events for child collection or status transitions; the implementation intentionally records only `family.updated`.

## Future Scalability Risks

- No outbox means audit writes cannot safely drive asynchronous workflows.
- `family.updated` is too coarse for future scheduling, notifications, or marketing automation consumers.
- Child collections are replaced wholesale, which is simple but makes field-level history and event derivation harder.
- Global `primary_contact_phone` uniqueness may become restrictive if tenant-specific duplicate handling is needed.
- Global `family_code` sequence is simple but not tenant-specific.
- `FamilyTag` has tables but no API/service ownership yet, so taxonomy growth is not governed.
- Generic API response typing weakens generated frontend read contracts.

## DDD Principle Violations

- Domain behavior is mostly in services and repositories; SQLAlchemy models are data-centric and do not expose aggregate methods.
- Audit event recording is manually called from application services rather than emitted from aggregate state transitions.
- `FamilyUpdate` replaces nested child collections directly, which can obscure domain intent such as adding a member versus correcting a member.
- `FamilyTagMapping` exists at the persistence layer without an application service or aggregate policy.

## Entities That Do Not Belong In The Family Aggregate

- `Organization`
- `Branch`
- `User`
- `Role`
- `Permission`
- `RefreshTokenSession`
- `AuditLog`
- `FamilyTag`

These entities have separate lifecycle, ownership, or reuse concerns and should remain outside the Family aggregate.

## Future Sprint Impacts

- Booking and session modules should reference `families.id`, not duplicate customer profile fields.
- Activity timeline work should read from `audit_logs` or a future outbox-backed event stream.
- Notification or automation work should not rely on audit rows as a durable integration event stream without adding outbox semantics.
- Tag management should be introduced as a separate taxonomy capability before exposing tag assignment workflows.
- If future modules need status-specific behavior, they will need either granular domain events or explicit status transition methods.

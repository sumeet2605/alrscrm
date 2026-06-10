# Sprint 6 Technical Debt

## Backend

- Replace deprecated `datetime.utcnow()` usage in gallery tests.
- Add startup validation for editing permissions and reference seed data.
- Add explicit branch-crossing EditingJob tests.
- Add negative tests for assignment to inactive users and users without the
  `Editor` role.
- Consider database check constraints for allowed editing priority, editing
  status, and review status values.
- Keep audit events separate from future integration events until an outbox is
  introduced.

## Frontend

- Split the production bundle with route-level lazy loading.
- Remove the existing Ant Design `act(...)` warning in
  `DashboardLayout.test.tsx`.
- Expand `EditingJobDetailPage` tests for assign, start, submit review, approve,
  and reject modal flows.
- Replace remaining manual Sprint 6 DTOs with generated OpenAPI-derived types
  where the generic API envelope allows practical use.
- Add richer empty-state messaging to production tables when filtered results
  are empty.

## Documentation

- Keep `docs/SPRINT6_API_REFERENCE.md` in sync with generated OpenAPI contracts.
- Update release notes when Delivery Management is introduced in a later
  sprint.

## Deferred By Design

These are not Sprint 6 debt because they were explicitly out of scope:

- Delivery
- Payments
- Invoices
- WhatsApp
- AI
- Outbox or event bus

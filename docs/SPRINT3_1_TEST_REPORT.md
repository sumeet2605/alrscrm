# Sprint 3.1 Test Report

## Backend Tests

Command:

```bash
cd backend
python -m pytest
```

Result:

```text
25 passed, 1 warning
```

Coverage added:

- Cross-tenant overdue follow-up aging isolation
- Cross-branch overdue follow-up aging isolation
- Pipeline response above 100 opportunities
- KPI exclusion of follow-ups from deleted opportunities
- Database probability constraint
- Database LOST-stage lost reason constraint

Existing coverage retained:

- Opportunity create/list/pipeline
- Follow-up create/list/update
- Metrics
- Stage history
- LostReason validation
- BOOKED read-only service behavior
- Sales RBAC write/delete/read rules

## Frontend Type Check

Command:

```bash
cd frontend
npm run lint
```

Result:

```text
Passed
```

## Frontend Tests

Command:

```bash
cd frontend
npm run test
```

Result:

```text
6 test files passed
9 tests passed
```

Coverage added:

- Opportunity detail edit workflow submits an update payload.
- Dragging an opportunity to `LOST` opens LostReason modal and submits
  `lost_reason_id` with optional notes.

## Frontend Build

Command:

```bash
cd frontend
npm run build
```

Result:

```text
Passed
```

Note:

- Vite still reports a large bundle warning. This is not a Sprint 3.1
  correctness failure; future code splitting should address it.

## Validation Summary

| Area | Result |
| --- | --- |
| Cross-tenant FollowUp mutation | Passed |
| Cross-branch FollowUp mutation | Passed |
| Pipeline over 100 records | Passed |
| KPI deleted-opportunity exclusion | Passed |
| LostReason workflow | Passed |
| Opportunity edit workflow | Passed |
| Database probability guard | Passed |
| Database LOST-stage guard | Passed |
| BOOKED read-only service behavior | Passed |

# Frontend Architecture

## Overview

The Sprint 1 frontend is a React, TypeScript, Vite, Ant Design, TanStack Query,
React Router, and Axios application for ALRSCRM Identity & Access.

The app is desktop-first, responsive for mobile, and integrates with the
existing `/api/v1` backend endpoints. It uses the seeded local super admin
account for first login:

- Email: `admin@admin.com`
- Password: `Admin@123`

## Folder Structure

- `frontend/src/app`: root app composition and React Query client.
- `frontend/src/api`: Axios client and backend API modules.
- `frontend/src/routes`: route definitions, protected route, and role rules.
- `frontend/src/layouts`: authenticated dashboard shell.
- `frontend/src/pages`: top-level route pages such as login.
- `frontend/src/modules`: domain feature modules.
- `frontend/src/components`: shared UI components.
- `frontend/src/hooks`: reusable React hooks.
- `frontend/src/contexts`: auth session context.
- `frontend/src/types`: shared TypeScript contracts.
- `frontend/src/utils`: local utilities such as token storage.
- `frontend/src/theme`: Ant Design theme tokens.
- `frontend/src/test`: frontend test setup and render helpers.

## Auth Flow

1. Login submits email and password to `POST /api/v1/auth/login`.
2. Access and refresh tokens are stored in local storage.
3. `GET /api/v1/auth/me` restores the session on page refresh.
4. Axios attaches the access token to API requests.
5. A `401` response triggers a single refresh request to
   `POST /api/v1/auth/refresh`.
6. Logout calls `POST /api/v1/auth/logout`, clears tokens, and returns to login.

## Routing

- `/login`: public login page.
- `/dashboard`: owner/manager/staff dashboard.
- `/branches`: branch management.
- `/users`: user management.
- `/roles`: read-only role and permission management.

Role routing:

- Owner: Dashboard, Branches, Users, Roles.
- Branch Manager: Dashboard, Users.
- Sales Executive: Dashboard.
- Photographer: Dashboard.
- Editor: Dashboard.
- Customer Success: Dashboard.
- Super Admin: Dashboard, Branches, Users, Roles.

## API Integration

The API layer preserves backend response envelopes:

```ts
interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data: T;
  meta?: PaginationMeta;
}
```

Integrated endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET|POST|PATCH|DELETE /api/v1/branches`
- `GET|POST|PATCH|DELETE /api/v1/users`
- `GET /api/v1/roles`

## Theme

Ant Design is configured with ALRSCRM theme tokens:

- Primary: `#6A4C93`
- Secondary accent: `#C8A2C8`
- Success: `#52C41A`
- Warning: `#FAAD14`
- Error: `#FF4D4F`
- Background: `#F7F8FC`

The UI uses restrained cards, dense tables, and a dark left navigation shell to
match a premium SaaS operating-system surface.

## Testing

Vitest and Testing Library cover:

- Login submit and error states.
- Protected route redirects and owner access.
- User management rendering from the API layer.

Commands:

```bash
cd frontend
npm run lint
npm run test
npm run build
```

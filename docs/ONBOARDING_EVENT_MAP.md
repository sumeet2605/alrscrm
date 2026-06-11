# Onboarding Event Map

Sprint 8 uses audit-backed events only. No outbox or event bus is introduced.

## Audit Events

| Event | Owner | Trigger |
| --- | --- | --- |
| `organization.created` | Organization | Organization CRUD create endpoint. |
| `organization.updated` | Organization | Organization details update. |
| `organization.activated` | Organization | Organization activation endpoint. |
| `organization.deactivated` | Organization | Organization deactivation endpoint. |
| `organization.onboarded` | Organization | Transactional onboarding command. |
| `organization.settings_updated` | Organization | Organization settings update. |

## Future Integration Events

If a future outbox is added, candidate integration events are:

- `OrganizationOnboarded`
- `OrganizationActivated`
- `OrganizationDeactivated`
- `OrganizationSettingsUpdated`

Until then, these are not asynchronous events.


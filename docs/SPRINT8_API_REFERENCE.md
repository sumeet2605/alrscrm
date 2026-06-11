# Sprint 8 API Reference

Base path:

```text
/api/v1
```

## Organization Management

### List Organizations

```text
GET /organizations
```

Permission:

```text
organizations:view
```

### Create Organization

```text
POST /organizations
```

Permission:

```text
organizations:create
```

Creates an Organization and default Organization Settings.

### Onboard Organization

```text
POST /organizations/onboard
```

Permission:

```text
organizations:onboard
```

Request:

```json
{
  "organization": {
    "name": "Alluring Lens Studios",
    "code": "ALS",
    "timezone": "Asia/Kolkata",
    "email": "hello@alluringlens.com",
    "phone": "+91 90000 00000"
  },
  "branch": {
    "name": "Main Studio"
  },
  "owner": {
    "name": "Studio Owner",
    "email": "owner@alluringlens.com",
    "phone": "+91 90000 00001"
  }
}
```

Creates:

- Organization
- Organization Settings
- Default Branch
- Owner User
- Owner role assignment

The response includes a one-time owner temporary password.

### Get Organization

```text
GET /organizations/{organization_id}
```

Permission:

```text
organizations:view
```

### Update Organization

```text
PATCH /organizations/{organization_id}
```

Permission:

```text
organizations:update
```

### Activate Organization

```text
POST /organizations/{organization_id}/activate
```

Permission:

```text
organizations:update
```

### Deactivate Organization

```text
POST /organizations/{organization_id}/deactivate
```

Permission:

```text
organizations:deactivate
```

Legacy delete route remains available:

```text
DELETE /organizations/{organization_id}
```

## Organization Settings

### Get Settings

```text
GET /organizations/{organization_id}/settings
```

Permission:

```text
organizations:view
```

### Update Settings

```text
PATCH /organizations/{organization_id}/settings
```

Permission:

```text
organizations:update
```

Fields:

- Studio Name
- Logo URL
- Contact Email
- Contact Phone
- Website
- Address
- Timezone
- Currency
- Delivery Expiry Default
- Gallery Selection Default Limit


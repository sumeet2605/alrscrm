# PBOS Target Model

**Created:** 2026-06-13  
**Architecture Review:** CTO, Principal Software Architect, Product Architect, DDD Expert

---

## PBOS Vision: Photography Business Operating System

A comprehensive SaaS platform designed to increase bookings from 6/month to 15+/month using the same lead volume through automated workflows, intelligent pipeline management, and end-to-end fulfillment automation.

---

## Core Entities & Aggregates

### Tier 1: Foundational (Always Required)

#### Organizations & Hierarchy
```
Organization (Aggregate Root)
├─ Branches (child collection)
├─ Configuration & Branding
└─ Subscription & Billing
```

**Characteristics:**
- Multi-tenant root boundary
- Supports multiple physical locations
- Branch-scoped RBAC
- Independent databases (future consideration)

#### Users & Authentication
```
User (Aggregate Root)
├─ Roles (child collection)
├─ Permissions (derived from roles)
├─ Authentication Sessions
├─ API Keys (future)
└─ Audit Log (shared)
```

**Characteristics:**
- Multi-role support per user
- Session management with refresh tokens
- Deactivation (soft delete) support
- Password policies and hashing

#### Clients (Aggregate Root)
```
Client (renamed from Family)
├─ Contact Information
├─ Members (family members or contacts)
├─ Addresses (multiple)
├─ Service Interests (past/future bookings)
├─ Communication Preferences
├─ Tags & Taxonomy
└─ Status & Lifecycle
```

**Characteristics:**
- Single source of customer truth
- No duplication across sales/bookings/galleries
- Searchable and filterable
- Timeline of interactions

---

### Tier 2: Sales & Booking Lifecycle

#### Projects (Aggregate Root, renamed from Booking)
```
Project (Aggregate Root)
├─ Client Reference (family_id)
├─ Opportunity Reference (sales conversion source)
├─ Services & Packages
│  ├─ Base Package
│  └─ Add-ons (optional upgrades)
├─ Project Items (deliverable line items)
├─ Scheduling
│  ├─ Shoot Sessions
│  └─ Team Assignments
├─ Payments & Invoicing
├─ Project Status Workflow
└─ Timeline & History
```

**Characteristics:**
- Post-booking fulfillment vehicle
- Aggregates all work for one client engagement
- Package-based pricing
- Multi-shoot support
- Status-driven workflows

#### Leads (CRM Contact Records)
```
Lead (Aggregate Root)
├─ Source (Instagram, referral, etc.)
├─ Contact Information
├─ Service Interest
├─ Communication Log (WhatsApp, SMS, email)
├─ Tags
└─ Lead Status (Active, Lost, Converted)
```

**Characteristics:**
- Pre-client prospect
- Converted to Client when booking occurs
- Integrated communication history
- Source tracking for marketing ROI

#### Opportunities (Aggregate Root)
```
Opportunity (Aggregate Root)
├─ Client Reference
├─ Lead Reference (optional for existing clients)
├─ Pipeline Stage
├─ Follow-ups (child collection)
├─ Estimated Value
├─ Probability
├─ Expected Booking Date
├─ Lost Reason (if applicable)
└─ Notes & Activity
```

**Characteristics:**
- Sales pipeline tracking
- Conversion metrics
- Follow-up governance
- Read-only when converted (BOOKED)

---

### Tier 3: Production & Fulfillment

#### Shoots (Project Work Sessions)
```
Shoot (Child of Project)
├─ Scheduled Date & Time
├─ Location
├─ Team Assignments
│  ├─ Assigned Photographer
│  └─ Assigned Assistants
├─ Session Notes
├─ Actual Duration
└─ Status (Scheduled, Completed, Cancelled)
```

**Characteristics:**
- Part of Project lifecycle
- Resource scheduling
- Team coordination
- Time tracking

#### Tasks & Milestones (Workflow Items)
```
Task (Child of Project)
├─ Task Type (Shoot, Editing, QC, Delivery)
├─ Assigned User
├─ Due Date
├─ Priority
├─ Status
└─ Notes

Milestone (Project Phase)
├─ Milestone Name
├─ Target Date
├─ Dependent Tasks
└─ Status
```

**Characteristics:**
- Workflow management
- Dependency tracking
- Team accountability

#### Galleries (Aggregate Root)
```
Gallery (Aggregate Root)
├─ Project & Shoot Reference
├─ Photos & Metadata
├─ Selection Governance
│  ├─ Selection Limit
│  ├─ Selection Deadline
│  ├─ Password Protection
│  ├─ Expiration
│  └─ Download & Watermark Settings
├─ Client Selection State
├─ Selections (child collection)
└─ Delivery Status
```

**Characteristics:**
- Client-facing portal
- Customizable access rules
- Photo selection workflow
- Watermark and download controls

#### Editing & QC (Aggregate Root)
```
EditingJob (Aggregate Root)
├─ Gallery Reference
├─ Assigned Editor
├─ Editing Status (Pending → In Progress → Review → Approved → Ready)
├─ Photo Progress Tracking
├─ Review Feedback
├─ Due Date & TAT
└─ Notes & Revision History
```

**Characteristics:**
- Post-selection fulfillment
- Editor assignment
- Quality control workflow
- Turnaround time management
- Revision support

#### Deliverables (Aggregate Root)
```
Deliverable (Aggregate Root)
├─ Gallery Reference
├─ Project Reference
├─ Edited Photos & Assets
├─ Delivery Method (Download, Print, USB)
├─ Client Access
├─ Download History
├─ Proof of Delivery
└─ Delivery Status
```

**Characteristics:**
- Final client fulfillment
- Multi-format support (digital, print, physical)
- Download tracking
- Proof of completion

---

### Tier 4: Finance & Operations

#### Finance (Aggregate Root)
```
Finance (Aggregate Root)
├─ Payments
│  ├─ Amount
│  ├─ Payment Method
│  ├─ Status (Pending, Completed, Failed, Refunded)
│  ├─ Transaction ID
│  ├─ Payment Date
│  └─ Gateway Metadata
├─ Invoices
│  ├─ Invoice Number
│  ├─ Line Items (from Project)
│  ├─ Subtotal, Tax, Total
│  ├─ Due Date
│  ├─ Terms
│  └─ Payment Schedule
├─ Quotes
│  ├─ Quote Items
│  ├─ Validity Period
│  ├─ Conversion to Invoice
│  └─ Expiry
└─ Financial Reporting
```

**Characteristics:**
- Payment processing integration
- Multi-payment support per project
- Invoice generation
- Tax handling
- Refund management

#### Operations (Aggregate Root)
```
Operations (Aggregate Root)
├─ Resources & Capacity
│  ├─ Team Members
│  ├─ Equipment & Studio
│  └─ Availability Calendar
├─ Scheduling & Allocation
│  ├─ Workload Balance
│  ├─ Capacity Planning
│  └─ Resource Conflicts
├─ Fulfillment Pipeline
├─ Quality Metrics
└─ Operational Analytics
```

**Characteristics:**
- Capacity planning
- Resource optimization
- Workload distribution
- Fulfillment visibility

---

### Tier 5: Marketing & Communications

#### Communications (Aggregate Root)
```
Communications (Aggregate Root)
├─ WhatsApp Integration
│  ├─ Message Template
│  ├─ Broadcast
│  └─ Automation
├─ Email Templates & Campaigns
├─ SMS Support
├─ Notification Preferences
├─ Message History & Audit
└─ Two-Way Conversation
```

**Characteristics:**
- Client engagement
- Automated workflows
- Multi-channel support
- Message tracking

#### Marketing (Aggregate Root)
```
Marketing (Aggregate Root)
├─ Referral Program
├─ Campaign Management
├─ Email Automation
├─ Social Media Scheduling (future)
├─ Lead Attribution
└─ Marketing ROI Tracking
```

**Characteristics:**
- Customer acquisition
- Retention programs
- Marketing analytics
- Lead source tracking

---

### Tier 6: Intelligence & Integration

#### Analytics & Reporting (Aggregate Root)
```
Analytics (Aggregate Root)
├─ Business Dashboards
│  ├─ Revenue
│  ├─ Bookings
│  ├─ Conversion Rate
│  └─ Pipeline Health
├─ Operational Dashboards
│  ├─ Team Workload
│  ├─ Project Status
│  ├─ Editing TAT
│  └─ Fulfillment Progress
├─ Custom Reports
├─ Export & Scheduling
└─ KPI Tracking
```

**Characteristics:**
- Real-time dashboards
- Drill-down analysis
- Custom reports
- Scheduled delivery

#### Integrations (Aggregate Root)
```
Integrations (Aggregate Root)
├─ Payment Gateways
│  ├─ Stripe
│  ├─ Square
│  └─ PayPal
├─ Cloud Storage
│  ├─ DigitalOcean Spaces
│  ├─ Google Drive
│  └─ Dropbox
├─ Calendar Systems
│  ├─ Google Calendar
│  └─ Outlook
├─ Email Service Providers
└─ Webhook Support
```

**Characteristics:**
- Third-party connections
- Webhook webhooks
- API authentication
- Sync management

#### AI & Automation (Aggregate Root)
```
AI (Aggregate Root)
├─ Photo Enhancement
│  ├─ Auto-Tagging
│  ├─ Background Removal
│  └─ Enhancement Suggestions
├─ Workflow Automation
│  ├─ Rule-Based Triggers
│  ├─ Smart Routing
│  └─ Auto-Assignment
├─ Predictive Analytics
│  ├─ Lead Scoring
│  ├─ Churn Prediction
│  └─ Opportunity Forecasting
└─ Natural Language Processing
```

**Characteristics:**
- Machine learning models
- Photo processing
- Workflow automation
- Predictive insights

---

### Tier 7: Extensions & Future

#### Mobile (Future Aggregate Root)
```
Mobile (Aggregate Root)
├─ Photographer App
│  ├─ Schedule View
│  ├─ Photo Upload
│  └─ Client Proofing
├─ Client App
│  ├─ Gallery Access
│  ├─ Photo Selection
│  └─ Status Tracking
└─ Push Notifications
```

**Characteristics:**
- Native mobile experiences
- Field photographers
- Real-time notifications

#### Subscriptions & Billing (Future Aggregate Root)
```
Subscriptions (Aggregate Root)
├─ Subscription Plans
├─ Metered Usage
├─ Billing Cycles
├─ Payment Methods
└─ Invoicing & Reporting
```

**Characteristics:**
- Recurring billing
- Usage-based pricing
- Plan management
- Billing history

#### Workflow Engine (Future Aggregate Root)
```
WorkflowEngine (Aggregate Root)
├─ Workflow Builder (No-Code)
├─ Workflow Definitions
├─ Execution History
├─ Task Routing
├─ Conditional Logic
└─ Integration Triggers
```

**Characteristics:**
- Low-code automation
- Process customization
- Audit trails
- Extensibility

---

## Data Architecture Principles

### 1. Aggregate Boundaries
- Each aggregate is independently addressable
- Customer profile (Client) is never duplicated
- References use IDs, not denormalization
- Ownership is explicit and enforced

### 2. Multi-Tenancy
- Organization is the top-level scope
- Branch extends organization scope
- All records include `organization_id` and `branch_id`
- Row-level security (RLS) supported at database layer

### 3. Soft Delete & Audit
- All transactional records support soft delete
- Audit log captures all changes
- Historical data remains queryable
- Compliance-ready for data retention

### 4. Idempotency
- All mutations are idempotent
- External API calls include idempotency keys
- Retry-safe by design
- State reconciliation supported

### 5. Time-Series Data
- Timestamps on all records
- Event-driven state transitions
- History preserved for analysis
- Audit trail immutable

---

## API Architecture

### Response Envelope (Consistent Across All APIs)
```json
{
  "success": boolean,
  "message": string,
  "data": T,
  "meta": {
    "page": number,
    "page_size": number,
    "total": number,
    "pages": number,
    "timestamp": ISO8601
  }
}
```

### Authentication
- JWT access tokens (short-lived)
- Refresh tokens (long-lived, rotated)
- Session persistence in database
- Token revocation on logout

### Authorization
- Role-based access control (RBAC)
- Resource-based policies
- Tenant scoping
- Branch scoping
- Audit logging for all access

### Versioning
- `/api/v1/` prefix for current version
- Backward compatibility maintained
- Deprecation warnings in headers
- Migration guides provided

---

## Frontend Architecture

### Core Technologies
- React 18+ with TypeScript
- Component-based architecture
- State management (TanStack Query for server state)
- Responsive design (mobile-first)
- Accessibility (WCAG 2.1 AA)

### Core Modules
1. **Identity** - Login, user management, roles
2. **CRM** - Client management, contact history
3. **Sales** - Pipeline board, opportunities, follow-ups
4. **Booking** - Project management, scheduling
5. **Production** - Gallery upload, editing, QC
6. **Delivery** - Client portal, downloads, proof
7. **Finance** - Invoices, payments, receipts
8. **Operations** - Dashboards, capacity planning
9. **Admin** - Settings, team management, integrations

### Design System
- Consistent component library
- Theming & branding support
- Accessibility built-in
- Responsive layouts

---

## Database Schema Strategy

### Core Tables (Always Present)
- `organizations`
- `branches`
- `users`
- `roles`
- `permissions`
- `audit_logs`

### Domain Tables (By Context)
- **CRM:** `clients`, `client_members`, `client_addresses`, `client_tags`, `client_timeline`
- **Sales:** `opportunities`, `followups`, `lost_reasons`, `opportunity_history`
- **Booking:** `projects`, `project_items`, `shoots`, `team_assignments`
- **Gallery:** `galleries`, `gallery_photos`, `selections`, `gallery_access`
- **Editing:** `editing_jobs`, `editing_reviews`, `editing_feedback`
- **Delivery:** `deliverables`, `download_tracking`, `delivery_proof`
- **Finance:** `payments`, `invoices`, `quotes`, `invoice_lines`
- **Integrations:** `integration_configs`, `webhook_logs`, `api_keys`

### Indexing Strategy
- Foreign key columns indexed
- Tenant + branch queries indexed
- Status columns indexed
- Date range queries indexed
- Full-text search support for names/descriptions

---

## Security & Compliance

### Authentication
- Password hashing (Argon2id or bcrypt)
- Password policies enforced
- Rate limiting on login
- Account lockout after failed attempts
- Session management with expiry

### Authorization
- Multi-tenant isolation enforced
- Branch-scoped access
- Role-based permissions
- Resource ownership validation
- Audit logging for all access decisions

### Data Protection
- Encryption at rest (database)
- Encryption in transit (TLS)
- PII masking in logs
- GDPR compliance support
- Data retention policies

### Compliance
- Audit trail immutable
- Access logs retained
- Change tracking enabled
- Compliance reports available

---

## Performance & Scalability

### Caching Strategy
- Query caching for reference data (roles, permissions)
- API response caching
- Client-side state management
- CDN for static assets

### Database Optimization
- Connection pooling
- Query optimization
- Index tuning
- Partitioning strategy (by organization)

### API Optimization
- Pagination on all list endpoints
- Filtering and sorting
- Lazy loading for relationships
- GraphQL readiness (future)

### Frontend Optimization
- Code splitting by route
- Lazy loading components
- Image optimization
- Bundle size monitoring

---

## Deployment Architecture

### Local Development
- Docker Compose with all services
- Seeded demo data
- Hot reload for development

### Staging
- Multi-tenant test data
- Performance monitoring
- Security scanning

### Production
- Kubernetes or serverless
- Auto-scaling
- High availability
- Disaster recovery
- CDN integration

---

## Success Metrics

### Business Metrics
- Bookings increased from 6 to 15+ per month
- Conversion rate improved
- Client satisfaction score
- Average project value
- Revenue per team member

### Operational Metrics
- Average turnaround time (shoot to delivery)
- Editing TAT
- Follow-up compliance
- Project on-time delivery rate

### Technical Metrics
- API response time < 200ms
- System uptime > 99.5%
- Zero unplanned downtime per month
- Audit log completeness 100%


# Photography Business Operating System (PBOS)

## Business Requirements Document (BRD) v1.0

### Vision
Run an entire photography business from a single platform.

### Target Market
- Solo photographers
- Photography studios
- Multi-branch studios
- Franchise photography brands

### Core Modules
- CRM & Lead Management
- Client Management
- Project Management
- Shoot Planning
- Resource Management
- Gallery Management
- Client Selection Portal
- Editing Workflow
- Delivery Management
- Finance & GST
- Marketing & Lead Capture
- Communication Hub
- Workflow Engine
- AI Copilot
- Analytics
- Mobile Apps
- Subscription & Billing

### Multi-Tenant Structure
Platform
 -> Organization
 -> Branch
 -> Users
 -> Projects
 -> Galleries
 -> Finance
 -> Integrations

### Roles
- Super Admin
- Organization Owner
- Branch Manager
- Sales Executive
- Photographer
- Editor
- QC Reviewer
- Accounts User
- Client

### Core Entity
Project is the primary business entity.

Project lifecycle:
Lead -> Opportunity -> Project -> Shoot -> Selection -> Editing -> QC -> Delivery -> Closure

### Lead Sources
- Website
- Meta Ads
- Instagram
- WhatsApp
- Google Business
- Referral
- Manual

### Gallery Requirements
- Multi-file upload
- Folder upload
- Resume upload
- 250+ photos per gallery
- Favorites
- Client selections
- Comments
- Downloads

### Finance
- Quotations
- Invoices
- GST
- Payments
- Receipts
- Credit Notes
- Revenue Analytics

### Integrations
Phase 1:
- WhatsApp Business
- Meta Lead Ads
- Instagram
- Google Business Profile

Phase 2:
- Gmail
- Outlook
- Razorpay
- Stripe
- Google Calendar

Phase 3:
- n8n Automation Platform

### AI Layer
Sales AI
Operations AI
Finance AI
Marketing AI

### Mobile
React Native
- iOS
- Android

### Technical Stack
Backend:
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic

Frontend:
- React
- TypeScript
- Ant Design

Storage:
- DigitalOcean Spaces

Automation:
- n8n

### Product Roadmap
Phase 1:
CRM + Projects + Galleries + Finance

Phase 2:
Integrations + Workflow Engine

Phase 3:
Mobile Applications

Phase 4:
AI Copilot Platform

### Success Criteria
A photography business should be able to operate its complete workflow from lead acquisition to payment collection and gallery delivery without leaving PBOS.
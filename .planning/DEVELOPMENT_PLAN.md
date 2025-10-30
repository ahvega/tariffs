# Development Plan: SicargaBox - Courier Quotation & Shipping Request System

## System Scope & Purpose

**Primary Goal:** Streamline client onboarding and shipping request process with instant online quotations and tracking.

**Core Workflow:**

1. **Quote** → Client enters item details, gets instant estimate
2. **Onboard** → New client registers account, existing client logs in
3. **Request** → Client accepts quote, submits shipping request with required info
4. **Track** → Point-to-point status updates available for client follow-up
5. **Liquidate & Invoice** → System produces a final liquidation and generates a PDF invoice for the staff.
6. **Payment** → Staff uses the generated invoice to request payment from the client upon package pickup.

**Out of Scope:**

- Online payment processing
- Payment gateway integration
- Automated financial reconciliation

## Current System Alignment

### ✅ Well-Aligned Features (Keep & Enhance)

**Core Models:**

- `PartidaArancelaria` - Tariff items with tax rates ✓
- `Cliente` - Client management with auto-generated codes ✓
- `Cotizacion` - Quote system ✓
- `Articulo` - Item details with tax calculations ✓
- `Envio` - Shipment tracking ✓
- `ParametroSistema` - System configuration ✓

**Functionality:**

- Quote calculator with tax computation (DAI, ISC, ISPC, ISV) ✓
- Freight cost calculation (volumetric vs actual weight) ✓
- User registration and authentication ✓
- Elasticsearch for item search ✓
- AI-powered search keyword generation ✓
- Elasticsearch for item search ✓
- AI-powered search keyword generation ✓

### ⚠️ Needs Adjustment

**Over-Engineered Features:**

- Payment status tracking - Not needed for offline payment model
- `Alerta` model - SMS/WhatsApp not critical for MVP

**Missing Features:**

- Shipping request acceptance workflow
- Detailed shipment status tracking (point-to-point updates)
- Final liquidation with actual vs estimated comparison
- Client history dashboard

### ❌ Remove/Deprioritize (Out of Scope)

- Payment gateway integration
- Online payment processing
- Payment webhooks and receipts
- Refund handling

## Revised System Flow

### 1. **Public Quote Calculator** (No Login Required)

- Anonymous users can calculate shipping costs
- Enter item description → AI suggests tariff classification
- Enter dimensions, weight, value
- Show instant breakdown: freight + taxes + total estimate
- CTA: "Create Account & Submit Shipping Request"

### 2. **Client Onboarding**

- **New Client:** Quick registration form (name, email, phone, address)
  - Auto-generate client code
  - Create credentials
  - Assign to "UsuariosClientes" group
- **Existing Client:** Simple login
- Post-login: Return to accepted quote

### 3. **Shipping Request Submission**

- Accept quote (converts to shipping request)
- Additional required info:
  - US tracking number (from retailer)
  - Purchase invoice upload (optional)
  - Delivery address confirmation
  - Special instructions (optional)
- Generate internal tracking number
- Status: "Request Submitted"

### 4. **Status Tracking** (Point-to-Point Updates)

**Status Flow:**

- `Solicitado` - Request submitted by client
- `Recibido en Miami` - Package received at Miami warehouse
- `Procesado` - Package processed and ready for shipment
- `En tránsito a Honduras` - In transit
- `En aduana` - Customs clearance
- `Liberado de aduana` - Cleared customs
- `En bodega local` - At local warehouse
- `Disponible para entrega` - Ready for pickup/delivery
- `Entregado` - Delivered to client

**Tracking Features:**

- Timeline view with timestamps
- Automated status updates (staff-triggered)
- Optional notifications (email/SMS for critical updates)
- Client-accessible tracking page (by tracking number or login)

### 5. **Final Liquidation** (Replaces Invoice)

**Purpose:** Reconcile estimated vs actual costs

**Liquidation Details:**

- Original estimate (from quote)
- Actual measurements (final weight, dimensions, volumetric weight)
- Actual freight cost (based on actual weight)
- Actual customs taxes (may differ from estimate)
- Final total amount
- Variance report (estimated vs actual)
- Status: `Liquidado` - Ready for offline payment

**Staff Workflow:**

- Update shipment with actual measurements
- System auto-calculates final costs
- Staff reviews and marks as "Liquidated"
- System generates liquidation document (PDF for internal use)

### 6. **Client History**

- View all past shipments
- Download liquidation documents
- Track current shipments
- Access quote history

## Revised Development Roadmap

### Phase 1: Backend Foundation (3-4 weeks)

This phase focuses on building the core backend functionality of the application. For a detailed breakdown of the tasks and subtasks, please refer to the following documents:

- [Public Quote Calculator & Onboarding](./PUBLIC_QUOTE_CALCULATOR_AND_ONBOARDING.md)
- [Shipment Tracking & Status Management](./SHIPMENT_TRACKING_AND_STATUS_MANAGEMENT.md)
- [Liquidation and Invoicing System](./LIQUIDATION_AND_INVOICING_SYSTEM.md)
- [x] [Data Model Changes](./DATA_MODEL_CHANGES.md)

### Phase 2: Search & AI Enhancement (Completed)

This phase, which is already complete, focused on implementing the AI-powered search and semantic matching capabilities of the application.

- [x] Consolidate AI keyword generation commands
- [x] Improve Elasticsearch fuzzy matching
- [x] Add autocomplete with highlighting
- [x] Cache frequent searches
- [x_] Multi-language keyword support (English/Spanish)
- [x] AI-powered item description → tariff matching
- [x] Confidence scoring for suggestions
- [x] Manual override option
- [x] Learning from staff corrections

### Phase 3: Elasticsearch Admin Management (1 week)

This phase focuses on creating a user-friendly interface within the Django admin for managing Elasticsearch. For a detailed breakdown of the tasks and subtasks, please refer to the [Elasticsearch Admin Management development plan](./ELASTICSEARCH_ADMIN_MANAGEMENT.md).

### Phase 4: Frontend Development (8-12 weeks)

This phase focuses on building the user interfaces for both customers and staff. For a detailed breakdown of the tasks and subtasks, please refer to the following documents:

- [Frontend Customer Portal](./FRONTEND_CUSTOMER_PORTAL.md)
- [Frontend Staff Portal](./FRONTEND_STAFF_PORTAL.md)

### Phase 5: Testing, Polish & Deployment (2-3 weeks)

This phase focuses on ensuring the quality and stability of the application before deploying it to production.

#### Week 15: Testing

- [ ] End-to-end testing (quote → liquidation flow)
- [ ] Load testing (concurrent quotes)
- [ ] Security audit
- [ ] Accessibility testing
- [ ] Cross-browser/device testing

#### Week 16: Production Setup

- [ ] Environment variables and secrets
- [ ] Redis for Channels
- [ ] Elasticsearch production cluster
- [ ] Database backups
- [ ] SSL/TLS certificates
- [ ] CDN for static assets

#### Week 17: Deployment & Monitoring

- [ ] Deploy to production server
- [ ] Setup monitoring (Sentry, logs)
- [ ] Health check endpoints
- [ ] Staff training documentation
- [ ] User manual for clients

### Phase 6: Mobile App (Optional - Future)

This phase focuses on building a mobile application for the SicargaBox platform.

- React Native or Flutter app
- Quote calculator
- Shipment tracking with push notifications
- Photo upload for invoices
- Barcode scanning for tracking numbers

## Immediate Next Steps (This Week)

### Day 1-2: Model Refactoring (Completed)

1. [x] Add new fields to `Liquidacion` model
2. [x] Update `Envio` model with enhanced status choices
3. [x] Create `StatusUpdate` model
4. [x] Update `Cotizacion` with expiration and session tracking

### Day 3-4: Quote Calculator Improvement

1. [ ] Make quote calculator publicly accessible (no login)
2. [ ] Add session-based quote storage
3. [ ] Improve UI/UX (mobile-responsive)
4. [ ] Add "Accept Quote" button → redirect to login/register

### Day 5: Testing & Documentation

1. [ ] Test new models with sample data
2. [ ] Update admin interface for new models
3. [ ] Document new workflow in README
4. [ ] Create user stories for Phase 1

## Success Metrics

### Operational KPIs

- Time to quote: < 2 minutes
- Client onboarding: < 5 minutes
- Quote acceptance rate: > 60%
- Shipment visibility: 100% of packages tracked
- Liquidation accuracy: < 5% variance

### Technical KPIs

- Quote calculator load time: < 1 second
- Search results: < 500ms
- System uptime: > 99%
- Mobile responsiveness: 100% of pages

### User Experience

- Client satisfaction: > 4.5/5
- Staff efficiency: 30% reduction in manual data entry
- Quote-to-shipment conversion: > 50%

## Out of Scope (Explicit)

❌ **Not Included:**

- Online payment processing (Stripe, PayPal, etc.)
- Automated client invoicing
- Accounting software integration
- Financial reconciliation
- Automated tax filing
- Subscription/membership systems
- Real-time customs API integration (manual for now)

✅ **What System Does:**

- Generate quotes
- Onboard clients
- Accept shipping requests
- Track shipment status
- Calculate final liquidation
- Store transaction history
- Produce documents for offline payment

## Notes

- **Language:** Primary Spanish, English secondary
- **Timezone:** America/Tegucigalpa (Honduras)
- **Currency:** USD (prices in dollars)
- **Regulations:** Honduras customs regulations
- **AI Models:** Available (OpenAI, DeepSeek, Anthropic)
- **Payment:** Staff handles offline, system tracks status only
- **Tariff Updates:** Manual import via PDF parser tool

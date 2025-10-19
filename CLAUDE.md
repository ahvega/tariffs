# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SicargaBox is a comprehensive courier quotation and shipping request system designed to streamline client onboarding and package tracking for international shipments from the US to Honduras.

**Primary Goal:** Streamline client onboarding and shipping request process with instant online quotations and tracking.

**Core Workflow:**

1. **Quote** → Client enters item details, gets instant estimate
2. **Onboard** → New client registers account, existing client logs in
3. **Request** → Client accepts quote, submits shipping request with required info
4. **Track** → Point-to-point status updates available for client follow-up
5. **Liquidate & Invoice** → System produces final liquidation and generates PDF invoice for staff
6. **Payment** → Staff handles offline payment using generated invoice upon package pickup

**Out of Scope:** Online payment processing, payment gateway integration, automated financial reconciliation

### Repository Structure

This is a monorepo with three main components:

1. **Backend (SicargaBox)**: Django-based courier control system for managing quotes, shipments, and tracking
2. **Tools (PDF Parser)**: Python utility for extracting tariff items from PDF documents
3. **Frontend/Mobile**: (Planned) Next.js customer and staff portals

## Backend: SicargaBox

### Technology Stack

- Django 5.0.2 with Django REST Framework
- PostgreSQL database
- Elasticsearch 8.17 for search functionality
- Redis/Channels for WebSocket support (currently using InMemory layer)
- Celery for background task processing (planned for Elasticsearch admin management)
- HTMX for dynamic frontend interactions
- TailwindCSS 3.4 with DaisyUI for styling
- AI integrations: OpenAI, DeepSeek, Anthropic for semantic search and keyword generation

### Development Commands

**Setup:**

```bash
cd backend/sicargabox
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Database:**

```bash
python manage.py migrate
python manage.py createsuperuser
```

**Development Server:**

```bash
python manage.py runserver
```

**Tests:**

```bash
pytest
pytest --cov  # with coverage
pytest tests/MiCasillero/test_views.py  # single test file
```

**TailwindCSS (Frontend Assets):**

```bash
cd theme/static_src
npm install
npm run dev      # watch mode for development
npm run build    # production build
```

**Code Quality:**

```bash
black .          # format code
flake8           # lint
isort .          # sort imports
mypy .           # type checking
```

**Elasticsearch Management:**

```bash
python manage.py search_index --rebuild     # rebuild entire index
python manage.py search_index --populate    # populate index
python manage.py search_index --delete      # delete index
python manage.py generate_search_keywords --api-provider=deepseek  # generate AI keywords
```

## Tools: PDF Parser

### Purpose

Extracts Partidas Arancelarias (tariff items) from PDF documents into structured CSV format.

### Commands

**Setup:**

```bash
cd tools/pdf_parser
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

**Usage:**

```bash
python src/parse_tariffs.py <pdf_filename>
```

Output includes: Partida (code), Descripción, Gravamen (tariff rate)

## Architecture

### Backend Architecture

#### **Core App: MiCasillero**

- Main business logic for the courier system
- Key models: `Cliente`, `Cotizacion`, `Articulo`, `Envio`, `Factura`, `PartidaArancelaria`, `ParametroSistema`
- Dual API approach: REST API (DRF) + HTMX views for server-side rendering
- Uses `django-guardian` for object-level permissions
- Elasticsearch documents for advanced search capabilities

**URL Structure:**

- `/api/v1/` - REST API endpoints (ViewSets)
- Standard CRUD views at model-specific URLs (e.g., `/Cliente/`, `/Cotizacion/`)
- `/htmx/` - HTMX endpoints for dynamic partial updates
- Special endpoints: `/cotizador/`, `/buscar-partidas/`, `/partida_arancelaria_autocomplete/`

**Key Models:**

- `PartidaArancelaria`: Tariff items with courier category classification (ALLOWED/RESTRICTED/PROHIBITED), restrictions, tax rates (DAI, ISC, ISPC, ISV), and AI-generated search keywords
- `Cliente`: Client management with auto-generated codes and group-based permissions
- `Cotizacion`: Quote system with expiration tracking and session-based storage for anonymous users
- `Articulo`: Item details with automatic tax calculations
- `Envio`: Shipment tracking with comprehensive status flow (see Status Tracking section)
- `StatusUpdate`: Event-sourced history of shipment status changes with timestamps
- `Factura`: Invoice/liquidation with estimated vs. actual cost comparison
- `ParametroSistema`: System-wide configuration with typed values (STRING/INTEGER/FLOAT/BOOLEAN)
- Permission system uses group-based access (Operadores, Administradores, UsuariosClientes)

**Settings:**

- Database: PostgreSQL (default: SicargaBox/postgres/honduras@localhost:5432)
- Language: Spanish (es)
- Timezone: America/Tegucigalpa
- Debug toolbar enabled on 127.0.0.1
- CORS enabled for <http://localhost:3000>

### Frontend Integration

- HTMX for dynamic interactions without full page reloads
- Django Select2 for enhanced select widgets
- TailwindCSS + DaisyUI for styling
- Theme switching support (dark/light mode via theme-change package)

### Status Tracking System

**Shipment Status Flow:**

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

- Timeline view with timestamps using `StatusUpdate` model
- Automated status updates (staff-triggered)
- Optional notifications (email/SMS for critical updates)
- Client-accessible tracking page (by tracking number or login)

### AI-Powered Search System

**Features:**

- Elasticsearch integration for fuzzy matching and autocomplete
- AI-powered semantic matching for item description → tariff classification
- Multi-language keyword support (English/Spanish)
- Confidence scoring for suggestions
- Manual override option for staff corrections
- Continuous learning from user selections via `ItemPartidaMapping` model

**AI Providers:**

- OpenAI (GPT models)
- DeepSeek (primary for keyword generation)
- Anthropic Claude (available)

**Management Commands:**

- `generate_search_keywords`: Generates AI-powered keywords for tariff items
- `search_index`: Manages Elasticsearch index (rebuild/populate/delete)

### Testing

- Uses pytest with pytest-django
- Test helpers in `test_helpers.py`
- Separate test settings in `test_settings.py`

## Development Roadmap

For detailed development plans, refer to:

- `DEVELOPMENT_PLAN.md` - Overall project roadmap and system scope
- `PUBLIC_QUOTE_CALCULATOR_AND_ONBOARDING.md` - Public quote calculator and client registration
- `SHIPMENT_TRACKING_AND_STATUS_MANAGEMENT.md` - Tracking system and status updates
- `LIQUIDATION_AND_INVOICING_SYSTEM.md` - Final cost calculation and PDF invoice generation
- `ELASTICSEARCH_ADMIN_MANAGEMENT.md` - Admin interface for Elasticsearch operations
- `FRONTEND_CUSTOMER_PORTAL.md` - Next.js customer portal (planned)
- `FRONTEND_STAFF_PORTAL.md` - Next.js staff portal (planned)

### Current Phase: Backend Foundation

**Completed:**

- ✅ Phase 2: Search & AI Enhancement (Elasticsearch, AI keyword generation)
- ✅ Data model changes (StatusUpdate, enhanced Envio, updated Cotizacion and Factura)

**In Progress:**

- Phase 1: Backend Foundation
  - Public quote calculator (anonymous access)
  - Client onboarding workflow
  - Shipment tracking system
  - Liquidation and invoicing

**Planned:**

- Phase 3: Elasticsearch Admin Management (Django admin interface for ES operations)
- Phase 4: Frontend Development (Next.js customer and staff portals)
- Phase 5: Testing, Polish & Deployment
- Phase 6: Mobile App (Optional - Future)

## Important Notes

- **Language:** Primary Spanish (es), English secondary
- **Timezone:** America/Tegucigalpa (Honduras)
- **Currency:** USD (prices in dollars)
- **Regulations:** Honduras customs regulations
- **Payment Model:** Offline payment handling by staff (no online payment integration)
- **Elasticsearch:** Must be running on localhost:9200 for search features
- **PostgreSQL:** Default credentials in `settings.py` (update for production)
- **Static Files:** Collected to `staticfiles/` directory
- **WebSocket:** Currently uses in-memory channel layer (consider Redis for production)
- **Celery:** Will be integrated for background tasks (Elasticsearch admin, keyword generation)

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

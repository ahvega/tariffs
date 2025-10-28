# Gemini Project Context: SicargaBox

This document provides a comprehensive overview of the SicargaBox project for the Gemini CLI.

## Project Overview

SicargaBox is a web and mobile application designed to streamline the process of shipping goods from the United States to Honduras. It serves as a "courier quotation and shipping request system," allowing clients to get instant online quotes, submit shipping requests, and track their packages.

The system is built with a modern technology stack, including a Django backend, a Next.js frontend, and a planned React Native mobile app. It leverages Elasticsearch for powerful search capabilities and includes AI-powered features for tariff classification and search keyword generation.

### Core Functionality

* **Instant Online Quotes:** Clients can enter item details (description, value, dimensions, weight) and receive an immediate estimate of shipping costs, including all relevant Honduran import tariffs (DAI, ISC, ISPC, ISV).
* **Client Onboarding:** New clients can register for an account, while existing clients can log in to manage their shipments.
* **Shipping Request Submission:** After accepting a quote, clients can submit a formal shipping request, providing necessary information like the US tracking number and purchase invoice.
* **Shipment Tracking:** The system provides point-to-point status updates for each shipment, from receipt at the Miami warehouse to final delivery in Honduras.
* **Final Liquidation:** Instead of traditional invoicing, the system generates a "liquidation" document that reconciles the initial estimated costs with the final actual costs, based on precise measurements and any adjustments during the shipping process.
* **Offline Payment:** The application tracks payment status, but all financial transactions are handled offline by staff.

### Technology Stack

* **Backend:** Django, with Django REST Framework for the API. Some services may use FastAPI.
* **Frontend:** Next.js
* **Mobile:** React Native (planned)
* **Database:** PostgreSQL
* **Search:** Elasticsearch
* **Real-time Communication:** Django Channels, Celery with Redis (for background tasks and real-time updates)
* **AI Integrations:** OpenAI, DeepSeek, Anthropic (for semantic search, keyword generation, and embeddings)
* **API Documentation:** OpenAPI (Swagger) generated with `drf-spectacular`.

## Building and Running the Project

### Backend (Django)

1. **Navigate to the backend directory:**

    ```powershell
    cd backend/sicargabox
    ```

2. **Activate the virtual environment:**

    ```powershell
    .\venv\Scripts\Activate.ps1
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    The backend will be available at `http://localhost:8000`.

### Frontend (Next.js)

1. **Navigate to the frontend directory:**

    ```bash
    cd frontend/
    ```

2. **Install dependencies:**

    ```bash
    npm install
    ```

3. **Run the development server:**

    ```bash
    npm run dev
    ```

    The frontend will be available at `http://localhost:3000`.

### Testing

To run the backend tests, use the following command:

```bash
pytest
```

## Development Conventions

* **API:** The project follows a standard RESTful API design, with endpoints for each of the core models (`PartidaArancelaria`, `Cliente`, `Cotizacion`, `Articulo`). The API is well-documented using OpenAPI.
* **Permissions:** The API uses a permission-based system, where staff users have access to all data, while regular users can only view their own information.
* **Search and AI:** The project uses a sophisticated hybrid search system that combines traditional keyword-based search with modern semantic search. This is powered by Elasticsearch and a custom-built AI engine.
  * **Elasticsearch:** Used for full-text search with features like fuzzy matching and a Spanish language analyzer.
  * **Semantic Search:** Item descriptions are converted into vector embeddings, which are then used to find semantically similar tariff classifications. This involves new data models like `ItemPartidaMapping` (for learning from user selections) and `PartidaArancelariaEmbedding` (for storing vector embeddings).
  * **AI-Powered Keyword Generation:** The system uses a management command (`generate_search_keywords`) to generate additional search keywords for each tariff item using AI (OpenAI or DeepSeek). These keywords enrich the search index and improve the accuracy of the keyword-based search.
  * **Continuous Learning:** The system learns from user selections and staff corrections, continuously improving its accuracy over time. This is facilitated by Celery background tasks that analyze new mappings and enrich the search index.
  * **Hierarchical Data:** The `PartidaArancelaria` data is hierarchical, with each item having a `parent_category`. However, the `partida_arancelaria` field itself is not a concatenated path of the hierarchy. The search and matching logic should take this hierarchical structure into account to provide contextually relevant results.
* **AI Integration:** The system is designed to incorporate AI for suggesting tariff classifications and generating search keywords. This is a key feature that should be maintained and enhanced.
* **HTMX:** The use of `django-htmx` suggests that some parts of the traditional Django application may use HTMX for dynamic updates without a full frontend framework. This is likely for the admin or staff-facing interfaces.
* **Modularity:** The project is organized into distinct `backend`, `frontend`, and `mobile` directories, promoting a clean separation of concerns.

## Development Plans

This project is organized into a master development plan and several detailed sub-plans for each of the major features. These documents provide a comprehensive overview of the project's roadmap, goals, and technical specifications.

* **Master Plan:** [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)

### Sub-Plans

* **Data Model:** [DATA_MODEL_CHANGES.md](./DATA_MODEL_CHANGES.md)
* **Onboarding:** [PUBLIC_QUOTE_CALCULATOR_AND_ONBOARDING.md](./PUBLIC_QUOTE_CALCULATOR_AND_ONBOARDING.md)
* **Tracking:** [SHIPMENT_TRACKING_AND_STATUS_MANAGEMENT.md](./SHIPMENT_TRACKING_AND_STATUS_MANAGEMENT.md)
* **Invoicing:** [LIQUIDATION_AND_INVOICING_SYSTEM.md](./LIQUIDATION_AND_INVOICING_SYSTEM.md)
* **Elasticsearch Admin:** [ELASTICSEARCH_ADMIN_MANAGEMENT.md](./ELASTICSEARCH_ADMIN_MANAGEMENT.md)
* **Customer Portal:** [FRONTEND_CUSTOMER_PORTAL.md](./FRONTEND_CUSTOMER_PORTAL.md)
* **Staff Portal:** [FRONTEND_STAFF_PORTAL.md](./FRONTEND_STAFF_PORTAL.md)
* **Search Keyword Improvement:** [SEARCH_KEYWORD_IMPROVEMENT_PLAN.md](./SEARCH_KEYWORD_IMPROVEMENT_PLAN.md)
* **AI Semantic Matching Design:** [AI_SEMANTIC_MATCHING_DESIGN.md](./AI_SEMANTIC_MATCHING_DESIGN.md)
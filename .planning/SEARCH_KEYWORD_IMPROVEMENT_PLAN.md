# Search Keyword Quality Improvement & Elasticsearch Admin UI - Detailed Implementation Plan

**Project:** SicargaBox - Courier Quotation System
**Focus:** Elasticsearch search optimization for Cotizador (Quote Calculator)
**Goal:** Improve search keyword quality and provide admin tools for Elasticsearch management
**Timeline:** 5 weeks (5 sprints)
**Last Updated:** 2025-10-20

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Keyword Quality Evaluation Strategy](#keyword-quality-evaluation-strategy)
4. [Phase 0: Baseline Evaluation & Model Comparison](#phase-0-baseline-evaluation--model-comparison)
5. [Phase 1: Infrastructure Foundation](#phase-1-infrastructure-foundation)
6. [Phase 2: Elasticsearch Admin UI](#phase-2-elasticsearch-admin-ui)
7. [Phase 3: Continuous Learning Pipeline](#phase-3-continuous-learning-pipeline)
8. [Phase 4: Advanced Search Features](#phase-4-advanced-search-features)
9. [Phase 5: Analytics & Optimization](#phase-5-analytics--optimization)
10. [Success Metrics](#success-metrics)
11. [Maintenance & Monitoring](#maintenance--monitoring)

---

## Executive Summary

### Problem Statement

The current search system has AI-generated keywords, but we need to:

1. **Evaluate** current keyword quality against modern AI models
2. **Rebuild** keywords if newer models (Claude 3.7, GPT-4, DeepSeek-V3) provide better results
3. **Implement** continuous learning from user behavior
4. **Provide** admin UI for Elasticsearch management without command-line access

### Current Infrastructure

- ✅ 7,524 PartidaArancelaria records with 100% keyword coverage
- ✅ Elasticsearch 8.19.5 indexing 4,682 ALLOWED items
- ✅ AI keyword generation using DeepSeek/OpenAI
- ⚠️ Keywords generated with older models (unknown generation date)
- ⚠️ No user learning data captured yet (0 ItemPartidaMapping records)
- ⚠️ No Celery for background tasks
- ⚠️ No admin UI for Elasticsearch operations

### Strategic Approach

1. **First:** Evaluate existing keywords vs. latest AI models
2. **Second:** Build infrastructure (Celery, tracking, admin UI)
3. **Third:** Implement continuous improvement (learning pipeline)
4. **Fourth:** Add advanced features (semantic search, analytics)

---

## Current State Assessment

### Database Statistics

```bash
Total Partidas:           7,524
  - ALLOWED:              4,682 (62.2%)
  - RESTRICTED:           [calculated]
  - PROHIBITED:           [calculated]

Keyword Coverage:         100% (all have search_keywords)
Elasticsearch Index:      4,682 documents (ALLOWED only)
ItemPartidaMapping:       0 records (no user learning data)
PartidaArancelariaEmb:    0 records (no vector embeddings)
```

### Technical Stack

```bash
Backend:         Django 5.0.2 + DRF
Database:        PostgreSQL
Search Engine:   Elasticsearch 8.19.5
AI Providers:    DeepSeek, OpenAI, Anthropic (configured)
Task Queue:      None (Celery needed)
Cache:           None (Redis needed for Celery)
```

### Search Implementation

- **View:** `buscar_partidas()` in `MiCasillero/views.py:398`
- **Document:** `PartidaArancelariaDocument` in `MiCasillero/documents.py`
- **Search Fields:**
  - `item_no^3` (boost: 3x - tariff codes)
  - `descripcion^2` (boost: 2x - descriptions)
  - `full_text_search` (boost: 1x - combined field)
  - `search_keywords` (boost: 1x - AI keywords)
- **Fuzziness:** AUTO (typo tolerance)
- **Result Limit:** Top 20 results

---

## Keyword Quality Evaluation Strategy

### Evaluation Methodology

#### 1. Test Dataset Creation

**Goal:** Create representative search queries covering diverse product categories

**Test Categories (20 categories × 5 queries = 100 test queries):**

1. **Electronics (Electrónicos)**
   - "laptop gaming"
   - "audifonos bluetooth"
   - "celular samsung"
   - "tablet para niños"
   - "cargador usb c"

2. **Clothing & Footwear (Ropa y Calzado)**
   - "zapatos deportivos"
   - "jeans para hombre"
   - "vestido de fiesta"
   - "ropa de bebé"
   - "botas de trabajo"

3. **Home & Kitchen (Hogar y Cocina)**
   - "licuadora"
   - "sartenes antiadherentes"
   - "almohadas"
   - "cortinas blackout"
   - "organizadores de cocina"

4. **Beauty & Personal Care (Belleza y Cuidado Personal)**
   - "perfume mujer"
   - "crema facial"
   - "maquillaje"
   - "shampoo para cabello rizado"
   - "cepillo de dientes electrico"

5. **Sports & Outdoors (Deportes y Exteriores)**
   - "bicicleta de montaña"
   - "pesas ajustables"
   - "tienda de campaña"
   - "balón de fútbol"
   - "guantes de box"

6. **Toys & Games (Juguetes y Juegos)**
   - "lego"
   - "muñecas"
   - "juegos de mesa"
   - "carros a control remoto"
   - "rompecabezas"

7. **Books & Media (Libros y Medios)**
   - "libros en español"
   - "audífonos"
   - "blu ray"
   - "kindle"
   - "comics marvel"

8. **Tools & Hardware (Herramientas y Ferretería)**
   - "taladro inalambrico"
   - "juego de destornilladores"
   - "sierra circular"
   - "nivel laser"
   - "escalera plegable"

9. **Automotive (Automotriz)**
   - "aceite de motor"
   - "llantas"
   - "bateria de carro"
   - "luces led"
   - "limpiador de inyectores"

10. **Baby Products (Productos para Bebé)**
    - "pañales"
    - "biberones"
    - "coche para bebé"
    - "monitor de bebé"
    - "juguetes educativos"

11. **Pet Supplies (Mascotas)**
    - "comida para perros"
    - "collar anti pulgas"
    - "juguetes para gatos"
    - "jaula para hamster"
    - "rascador para gatos"

12. **Office Supplies (Oficina)**
    - "impresora"
    - "silla ergonomica"
    - "calculadora cientifica"
    - "archivadores"
    - "marcadores permanentes"

13. **Health & Wellness (Salud y Bienestar)**
    - "vitaminas"
    - "proteina whey"
    - "glucometro"
    - "termometro digital"
    - "masajeador electrico"

14. **Jewelry & Watches (Joyería y Relojes)**
    - "reloj inteligente"
    - "anillos de plata"
    - "collares de oro"
    - "aretes de diamantes"
    - "pulseras de cuero"

15. **Musical Instruments (Instrumentos Musicales)**
    - "guitarra electrica"
    - "teclado musical"
    - "bateria acustica"
    - "microfono de estudio"
    - "violin"

16. **Camera & Photo (Cámaras y Fotografía)**
    - "camara canon"
    - "tripode para celular"
    - "lentes para nikon"
    - "memoria sd"
    - "flash externo"

17. **Garden & Outdoor (Jardín y Exterior)**
    - "manguera de jardin"
    - "semillas de flores"
    - "cortadora de cesped"
    - "macetas decorativas"
    - "fertilizante organico"

18. **Arts & Crafts (Arte y Manualidades)**
    - "pinturas acrilicas"
    - "pinceles"
    - "lienzo para pintar"
    - "pegamento hot glue"
    - "tijeras de precision"

19. **Luggage & Travel (Equipaje y Viajes)**
    - "maleta de viaje"
    - "mochila antirrobo"
    - "almohada de viaje"
    - "adaptador universal"
    - "organizador de maletas"

20. **Household Appliances (Electrodomésticos)**
    - "microondas"
    - "refrigerador"
    - "lavadora"
    - "aspiradora robot"
    - "cafetera"

**Additional Query Types:**

- **Typos:** "lapto" (laptop), "telefno" (teléfono), "sapatos" (zapatos)
- **English queries:** "shoes", "phone", "laptop", "toys", "vitamins"
- **Misspellings:** "audifonoz", "bisicleta", "perfune"
- **Generic terms:** "cosa para cocinar", "para hacer ejercicio", "para el cabello"
- **Brand names:** "nike", "apple", "samsung", "lego", "barbie"

#### 2. Evaluation Metrics

**For Each Test Query, Measure:**

1. **Result Quality**
   - Number of results returned (0 = bad, 1-5 = good, 6-20 = excellent)
   - Relevance of top 5 results (manual review: 0-5 scale)
   - Position of most relevant result (lower = better)

2. **Keyword Match Analysis**
   - Which keywords triggered the match?
   - Were matches from AI keywords or base description?
   - Were matches exact, fuzzy, or semantic?

3. **Zero-Result Rate**
   - % of queries returning 0 results
   - Target: <5%

4. **Precision @ K**
   - Precision@1: Is top result relevant?
   - Precision@3: How many of top 3 are relevant?
   - Precision@5: How many of top 5 are relevant?

5. **Mean Reciprocal Rank (MRR)**
   - Average of 1/rank for first relevant result
   - Score: 0-1 (higher = better)

#### 3. Model Comparison Framework

**Test AI Models:**

| Provider | Model | Context | Cost/1K | Speed | Notes |
|----------|-------|---------|---------|-------|-------|
| DeepSeek | deepseek-chat | 64K | $0.14 | Fast | Current |
| OpenAI | gpt-4o-mini | 128K | $0.15 | Fast | Latest mini |
| OpenAI | gpt-4o | 128K | $2.50 | Medium | Most capable |
| Anthropic | claude-3-5-sonnet | 200K | $3.00 | Medium | Latest Claude |
| DeepSeek | deepseek-v3 | 64K | $0.27 | Fast | Latest DeepSeek |

**Comparison Process:**

1. Select 100 diverse partidas (stratified sample)
2. Generate keywords with each model
3. Compare keyword quality:
   - Relevance to user search terms
   - Honduran Spanish appropriateness
   - Coverage (synonyms, variations, colloquialisms)
   - Absence of over-generalization
4. Score each model (1-10 scale)
5. Select best model for production

#### 4. Automated Testing Script

**Create:** `backend/sicargabox/MiCasillero/management/commands/evaluate_search_quality.py`

**Features:**

- Load test queries from JSON file
- Execute searches against Elasticsearch
- Calculate metrics (MRR, Precision@K, zero-result rate)
- Generate HTML report with:
  - Overall scores
  - Per-query breakdown
  - Failed queries (zero results)
  - Keyword match analysis
- Compare before/after keyword regeneration

---

## Phase 0: Baseline Evaluation & Model Comparison

**Duration:** 3-4 days
**Goal:** Evaluate current keywords, test latest AI models, decide on rebuild strategy

### Task 0.1: Create Test Dataset

**Owner:** Dev Team
**Duration:** 4 hours
**Priority:** Critical

**Subtasks:**

- [ ] 0.1.1: Create `test_queries.json` with 100 search queries
  - 20 categories × 5 queries each
  - Include Spanish, English, typos, generic terms
  - Include expected partida codes (manual mapping)
  - File location: `backend/sicargabox/MiCasillero/fixtures/test_queries.json`

- [ ] 0.1.2: Document query creation rationale
  - Why each category was chosen
  - How queries represent real user behavior
  - Edge cases included

- [ ] 0.1.3: Validate test dataset
  - Manual review by 2 team members
  - Ensure diverse coverage
  - Check for Honduras-specific terms

**Deliverable:** `test_queries.json` with structure:

```json
{
  "queries": [
    {
      "id": 1,
      "category": "Electronics",
      "query": "laptop gaming",
      "query_type": "normal",
      "language": "es",
      "expected_partida_codes": ["8471.30.00.00"],
      "notes": "Common user search for gaming laptops"
    }
  ]
}
```

---

### Task 0.2: Create Search Evaluation Script

**Owner:** Dev Team
**Duration:** 8 hours
**Priority:** Critical

**Subtasks:**

- [ ] 0.2.1: Create management command skeleton

  ```bash
  python manage.py startcommand evaluate_search_quality
  ```

  - File: `backend/sicargabox/MiCasillero/management/commands/evaluate_search_quality.py`

- [ ] 0.2.2: Implement test query loader
  - Load from `test_queries.json`
  - Parse and validate structure
  - Handle missing/invalid queries

- [ ] 0.2.3: Implement search execution
  - Use same logic as `buscar_partidas()` view
  - Capture: results, scores, match info
  - Handle Elasticsearch errors gracefully

- [ ] 0.2.4: Implement metrics calculation
  - **Zero-result rate:** % queries with 0 results
  - **Precision@K:** Relevance of top K results
  - **MRR:** Mean Reciprocal Rank
  - **Average results per query**
  - **Keyword match distribution** (which fields matched)

- [ ] 0.2.5: Implement HTML report generator
  - Bootstrap 5 template
  - Overall summary table
  - Per-query breakdown table (sortable)
  - Charts: zero-result rate, results distribution
  - Export to `reports/search_evaluation_{timestamp}.html`

- [ ] 0.2.6: Add comparison mode
  - `--baseline` flag to save current results
  - `--compare` flag to compare with baseline
  - Show improvement/regression metrics
  - Highlight queries with biggest changes

**Command Usage:**

```bash
# Run baseline evaluation
python manage.py evaluate_search_quality --baseline

# Compare after keyword regeneration
python manage.py evaluate_search_quality --compare

# Test specific category
python manage.py evaluate_search_quality --category "Electronics"

# Verbose output
python manage.py evaluate_search_quality --verbose
```

**Deliverable:** Working evaluation script with HTML report generation

---

### Task 0.3: Run Baseline Evaluation

**Owner:** Dev Team
**Duration:** 2 hours
**Priority:** Critical

**Subtasks:**

- [ ] 0.3.1: Execute baseline evaluation

  ```bash
  python manage.py evaluate_search_quality --baseline --verbose
  ```

- [ ] 0.3.2: Review baseline report
  - Analyze zero-result queries
  - Identify poorly performing categories
  - Note keyword gaps (queries that should match but don't)

- [ ] 0.3.3: Manual spot-checking (30 queries)
  - Verify top results are truly relevant
  - Check for false positives
  - Document issues

- [ ] 0.3.4: Create baseline summary document
  - Overall metrics
  - Problem areas
  - Recommendations

**Deliverable:**

- Baseline report: `reports/baseline_search_evaluation_2025-10-20.html`
- Summary document: `docs/baseline_search_analysis.md`

---

### Task 0.4: AI Model Comparison

**Owner:** Dev Team
**Duration:** 1 day
**Priority:** High

**Subtasks:**

- [ ] 0.4.1: Select 100 representative partidas
  - Stratified sampling across categories
  - Include "Los demás" partidas (challenging)
  - Include simple partidas (baseline)
  - Include multi-level hierarchical partidas

- [ ] 0.4.2: Create model comparison script
  - File: `backend/sicargabox/MiCasillero/management/commands/compare_ai_models.py`
  - Generate keywords with each model
  - Store in temporary comparison table
  - Don't update production data

- [ ] 0.4.3: Run keyword generation for each model

  ```bash
  # DeepSeek (current)
  python manage.py compare_ai_models --model deepseek --sample-size 100

  # GPT-4o-mini
  python manage.py compare_ai_models --model gpt-4o-mini --sample-size 100

  # Claude 3.5 Sonnet
  python manage.py compare_ai_models --model claude-3-5-sonnet --sample-size 100
  ```

- [ ] 0.4.4: Human evaluation of generated keywords
  - Rate each model's keywords (1-10 scale) for:
    - Relevance
    - User-friendliness
    - Honduran Spanish appropriateness
    - Coverage (variety of synonyms)
    - Absence of noise (irrelevant keywords)
  - 3 evaluators × 100 partidas = 300 ratings per model

- [ ] 0.4.5: Automated quality testing
  - Run test queries against keywords from each model
  - Measure which model's keywords match test queries best
  - Calculate improvement over current keywords

- [ ] 0.4.6: Cost-benefit analysis
  - Estimate cost to regenerate all 7,524 partidas
  - Compare performance gain vs. cost
  - Recommend optimal model

**Deliverable:**

- Model comparison report: `reports/ai_model_comparison_2025-10-20.html`
- Recommended model with justification
- Cost estimate for full regeneration

---

### Task 0.5: Keyword Regeneration Decision

**Owner:** Tech Lead + Product Owner
**Duration:** 2 hours
**Priority:** Critical

**Subtasks:**

- [ ] 0.5.1: Review all evaluation reports
  - Baseline search quality
  - Model comparison results
  - Cost estimates

- [ ] 0.5.2: Decision meeting
  - **Decision A:** Keep current keywords (if quality is good)
  - **Decision B:** Partial regeneration (only poor-performing categories)
  - **Decision C:** Full regeneration with new model
  - **Decision D:** Hybrid approach (current + AI enrichment)

- [ ] 0.5.3: Document decision rationale
  - Why chosen approach was selected
  - Expected improvements
  - Budget allocated

- [ ] 0.5.4: Create regeneration plan (if B or C chosen)
  - Batch size
  - API rate limits
  - Estimated completion time
  - Rollback plan

**Deliverable:**

- Decision document: `docs/keyword_regeneration_decision.md`
- Regeneration execution plan (if applicable)

---

### Task 0.6: Execute Keyword Regeneration (If Approved)

**Owner:** Dev Team
**Duration:** 4-8 hours (depending on batch size and API speed)
**Priority:** High (if approved)

**Subtasks:**

- [ ] 0.6.1: Backup current keywords

  ```sql
  -- Export current keywords to CSV
  COPY (
    SELECT id, item_no, descripcion, search_keywords
    FROM "MiCasillero_partidaarancelaria"
  ) TO '/tmp/partidas_keywords_backup_2025-10-20.csv'
  WITH CSV HEADER;
  ```

- [ ] 0.6.2: Update `generate_search_keywords` command
  - Enhance prompts based on findings
  - Add new model support (if needed)
  - Improve error handling
  - Add progress tracking

- [ ] 0.6.3: Run regeneration in batches

  ```bash
  # Test first 50
  python manage.py generate_search_keywords \
    --api-provider claude-3-5-sonnet \
    --batch-size 10 \
    --start-from 0 \
    --dry-run

  # If successful, run full regeneration
  python manage.py generate_search_keywords \
    --api-provider claude-3-5-sonnet \
    --batch-size 20 \
    --start-from 0 \
    2>&1 | tee logs/keyword_regeneration.log
  ```

- [ ] 0.6.4: Monitor regeneration progress
  - Track API errors
  - Monitor costs
  - Check keyword quality samples

- [ ] 0.6.5: Rebuild Elasticsearch index

  ```bash
  python manage.py search_index --rebuild
  ```

- [ ] 0.6.6: Run post-regeneration evaluation

  ```bash
  python manage.py evaluate_search_quality --compare
  ```

- [ ] 0.6.7: Review improvement metrics
  - Compare before/after reports
  - Verify improvement in problem queries
  - Check for regressions

**Deliverable:**

- Regenerated keywords in database
- Updated Elasticsearch index
- Post-regeneration evaluation report
- Comparison showing improvement

---

## Phase 1: Infrastructure Foundation

**Duration:** 1 week
**Goal:** Set up Celery, Redis, user tracking, and basic admin interface

### Task 1.1: Celery & Redis Setup

**Owner:** DevOps + Backend Dev
**Duration:** 1 day
**Priority:** Critical

**Subtasks:**

- [ ] 1.1.1: Install dependencies

  ```bash
  cd backend/sicargabox
  pip install celery redis django-celery-results django-celery-beat
  pip freeze > requirements.txt
  ```

- [ ] 1.1.2: Install and configure Redis
  - **Windows:** Download Redis for Windows or use WSL
  - **Linux/Mac:** `sudo apt-get install redis-server`
  - Start Redis: `redis-server`
  - Verify: `redis-cli ping` → should return `PONG`

- [ ] 1.1.3: Create Celery configuration
  - File: `backend/sicargabox/SicargaBox/celery.py`
  - Configure broker: `redis://localhost:6379/0`
  - Configure result backend: `redis://localhost:6379/0`
  - Configure task routes (separate queues)
  - Set timezone: `America/Tegucigalpa`

- [ ] 1.1.4: Update Django settings
  - Add `django_celery_results` to `INSTALLED_APPS`
  - Add `django_celery_beat` to `INSTALLED_APPS`
  - Configure Celery settings in `settings.py`
  - Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`

- [ ] 1.1.5: Create task queues

  ```python
  CELERY_TASK_ROUTES = {
      'admintools.tasks.rebuild_elasticsearch_index': {
          'queue': 'elasticsearch'
      },
      'admintools.tasks.generate_ai_keywords': {
          'queue': 'ai_generation'
      },
      'admintools.tasks.enrich_search_keywords': {
          'queue': 'learning'
      },
  }
  ```

- [ ] 1.1.6: Run Celery migrations

  ```bash
  python manage.py migrate django_celery_results
  python manage.py migrate django_celery_beat
  ```

- [ ] 1.1.7: Test Celery setup
  - Create test task
  - Start Celery worker: `celery -A SicargaBox worker -l info`
  - Execute test task
  - Verify task completion in Django shell

- [ ] 1.1.8: Create systemd service (production) or supervisor config
  - Celery worker service
  - Celery beat service (for periodic tasks)
  - Auto-restart on failure

**Deliverable:**

- Working Celery + Redis installation
- Test task successfully executed
- Documentation: `docs/celery_setup.md`

---

### Task 1.2: Create Admin Tools App

**Owner:** Backend Dev
**Duration:** 2 hours
**Priority:** High

**Subtasks:**

- [ ] 1.2.1: Generate Django app

  ```bash
  cd backend/sicargabox
  python manage.py startapp admintools
  ```

- [ ] 1.2.2: Add to INSTALLED_APPS
  - Edit `settings.py`
  - Add `'admintools',` to `INSTALLED_APPS`

- [ ] 1.2.3: Create app structure

  ```bash
  admintools/
  ├── __init__.py
  ├── admin.py          # Admin interface registration
  ├── apps.py
  ├── models.py         # TaskHistory, KeywordSuggestion
  ├── tasks.py          # Celery tasks
  ├── views.py          # Dashboard views
  ├── urls.py           # URL routing
  ├── templates/
  │   └── admintools/
  │       ├── dashboard.html
  │       ├── keyword_review.html
  │       └── task_history.html
  └── static/
      └── admintools/
          ├── css/
          └── js/
  ```

- [ ] 1.2.4: Create base models
  - `TaskHistory`: Track Celery task executions
  - `KeywordSuggestion`: Store AI/user-suggested keywords for review

- [ ] 1.2.5: Run migrations

  ```bash
  python manage.py makemigrations admintools
  python manage.py migrate admintools
  ```

**Deliverable:** Basic admintools app structure

---

### Task 1.3: User Selection Tracking (Frontend)

**Owner:** Frontend Dev
**Duration:** 4 hours
**Priority:** High

**Subtasks:**

- [ ] 1.3.1: Update Cotizador template
  - File: `backend/sicargabox/MiCasillero/templates/cotizador.html`
  - Add JavaScript to track Select2 selection events
  - Capture: query text, selected partida ID, selection rank

- [ ] 1.3.2: Create tracking AJAX handler

  ```javascript
  // When user selects a partida from search results
  $('#partida_search').on('select2:select', function(e) {
    const data = e.params.data;
    const searchQuery = $('#partida_search').data('select2').$dropdown
      .find('input.select2-search__field').val();

    // Send tracking data
    fetch('/api/track-partida-selection/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({
        query: searchQuery,
        partida_id: data.id,
        ranking_position: data.rank || 1,
        confidence_score: data.score || 0,
        session_key: getSessionKey()
      })
    });
  });
  ```

- [ ] 1.3.3: Add session tracking
  - Store anonymous user's session key
  - Link selections to user if authenticated
  - Preserve selections across login/register

- [ ] 1.3.4: Add visual feedback
  - Show "Selection recorded" message
  - Highlight previously selected partidas
  - Show "Popular choice" badge for frequently selected items

**Deliverable:** Frontend tracking implemented in Cotizador

---

### Task 1.4: User Selection Tracking (Backend)

**Owner:** Backend Dev
**Duration:** 4 hours
**Priority:** High

**Subtasks:**

- [ ] 1.4.1: Create tracking API endpoint
  - File: `MiCasillero/views.py`
  - View: `track_partida_selection(request)`
  - Method: POST
  - Authentication: Optional (allow anonymous)

- [ ] 1.4.2: Implement tracking logic

  ```python
  @require_http_methods(["POST"])
  def track_partida_selection(request):
      data = json.loads(request.body)

      # Get or create ItemPartidaMapping
      mapping = ItemPartidaMapping.objects.create(
          item_description_original=data['query'],
          partida_arancelaria_id=data['partida_id'],
          confidence_score=data.get('confidence_score', 0),
          ranking_position=data.get('ranking_position', 1),
          was_ai_suggestion=True,
          selected_by=request.user if request.user.is_authenticated else None,
          session_key=data.get('session_key', ''),
          is_staff_verified=request.user.is_staff if request.user.is_authenticated else False
      )

      return JsonResponse({'status': 'success', 'mapping_id': mapping.id})
  ```

- [ ] 1.4.3: Add URL routing
  - File: `MiCasillero/urls.py`
  - Add: `path('api/track-partida-selection/', views.track_partida_selection, name='track_partida_selection')`

- [ ] 1.4.4: Add rate limiting
  - Prevent spam tracking
  - Max 100 selections per session per day
  - Use Django cache or Redis

- [ ] 1.4.5: Add analytics triggers
  - Update partida "popularity score"
  - Trigger learning pipeline if threshold met (e.g., 10 new mappings)

**Deliverable:** Working selection tracking API

---

### Task 1.5: Basic Elasticsearch Status Dashboard

**Owner:** Backend Dev
**Duration:** 1 day
**Priority:** Medium

**Subtasks:**

- [ ] 1.5.1: Create dashboard view
  - File: `admintools/views.py`
  - View: `ElasticsearchDashboardView`
  - Permission: `@user_passes_test(lambda u: u.is_superuser)`

- [ ] 1.5.2: Fetch Elasticsearch metrics

  ```python
  from django_elasticsearch_dsl import get_connection

  def get_elasticsearch_status():
      es = get_connection()

      # Cluster health
      health = es.cluster.health()

      # Index stats
      index_stats = es.indices.stats(index='partidas_arancelarias')

      # Last rebuild time (from TaskHistory)
      last_rebuild = TaskHistory.objects.filter(
          task_name='rebuild_elasticsearch_index',
          status='SUCCESS'
      ).order_by('-completed_at').first()

      return {
          'cluster_status': health['status'],
          'document_count': index_stats['_all']['total']['docs']['count'],
          'index_size': index_stats['_all']['total']['store']['size_in_bytes'],
          'last_rebuild': last_rebuild.completed_at if last_rebuild else None
      }
  ```

- [ ] 1.5.3: Create dashboard template
  - File: `admintools/templates/admintools/dashboard.html`
  - Bootstrap 5 cards for each metric
  - Color-coded status (green/yellow/red)
  - Auto-refresh every 30 seconds

- [ ] 1.5.4: Add URL routing
  - File: `admintools/urls.py`
  - Include in main `urls.py`
  - Path: `/admin/elasticsearch/`

- [ ] 1.5.5: Add navigation link in Django admin
  - Customize admin template
  - Add "Elasticsearch Management" link to admin sidebar

**Deliverable:** Basic status dashboard accessible at `/admin/elasticsearch/`

---

## Phase 2: Elasticsearch Admin UI

**Duration:** 1 week
**Goal:** Build comprehensive admin interface for Elasticsearch operations

### Task 2.1: Create Celery Task Wrappers

**Owner:** Backend Dev
**Duration:** 1 day
**Priority:** High

**Subtasks:**

- [ ] 2.1.1: Create `tasks.py` in admintools
  - File: `admintools/tasks.py`

- [ ] 2.1.2: Implement `rebuild_elasticsearch_index` task

  ```python
  from celery import shared_task
  from django.core.management import call_command
  from .models import TaskHistory

  @shared_task(bind=True)
  def rebuild_elasticsearch_index(self):
      task_history = TaskHistory.objects.create(
          task_name='rebuild_elasticsearch_index',
          task_id=self.request.id,
          status='STARTED'
      )

      try:
          # Call Django management command
          call_command('search_index', '--rebuild', '-f')

          task_history.status = 'SUCCESS'
          task_history.save()

          return {'status': 'success', 'message': 'Index rebuilt successfully'}

      except Exception as e:
          task_history.status = 'FAILURE'
          task_history.error_message = str(e)
          task_history.save()
          raise
  ```

- [ ] 2.1.3: Implement `delete_elasticsearch_index` task
  - Similar structure to rebuild
  - Call `search_index --delete -f`

- [ ] 2.1.4: Implement `populate_elasticsearch_index` task
  - Call `search_index --populate -f`

- [ ] 2.1.5: Implement `generate_ai_keywords` task

  ```python
  @shared_task(bind=True)
  def generate_ai_keywords(self, api_provider='deepseek', batch_size=10, start_from=0):
      task_history = TaskHistory.objects.create(
          task_name='generate_ai_keywords',
          task_id=self.request.id,
          status='STARTED',
          parameters={
              'api_provider': api_provider,
              'batch_size': batch_size,
              'start_from': start_from
          }
      )

      try:
          call_command(
              'generate_search_keywords',
              f'--api-provider={api_provider}',
              f'--batch-size={batch_size}',
              f'--start-from={start_from}'
          )

          task_history.status = 'SUCCESS'
          task_history.save()

          return {'status': 'success'}

      except Exception as e:
          task_history.status = 'FAILURE'
          task_history.error_message = str(e)
          task_history.save()
          raise
  ```

- [ ] 2.1.6: Create `TaskHistory` model

  ```python
  class TaskHistory(models.Model):
      task_name = models.CharField(max_length=100)
      task_id = models.CharField(max_length=100, unique=True)
      status = models.CharField(max_length=20, choices=[
          ('PENDING', 'Pending'),
          ('STARTED', 'Started'),
          ('SUCCESS', 'Success'),
          ('FAILURE', 'Failure'),
          ('RETRY', 'Retry')
      ])
      parameters = models.JSONField(default=dict)
      result = models.JSONField(null=True, blank=True)
      error_message = models.TextField(blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      started_at = models.DateTimeField(null=True)
      completed_at = models.DateTimeField(null=True)
      initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  ```

- [ ] 2.1.7: Add progress tracking
  - Use `self.update_state()` in tasks
  - Store progress in TaskHistory
  - Enable real-time progress display

**Deliverable:** Working Celery task wrappers for all Elasticsearch operations

---

### Task 2.2: Management Actions Interface

**Owner:** Backend Dev + Frontend Dev
**Duration:** 2 days
**Priority:** High

**Subtasks:**

- [ ] 2.2.1: Create management actions view
  - File: `admintools/views.py`
  - View: `ManagementActionsView`
  - Render buttons for each action

- [ ] 2.2.2: Implement action handler endpoints
  - `POST /admin/elasticsearch/rebuild/`
  - `POST /admin/elasticsearch/delete/`
  - `POST /admin/elasticsearch/populate/`
  - `POST /admin/elasticsearch/generate-keywords/`

- [ ] 2.2.3: Add confirmation modals
  - Bootstrap modal for destructive actions (delete)
  - Show impact estimate (e.g., "This will delete 4,682 documents")
  - Require typing "CONFIRM" for critical actions

- [ ] 2.2.4: Implement action handlers

  ```python
  @require_http_methods(["POST"])
  @user_passes_test(lambda u: u.is_superuser)
  def rebuild_index_action(request):
      task = rebuild_elasticsearch_index.delay()

      TaskHistory.objects.filter(task_id=task.id).update(
          initiated_by=request.user
      )

      return JsonResponse({
          'status': 'started',
          'task_id': task.id,
          'message': 'Index rebuild started'
      })
  ```

- [ ] 2.2.5: Add keyword generation form
  - Select AI provider (DeepSeek, OpenAI, Claude)
  - Batch size slider (5-50)
  - Start from ID (for resuming)
  - Target selection (All / ALLOWED only / Specific category)
  - Cost estimator (dynamic calculation)

- [ ] 2.2.6: Style action buttons
  - Color-coded by severity (green, yellow, red)
  - Disabled state when task is running
  - Show last execution time on button

**Deliverable:** Functional management actions interface

---

### Task 2.3: Real-Time Task Status Display

**Owner:** Frontend Dev
**Duration:** 1 day
**Priority:** High

**Subtasks:**

- [ ] 2.3.1: Create task status API endpoint

  ```python
  @require_http_methods(["GET"])
  def get_task_status(request, task_id):
      task_result = AsyncResult(task_id)
      task_history = TaskHistory.objects.get(task_id=task_id)

      return JsonResponse({
          'task_id': task_id,
          'status': task_result.status,
          'progress': task_result.info.get('progress', 0) if task_result.info else 0,
          'current': task_result.info.get('current', 0) if task_result.info else 0,
          'total': task_result.info.get('total', 0) if task_result.info else 0,
          'message': task_result.info.get('message', '') if task_result.info else '',
          'result': task_result.result,
          'error': task_history.error_message
      })
  ```

- [ ] 2.3.2: Create JavaScript polling function

  ```javascript
  function pollTaskStatus(taskId, callback) {
      const pollInterval = setInterval(() => {
          fetch(`/admin/elasticsearch/task-status/${taskId}/`)
              .then(res => res.json())
              .then(data => {
                  callback(data);

                  if (['SUCCESS', 'FAILURE'].includes(data.status)) {
                      clearInterval(pollInterval);
                  }
              });
      }, 2000); // Poll every 2 seconds
  }
  ```

- [ ] 2.3.3: Create progress bar component
  - Bootstrap progress bar
  - Show percentage
  - Show current/total (e.g., "Processed 150/7524 partidas")
  - Animated when in progress

- [ ] 2.3.4: Create task log viewer
  - Collapsible section
  - Real-time log streaming
  - Auto-scroll to bottom
  - Color-coded log levels (ERROR, WARNING, INFO)

- [ ] 2.3.5: Add notifications
  - Browser notification when task completes
  - Toast notification in UI
  - Email notification for long-running tasks (optional)

**Deliverable:** Real-time task monitoring with progress bars

---

### Task 2.4: Task History Table

**Owner:** Backend Dev
**Duration:** 4 hours
**Priority:** Medium

**Subtasks:**

- [ ] 2.4.1: Create task history view
  - List last 100 tasks
  - Paginated (20 per page)
  - Sortable columns (date, task name, status, duration)

- [ ] 2.4.2: Add filters
  - Filter by task name
  - Filter by status
  - Filter by date range
  - Filter by initiated user

- [ ] 2.4.3: Add task detail modal
  - Click row to open modal
  - Show full parameters
  - Show full result/error
  - Show execution timeline

- [ ] 2.4.4: Add re-run button
  - For failed tasks
  - Pre-fill parameters
  - Confirm before re-running

**Deliverable:** Task history table with filtering and detail view

---

## Phase 3: Continuous Learning Pipeline

**Duration:** 1 week
**Goal:** Implement automated learning from user behavior

### Task 3.1: Learning Analysis Task

**Owner:** Backend Dev
**Duration:** 2 days
**Priority:** High

**Subtasks:**

- [ ] 3.1.1: Create `analyze_new_mappings` Celery task

  ```python
  @shared_task
  def analyze_new_mappings():
      """
      Analyze ItemPartidaMapping records to identify new keyword suggestions.
      Run nightly or weekly.
      """
      # Get mappings created since last run
      last_run = TaskHistory.objects.filter(
          task_name='analyze_new_mappings',
          status='SUCCESS'
      ).order_by('-completed_at').first()

      if last_run:
          mappings = ItemPartidaMapping.objects.filter(
              created_at__gt=last_run.completed_at
          )
      else:
          mappings = ItemPartidaMapping.objects.all()

      # Group by partida
      partida_mappings = {}
      for mapping in mappings:
          partida_id = mapping.partida_arancelaria_id
          if partida_id not in partida_mappings:
              partida_mappings[partida_id] = []
          partida_mappings[partida_id].append(mapping)

      # Analyze each partida's mappings
      for partida_id, mappings in partida_mappings.items():
          # Extract search terms
          search_terms = [m.item_description_normalized for m in mappings]

          # Count frequency
          term_counts = Counter(search_terms)

          # Get partida's current keywords
          partida = PartidaArancelaria.objects.get(id=partida_id)
          current_keywords = set(partida.search_keywords or [])

          # Identify new candidate keywords (frequency >= threshold)
          threshold = 3  # Must appear at least 3 times
          candidates = [
              term for term, count in term_counts.items()
              if count >= threshold and term not in current_keywords
          ]

          # Create KeywordSuggestion records
          for term in candidates:
              KeywordSuggestion.objects.get_or_create(
                  partida_arancelaria=partida,
                  suggested_keyword=term,
                  defaults={
                      'source': 'USER_SELECTION',
                      'frequency': term_counts[term],
                      'status': 'PENDING'
                  }
              )
  ```

- [ ] 3.1.2: Create `KeywordSuggestion` model

  ```python
  class KeywordSuggestion(models.Model):
      partida_arancelaria = models.ForeignKey(
          PartidaArancelaria,
          on_delete=models.CASCADE,
          related_name='keyword_suggestions'
      )
      suggested_keyword = models.CharField(max_length=200)
      source = models.CharField(max_length=20, choices=[
          ('AI_GENERATION', 'AI Generation'),
          ('USER_SELECTION', 'User Selection'),
          ('STAFF_MANUAL', 'Staff Manual')
      ])
      frequency = models.IntegerField(default=1)
      status = models.CharField(max_length=20, choices=[
          ('PENDING', 'Pending Review'),
          ('APPROVED', 'Approved'),
          ('REJECTED', 'Rejected')
      ])
      reviewed_by = models.ForeignKey(
          User,
          on_delete=models.SET_NULL,
          null=True,
          blank=True
      )
      reviewed_at = models.DateTimeField(null=True, blank=True)
      rejection_reason = models.TextField(blank=True)
      created_at = models.DateTimeField(auto_now_add=True)

      class Meta:
          unique_together = ['partida_arancelaria', 'suggested_keyword']
  ```

- [ ] 3.1.3: Add Celery beat schedule

  ```python
  # In settings.py
  from celery.schedules import crontab

  CELERY_BEAT_SCHEDULE = {
      'analyze-new-mappings': {
          'task': 'admintools.tasks.analyze_new_mappings',
          'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
      },
  }
  ```

- [ ] 3.1.4: Add notification for new suggestions
  - Email to admin when new suggestions are ready
  - Badge count in admin UI

**Deliverable:** Automated learning analysis running nightly

---

### Task 3.2: Keyword Enrichment Task

**Owner:** Backend Dev
**Duration:** 1 day
**Priority:** High

**Subtasks:**

- [ ] 3.2.1: Create `enrich_search_keywords` task

  ```python
  @shared_task
  def enrich_search_keywords(auto_approve_threshold=10):
      """
      Apply approved keyword suggestions to partidas.
      Auto-approve suggestions above threshold.
      """
      # Get pending suggestions
      suggestions = KeywordSuggestion.objects.filter(status='PENDING')

      for suggestion in suggestions:
          # Auto-approve high-frequency suggestions
          if suggestion.frequency >= auto_approve_threshold:
              suggestion.status = 'APPROVED'
              suggestion.reviewed_at = timezone.now()
              suggestion.save()
          else:
              continue  # Wait for manual review

      # Apply approved suggestions
      approved = KeywordSuggestion.objects.filter(
          status='APPROVED',
          applied=False
      )

      partidas_to_reindex = []

      for suggestion in approved:
          partida = suggestion.partida_arancelaria

          # Add keyword if not already present
          if suggestion.suggested_keyword not in partida.search_keywords:
              partida.search_keywords.append(suggestion.suggested_keyword)
              partida.save()
              partidas_to_reindex.append(partida)

          # Mark as applied
          suggestion.applied = True
          suggestion.save()

      # Re-index updated partidas
      if partidas_to_reindex:
          for partida in partidas_to_reindex:
              PartidaArancelariaDocument().update(partida)

      return {
          'approved_count': approved.count(),
          'partidas_updated': len(partidas_to_reindex)
      }
  ```

- [ ] 3.2.2: Add `applied` field to KeywordSuggestion

  ```python
  applied = models.BooleanField(default=False)
  applied_at = models.DateTimeField(null=True, blank=True)
  ```

- [ ] 3.2.3: Add to Celery beat schedule

  ```python
  'enrich-search-keywords': {
      'task': 'admintools.tasks.enrich_search_keywords',
      'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily, after analysis
  }
  ```

**Deliverable:** Automated keyword enrichment from user data

---

### Task 3.3: Staff Override Tracking

**Owner:** Backend Dev
**Duration:** 4 hours
**Priority:** Medium

**Subtasks:**

- [ ] 3.3.1: Create staff correction interface
  - When staff changes partida selection in admin
  - Show "Was this an AI suggestion?" checkbox
  - If yes, record as override in ItemPartidaMapping

- [ ] 3.3.2: Add override recording logic

  ```python
  def record_staff_override(original_partida, corrected_partida, item_description, reason=''):
      # Find the original AI suggestion
      original_mapping = ItemPartidaMapping.objects.filter(
          item_description_normalized=normalize(item_description),
          partida_arancelaria=original_partida
      ).first()

      # Create correction record
      ItemPartidaMapping.objects.create(
          item_description_original=item_description,
          item_description_normalized=normalize(item_description),
          partida_arancelaria=corrected_partida,
          was_ai_suggestion=False,
          is_staff_verified=True,
          selected_by=request.user,
          staff_override=True,
          override_from=original_partida,
          override_reason=reason
      )

      # Penalize original suggestion
      if original_mapping:
          original_mapping.confidence_score *= 0.5  # Reduce confidence
          original_mapping.save()
  ```

- [ ] 3.3.3: Add override analytics
  - Dashboard widget showing override rate
  - Report of most-overridden suggestions
  - Use to identify poor AI suggestions

**Deliverable:** Staff override tracking in place

---

### Task 3.4: Keyword Review Interface

**Owner:** Backend Dev + Frontend Dev
**Duration:** 1.5 days
**Priority:** High

**Subtasks:**

- [ ] 3.4.1: Create keyword review list view
  - File: `admintools/templates/admintools/keyword_review.html`
  - List all PENDING KeywordSuggestion records
  - Group by partida
  - Show frequency, source, creation date

- [ ] 3.4.2: Implement bulk actions
  - Select multiple suggestions
  - Bulk approve
  - Bulk reject
  - Bulk "need more data"

- [ ] 3.4.3: Create per-partida review modal
  - Show current keywords
  - Show pending suggestions
  - Show user search context (what queries led to this suggestion)
  - One-click approve/reject
  - Add custom keywords manually

- [ ] 3.4.4: Add search and filter
  - Search by keyword
  - Filter by partida code
  - Filter by frequency threshold
  - Filter by source

- [ ] 3.4.5: Add approval/rejection endpoints

  ```python
  @require_http_methods(["POST"])
  @user_passes_test(lambda u: u.is_staff)
  def approve_keyword_suggestion(request, suggestion_id):
      suggestion = get_object_or_404(KeywordSuggestion, id=suggestion_id)

      suggestion.status = 'APPROVED'
      suggestion.reviewed_by = request.user
      suggestion.reviewed_at = timezone.now()
      suggestion.save()

      # Trigger enrichment task
      enrich_search_keywords.delay()

      return JsonResponse({'status': 'success'})
  ```

**Deliverable:** Full keyword review interface for staff

---

## Phase 4: Advanced Search Features

**Duration:** 1 week
**Goal:** Implement semantic search and hybrid ranking

### Task 4.1: Vector Embeddings Generation

**Owner:** Backend Dev
**Duration:** 2 days
**Priority:** Medium

**Subtasks:**

- [ ] 4.1.1: Choose embedding approach
  - **Option A:** PostgreSQL with pgvector extension
  - **Option B:** Elasticsearch dense_vector field
  - **Option C:** External vector DB (Pinecone, Weaviate)
  - **Decision:** Option B (Elasticsearch) - simpler integration

- [ ] 4.1.2: Update Elasticsearch document

  ```python
  # In MiCasillero/documents.py
  from django_elasticsearch_dsl import fields

  class PartidaArancelariaDocument(Document):
      # ... existing fields ...

      embedding_vector = fields.DenseVectorField(dims=1536)  # OpenAI embedding size
  ```

- [ ] 4.1.3: Create embedding generation task

  ```python
  @shared_task
  def generate_embeddings(api_provider='openai', batch_size=100):
      from openai import OpenAI

      client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

      partidas = PartidaArancelaria.objects.filter(
          courier_category='ALLOWED',
          embedding_data__isnull=True  # Only generate for partidas without embeddings
      )

      for i in range(0, partidas.count(), batch_size):
          batch = partidas[i:i+batch_size]

          for partida in batch:
              # Combine description + keywords + learned terms
              text_parts = [partida.descripcion]
              text_parts.extend(partida.search_keywords or [])

              # Get learned terms from mappings
              learned_terms = ItemPartidaMapping.objects.filter(
                  partida_arancelaria=partida,
                  is_staff_verified=True
              ).values_list('item_description_normalized', flat=True)
              text_parts.extend(learned_terms)

              embedding_text = ' '.join(text_parts)

              # Generate embedding
              response = client.embeddings.create(
                  input=embedding_text,
                  model='text-embedding-3-small'
              )

              embedding_vector = response.data[0].embedding

              # Store in PartidaArancelariaEmbedding model
              PartidaArancelariaEmbedding.objects.update_or_create(
                  partida_arancelaria=partida,
                  defaults={
                      'embedding_vector': embedding_vector,
                      'embedding_text': embedding_text,
                      'embedding_model': 'text-embedding-3-small',
                      'version': 1
                  }
              )
  ```

- [ ] 4.1.4: Run embedding generation

  ```bash
  python manage.py shell
  >>> from admintools.tasks import generate_embeddings
  >>> generate_embeddings.delay(batch_size=50)
  ```

- [ ] 4.1.5: Update Elasticsearch index with embeddings

  ```bash
  python manage.py search_index --rebuild
  ```

**Deliverable:** Vector embeddings for all ALLOWED partidas

---

### Task 4.2: Semantic Search Implementation

**Owner:** Backend Dev
**Duration:** 2 days
**Priority:** Medium

**Subtasks:**

- [ ] 4.2.1: Create semantic search function

  ```python
  def semantic_search(query_text, top_k=20):
      from openai import OpenAI

      client = OpenAI()

      # Generate query embedding
      response = client.embeddings.create(
          input=query_text,
          model='text-embedding-3-small'
      )
      query_vector = response.data[0].embedding

      # Search Elasticsearch with kNN
      search = PartidaArancelariaDocument.search()
      search = search.query(
          'script_score',
          query={'match_all': {}},
          script={
              'source': "cosineSimilarity(params.query_vector, 'embedding_vector') + 1.0",
              'params': {'query_vector': query_vector}
          }
      )
      search = search[:top_k]

      return search.execute()
  ```

- [ ] 4.2.2: Implement hybrid search

  ```python
  def hybrid_search(query_text, top_k=20, keyword_weight=0.6, semantic_weight=0.4):
      # Keyword search results
      keyword_results = keyword_search(query_text, top_k=50)

      # Semantic search results
      semantic_results = semantic_search(query_text, top_k=50)

      # Reciprocal Rank Fusion (RRF)
      scores = {}

      for rank, hit in enumerate(keyword_results, start=1):
          scores[hit.meta.id] = scores.get(hit.meta.id, 0) + keyword_weight / rank

      for rank, hit in enumerate(semantic_results, start=1):
          scores[hit.meta.id] = scores.get(hit.meta.id, 0) + semantic_weight / rank

      # Sort by combined score
      ranked_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

      # Fetch final results
      final_results = PartidaArancelaria.objects.filter(
          id__in=[id for id, _ in ranked_ids]
      )

      return final_results
  ```

- [ ] 4.2.3: Update `buscar_partidas` view
  - Add `?mode=hybrid` parameter
  - Default to keyword-only (backward compatible)
  - Allow hybrid mode opt-in

- [ ] 4.2.4: A/B testing setup
  - Randomly assign 50% users to hybrid mode
  - Track selection metrics for both modes
  - Compare performance after 1 week

**Deliverable:** Working hybrid search with A/B testing

---

### Task 4.3: Search Result Enhancement

**Owner:** Frontend Dev
**Duration:** 1 day
**Priority:** Low

**Subtasks:**

- [ ] 4.3.1: Highlight matching terms
  - Use Elasticsearch highlighting
  - Wrap matching keywords in `<mark>` tags
  - Display in search results

- [ ] 4.3.2: Show match indicators
  - Badge showing "Keyword match" vs "Semantic match"
  - Confidence score visualization
  - "Popular choice" badge (based on selection frequency)

- [ ] 4.3.3: Add "Did you mean?" suggestions
  - Use Elasticsearch suggest API
  - Show for queries with few results
  - Clickable alternative queries

- [ ] 4.3.4: Related searches
  - Based on ItemPartidaMapping
  - "Users who searched X also searched Y"
  - Display below search results

**Deliverable:** Enhanced search results UI

---

## Phase 5: Analytics & Optimization

**Duration:** 1 week
**Goal:** Monitor search performance and optimize based on data

### Task 5.1: Search Analytics Tracking

**Owner:** Backend Dev
**Duration:** 2 days
**Priority:** Medium

**Subtasks:**

- [ ] 5.1.1: Create `SearchQuery` model

  ```python
  class SearchQuery(models.Model):
      query_text = models.CharField(max_length=500)
      query_normalized = models.CharField(max_length=500, db_index=True)
      result_count = models.IntegerField()
      top_result_id = models.IntegerField(null=True)
      selected_result_id = models.IntegerField(null=True)
      selected_rank = models.IntegerField(null=True)
      search_mode = models.CharField(max_length=20)  # 'keyword', 'semantic', 'hybrid'
      user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
      session_key = models.CharField(max_length=40)
      created_at = models.DateTimeField(auto_now_add=True)
  ```

- [ ] 5.1.2: Add tracking to `buscar_partidas` view
  - Log every search query
  - Log selection (link with ItemPartidaMapping)
  - Async logging (don't slow down search)

- [ ] 5.1.3: Create analytics aggregation task

  ```python
  @shared_task
  def aggregate_search_analytics():
      """
      Run daily to aggregate search analytics.
      """
      # Top searches
      top_queries = SearchQuery.objects.values('query_normalized').annotate(
          count=Count('id')
      ).order_by('-count')[:100]

      # Zero-result searches
      zero_results = SearchQuery.objects.filter(result_count=0)

      # Average results per query
      avg_results = SearchQuery.objects.aggregate(Avg('result_count'))

      # Selection position distribution
      selection_distribution = SearchQuery.objects.exclude(
          selected_rank__isnull=True
      ).values('selected_rank').annotate(count=Count('id'))

      # Store in SearchAnalyticsSummary model
      # ...
  ```

**Deliverable:** Search analytics tracking in place

---

### Task 5.2: Analytics Dashboard

**Owner:** Backend Dev + Frontend Dev
**Duration:** 2 days
**Priority:** Medium

**Subtasks:**

- [ ] 5.2.1: Create analytics view
  - File: `admintools/views.py`
  - View: `SearchAnalyticsView`

- [ ] 5.2.2: Display key metrics
  - Total searches (last 30 days)
  - Zero-result rate
  - Average results per query
  - Selection position distribution (chart)
  - Keyword vs Semantic performance (if A/B testing)

- [ ] 5.2.3: Top searches table
  - Top 100 search queries
  - Click-through rate
  - Average result count
  - Actions: "Test this query", "Add to test dataset"

- [ ] 5.2.4: Zero-result searches
  - List all queries with 0 results
  - Manual review interface
  - Action: "Add keyword suggestion for partida X"

- [ ] 5.2.5: Create charts
  - Chart.js or similar
  - Search volume over time
  - Selection position distribution
  - Keyword vs semantic performance

**Deliverable:** Analytics dashboard at `/admin/elasticsearch/analytics/`

---

### Task 5.3: Automated Quality Monitoring

**Owner:** Backend Dev
**Duration:** 1 day
**Priority:** Low

**Subtasks:**

- [ ] 5.3.1: Create quality monitoring task

  ```python
  @shared_task
  def monitor_search_quality():
      """
      Run test queries weekly to detect regressions.
      """
      # Load test queries
      with open('MiCasillero/fixtures/test_queries.json') as f:
          test_data = json.load(f)

      # Run evaluation
      call_command('evaluate_search_quality', '--compare')

      # Check for regressions
      latest_report = get_latest_evaluation_report()

      if latest_report['zero_result_rate'] > 0.10:  # More than 10%
          # Send alert
          send_alert('Search quality degraded: High zero-result rate')
  ```

- [ ] 5.3.2: Add to Celery beat schedule

  ```python
  'monitor-search-quality': {
      'task': 'admintools.tasks.monitor_search_quality',
      'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Every Monday at 6 AM
  }
  ```

- [ ] 5.3.3: Create alert system
  - Email alerts for quality degradation
  - Slack webhook (optional)
  - Admin notification in dashboard

**Deliverable:** Automated quality monitoring with alerts

---

## Success Metrics

### Search Quality Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Zero-result rate | TBD | <5% | % of queries returning 0 results |
| Precision@1 | TBD | >70% | % of top results that are relevant |
| Precision@5 | TBD | >85% | % of top 5 results that are relevant |
| MRR (Mean Reciprocal Rank) | TBD | >0.75 | Average 1/rank of first relevant result |
| Avg results per query | TBD | 5-15 | Sweet spot: not too few, not too many |

### User Behavior Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Selection in top 3 | >60% | % of users selecting top 3 results |
| Selection in top 5 | >75% | % of users selecting top 5 results |
| Query refinement rate | <30% | % of users changing query after search |
| Search-to-selection time | <30s | Average time from search to selection |

### Learning Pipeline Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| New mappings per week | >100 | ItemPartidaMapping records created |
| Keyword enrichment rate | +5% monthly | % increase in keywords from user data |
| Staff override rate | <10% | % of AI suggestions corrected by staff |
| Auto-approval rate | >50% | % of suggestions auto-approved (high frequency) |

### System Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search response time | <300ms | 95th percentile |
| Index rebuild time | <5min | For 4,682 documents |
| Keyword generation time | <2hrs | For all 7,524 partidas |
| Celery task success rate | >95% | % of tasks completing successfully |

---

## Maintenance & Monitoring

### Daily Tasks (Automated)

- [ ] Analyze new ItemPartidaMapping records (2 AM)
- [ ] Enrich keywords from approved suggestions (3 AM)
- [ ] Aggregate search analytics (4 AM)
- [ ] Backup task history (5 AM)

### Weekly Tasks (Automated)

- [ ] Run search quality evaluation (Monday 6 AM)
- [ ] Generate analytics report (Sunday 8 AM)
- [ ] Clean old task history (>90 days old)

### Monthly Tasks (Manual)

- [ ] Review keyword suggestions dashboard
- [ ] Analyze search analytics trends
- [ ] Update test query dataset
- [ ] Review and approve/reject pending keyword suggestions

### Quarterly Tasks (Manual)

- [ ] Full search quality audit
- [ ] Re-evaluate AI model performance
- [ ] Consider keyword regeneration if new models available
- [ ] Review and update search algorithm weights

---

## Rollback & Recovery Plans

### Keyword Regeneration Rollback

**Scenario:** New keywords perform worse than old ones

**Steps:**

1. Restore from backup:

   ```sql
   -- Load backup CSV
   COPY temp_partidas_backup FROM '/tmp/partidas_keywords_backup_2025-10-20.csv' CSV HEADER;

   -- Restore keywords
   UPDATE "MiCasillero_partidaarancelaria" p
   SET search_keywords = b.search_keywords
   FROM temp_partidas_backup b
   WHERE p.id = b.id;
   ```

2. Rebuild Elasticsearch index:

   ```bash
   python manage.py search_index --rebuild
   ```

3. Verify restoration with evaluation script

### Elasticsearch Index Recovery

**Scenario:** Index becomes corrupted or deleted accidentally

**Steps:**

1. Delete corrupted index:

   ```bash
   python manage.py search_index --delete -f
   ```

2. Rebuild from database:

   ```bash
   python manage.py search_index --create
   python manage.py search_index --populate
   ```

3. Verify document count matches expected

### Task Queue Recovery

**Scenario:** Celery tasks stuck or failing

**Steps:**

1. Inspect Celery workers:

   ```bash
   celery -A SicargaBox inspect active
   ```

2. Purge stuck tasks:

   ```bash
   celery -A SicargaBox purge
   ```

3. Restart workers:

   ```bash
   # Graceful restart
   celery -A SicargaBox control shutdown
   celery -A SicargaBox worker -l info &
   ```

4. Retry failed tasks from TaskHistory

---

## Cost Estimates

### One-Time Costs

**Keyword Regeneration (if using Claude 3.5 Sonnet):**

- 7,524 partidas × $0.003/request (input) = $22.57
- 7,524 partidas × $0.015/request (output) = $112.86
- **Total:** ~$135

**Embedding Generation (OpenAI text-embedding-3-small):**

- 7,524 partidas × $0.00002/1K tokens = ~$5
- **Total:** ~$5

### Recurring Costs

**Daily Learning Pipeline:**

- ~100 new mappings/day
- Analysis task: <$0.01
- Enrichment: free (database operations)

**Weekly Quality Monitoring:**

- 100 test queries × $0.00002 = <$0.01

**Monthly Total:** <$1

---

## Dependencies & Prerequisites

### Software Requirements

- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Elasticsearch 8.19+
- Node.js (for frontend builds)

### Python Packages

```bash
celery>=5.3.0
redis>=5.0.0
django-celery-results>=2.5.0
django-celery-beat>=2.5.0
openai>=1.0.0
anthropic>=0.18.0
elasticsearch>=8.17.0
django-elasticsearch-dsl>=8.0
```

### API Keys Required

- OpenAI API key (for embeddings)
- DeepSeek API key OR OpenAI key (for keyword generation)
- Anthropic API key (optional, for Claude models)

### Infrastructure

- Elasticsearch server (localhost:9200)
- Redis server (localhost:6379)
- PostgreSQL database

---

## Next Steps After Planning

1. **Review & Approve Plan**
   - Tech lead review
   - Product owner approval
   - Budget approval

2. **Prioritize Phases**
   - Confirm sprint schedule
   - Allocate resources
   - Identify dependencies

3. **Begin Phase 0**
   - Create test dataset
   - Run baseline evaluation
   - Make keyword regeneration decision

4. **Set Up Development Environment**
   - Install Celery & Redis
   - Configure development settings
   - Set up test Elasticsearch instance

5. **Begin Implementation**
   - Follow sprint plan
   - Daily standups to track progress
   - Weekly demos to stakeholders

---

**Document Version:** 1.0
**Last Updated:** 2025-10-20
**Author:** Development Team
**Status:** Draft - Awaiting Approval

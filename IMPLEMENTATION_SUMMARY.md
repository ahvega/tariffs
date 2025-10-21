# Search Keyword Improvement - Implementation Summary

## Quick Reference

**Full Plan:** [SEARCH_KEYWORD_IMPROVEMENT_PLAN.md](./SEARCH_KEYWORD_IMPROVEMENT_PLAN.md)

---

## Key Observations from Current Keywords

Looking at sample data, current AI-generated keywords show:

**Strengths:**
- Good coverage of synonyms and variations
- Technical and colloquial terms included
- Spanish language appropriate

**Potential Issues:**
- Some keywords may be too technical (e.g., "napa de fibras de celulosa revestida")
- Possibly missing common user search terms
- Unknown which AI model/version generated them
- Need evaluation against real user queries

---

## Recommended Approach

### Phase 0: CRITICAL - Evaluate Before Rebuilding (3-4 days)

**Don't rebuild keywords blindly!** First:

1. **Create Test Dataset** (4 hours)
   - 100 real-world search queries across 20 product categories
   - File: `backend/sicargabox/MiCasillero/fixtures/test_queries.json`

2. **Build Evaluation Script** (8 hours)
   - Management command: `evaluate_search_quality`
   - Measures: Zero-result rate, Precision@K, MRR
   - Generates HTML report

3. **Run Baseline** (2 hours)
   - Test current keywords against 100 queries
   - Document current performance
   - Identify problem areas

4. **Compare AI Models** (1 day)
   - Test 100 partidas with:
     - DeepSeek (current)
     - GPT-4o-mini ($0.15/1K tokens)
     - Claude 3.5 Sonnet ($3.00/1K tokens)
   - Human evaluation + automated testing

5. **Make Decision** (2 hours)
   - Keep current keywords?
   - Partial regeneration?
   - Full rebuild with new model?
   - **Decision drives next phases**

**Estimated Cost:**
- Full regeneration with Claude 3.5: ~$135
- Full regeneration with GPT-4o-mini: ~$20
- Embeddings (one-time): ~$5

---

### Phase 1: Infrastructure (1 week)

**Enables continuous improvement from user behavior**

- [ ] Celery + Redis setup
- [ ] User selection tracking (capture which partida users choose)
- [ ] Basic admin dashboard (Elasticsearch status)

**Why First?**
- Starts collecting valuable user data immediately
- Required for all future learning/automation

---

### Phase 2: Elasticsearch Admin UI (1 week)

**Makes Elasticsearch management accessible to non-technical staff**

- [ ] One-click index rebuild/delete/populate
- [ ] Keyword generation interface with progress tracking
- [ ] Task monitoring dashboard
- [ ] Task history with logs

**Key Features:**
- No command-line access needed
- Real-time progress bars
- Cost estimates before running
- Rollback capability

---

### Phase 3: Continuous Learning (1 week)

**System gets smarter over time from user behavior**

- [ ] Automated learning pipeline (runs nightly)
- [ ] Extract keywords from user searches
- [ ] Staff review interface for suggested keywords
- [ ] Auto-approval for high-frequency terms

**Example:**
- 10 users search "audifonos bluetooth" → select partida 8518.30.00.00
- System learns: add "audifonos bluetooth" to keywords
- Future searches match better

---

### Phase 4: Advanced Search (1 week)

**Semantic understanding, not just keyword matching**

- [ ] Vector embeddings generation
- [ ] Semantic search implementation
- [ ] Hybrid keyword + semantic ranking
- [ ] A/B testing framework

**Benefit:**
- Matches "laptop para juegos" even if keywords say "computadora gaming"
- Understands context and intent

---

### Phase 5: Analytics (1 week)

**Data-driven optimization**

- [ ] Search analytics tracking
- [ ] Dashboard with key metrics
- [ ] Automated quality monitoring
- [ ] Alerting for regressions

**Metrics Tracked:**
- Top searches
- Zero-result queries
- Selection position (are users picking top results?)
- Keyword vs semantic performance

---

## Critical Success Metrics

### Must Achieve (Phase 0 Baseline → Post-Implementation)

| Metric | Target | Impact |
|--------|--------|--------|
| Zero-result rate | <5% | Users find what they need |
| Precision@1 | >70% | Top result is usually relevant |
| Selection in top 3 | >60% | Users pick from first 3 results |
| Search response time | <300ms | Fast user experience |

---

## Task Checklist (Abbreviated)

### Week 0: Evaluation (MUST DO FIRST)
- [ ] 0.1: Create test dataset (100 queries)
- [ ] 0.2: Build evaluation script
- [ ] 0.3: Run baseline evaluation
- [ ] 0.4: Compare AI models
- [ ] 0.5: Make regeneration decision
- [ ] 0.6: Execute regeneration (if approved)

### Week 1: Infrastructure
- [ ] 1.1: Install Celery + Redis
- [ ] 1.2: Create admintools app
- [ ] 1.3: User selection tracking (frontend)
- [ ] 1.4: User selection tracking (backend)
- [ ] 1.5: Basic Elasticsearch dashboard

### Week 2: Admin UI
- [ ] 2.1: Celery task wrappers
- [ ] 2.2: Management actions interface
- [ ] 2.3: Real-time task status display
- [ ] 2.4: Task history table

### Week 3: Learning Pipeline
- [ ] 3.1: Learning analysis task
- [ ] 3.2: Keyword enrichment task
- [ ] 3.3: Staff override tracking
- [ ] 3.4: Keyword review interface

### Week 4: Advanced Search
- [ ] 4.1: Generate vector embeddings
- [ ] 4.2: Implement semantic search
- [ ] 4.3: Enhance search results UI

### Week 5: Analytics
- [ ] 5.1: Search analytics tracking
- [ ] 5.2: Analytics dashboard
- [ ] 5.3: Automated quality monitoring

---

## Quick Start Commands

### Evaluation (Week 0)
```bash
# Create test queries
# (Manual: edit backend/sicargabox/MiCasillero/fixtures/test_queries.json)

# Run baseline evaluation
python manage.py evaluate_search_quality --baseline

# Compare AI models
python manage.py compare_ai_models --model gpt-4o-mini --sample-size 100

# Run keyword regeneration (if approved)
python manage.py generate_search_keywords \
  --api-provider claude-3-5-sonnet \
  --batch-size 20

# Rebuild index
python manage.py search_index --rebuild

# Compare before/after
python manage.py evaluate_search_quality --compare
```

### Daily Operations (After Implementation)
```bash
# Start Celery worker
celery -A SicargaBox worker -l info

# Start Celery beat (scheduled tasks)
celery -A SicargaBox beat -l info

# Access admin UI
# Navigate to: http://localhost:8000/admin/elasticsearch/
```

---

## Risk Mitigation

### Risk: New keywords perform worse
**Mitigation:**
- Always backup before regeneration
- Run comparison evaluation before/after
- Rollback script ready: `restore_keywords_from_backup.sql`

### Risk: Celery tasks fail silently
**Mitigation:**
- TaskHistory tracks all executions
- Email alerts on failure
- Retry logic built-in
- Manual retry from admin UI

### Risk: Elasticsearch index corruption
**Mitigation:**
- One-click rebuild from Django database
- No data loss (source of truth is PostgreSQL)
- Index snapshots (if using production Elasticsearch cluster)

---

## Cost Breakdown

### Development (One-time)
- 5 weeks × 40 hours = 200 developer hours

### AI API Costs
- Keyword regeneration (one-time): $20-135 (depends on model)
- Embeddings (one-time): ~$5
- Monthly learning pipeline: <$1

### Infrastructure
- Redis: Free (local/Docker)
- Elasticsearch: Free (local/Docker) or $50-200/month (managed)
- Celery: Free (open source)

**Total Monthly Recurring:** <$5 (if using local infrastructure)

---

## Next Actions

1. **Review this plan** with team
2. **Allocate resources** (1 backend dev + 0.5 frontend dev)
3. **Get budget approval** for AI API costs
4. **Start Week 0** immediately (evaluation phase)
5. **Daily standups** during implementation
6. **Weekly demos** to stakeholders

---

## Questions to Answer

Before starting implementation:

1. **AI Provider:** Which model for keyword generation? (impacts cost)
2. **Celery Broker:** Redis available or need RabbitMQ?
3. **User Testing:** Can we A/B test with real users?
4. **Staff Time:** Who reviews keyword suggestions? Hours/week?
5. **Elasticsearch:** Local sufficient or need production cluster?

---

**Full Details:** See [SEARCH_KEYWORD_IMPROVEMENT_PLAN.md](./SEARCH_KEYWORD_IMPROVEMENT_PLAN.md) (23,000 words, complete task breakdown)

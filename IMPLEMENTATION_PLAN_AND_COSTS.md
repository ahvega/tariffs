# Implementation Plan & Cost Estimates
# Phase 1 Post-Completion Analysis

**Date:** 2025-10-23
**Status:** Phase 1 Complete - Ready for Next Steps

---

## Phase 1 Completion Summary

### ✅ Completed Tasks

1. **Migration Created** - `0020_add_hierarchy_fields.py`
2. **Model Updated** - Removed `parent_category`, added 6 hierarchy fields
3. **Populate Command** - Created `populate_hierarchy_fields.py`
4. **Hierarchy Data Populated** - 7,508 of 7,524 partidas (99.8%)
5. **Admin Interface Updated** - Updated to use new hierarchy fields

### 📊 Current Database State

**Total Partidas:** 7,524

**Bilingual Keyword Coverage:**
- ✅ With bilingual keywords: 7,452 (99.0%)
- ⚠️  Spanish only: 1 (0.0%)
- ❌ Empty: 71 (0.9%)

**"Los demás" Analysis:**
- Total "Los demás" partidas: **1,328** (17.7% of database)
- With existing keywords (>5): **1,289** (97.1%)
- Without keywords (≤5): **39** (2.9%)

**Hierarchy Population:**
- Successfully populated: 7,508 (99.8%)
- Errors (irregular codes): 16 (0.2%)

---

## Remaining Tasks & Cost Estimates

### Option A: Minimal Approach - Fix Only Empty "Los demás"

**Scope:** Regenerate 39 "Los demás" partidas with no keywords

**Provider:** Claude 3.5 Sonnet (best quality for catch-all categories)

**Cost Estimate:**
- Tokens: ~39,000 (1,000 per partida)
- Cost: **$0.40**
- Time: **~1.3 minutes**

**Pros:**
- ✅ Very low cost
- ✅ Quick implementation
- ✅ Fixes all empty categories

**Cons:**
- ⚠️  Doesn't improve existing 1,289 "Los demás" with keywords
- ⚠️  Existing may have overlapping keywords with siblings

---

### Option B: Comprehensive Approach - Regenerate All "Los demás"

**Scope:** Regenerate ALL 1,328 "Los demás" partidas with proper sibling exclusion

**Provider:** Claude 3.5 Sonnet (premium quality)

**Cost Estimate:**
- Tokens: ~1,328,000 (1,000 per partida)
- Cost: **$13.55**
- Time: **~44 minutes**

**Breakdown:**
- Input tokens: 531,200 @ $3/MTok = $1.59
- Output tokens: 796,800 @ $15/MTok = $11.95
- **Total: $13.55**

**Pros:**
- ✅ Ensures NO overlap between siblings
- ✅ Premium quality for all catch-all categories
- ✅ Consistent with CKOP Phase 2 strategy

**Cons:**
- ⚠️  Higher cost (~$14)
- ⚠️  Takes 44 minutes

---

### Option C: Tiered Approach (RECOMMENDED)

**Scope:** Following COMPREHENSIVE_KEYWORD_OPTIMIZATION_PLAN.md

#### **Tier 1: Top 200 Most Common Partidas**
- **Provider:** Claude 3.5 Sonnet
- **Cost:** ~$2-3
- **Time:** ~7 minutes
- **Coverage:** 40-60% of actual user queries

#### **Tier 2: "Los demás" Without Keywords**
- **Scope:** 39 partidas
- **Provider:** Claude 3.5 Sonnet
- **Cost:** $0.40
- **Time:** 1.3 minutes

#### **Tier 3: All Remaining "Los demás"** (Optional)
- **Scope:** Remaining 1,289 "Los demás"
- **Provider:** Claude 3.5 Sonnet
- **Cost:** ~$13
- **Time:** ~43 minutes

#### **Total for Tier 1 + Tier 2:**
- **Cost:** ~$2.40-3.40
- **Time:** ~8-9 minutes
- **Impact:** High (covers most common items + fixes all empty)

#### **Total for All Tiers:**
- **Cost:** ~$15.40-16.40
- **Time:** ~51-52 minutes
- **Impact:** Maximum (complete optimization)

---

## Recommended Implementation Order

### **PHASE 2A: Immediate Fixes (TODAY)**

**Priority:** HIGH
**Cost:** $0.40
**Time:** 5-10 minutes

```bash
# Step 1: Update generate_search_keywords.py to use sibling keywords
# Step 2: Test with one "Los demás" partida
# Step 3: Regenerate 39 empty "Los demás" with Claude

python manage.py generate_search_keywords \
  --api-provider=anthropic \
  --los-demas-only \
  --batch-size=10
```

**Tasks:**
1. ✅ Update `generate_search_keywords.py`:
   - Use `heading_code` for sibling detection
   - Collect sibling keywords (not just descriptions)
   - Pass excluded keywords to AI prompt
2. ⏳ Test with 1-2 "Los demás" partidas
3. ⏳ Run on all 39 empty partidas
4. ⏳ Verify no keyword overlap with siblings

---

### **PHASE 2B: Top 200 Optimization (THIS WEEK)**

**Priority:** MEDIUM-HIGH
**Cost:** $2-3
**Time:** ~7 minutes + analysis time

**Prerequisites:**
1. Analyze quote/shipment history OR
2. Use industry research for top items

**Tasks:**
1. Identify top 200 most-shipped partidas
2. Create `top_200_partidas.json` file
3. Regenerate with Claude:
```bash
python manage.py generate_search_keywords \
  --api-provider=anthropic \
  --partidas-file=top_200_partidas.json \
  --batch-size=50
```
4. Compare quality with DeepSeek baseline
5. Measure impact on search accuracy

---

### **PHASE 2C: Full "Los demás" Regeneration (OPTIONAL)**

**Priority:** LOW-MEDIUM
**Cost:** $13
**Time:** ~44 minutes

**When to do this:**
- After Phase 2A/2B results are validated
- If keyword overlap issues persist
- If search accuracy needs improvement

**Tasks:**
1. Regenerate all 1,328 "Los demás" with Claude
2. Verify sibling exclusion working correctly
3. Update Elasticsearch index
4. Run quality tests

---

## Code Changes Required

### 1. Update `generate_search_keywords.py`

**Location:** `MiCasillero/management/commands/generate_search_keywords.py`

**Changes:**

#### A. Sibling Detection (Lines 67-69)
```python
# OLD (description-based, unreliable)
siblings = PartidaArancelaria.objects.filter(
    descripcion__contains=parent_desc
).exclude(id=partida.id)[:20]

# NEW (hierarchy-based, precise)
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida.heading_code
).exclude(id=partida.id).order_by('item_no')
```

#### B. Keyword Collection (Lines 72-95)
```python
# OLD (only descriptions)
sibling_specific_descs = [
    s.descripcion.split('|')[0].strip()
    for s in siblings
]
excluded_terms = sibling_specific_descs

# NEW (actual keywords)
if is_others:
    excluded_keywords = []
    for sibling in siblings:
        if sibling.search_keywords:
            excluded_keywords.extend(sibling.search_keywords)

    # Deduplicate and normalize
    excluded_keywords = list(set([kw.lower().strip() for kw in excluded_keywords]))
else:
    excluded_keywords = []
```

#### C. AI Prompt Update (Lines 173-198)
```python
# OLD
prompt = f"""
- Términos a excluir: {json.dumps(excluded_terms)}
"""

# NEW
prompt = f"""
CRITICAL: This is a "Los demás" (catch-all) category.

SIBLING PARTIDAS (specific categories at same level):
{json.dumps([{
    'code': s.item_no,
    'desc': s.descripcion.split('|')[0].strip(),
    'keywords_count': len(s.search_keywords) if s.search_keywords else 0
} for s in siblings], indent=2)}

KEYWORDS TO EXCLUDE (already used by siblings):
{json.dumps(excluded_keywords[:50], indent=2)}  # Show first 50
Total excluded: {len(excluded_keywords)} keywords

INSTRUCTIONS:
1. Generate keywords for items NOT matching any sibling
2. DO NOT use any of the excluded keywords
3. DO NOT use variations of excluded keywords
4. Focus on generic terms within parent category
5. Include bilingual keywords (English + Spanish)
"""
```

#### D. Add --los-demas-only flag
```python
def add_arguments(self, parser):
    # ... existing arguments ...
    parser.add_argument(
        '--los-demas-only',
        action='store_true',
        help='Process only "Los demás" partidas',
    )

def handle(self, *args, **options):
    if options['los_demas_only']:
        # Filter for Los demás partidas
        partidas = partidas.filter(
            descripcion__iregex=r'^(los|las) demás'
        )
```

---

### 2. Clean Up Old Commands

**Delete obsolete management commands:**
- `clean_parent_partidas.py` (uses old `parent_category`)
- `update_parent_relations.py` (uses old `parent_category`)

**Replace with:**
- `populate_hierarchy_fields.py` (already created)

---

### 3. Update Documentation

**Files to update:**
- `REGENERATION_STATE.md` - Add Phase 1 completion
- `RESUME_AFTER_REBOOT.md` - Update with new hierarchy fields

---

## Quality Verification Tests

### Test 1: Sibling Exclusion Test

**Example: Horses (0101.2X)**

```python
# Get siblings
partida_others = PartidaArancelaria.objects.get(item_no="0101.29.00.00")
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida_others.heading_code
).exclude(id=partida_others.id)

# Check for overlap
others_kw = set([k.lower() for k in partida_others.search_keywords])
for s in siblings:
    sibling_kw = set([k.lower() for k in s.search_keywords])
    overlap = others_kw & sibling_kw
    if overlap:
        print(f"OVERLAP DETECTED: {s.item_no}")
        print(f"  Overlapping keywords: {overlap}")
```

**Expected:** ZERO overlap

---

### Test 2: Coverage Test

**Check that "Los demás" covers parent category:**

```python
partida = PartidaArancelaria.objects.get(item_no="0101.29.00.00")
parent_desc = partida.descripcion.split('|')[1].strip()  # "Caballos"

# Keywords should include generic horse terms
expected_terms = ["horses", "caballos", "work horses", "riding horses"]
actual_kw = [k.lower() for k in partida.search_keywords]

for term in expected_terms:
    if term.lower() not in actual_kw:
        print(f"MISSING: {term}")
```

**Expected:** All generic parent terms present

---

## Budget Summary

| Phase | Scope | Provider | Cost | Time | Priority |
|-------|-------|----------|------|------|----------|
| **2A** | 39 empty "Los demás" | Claude | $0.40 | 1.3 min | ⭐⭐⭐ HIGH |
| **2B** | Top 200 partidas | Claude | $2-3 | 7 min | ⭐⭐ MEDIUM |
| **2C** | All 1,328 "Los demás" | Claude | $13 | 44 min | ⭐ LOW |
| **Total (2A+2B)** | 239 partidas | Claude | **$2.40-3.40** | **8-9 min** | **RECOMMENDED** |
| **Total (All)** | 1,528 partidas | Claude | **$15.40-16.40** | **52 min** | COMPREHENSIVE |

---

## Success Metrics

### Phase 2A Success Criteria:
- ✅ All 39 "Los demás" have >20 keywords
- ✅ ZERO overlap with sibling keywords
- ✅ Keywords include both English and Spanish
- ✅ Generic terms from parent category present

### Phase 2B Success Criteria:
- ✅ Top 200 keywords higher quality than DeepSeek baseline
- ✅ Search accuracy improved for common items
- ✅ User search results more relevant

### Overall Success:
- ✅ 100% of partidas have bilingual keywords
- ✅ "Los demás" categories properly differentiated
- ✅ Search results don't show overlapping categories

---

## Next Immediate Actions

1. **Update `generate_search_keywords.py`** (30 minutes)
2. **Test with 1-2 "Los demás" partidas** (5 minutes)
3. **Run Phase 2A** - 39 empty partidas ($0.40, 10 minutes)
4. **Verify results** - Check for overlaps (10 minutes)
5. **Update REGENERATION_STATE.md** (5 minutes)

**Total Time:** ~1 hour
**Total Cost:** $0.40

---

## Long-Term Roadmap

### Phase 3: RAG Implementation (Future)
- Setup Supabase vector store
- Load "Notas Explicativas"
- Enhance ambiguous categories
- **Cost:** ~$50-100 (Supabase setup)

### Phase 4: Continuous Improvement
- Track zero-result queries
- Monthly keyword refinement
- A/B testing of search algorithms
- **Cost:** Ongoing, minimal

---

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Status:** Ready for Implementation

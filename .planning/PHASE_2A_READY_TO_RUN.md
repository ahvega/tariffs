# Phase 2A - Ready to Execute
**Date:** 2025-10-23
**Status:** ✅ Code Updated - Ready to Run

---

## ✅ Completed Preparation

### 1. Code Updates
- ✅ `generate_search_keywords.py` updated with:
  - Hierarchy-based sibling detection (`heading_code`)
  - Sibling keyword collection and exclusion
  - Enhanced AI prompt with excluded keywords
  - `--los-demas-only` flag for filtering

- ✅ `models.py` updated with 6 new hierarchy fields
- ✅ `admin.py` updated to display hierarchy fields
- ✅ Old commands deprecated
- ✅ Hierarchy data populated (7,508/7,524 = 99.8%)

### 2. Documentation Created
- ✅ `CKOP_PHASE-01.md` - Phase 1 implementation review
- ✅ `IMPLEMENTATION_PLAN_AND_COSTS.md` - Cost estimates and roadmap
- ✅ `PHASE_2A_READY_TO_RUN.md` - This file

---

## 💰 Claude API Top-Up Recommendation

### **Recommended: $10**

**Why $10?**
- Covers Phase 2A: $0.40 ✅
- Covers Phase 2B: $2-3 ✅
- Buffer for testing/retries: $1-2 ✅
- Extra buffer: $4-5 ✅

**Alternative Options:**
- **Minimal:** $5 (just 2A + 2B, tight)
- **Comprehensive:** $20 (includes all phases + ample buffer)

---

## 🚀 Phase 2A Execution Plan

### **Scope**
- **Partidas:** 39 "Los demás" without keywords
- **Provider:** Claude 3.5 Sonnet (anthropic)
- **Cost:** $0.40
- **Time:** ~10-15 minutes total

### **Commands to Run**

#### Step 1: Test with 1 partida (dry-run)
```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

venv/Scripts/python.exe manage.py generate_search_keywords \
  --api-provider=anthropic \
  --los-demas-only \
  --limit=1 \
  --dry-run
```

**Expected output:**
- Should show 1 "Los demás" partida
- Display sibling information
- Show excluded keywords list
- Generate sample keywords

#### Step 2: Test with 1 partida (actual generation)
```bash
venv/Scripts/python.exe manage.py generate_search_keywords \
  --api-provider=anthropic \
  --los-demas-only \
  --limit=1
```

**Verify:**
- Keywords saved to database
- No overlap with sibling keywords
- Bilingual coverage (English + Spanish)

#### Step 3: Run on all 39 partidas
```bash
venv/Scripts/python.exe manage.py generate_search_keywords \
  --api-provider=anthropic \
  --los-demas-only \
  --batch-size=10
```

**Progress monitoring:**
- Process runs in ~10-15 minutes
- Batch size: 10 partidas per batch
- Total batches: 4 (39 partidas)

---

## ✅ Verification Steps

### 1. Check Keyword Coverage
```python
# In Django shell
from MiCasillero.models import PartidaArancelaria

# Get "Los demás" partidas
los_demas = PartidaArancelaria.objects.filter(
    descripcion__iregex=r'^(los|las) demás'
).filter(
    search_keywords__len__lte=5
)

print(f"Remaining without keywords: {los_demas.count()}")
# Should be 0 after Phase 2A
```

### 2. Check for Overlap
```python
# Test one "Los demás" partida for keyword overlap
partida = PartidaArancelaria.objects.get(item_no="0101.29.00.00")
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida.heading_code
).exclude(id=partida.id)

# Check for overlaps
others_kw = set([k.lower() for k in partida.search_keywords])
for s in siblings:
    sibling_kw = set([k.lower() for k in s.search_keywords])
    overlap = others_kw & sibling_kw
    if overlap:
        print(f"OVERLAP: {s.item_no}")
        print(f"  Keywords: {overlap}")

# Should print nothing (no overlaps)
```

### 3. Verify Bilingual Coverage
```python
import re

partida = PartidaArancelaria.objects.get(item_no="0101.29.00.00")

# Count English keywords (4+ letter words without accents)
en_kw = [k for k in partida.search_keywords if re.search(r'\b[a-z]{4,}\b', k)]

# Count Spanish keywords (with accents or common Spanish words)
es_kw = [k for k in partida.search_keywords if re.search(r'[áéíóúñ]', k, re.IGNORECASE)]

print(f"Total keywords: {len(partida.search_keywords)}")
print(f"English: {len(en_kw)}")
print(f"Spanish: {len(es_kw)}")

# Both should be >10
```

---

## 📊 Success Criteria

Phase 2A will be considered successful if:

- ✅ All 39 "Los demás" have >20 keywords
- ✅ ZERO keyword overlap with siblings
- ✅ >10 English keywords per partida
- ✅ >10 Spanish keywords per partida
- ✅ Keywords are relevant to parent category
- ✅ No errors during generation

---

## 🔧 Troubleshooting

### Issue: "No ANTHROPIC_API_KEY found"

**Solution:**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# If not set, add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### Issue: API Rate Limit

**Solution:**
- Reduce `--batch-size` to 5
- Add delays between batches (handled automatically)

### Issue: Keywords Still Overlap

**Cause:** Sibling didn't have keywords when "Los demás" was processed

**Solution:**
- Run siblings first, THEN "Los demás"
- Or regenerate the overlapping partida

---

## 📋 Post-Execution Checklist

After completing Phase 2A:

- [ ] Verify 0 partidas without keywords
- [ ] Check random samples for overlap
- [ ] Test search with some keywords
- [ ] Update `REGENERATION_STATE.md`
- [ ] Commit changes to git
- [ ] Consider Phase 2B (Top 200)

---

## 📈 Next Phase (Optional)

### Phase 2B: Top 200 Optimization

**When:** This week (after 2A validation)

**Steps:**
1. Analyze quote/shipment history OR
2. Use industry research
3. Identify top 200 most-common partidas
4. Create `top_200_partidas.json`
5. Regenerate with Claude:
```bash
venv/Scripts/python.exe manage.py generate_search_keywords \
  --api-provider=anthropic \
  --partidas-file=top_200_partidas.json \
  --batch-size=50
```

**Cost:** $2-3
**Time:** ~7 minutes
**Impact:** 40-60% of user queries

---

## 💾 Backup Recommendation

Before running Phase 2A, consider backing up:

```bash
# Backup database
pg_dump SicargaBox > backup_before_phase2a_$(date +%Y%m%d).sql

# Or just export current keywords
venv/Scripts/python.exe manage.py dumpdata MiCasillero.PartidaArancelaria \
  --output=partidas_backup_$(date +%Y%m%d).json
```

---

## 📞 Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Review `IMPLEMENTATION_PLAN_AND_COSTS.md`
3. Check Django debug toolbar
4. Review API usage in Anthropic console

---

**Status:** ✅ Ready to Execute
**Next Action:** Top up Claude API with $10, then run Step 1 (test)

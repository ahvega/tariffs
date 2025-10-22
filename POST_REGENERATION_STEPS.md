# Post-Regeneration Steps
# SicargaBox Bilingual Keyword Regeneration

**Date:** 2025-10-22
**Status:** Regeneration in progress (152/7524 - 2.0%)

---

## Overview

This document outlines the steps to complete after the bilingual keyword regeneration finishes.

## Current Regeneration Status

- **Started:** 2025-10-22 ~00:24
- **Process ID:** fcb929
- **Log file:** `E:/MyDevTools/tariffs/logs/keyword_generation_deepseek.log`
- **API Provider:** DeepSeek
- **Batch size:** 100
- **Estimated completion:** ~90 minutes total
- **Cost:** $2-3

## Verification Steps (After Completion)

### Step 1: Verify Completion Statistics

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

# Check total keywords generated
venv/Scripts/python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SicargaBox.settings')
django.setup()
from MiCasillero.models import PartidaArancelaria
import re

total = PartidaArancelaria.objects.count()
with_keywords = PartidaArancelaria.objects.exclude(search_keywords=[]).count()

# Sample bilingual quality
sample = list(PartidaArancelaria.objects.all()[100:110])
bilingual_count = 0
for p in sample:
    en_count = len([k for k in p.search_keywords if re.search(r'\b[a-z]{3,}\b', k)])
    if en_count >= 5:  # At least 5 English keywords
        bilingual_count += 1

print(f'Total partidas: {total}')
print(f'With keywords: {with_keywords} ({(with_keywords/total)*100:.1f}%)')
print(f'Bilingual quality (sample): {bilingual_count}/10 ({(bilingual_count/10)*100:.0f}%)')
"
```

**Expected Output:**
```
Total partidas: 7524
With keywords: 7524 (100.0%)
Bilingual quality (sample): 10/10 (100%)
```

### Step 2: Sample Quality Check

```bash
# Check specific high-traffic items
venv/Scripts/python.exe manage.py shell
```

```python
from MiCasillero.models import PartidaArancelaria
import json

# Check smartphone keywords
smartphones = PartidaArancelaria.objects.filter(descripcion__icontains='teléfono inteligente').first()
if smartphones:
    print(f"Partida: {smartphones.item_no}")
    print(f"Description: {smartphones.descripcion[:80]}")
    print(f"Total keywords: {len(smartphones.search_keywords)}")
    print("\nKeywords:")
    for kw in smartphones.search_keywords[:20]:
        print(f"  - {kw}")
```

### Step 3: Check Log for Errors

```bash
cd E:/MyDevTools/tariffs/logs

# Check for any errors or warnings
grep -i "error\|warning\|failed" keyword_generation_deepseek.log

# Count total processed
grep -c "Keywords generados:" keyword_generation_deepseek.log
```

Should show: `7524` (all partidas processed)

## Elasticsearch Rebuild

### Prerequisites
✅ Elasticsearch running on localhost:9200 (verified: status=green)

### Step 4: Rebuild Elasticsearch Index

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

# Option 1: Full rebuild (recommended)
venv/Scripts/python.exe manage.py search_index --rebuild

# Option 2: Populate only (if index exists)
# venv/Scripts/python.exe manage.py search_index --populate
```

**Expected output:**
```
Deleting index 'partidaarancelaria'
Creating index 'partidaarancelaria'
Indexing 7524 'PartidaArancelaria' objects
Successfully indexed 7524 documents
```

**Estimated time:** 5-10 minutes

### Step 5: Verify Elasticsearch Index

```bash
# Check index status
curl -s http://localhost:9200/partidaarancelaria/_count?pretty

# Search test with bilingual query
curl -s -X GET "http://localhost:9200/partidaarancelaria/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "multi_match": {
        "query": "smartphone",
        "fields": ["descripcion", "search_keywords"]
      }
    },
    "size": 3
  }'
```

**Expected:** Should return relevant smartphone partidas

## Search Quality Testing

### Step 6: Test Bilingual Search

Create test queries file:

```bash
cd E:/MyDevTools/tariffs

cat > test_queries.txt << 'EOF'
# English queries
smartphone
laptop
running shoes
USB cable
wireless headphones
iPhone
bluetooth speaker
power adapter
sneakers
cell phone

# Spanish queries
teléfono inteligente
computadora portátil
zapatos deportivos
cable USB
auriculares inalámbricos
celular
bocina bluetooth
adaptador de corriente
tenis
móvil

# Mixed queries
iPhone charger
Samsung phone
Nike shoes
Adidas sneakers
laptop Dell
EOF
```

### Step 7: Manual Search Testing

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
venv/Scripts/python.exe manage.py shell
```

```python
from MiCasillero.documents import PartidaArancelariaDocument

# Test English query
results = PartidaArancelariaDocument.search().query("match", search_keywords="smartphone")[:5]
print("Results for 'smartphone':")
for r in results:
    print(f"  {r.item_no}: {r.descripcion[:60]}")

# Test Spanish query
results = PartidaArancelariaDocument.search().query("match", search_keywords="teléfono inteligente")[:5]
print("\nResults for 'teléfono inteligente':")
for r in results:
    print(f"  {r.item_no}: {r.descripcion[:60]}")
```

## Expected Results

Based on the comprehensive plan:

### Baseline (Before - Spanish-only):
- Precision@5: Low or 0% for English queries
- Zero-result rate: ~100% for English queries

### After Bilingual (DeepSeek):
- Precision@5: **88-92%** for both English and Spanish
- Zero-result rate: **<10%**
- Bilingual coverage: **100%** of partidas

## Success Criteria

✅ All 7,524 partidas have keywords
✅ Keywords are bilingual (English + Spanish)
✅ Average 20-40 keywords per partida
✅ Elasticsearch index rebuilt successfully
✅ Search returns relevant results for English queries
✅ Search returns relevant results for Spanish queries
✅ Technical terms preserved (USB-C, HDMI, Bluetooth, etc.)

## Next Phase (After This)

According to the comprehensive plan, Phase 1 focuses on:
- Hierarchy enhancement
- Trend-based prioritization for top 200 items
- Using Claude for high-quality keywords on top items

## Troubleshooting

### If Regeneration Failed or Incomplete

```bash
# Check where it stopped
grep -c "Keywords generados:" logs/keyword_generation_deepseek.log

# Get the last processed item
tail -50 logs/keyword_generation_deepseek.log | grep "Partida:"

# Resume from specific ID if needed
cd backend/sicargabox
venv/Scripts/python.exe manage.py generate_search_keywords \
  --batch-size=100 \
  --api-provider=deepseek \
  --start-from=LAST_ID
```

### If Elasticsearch Rebuild Fails

```bash
# Delete and recreate index
venv/Scripts/python.exe manage.py search_index --delete
venv/Scripts/python.exe manage.py search_index --create
venv/Scripts/python.exe manage.py search_index --populate
```

## Documentation

Once complete, document results in:
- Update [COMPREHENSIVE_KEYWORD_OPTIMIZATION_PLAN.md](COMPREHENSIVE_KEYWORD_OPTIMIZATION_PLAN.md) Phase 0 status
- Create performance report with before/after metrics
- Update [CLAUDE.md](CLAUDE.md) with bilingual keyword status

---

**Last updated:** 2025-10-22 00:56

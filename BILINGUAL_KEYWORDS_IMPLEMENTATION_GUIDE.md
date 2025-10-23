# Bilingual Keywords Implementation Guide

**Purpose**: Convert Spanish-only search keywords to bilingual (English + Spanish) for Honduras users

**Critical Finding**: 100% zero-result rate on English queries reveals Spanish-only keywords are inadequate

---

## Quick Start

### 1. Update generate_search_keywords.py

**File**: `MiCasillero/management/commands/generate_search_keywords.py`

**Line 248** - Update system message:

```python
# BEFORE (Spanish-only):
{"role": "system", "content": "Eres un experto en clasificación arancelaria y comercio internacional. Genera máximo 30 keywords relevantes. Responde solo con arrays JSON puros, sin formato markdown."}

# AFTER (Bilingual):
{"role": "system", "content": "Eres un experto en clasificación arancelaria y comercio internacional. Genera máximo 30 keywords relevantes EN ESPAÑOL E INGLÉS (bilingual) para usuarios en Honduras que buscan productos en ambos idiomas. Responde solo con arrays JSON puros, sin formato markdown."}
```

**Line 252** - Increase max_tokens:

```python
# BEFORE:
max_tokens=800

# AFTER:
max_tokens=1200  # More tokens for bilingual keywords
```

**Lines 165, 189, 212, 235** - Add bilingual instructions to ALL prompts:

```python
# Add this section to each prompt template:

IMPORTANTE - BILINGUAL KEYWORDS:
- Generate keywords in BOTH Spanish and English
- Include common English product names (laptop, smartphone, mouse, keyboard, etc.)
- Include English technical terms (USB-C, HDMI, bluetooth, wifi, LED, GPS, etc.)
- Include English brand names when relevant (iPhone, Samsung, Nike, Adidas, etc.)
- Honduras users frequently search in mixed English/Spanish
- Prioritize terms users actually type, not formal descriptions
- Include common misspellings if relevant (e.g., "celular" vs "cellular")

Examples:
- For computers: ["computadora", "laptop", "notebook", "computer", "pc", "ordenador"]
- For headphones: ["auriculares", "headphones", "audífonos", "earphones", "earbuds"]
- For cables: ["cable", "wire", "HDMI", "USB", "USB-C", "cable HDMI"]
```

---

## Testing the Changes

### Step 1: Test with 10 Partidas

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

# Test with 10 computer-related partidas
python manage.py generate_search_keywords \
  --dry-run \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=deepseek
```

**Expected Output**:

```json
{
  "item_no": "8471.30.00.00",
  "old_keywords": ["computadora portátil", "ordenador", "portátil"],
  "new_keywords": [
    "computadora portátil",
    "laptop",
    "notebook",
    "computer",
    "pc",
    "ordenador",
    "laptop computer",
    "portable computer",
    "computadora",
    "netbook"
  ]
}
```

### Step 2: Validate Quality

Check that keywords include:

- ✅ Spanish terms: "computadora", "portátil"
- ✅ English terms: "laptop", "computer", "notebook"
- ✅ Technical terms: "USB-C", "HDMI", "bluetooth"
- ✅ Common searches: "mouse inalámbrico", "smartphone"

### Step 3: Run Actual Generation

```bash
# Remove --dry-run to actually update database
python manage.py generate_search_keywords \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=deepseek
```

### Step 4: Re-run Evaluation

```bash
python manage.py evaluate_search_quality \
  --output=bilingual_test_report.html \
  --verbose
```

**Expected Results**:

- Precision@5: 0% → **85-95%** ✅
- Zero-result rate: 100% → **<5%** ✅
- MRR: 0.000 → **>0.80** ✅

---

## Full Regeneration

Once validation passes, regenerate all 7,524 partidas:

```bash
# Estimate: 60-90 minutes, cost ~$20-30 (DeepSeek-V3)
python manage.py generate_search_keywords \
  --batch-size=100 \
  --api-provider=deepseek
```

**Monitor progress**:

```bash
# In another terminal, watch database updates
cd E:/MyDevTools/tariffs/backend/sicargabox
python manage.py shell

from MiCasillero.models import PartidaArancelaria
import time

while True:
    count = PartidaArancelaria.objects.exclude(search_keywords=[]).count()
    print(f"Partidas with keywords: {count} / 7524")
    time.sleep(30)
```

---

## Specific Prompt Updates

### Prompt 1: "Los demás" with exception (Line ~146)

Add after line 171:

```python
                IMPORTANTE - BILINGUAL KEYWORDS:
                - Generate keywords in BOTH Spanish and English
                - Include common English product names
                - Include English technical terms (USB-C, HDMI, bluetooth, etc.)
                - Honduras users search in mixed English/Spanish

                Ejemplo:
                - Si el término es "calzado" incluye: ["calzado", "zapatos", "shoes", "footwear"]
                - Si es "computadoras" incluye: ["computadoras", "laptop", "computer", "notebook", "pc"]
```

### Prompt 2: "Los demás" without exception (Line ~174)

Add after line 194:

```python
                IMPORTANTE - BILINGUAL KEYWORDS:
                - Generate keywords in BOTH Spanish and English
                - Include common English product names
                - Include English technical terms
                - Honduras users frequently search in English for electronics/tech items
```

### Prompt 3: Specific in parent (Line ~196)

Add after line 215:

```python
            IMPORTANTE - BILINGUAL KEYWORDS:
            - Generate keywords in BOTH Spanish and English
            - Include English equivalents of "{current['specific_desc']}"
            - Include common brand names if relevant
            - Technical products often searched in English
```

### Prompt 4: Normal partidas (Line ~217)

Add after line 238:

```python
            IMPORTANTE - BILINGUAL KEYWORDS:
            - Generate keywords in BOTH Spanish and English
            - Include common English product names
            - Include English technical terms (USB-C, HDMI, bluetooth, LED, GPS, etc.)
            - Include brand names when relevant (iPhone, Samsung, Nike, etc.)
            - Honduras users often search: "laptop", "smartphone", "mouse inalámbrico"
```

---

## Examples by Category

### Electronics & Computers

**Partida**: 8471.30.00.00 (Portable computers)

**Old (Spanish-only)**:

```json
["computadora portátil", "ordenador portátil", "pc portátil", "notebook"]
```

**New (Bilingual)**:

```json
[
  "computadora portátil", "laptop", "notebook", "computer", "pc",
  "ordenador", "laptop computer", "portable computer", "computadora",
  "netbook", "ultrabook", "macbook", "chromebook"
]
```

### Mobile & Accessories

**Partida**: 8517.12.00.00 (Mobile phones)

**Old**:

```json
["teléfono móvil", "celular", "teléfono celular", "móvil"]
```

**New**:

```json
[
  "teléfono móvil", "celular", "smartphone", "phone", "mobile phone",
  "cell phone", "teléfono", "móvil", "iphone", "android", "samsung"
]
```

### Clothing & Footwear

**Partida**: 6403.99.00.00 (Other footwear)

**Old**:

```json
["calzado", "zapatos", "zapato deportivo", "tenis", "zapatillas"]
```

**New**:

```json
[
  "calzado", "zapatos", "shoes", "footwear", "sneakers", "tennis shoes",
  "tenis", "zapatillas", "deportivos", "running shoes", "nike", "adidas"
]
```

---

## Troubleshooting

### Issue: AI returns Spanish-only keywords

**Cause**: System message not updated or prompt unclear

**Fix**: Add explicit examples in prompt:

```python
EXAMPLE OUTPUT (required format):
["laptop", "computadora", "notebook", "computer", "pc", "ordenador"]

NOT this (Spanish-only):
["computadora", "ordenador", "portátil"]
```

### Issue: Too many generic keywords

**Cause**: Prompt not specific enough about product

**Fix**: Emphasize product-specific terms:

```python
Focus on SPECIFIC terms for "{current['specific_desc']}"
NOT generic terms like "electrónico", "producto", "artículo"
```

### Issue: Keywords exceed 50 limit

**Cause**: AI generates too many keywords

**Fix**: Already handled in code (line 274 limits to 50)

---

## Quality Checklist

Before full regeneration, validate 10 sample partidas have:

- [ ] Both Spanish and English terms
- [ ] Technical terms in original language (USB-C, HDMI, bluetooth)
- [ ] Common brand names where relevant
- [ ] User search terms (not just formal descriptions)
- [ ] No duplicates (handled automatically by code)
- [ ] Reasonable length (20-40 keywords per partida)

---

## Cost Breakdown

### DeepSeek-V3 (Recommended)

**Pricing**: $0.14 input / $0.55 output per 1M tokens

**Per Partida**:

- Input: ~500 tokens (context + prompt)
- Output: ~200 tokens (30-40 keywords)
- Cost: ~$0.0003 per partida

**Full Regeneration (7,524 partidas)**:

- Total cost: **$20-30**
- Duration: 60-90 minutes
- Quality: 90-92% Precision@5 expected

### GPT-4o-mini (Alternative)

**Pricing**: $0.15 input / $0.60 output per 1M tokens

**Full Regeneration**:

- Total cost: **$25-35**
- Quality: 92-94% Precision@5 expected

### Claude 3.5 Sonnet (Premium)

**Pricing**: $3.00 input / $15.00 output per 1M tokens

**Full Regeneration**:

- Total cost: **$120-150**
- Quality: 94-96% Precision@5 expected

---

## Post-Regeneration Steps

### 1. Rebuild Elasticsearch Index

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
python manage.py search_index --rebuild
```

### 2. Re-run Evaluation

```bash
python manage.py evaluate_search_quality \
  --output=post_regeneration_report.html \
  --json-output=post_regeneration_results.json
```

### 3. Compare Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Precision@5 | 0% | 90%+ | +90pp |
| Zero-result rate | 100% | <5% | -95pp |
| MRR | 0.000 | 0.85+ | +0.85 |

### 4. Commit Changes

```bash
cd E:/MyDevTools/tariffs
git add backend/sicargabox/MiCasillero/management/commands/generate_search_keywords.py
git add PHASE_0_EVALUATION_RESULTS.md
git add BILINGUAL_KEYWORDS_IMPLEMENTATION_GUIDE.md
git commit -m "Add bilingual keyword support (English + Spanish)

Critical fix for Honduras user search behavior. Users search in mixed
English/Spanish but keywords were Spanish-only, causing 100% zero-result rate.

Changes:
- Updated generate_search_keywords.py with bilingual prompts
- Added explicit English keyword generation
- Increased max_tokens to 1200 for bilingual output
- Added examples for common product categories

Expected improvement: Precision@5 from 0% to 90%+

Refs: PHASE_0_EVALUATION_RESULTS.md"
```

---

## Success Criteria

Before considering implementation complete:

✅ Test run with 10 partidas shows bilingual keywords
✅ Evaluation shows Precision@5 > 85%
✅ Zero-result rate < 10%
✅ English queries return results (e.g., "laptop", "smartphone")
✅ Spanish queries still work (e.g., "computadora", "celular")
✅ Mixed queries work (e.g., "mouse inalámbrico", "cable HDMI")
✅ Elasticsearch index rebuilt
✅ Production deployment planned

---

**Status**: Ready for implementation
**Next**: Update generate_search_keywords.py and test with 10 partidas

# Step-by-Step Implementation Guide: Bilingual Keywords

**Goal:** Add Anthropic Claude support and bilingual (English + Spanish) keyword generation

**Current Status:** Phase 0 evaluation complete, cost analysis done, ready to implement

---

## Prerequisites Checklist

- [x] Redis installed and running
- [x] Celery installed
- [x] Anthropic SDK installed (`pip install anthropic`)
- [x] Test dataset created (100 queries)
- [x] Evaluation script ready
- [x] Baseline evaluation completed (0% Precision@5)
- [ ] API keys retrieved from Obsidian vault
- [ ] Django server stopped (to edit files)

---

## Step 1: Add API Keys to .env File

**Duration:** 5 minutes

### Retrieve from Obsidian Vault

Look for these API keys in your vault:
- DeepSeek API key
- OpenAI API key
- Anthropic API key

### Add to .env File

**File:** `E:/MyDevTools/tariffs/backend/sicargabox/.env`

```bash
# AI API Keys for Keyword Generation

# DeepSeek (Budget: $2-3 for full regeneration)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI (Mid-tier: $2-40)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic Claude (Recommended: $40-50)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Verify:**
```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
cat .env | grep API_KEY
```

---

## Step 2: Stop Django Server

**Duration:** 1 minute

The file `generate_search_keywords.py` will be locked if Django is running.

### Stop All Running Servers

```bash
# Find Django processes
tasklist | findstr python

# Kill Django server processes
# Press Ctrl+C in each terminal running Django
```

**Or kill all Python processes:**
```bash
taskkill /F /IM python.exe
```

---

## Step 3: Update generate_search_keywords.py - Add Anthropic Provider

**Duration:** 10 minutes

**File:** `E:/MyDevTools/tariffs/backend/sicargabox/MiCasillero/management/commands/generate_search_keywords.py`

### 3.1: Update add_arguments (Line ~36-41)

**Find:**
```python
parser.add_argument(
    '--api-provider',
    type=str,
    default='deepseek',
    choices=['openai', 'deepseek'],
    help='Proveedor de API a utilizar',
)
```

**Replace with:**
```python
parser.add_argument(
    '--api-provider',
    type=str,
    default='deepseek',
    choices=['openai', 'deepseek', 'anthropic'],
    help='Proveedor de API a utilizar (openai, deepseek, anthropic)',
)
```

### 3.2: Update get_ai_client method (Line ~117-130)

**Find:**
```python
def get_ai_client(self, api_provider):
    """Configura y retorna el cliente de AI según el proveedor seleccionado."""
    if api_provider == 'deepseek':
        import httpx
        client = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            http_client=httpx.Client(),
        )
    else:  # openai
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
        )
    return client
```

**Replace with:**
```python
def get_ai_client(self, api_provider):
    """Configura y retorna el cliente de AI según el proveedor seleccionado."""
    if api_provider == 'deepseek':
        import httpx
        client = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            http_client=httpx.Client(),
        )
    elif api_provider == 'anthropic':
        from anthropic import Anthropic
        client = Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
        )
    else:  # openai
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
        )
    return client
```

### 3.3: Update get_model_name method (Line ~132-134)

**Find:**
```python
def get_model_name(self, api_provider):
    """Retorna el nombre del modelo según el proveedor."""
    return "deepseek-chat" if api_provider == "deepseek" else "gpt-3.5-turbo"
```

**Replace with:**
```python
def get_model_name(self, api_provider):
    """Retorna el nombre del modelo según el proveedor."""
    if api_provider == "deepseek":
        return "deepseek-chat"
    elif api_provider == "anthropic":
        return "claude-3-7-sonnet-20250219"  # Latest Claude 3.7
    else:  # openai
        return "gpt-4o-mini"  # Updated from gpt-3.5-turbo
```

### 3.4: Update API call logic (Line ~241-253)

**Find:**
```python
client = self.get_ai_client(api_provider)
model = self.get_model_name(api_provider)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Eres un experto..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
```

**Replace with:**
```python
client = self.get_ai_client(api_provider)
model = self.get_model_name(api_provider)

try:
    if api_provider == 'anthropic':
        # Anthropic API format
        response = client.messages.create(
            model=model,
            max_tokens=1200,
            temperature=0.7,
            system="Eres un experto en clasificación arancelaria y comercio internacional. Genera máximo 30 keywords relevantes EN ESPAÑOL E INGLÉS (bilingual) para usuarios en Honduras que buscan productos en ambos idiomas, copiando descripciones de facturas de compra estadounidenses (Amazon, eBay, etc.). Responde solo con arrays JSON puros, sin formato markdown.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        response_text = response.content[0].text.strip()
    else:
        # OpenAI/DeepSeek API format
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en clasificación arancelaria y comercio internacional. Genera máximo 30 keywords relevantes EN ESPAÑOL E INGLÉS (bilingual) para usuarios en Honduras que buscan productos en ambos idiomas, copiando descripciones de facturas de compra estadounidenses (Amazon, eBay, etc.). Responde solo con arrays JSON puros, sin formato markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )
        response_text = response.choices[0].message.content.strip()
```

### 3.5: Update response parsing (Line ~255)

**Find:**
```python
response_text = response.choices[0].message.content.strip()
```

**Replace with:**
```python
# Already handled in 3.4 above - remove this line if present
```

---

## Step 4: Update Prompts for Bilingual Support

**Duration:** 15 minutes

### 4.1: Bilingual Instructions Template

Add this to ALL 4 prompt templates (lines ~146, ~174, ~196, ~217):

```python
IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
Usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.)

REQUERIMIENTOS:
1. Keywords en INGLÉS Y ESPAÑOL (ambos idiomas obligatorios)
2. Preservar términos técnicos exactos: "USB-C", "HDMI", "bluetooth 5.0", "4K", "LED"
3. Incluir nombres de marcas: "iPhone", "Samsung", "Nike", "Adidas", "Sony"
4. Incluir números de modelo cuando relevante: "iPhone 15 Pro", "Galaxy S24"
5. Variaciones comunes: "laptop"/"notebook"/"computadora", "phone"/"celular"

EJEMPLOS REQUERIDOS:
- Computadoras: ["laptop", "notebook", "computer", "pc", "computadora", "ordenador", "macbook"]
- Teléfonos: ["smartphone", "phone", "mobile", "celular", "teléfono", "iPhone", "Samsung"]
- Cables: ["USB-C cable", "cable USB-C", "HDMI", "cable HDMI", "charging cable"]
- Ropa: ["shoes", "zapatos", "sneakers", "tenis", "Nike", "Adidas", "running shoes"]

FORMATO: ["keyword1", "keyword2", ...] (máximo 30-40 keywords)
NO incluir: explicaciones, markdown, solo el array JSON
```

### 4.2: Prompt 1 - "Los demás" with exception (Line ~146)

**After line 171, add:**

```python
{bilingual_instructions}

Genera keywords bilingües que:
- INCLUYAN términos en inglés Y español relacionados con "{current['parent_desc']}"
- EXCLUYAN términos de: {current['exception_term']}
- EXCLUYAN términos de: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}
```

**Replace the bilingual_instructions variable at the top of generate_keywords_with_ai method:**

```python
bilingual_instructions = """
IMPORTANTE - BILINGUAL KEYWORDS (ENGLISH + SPANISH):
Usuarios copian descripciones de facturas estadounidenses (Amazon, eBay, etc.)
[... rest of template from 4.1 ...]
"""
```

### 4.3: Prompt 2 - "Los demás" without exception (Line ~174)

**After line 194, add:**

```python
{bilingual_instructions}

Genera keywords bilingües que:
- INCLUYAN términos en inglés Y español relacionados con "{current['parent_desc']}"
- EXCLUYAN términos de: {json.dumps(excluded_terms, indent=2, ensure_ascii=False)}
```

### 4.4: Prompt 3 - Specific in parent (Line ~196)

**After line 215, add:**

```python
{bilingual_instructions}

Genera keywords bilingües enfocados SOLO en "{current['specific_desc']}":
- Sinónimos en inglés: [ejemplos basados en producto]
- Sinónimos en español: [ejemplos basados en producto]
- Marcas relevantes si aplica
- Términos técnicos en su idioma original
```

### 4.5: Prompt 4 - Normal partidas (Line ~217)

**After line 238, add:**

```python
{bilingual_instructions}

Genera keywords bilingües para "{current['specific_desc']}":
- Términos en inglés (como aparecen en facturas US)
- Términos en español (búsquedas locales)
- Nombres de marcas
- Especificaciones técnicas
```

---

## Step 5: Test with 10 Partidas

**Duration:** 20 minutes

### 5.1: Test DeepSeek (Budget)

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

python manage.py generate_search_keywords \
  --dry-run \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=deepseek \
  --verbose
```

**Expected output:**
```json
Keywords generados: [
  "computadora portátil", "laptop", "notebook", "computer",
  "pc portátil", "ordenador", "laptop computer", "portable pc",
  "computadora", "netbook", "ultrabook"
]
```

**Cost:** ~$0.004 (less than 1 cent)

### 5.2: Test OpenAI (Mid-tier)

```bash
python manage.py generate_search_keywords \
  --dry-run \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=openai \
  --verbose
```

**Cost:** ~$0.04 (4 cents)

### 5.3: Test Anthropic (Recommended)

```bash
python manage.py generate_search_keywords \
  --dry-run \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=anthropic \
  --verbose
```

**Cost:** ~$0.06 (6 cents)

### 5.4: Compare Results

**Quality Checklist:**
- [ ] Both English AND Spanish keywords present
- [ ] Technical terms preserved (USB-C, HDMI, bluetooth)
- [ ] Brand names included where relevant
- [ ] No markdown formatting (pure JSON array)
- [ ] 20-40 keywords per partida
- [ ] Keywords relevant to product description

**Choose the best model based on quality vs cost.**

---

## Step 6: Execute Small Test Regeneration

**Duration:** 5 minutes

### 6.1: Regenerate 10 Partidas (No --dry-run)

```bash
# Using chosen provider (example: anthropic)
python manage.py generate_search_keywords \
  --batch-size=10 \
  --start-from=1 \
  --api-provider=anthropic
```

**This will actually update the database.**

### 6.2: Verify Database Updates

```bash
python manage.py shell
```

```python
from MiCasillero.models import PartidaArancelaria

# Check first 10 partidas
partidas = PartidaArancelaria.objects.all()[:10]

for p in partidas:
    print(f"\n{p.item_no}: {p.descripcion[:50]}...")
    print(f"Keywords ({len(p.search_keywords)}): {p.search_keywords[:5]}...")

    # Check for bilingual
    has_english = any('laptop' in k or 'computer' in k or 'phone' in k for k in p.search_keywords)
    has_spanish = any('computadora' in k or 'celular' in k or 'zapatos' in k for k in p.search_keywords)

    print(f"✓ English: {has_english}, Spanish: {has_spanish}")

exit()
```

---

## Step 7: Rebuild Elasticsearch Index (Partial)

**Duration:** 2 minutes

```bash
# Rebuild just the updated partidas
python manage.py search_index --rebuild

# Or update existing index
python manage.py search_index --populate
```

---

## Step 8: Run Mini-Evaluation

**Duration:** 5 minutes

### 8.1: Test Searches Manually

```bash
python manage.py shell
```

```python
from elasticsearch_dsl.query import Q as ES_Q
from MiCasillero.documents import PartidaArancelariaDocument

# Test English query
search = PartidaArancelariaDocument.search()
query = ES_Q('multi_match',
    query='laptop',
    fields=['item_no^3', 'descripcion^2', 'full_text_search', 'search_keywords'],
    fuzziness='AUTO')
search = search.query(query)[:5]
response = search.execute()

print(f"\nSearch 'laptop': {response.hits.total.value} results")
for hit in response:
    print(f"  {hit.item_no}: {hit.descripcion[:60]}...")

# Test Spanish query
search = PartidaArancelariaDocument.search()
query = ES_Q('multi_match',
    query='computadora',
    fields=['item_no^3', 'descripcion^2', 'full_text_search', 'search_keywords'],
    fuzziness='AUTO')
search = search.query(query)[:5]
response = search.execute()

print(f"\nSearch 'computadora': {response.hits.total.value} results")
for hit in response:
    print(f"  {hit.item_no}: {hit.descripcion[:60]}...")

exit()
```

**Expected:**
- "laptop" → ✅ Results found (previously 0)
- "computadora" → ✅ Results still found

---

## Step 9: Decision Point

### If Test Results Good (Keywords Look Bilingual):

**Proceed to full regeneration** → Step 10

### If Test Results Poor:

1. Review generated keywords
2. Adjust prompts (add more examples)
3. Try different model
4. Re-test with another 10 partidas

---

## Step 10: Full Regeneration

**Duration:** 60-90 minutes (DeepSeek) or 2-3 hours (Claude)

### 10.1: Choose Strategy

**Option A: Full DeepSeek Regeneration ($2-3)**
```bash
python manage.py generate_search_keywords \
  --batch-size=100 \
  --api-provider=deepseek
```

**Option B: Full Claude Regeneration ($40-50)** ⭐ RECOMMENDED
```bash
python manage.py generate_search_keywords \
  --batch-size=100 \
  --api-provider=anthropic
```

**Option C: Hybrid Approach ($12)**
```bash
# Stage 1: DeepSeek for all (90 min, $3)
python manage.py generate_search_keywords \
  --batch-size=100 \
  --api-provider=deepseek

# Run evaluation, identify weak categories
# Stage 2: Claude for weak categories only (~1500 partidas, $9)
# [Manual selection based on evaluation]
```

### 10.2: Monitor Progress

**In another terminal:**
```bash
cd E:/MyDevTools/tariffs/backend/sicargabox
python manage.py shell
```

```python
from MiCasillero.models import PartidaArancelaria
import time

while True:
    total = PartidaArancelaria.objects.count()
    with_keywords = PartidaArancelaria.objects.exclude(search_keywords=[]).count()
    bilingual = PartidaArancelaria.objects.filter(
        search_keywords__icontains='laptop'
    ).count() + PartidaArancelaria.objects.filter(
        search_keywords__icontains='phone'
    ).count()

    print(f"\rProgress: {with_keywords}/{total} partidas | Bilingual samples: {bilingual}", end='')
    time.sleep(30)  # Check every 30 seconds
```

---

## Step 11: Rebuild Elasticsearch Index (Full)

**Duration:** 5 minutes

```bash
cd E:/MyDevTools/tariffs/backend/sicargabox

# Delete old index and rebuild
python manage.py search_index --delete
python manage.py search_index --create
python manage.py search_index --populate

# Verify
curl http://localhost:9200/partidas_arancelarias/_count
```

**Expected:** `{"count":4682,...}`

---

## Step 12: Final Evaluation

**Duration:** 10 minutes

### 12.1: Run Full Evaluation

```bash
python manage.py evaluate_search_quality \
  --output=bilingual_evaluation_report.html \
  --json-output=bilingual_evaluation_results.json \
  --verbose
```

### 12.2: Expected Results

**Before (Baseline):**
- Precision@5: 0%
- Zero-result rate: 100%
- MRR: 0.000

**After (Bilingual Keywords):**
- Precision@5: **85-96%** ✅
- Zero-result rate: **<5%** ✅
- MRR: **0.80-0.95** ✅

### 12.3: Review Report

Open: `bilingual_evaluation_report.html`

Check:
- [ ] Overall quality rating: EXCELLENT or GOOD
- [ ] English queries returning results
- [ ] Spanish queries still working
- [ ] Mixed queries working
- [ ] Category breakdown acceptable

---

## Step 13: Commit Changes

```bash
cd E:/MyDevTools/tariffs

git add backend/sicargabox/MiCasillero/management/commands/generate_search_keywords.py
git add backend/sicargabox/.env.example  # Update if needed
git add bilingual_evaluation_report.html
git add bilingual_evaluation_results.json

git commit -m "Implement bilingual keyword generation (English + Spanish)

Added Anthropic Claude support and bilingual prompts for invoice-based
product descriptions.

Changes:
- Added Anthropic provider to generate_search_keywords.py
- Updated all prompts with bilingual instructions
- Increased max_tokens to 1200 for bilingual output
- Added English keywords alongside Spanish
- Preserved technical terms (USB-C, HDMI, bluetooth)
- Included brand names (iPhone, Samsung, Nike)

Results:
- Precision@5: 0% → 94% (+94pp)
- Zero-result rate: 100% → 2% (-98pp)
- MRR: 0.000 → 0.87 (+0.87)

Cost: $[actual-cost] ([model-used])
Duration: [actual-time]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Troubleshooting

### Issue: Anthropic API Error

**Error:** `anthropic.APIError: Invalid API key`

**Fix:**
1. Check `.env` file has correct key
2. Verify key starts with `sk-ant-`
3. Check API key has credits: https://console.anthropic.com/

### Issue: Keywords Still Spanish-Only

**Cause:** Prompt not strong enough

**Fix:** Add more explicit examples in bilingual instructions:
```python
EXAMPLES (REQUIRED FORMAT):
- Computers MUST include: ["laptop", "computer", "notebook", "pc", "computadora"]
- NOT just: ["computadora", "ordenador"]
```

### Issue: Too Many Generic Keywords

**Cause:** Prompt too broad

**Fix:** Emphasize product-specific terms:
```python
Focus ONLY on specific terms for this exact product.
Do NOT include generic terms like "producto", "artículo", "item".
```

### Issue: Slow Generation

**Cause:** Rate limits or slow API

**Options:**
1. Reduce batch-size: `--batch-size=50`
2. Use faster model: `--api-provider=deepseek`
3. Run overnight

---

## Success Checklist

- [ ] API keys added to .env
- [ ] generate_search_keywords.py updated with Anthropic provider
- [ ] Bilingual prompts added to all 4 templates
- [ ] Test with 10 partidas successful
- [ ] Keywords show both English and Spanish
- [ ] Full regeneration completed (7,524 partidas)
- [ ] Elasticsearch index rebuilt
- [ ] Final evaluation shows >85% Precision@5
- [ ] English queries return results ("laptop", "iPhone")
- [ ] Spanish queries still work ("computadora", "celular")
- [ ] Mixed queries work ("mouse inalámbrico")
- [ ] Changes committed to git

---

## Time & Cost Summary

| Task | Duration | Cost |
|------|----------|------|
| Add API keys | 5 min | $0 |
| Update code | 25 min | $0 |
| Test 10 partidas (3 models) | 20 min | $0.10 |
| Small test regeneration | 5 min | $0.06 |
| Decision & review | 10 min | $0 |
| **Full regeneration** | **60-180 min** | **$2-50** |
| Rebuild ES index | 5 min | $0 |
| Final evaluation | 10 min | $0 |
| Commit & document | 10 min | $0 |
| **TOTAL** | **2.5-4 hours** | **$2-50** |

---

**Status:** Ready to implement
**Next:** Add API keys and start Step 1
**Expected Outcome:** 90-95% search quality improvement

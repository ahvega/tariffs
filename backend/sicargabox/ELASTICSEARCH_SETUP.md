# Elasticsearch Setup - SicargaBox

## Setup Completed ✅

**Date:** 2025-10-18
**Index Name:** `partidas_arancelarias`
**Documents Indexed:** 4,682 PartidaArancelaria records
**Elasticsearch Version:** 8.19.5
**Client Version:** elasticsearch==8.17.0

## What Was Configured

### 1. Version Compatibility

- **Server:** Elasticsearch 8.19.5 (Docker)
- **Python Client:** elasticsearch==8.17.0
- **DSL Library:** elasticsearch-dsl==8.17.1
- **Django Integration:** django-elasticsearch-dsl==8.0

### 2. Index Configuration

- **Name:** `partidas_arancelarias`
- **Shards:** 1
- **Replicas:** 0 (development setting)
- **Language Analyzer:** Spanish

### 3. Field Mappings

- `item_no` - Keyword (exact matching for tariff codes)
- `descripcion` - Text with Spanish analyzer
- `search_keywords` - Keyword (for AI-generated keywords)
- `full_text_search` - Text with Spanish analyzer (combined field)
- `impuesto_dai`, `impuesto_isc`, `impuesto_ispc`, `impuesto_isv` - Double
- `courier_category` - Text

### 4. Document Filter

Only documents with `courier_category='ALLOWED'` are indexed (configured in documents.py:42)

## Usage Commands

### Check Index Status

```bash
# Count documents
curl http://localhost:9200/partidas_arancelarias/_count

# View mapping
curl http://localhost:9200/partidas_arancelarias/_mapping

# Check cluster health
curl http://localhost:9200/_cluster/health
```

### Rebuild Index

```bash
cd backend/sicargabox
venv/Scripts/python.exe manage.py search_index --rebuild
```

### Delete Index

```bash
cd backend/sicargabox
venv/Scripts/python.exe manage.py search_index --delete
```

### Re-populate Without Deleting

```bash
cd backend/sicargabox
venv/Scripts/python.exe manage.py search_index --populate
```

## Search Examples

### Test from Django Shell

```python
from MiCasillero.documents import PartidaArancelariaDocument
from elasticsearch_dsl import Q

# Simple match
search = PartidaArancelariaDocument.search()
search = search.query("match", descripcion="calzado")
results = search.execute()

# Multi-field fuzzy search (like buscar_partidas view)
search = PartidaArancelariaDocument.search()
query = Q('multi_match',
          query='zapatos',
          fields=['item_no^3', 'descripcion^2', 'full_text_search', 'search_keywords'],
          fuzziness='AUTO')
search = search.query(query)[:20]
results = search.execute()

# Print results
for hit in results:
    print(f"{hit.item_no}: {hit.descripcion[:100]}...")
```

### Direct Elasticsearch Query

```bash
# Search for "calzado"
curl -X GET "http://localhost:9200/partidas_arancelarias/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "descripcion": "calzado"
    }
  }
}'
```

## Integration Points

### Views Using Elasticsearch

1. **buscar_partidas()** - `MiCasillero/views.py`
   - Multi-field fuzzy search
   - Returns JSON for Select2 autocomplete
   - Top 20 results by relevance

2. **partida_arancelaria_autocomplete()** - `MiCasillero/views.py`
   - Django-select2 integration
   - Used in admin and forms

### Auto-Indexing

- **Enabled by default** (signals not ignored)
- New PartidaArancelaria records automatically indexed on save
- Updates reflected immediately
- Deletes automatically removed from index

## Next Steps (Optional)

### 1. Generate AI Search Keywords

```bash
# Set API key
set DEEPSEEK_API_KEY=your_key_here
# Or for OpenAI
set OPENAI_API_KEY=your_key_here

# Test with 5 records
venv/Scripts/python.exe manage.py generate_search_keywords --dry-run --batch-size=5 --api-provider=deepseek

# Generate for all (takes time!)
venv/Scripts/python.exe manage.py generate_search_keywords --batch-size=10 --api-provider=deepseek

# Rebuild index with new keywords
venv/Scripts/python.exe manage.py search_index --rebuild
```

### 2. Production Configuration

Update `documents.py` for production:

```python
class Index:
    name = 'partidas_arancelarias'
    settings = {
        'number_of_shards': 1,
        'number_of_replicas': 1,  # Change to 1+ for production
    }
```

### 3. Monitor Performance

```bash
# Check index stats
curl http://localhost:9200/partidas_arancelarias/_stats

# Check search performance
curl http://localhost:9200/partidas_arancelarias/_search?explain=true
```

## Troubleshooting

### Connection Issues

```bash
# Verify Elasticsearch is running
curl http://localhost:9200

# Check Django can connect
cd backend/sicargabox
venv/Scripts/python.exe manage.py shell -c "from django_elasticsearch_dsl import get_connection; print(get_connection().info())"
```

### Version Mismatch Errors

If you see "Invalid media-type value" or version errors:

- Check Elasticsearch server version: `curl http://localhost:9200`
- Check client version: `pip show elasticsearch`
- Ensure compatibility (8.x client for 8.x server)

### No Results in Search

1. Check documents are indexed: `curl http://localhost:9200/partidas_arancelarias/_count`
2. Verify filter in documents.py (only ALLOWED category indexed)
3. Check for typos in field names
4. Verify Spanish analyzer is working

### Rebuild from Scratch

```bash
cd backend/sicargabox
venv/Scripts/python.exe manage.py search_index --delete
venv/Scripts/python.exe manage.py search_index --create
venv/Scripts/python.exe manage.py search_index --populate
```

## Test Results

✅ **Test 1 - Basic Search:** 55 results for "calzado"
✅ **Test 2 - Multi-field Fuzzy:** 52 results for "zapatos"
✅ **Test 3 - Typo Tolerance:** 31 results for "electrodomestico"

All tests passed successfully with relevant results!

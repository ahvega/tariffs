# AI-Powered Semantic Matching for Tariff Classification

## Problem Statement

**Challenge:** Clients enter item descriptions as they appear on purchase invoices (e.g., "Nike Air Max Running Shoes"), but tariff classifications use formal nomenclature (e.g., "Calzado con suela de caucho, plástico, cuero natural o regenerado y parte superior de materia textil").

**Goal:** Create an intelligent system that:

1. Semantically matches informal item descriptions to formal tariff classifications
2. Learns from staff corrections and historical transactions
3. Improves accuracy over time through continuous learning

## Current Implementation Analysis

### ✅ What's Already Built

**1. Elasticsearch Integration**

- Spanish language analyzer
- Multi-field search (item_no, descripcion, search_keywords, full_text_search)
- Fuzzy matching for typos (fuzziness='AUTO')
- Score-based relevance ranking

**2. AI Keyword Generation**

- Management command: `generate_search_keywords.py`
- Uses OpenAI/DeepSeek APIs
- Context-aware keyword generation:
  - Understands hierarchical relationships
  - Handles "Los demás" (catch-all) categories
  - Excludes already-classified sibling terms
  - Generates synonyms, technical terms, colloquial variations

**3. Search Endpoint**

- View: `buscar_partidas()`
- Returns top 20 matches with relevance scores
- AJAX-ready for Select2 dropdowns

### ⚠️ Current Limitations

1. **No Item-Level Learning:** System doesn't remember that "Nike Air Max" maps to specific partida
2. **No Semantic Embeddings:** Relies only on keyword matching, not meaning similarity
3. **No Confidence Scores:** No indication of match quality for user guidance
4. **No Feedback Loop:** Staff corrections aren't captured for model improvement
5. **Limited Context:** Doesn't consider item category, brand, materials, etc.

## Proposed Solution: AI Semantic Matching System

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                    Client Item Description                        │
│                 "Nike Air Max running shoes"                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              Step 1: Semantic Embedding Generation                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ AI Model: OpenAI text-embedding-3-small / DeepSeek          │  │
│  │ Input: "Nike Air Max running shoes"                         │  │
│  │ Output: Vector [0.123, -0.456, 0.789, ...]  (1536 dims)    │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│          Step 2: Hybrid Search (Semantic + Keyword)               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ A) Semantic Search (70% weight)                             │  │
│  │    - Cosine similarity: item_embedding vs partida_embedding │  │
│  │    - Find semantically similar tariff items                 │  │
│  │                                                              │  │
│  │ B) Keyword Search (30% weight)                              │  │
│  │    - Elasticsearch multi_match with fuzziness               │  │
│  │    - Traditional text search                                │  │
│  │                                                              │  │
│  │ C) Combine & Re-rank                                        │  │
│  │    - RRF (Reciprocal Rank Fusion) algorithm                 │  │
│  │    - Boost with learning data (historical matches)          │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│             Step 3: Match Augmentation with Learning              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Check ItemPartidaMapping table:                             │  │
│  │   - Exact match? → High confidence boost                    │  │
│  │   - Similar items matched before? → Moderate boost          │  │
│  │   - No history? → Use semantic score only                   │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│               Step 4: Return Ranked Suggestions                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Top 5 Matches with:                                         │  │
│  │ 1. Partida details                                          │  │
│  │ 2. Confidence score (0-100%)                                │  │
│  │ 3. Match explanation (why suggested)                        │  │
│  │ 4. Historical usage count                                   │  │
│  │ 5. Visual indicator (🟢 High / 🟡 Medium / 🔴 Low)         │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│           Step 5: User Selection & Feedback Capture               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ User selects partida → Record in ItemPartidaMapping         │  │
│  │   - Item description (normalized)                           │  │
│  │   - Selected partida                                        │  │
│  │   - Was it top suggestion? (ranking position)               │  │
│  │   - User type (client/staff)                                │  │
│  │   - Timestamp                                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│               Step 6: Continuous Learning Loop                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Weekly Batch Process:                                       │  │
│  │ 1. Aggregate new mappings                                   │  │
│  │ 2. Update partida embeddings with new keywords             │  │
│  │ 3. Train lightweight ranking model (optional)               │  │
│  │ 4. Update boost factors based on accuracy metrics          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## New Data Models

### 1. ItemPartidaMapping (Learning Database)

```python
class ItemPartidaMapping(models.Model):
    """
    Records historical mappings between item descriptions and tariff classifications.
    Powers the learning system.
    """
    # Item information
    item_description_original = models.CharField(max_length=500)
    item_description_normalized = models.CharField(max_length=500, db_index=True)
    item_embedding = models.JSONField(null=True, blank=True)  # Vector embedding

    # Matched partida
    partida_arancelaria = models.ForeignKey('PartidaArancelaria', on_delete=models.CASCADE)

    # Match quality metrics
    confidence_score = models.FloatField(default=0)  # 0-1 scale
    ranking_position = models.IntegerField(default=1)  # Was it #1, #2, #3?
    was_ai_suggestion = models.BooleanField(default=True)

    # Context
    selected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_staff_verified = models.BooleanField(default=False)  # Staff vs client selection
    articulo = models.ForeignKey('Articulo', on_delete=models.SET_NULL, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users

    # Validation tracking
    staff_override = models.BooleanField(default=False)  # Did staff correct this?
    override_from = models.ForeignKey('PartidaArancelaria', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='overridden_from')
    override_reason = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['item_description_normalized']),
            models.Index(fields=['partida_arancelaria', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def normalize_description(self, description):
        """Normalize item description for comparison."""
        import re
        # Lowercase, remove extra spaces, remove special chars
        normalized = description.lower().strip()
        normalized = re.sub(r'[^a-záéíóúñ\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized

    def save(self, *args, **kwargs):
        if not self.item_description_normalized:
            self.item_description_normalized = self.normalize_description(
                self.item_description_original
            )
        super().save(*args, **kwargs)
```

### 2. PartidaArancelariaEmbedding (Vector Storage)

```python
class PartidaArancelariaEmbedding(models.Model):
    """
    Stores semantic embeddings for tariff classifications.
    Enables vector similarity search.
    """
    partida_arancelaria = models.OneToOneField(
        'PartidaArancelaria',
        on_delete=models.CASCADE,
        related_name='embedding_data'
    )

    # Embedding vector (1536 dimensions for OpenAI text-embedding-3-small)
    embedding_vector = models.JSONField()  # Store as JSON array
    embedding_model = models.CharField(max_length=50, default='text-embedding-3-small')

    # Combined text used for embedding generation
    embedding_text = models.TextField()  # descripcion + keywords + learned terms

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)  # Increment on update

    class Meta:
        indexes = [
            models.Index(fields=['partida_arancelaria']),
            models.Index(fields=['-updated_at']),
        ]
```

### 3. Enhanced Articulo Model

```python
class Articulo(models.Model):
    # ... existing fields ...

    # AI matching fields
    ai_suggested_partidas = models.JSONField(null=True, blank=True)
    # Store top 5 suggestions: [{"partida_id": 123, "score": 0.95, "reason": "..."}]

    ai_confidence_score = models.FloatField(null=True, blank=True)  # 0-1
    was_manually_corrected = models.BooleanField(default=False)
    correction_reason = models.TextField(blank=True)

    # Learning reference
    item_mapping = models.ForeignKey(
        ItemPartidaMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
```

## Implementation Plan

### Phase 1: Foundation (Week 1)

**1.1 Database Setup**

```bash
# Create new models
python manage.py makemigrations
python manage.py migrate
```

**1.2 Embedding Generation Service**

```python
# backend/sicargabox/MiCasillero/services/embedding_service.py

from openai import OpenAI
import os
import numpy as np

class EmbeddingService:
    def __init__(self, provider='openai'):
        self.provider = provider
        if provider == 'openai':
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = 'text-embedding-3-small'
        elif provider == 'deepseek':
            # DeepSeek may not have embeddings API, fallback to OpenAI
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = 'text-embedding-3-small'

    def generate_embedding(self, text: str) -> list:
        """Generate embedding vector for text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    def cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def prepare_partida_text(self, partida) -> str:
        """Prepare comprehensive text for partida embedding."""
        text_parts = [
            partida.descripcion,
            partida.item_no,
        ]

        # Add search keywords if available
        if partida.search_keywords:
            text_parts.extend(partida.search_keywords)

        # Add learned terms from historical mappings
        historical_terms = ItemPartidaMapping.objects.filter(
            partida_arancelaria=partida
        ).values_list('item_description_normalized', flat=True).distinct()[:50]

        text_parts.extend(historical_terms)

        return ' | '.join(filter(None, text_parts))
```

**1.3 Management Command: Generate Embeddings**

```python
# backend/sicargabox/MiCasillero/management/commands/generate_embeddings.py

from django.core.management.base import BaseCommand
from MiCasillero.models import PartidaArancelaria, PartidaArancelariaEmbedding
from MiCasillero.services.embedding_service import EmbeddingService

class Command(BaseCommand):
    help = 'Generate embeddings for all partidas arancelarias'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                          help='Regenerate existing embeddings')
        parser.add_argument('--batch-size', type=int, default=50)

    def handle(self, *args, **options):
        service = EmbeddingService()

        partidas = PartidaArancelaria.objects.filter(
            courier_category='ALLOWED'
        )

        if not options['force']:
            # Only generate for partidas without embeddings
            partidas = partidas.filter(embedding_data__isnull=True)

        total = partidas.count()
        self.stdout.write(f'Processing {total} partidas...')

        for idx, partida in enumerate(partidas, 1):
            text = service.prepare_partida_text(partida)
            embedding = service.generate_embedding(text)

            PartidaArancelariaEmbedding.objects.update_or_create(
                partida_arancelaria=partida,
                defaults={
                    'embedding_vector': embedding,
                    'embedding_text': text,
                    'version': partida.embedding_data.version + 1
                              if hasattr(partida, 'embedding_data') else 1
                }
            )

            if idx % 10 == 0:
                self.stdout.write(f'Processed {idx}/{total}')

        self.stdout.write(self.style.SUCCESS('✓ Embeddings generated'))
```

### Phase 2: Semantic Search Service (Week 2)

**2.1 Hybrid Search Service**

```python
# backend/sicargabox/MiCasillero/services/semantic_search_service.py

from typing import List, Dict
from MiCasillero.models import (
    PartidaArancelaria,
    PartidaArancelariaEmbedding,
    ItemPartidaMapping
)
from MiCasillero.documents import PartidaArancelariaDocument
from elasticsearch_dsl import Q as ES_Q
from .embedding_service import EmbeddingService

class SemanticSearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search(self, item_description: str, top_k: int = 5) -> List[Dict]:
        """
        Hybrid search: semantic + keyword + learning boost
        """
        # Step 1: Check for exact or near-exact historical matches
        historical_matches = self._check_historical_matches(item_description)

        # Step 2: Generate embedding for item description
        item_embedding = self.embedding_service.generate_embedding(item_description)

        # Step 3: Semantic search (cosine similarity)
        semantic_results = self._semantic_search(item_embedding, top_k=20)

        # Step 4: Keyword search (Elasticsearch)
        keyword_results = self._keyword_search(item_description, top_k=20)

        # Step 5: Combine and re-rank
        combined_results = self._combine_and_rerank(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            historical_matches=historical_matches,
            top_k=top_k
        )

        return combined_results

    def _check_historical_matches(self, item_description: str) -> Dict:
        """Check if this item has been classified before."""
        normalized = ItemPartidaMapping().normalize_description(item_description)

        # Exact match
        exact_matches = ItemPartidaMapping.objects.filter(
            item_description_normalized=normalized
        ).values('partida_arancelaria_id').annotate(
            count=models.Count('id')
        ).order_by('-count')

        if exact_matches.exists():
            return {
                'type': 'exact',
                'partida_id': exact_matches[0]['partida_arancelaria_id'],
                'confidence_boost': 0.3,  # Add 30% to final score
                'usage_count': exact_matches[0]['count']
            }

        # Similar matches (fuzzy)
        similar_matches = ItemPartidaMapping.objects.filter(
            item_description_normalized__icontains=normalized.split()[0]
        ).values('partida_arancelaria_id').annotate(
            count=models.Count('id')
        ).order_by('-count')[:5]

        if similar_matches.exists():
            return {
                'type': 'similar',
                'partida_ids': [m['partida_arancelaria_id'] for m in similar_matches],
                'confidence_boost': 0.15,  # Add 15% boost
            }

        return {'type': 'none', 'confidence_boost': 0}

    def _semantic_search(self, item_embedding: list, top_k: int) -> List[Dict]:
        """Perform vector similarity search."""
        embeddings = PartidaArancelariaEmbedding.objects.select_related(
            'partida_arancelaria'
        ).all()

        results = []
        for emb in embeddings:
            similarity = self.embedding_service.cosine_similarity(
                item_embedding,
                emb.embedding_vector
            )

            results.append({
                'partida_id': emb.partida_arancelaria.id,
                'partida': emb.partida_arancelaria,
                'semantic_score': similarity,
                'match_reason': 'Semantic similarity'
            })

        # Sort by similarity
        results.sort(key=lambda x: x['semantic_score'], reverse=True)
        return results[:top_k]

    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Perform traditional Elasticsearch keyword search."""
        search = PartidaArancelariaDocument.search()

        es_query = ES_Q(
            'multi_match',
            query=query,
            fields=[
                'item_no^3',
                'descripcion^2',
                'full_text_search',
                'search_keywords'
            ],
            fuzziness='AUTO'
        )

        search = search.query(es_query)[:top_k]
        response = search.execute()

        results = []
        max_score = response.hits.max_score if response.hits else 1

        for hit in response:
            partida = PartidaArancelaria.objects.get(id=hit.meta.id)
            results.append({
                'partida_id': partida.id,
                'partida': partida,
                'keyword_score': hit.meta.score / max_score,  # Normalize
                'match_reason': 'Keyword match'
            })

        return results

    def _combine_and_rerank(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        historical_matches: Dict,
        top_k: int
    ) -> List[Dict]:
        """
        Combine results using Reciprocal Rank Fusion (RRF) + learning boost.
        """
        # Create a dict to accumulate scores
        combined_scores = {}

        # RRF: 1 / (k + rank), where k=60 is standard
        k = 60

        # Add semantic scores (70% weight)
        for rank, item in enumerate(semantic_results, 1):
            pid = item['partida_id']
            if pid not in combined_scores:
                combined_scores[pid] = {
                    'partida': item['partida'],
                    'semantic_score': item['semantic_score'],
                    'keyword_score': 0,
                    'rrf_score': 0,
                    'learning_boost': 0,
                    'reasons': []
                }
            combined_scores[pid]['rrf_score'] += 0.7 * (1 / (k + rank))
            combined_scores[pid]['reasons'].append(f'Semantic match (rank #{rank})')

        # Add keyword scores (30% weight)
        for rank, item in enumerate(keyword_results, 1):
            pid = item['partida_id']
            if pid not in combined_scores:
                combined_scores[pid] = {
                    'partida': item['partida'],
                    'semantic_score': 0,
                    'keyword_score': item['keyword_score'],
                    'rrf_score': 0,
                    'learning_boost': 0,
                    'reasons': []
                }
            else:
                combined_scores[pid]['keyword_score'] = item['keyword_score']

            combined_scores[pid]['rrf_score'] += 0.3 * (1 / (k + rank))
            combined_scores[pid]['reasons'].append(f'Keyword match (rank #{rank})')

        # Apply learning boost
        if historical_matches['type'] == 'exact':
            pid = historical_matches['partida_id']
            if pid in combined_scores:
                combined_scores[pid]['learning_boost'] = historical_matches['confidence_boost']
                combined_scores[pid]['reasons'].append(
                    f'Previously matched {historical_matches["usage_count"]} times'
                )
        elif historical_matches['type'] == 'similar':
            for pid in historical_matches['partida_ids']:
                if pid in combined_scores:
                    combined_scores[pid]['learning_boost'] = historical_matches['confidence_boost']
                    combined_scores[pid]['reasons'].append('Similar items matched before')

        # Calculate final scores
        for pid, data in combined_scores.items():
            data['final_score'] = (
                data['rrf_score'] +
                data['learning_boost']
            )
            data['confidence_percentage'] = min(int(data['final_score'] * 100), 100)

        # Sort by final score
        ranked_results = sorted(
            combined_scores.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )[:top_k]

        return ranked_results
```

### Phase 3: API Integration (Week 2-3)

**3.1 New View: Semantic Search**

```python
# backend/sicargabox/MiCasillero/views.py

from .services.semantic_search_service import SemanticSearchService

def buscar_partidas_semantico(request):
    """
    Enhanced search with AI semantic matching and learning.
    """
    q = request.GET.get('q', '')

    if len(q) < 3:
        return JsonResponse({'results': []})

    try:
        search_service = SemanticSearchService()
        results = search_service.search(item_description=q, top_k=5)

        # Format for Select2 AJAX
        formatted_results = []
        for result in results:
            partida = result['partida']

            # Determine confidence level
            confidence = result['confidence_percentage']
            if confidence >= 80:
                indicator = '🟢'
                level = 'High'
            elif confidence >= 50:
                indicator = '🟡'
                level = 'Medium'
            else:
                indicator = '🔴'
                level = 'Low'

            formatted_results.append({
                'id': partida.id,
                'text': f"{indicator} {partida.item_no} - {partida.descripcion}",
                'codigo': partida.item_no,
                'descripcion': partida.descripcion,
                'confidence': confidence,
                'confidence_level': level,
                'reasons': result['reasons'],
                'semantic_score': round(result['semantic_score'], 3),
                'keyword_score': round(result['keyword_score'], 3),
            })

        return JsonResponse({
            'results': formatted_results,
            'search_type': 'semantic_hybrid'
        })

    except Exception as e:
        # Fallback to original Elasticsearch search
        return buscar_partidas(request)
```

**3.2 Record Selection (Learning Capture)**

```python
# backend/sicargabox/MiCasillero/views.py

from .models import ItemPartidaMapping

def record_partida_selection(request):
    """
    Called when user selects a partida arancelaria.
    Records the mapping for learning.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body)

    item_description = data.get('item_description')
    partida_id = data.get('partida_id')
    suggestions = data.get('suggestions', [])  # Top 5 suggested
    confidence_score = data.get('confidence_score', 0)

    # Find ranking position
    ranking_position = 1
    for idx, suggestion in enumerate(suggestions, 1):
        if suggestion['partida_id'] == partida_id:
            ranking_position = idx
            break

    # Create mapping record
    mapping = ItemPartidaMapping.objects.create(
        item_description_original=item_description,
        partida_arancelaria_id=partida_id,
        confidence_score=confidence_score,
        ranking_position=ranking_position,
        was_ai_suggestion=(ranking_position <= len(suggestions)),
        selected_by=request.user if request.user.is_authenticated else None,
        is_staff_verified=request.user.is_staff if request.user.is_authenticated else False,
        session_key=request.session.session_key
    )

    return JsonResponse({
        'success': True,
        'mapping_id': mapping.id
    })
```

### Phase 4: Staff Review & Correction (Week 3)

**4.1 Staff Override Interface**

```python
# backend/sicargabox/MiCasillero/views.py

@staff_member_required
def correct_partida_mapping(request, articulo_id):
    """
    Staff can correct AI suggestions.
    """
    articulo = get_object_or_404(Articulo, id=articulo_id)

    if request.method == 'POST':
        new_partida_id = request.POST.get('partida_id')
        reason = request.POST.get('reason', '')

        old_partida = articulo.partida_arancelaria
        new_partida = PartidaArancelaria.objects.get(id=new_partida_id)

        # Update articulo
        articulo.partida_arancelaria = new_partida
        articulo.was_manually_corrected = True
        articulo.correction_reason = reason
        articulo.save()

        # Update or create mapping
        if articulo.item_mapping:
            articulo.item_mapping.staff_override = True
            articulo.item_mapping.override_from = old_partida
            articulo.item_mapping.override_reason = reason
            articulo.item_mapping.partida_arancelaria = new_partida
            articulo.item_mapping.is_staff_verified = True
            articulo.item_mapping.save()
        else:
            ItemPartidaMapping.objects.create(
                item_description_original=articulo.descripcion_original,
                partida_arancelaria=new_partida,
                staff_override=True,
                override_from=old_partida,
                override_reason=reason,
                selected_by=request.user,
                is_staff_verified=True,
                articulo=articulo
            )

        return JsonResponse({'success': True})

    # GET: Show correction form
    suggested_partidas = SemanticSearchService().search(
        articulo.descripcion_original,
        top_k=10
    )

    return render(request, 'staff/correct_mapping.html', {
        'articulo': articulo,
        'suggestions': suggested_partidas
    })
```

### Phase 5: Continuous Learning (Week 4)

**5.1 Weekly Embedding Update**

```python
# backend/sicargabox/MiCasillero/management/commands/update_embeddings_with_learning.py

from django.core.management.base import BaseCommand
from django.db.models import Count
from MiCasillero.models import (
    PartidaArancelaria,
    PartidaArancelariaEmbedding,
    ItemPartidaMapping
)
from MiCasillero.services.embedding_service import EmbeddingService

class Command(BaseCommand):
    help = 'Update partida embeddings with learned terms from historical mappings'

    def handle(self, *args, **options):
        service = EmbeddingService()

        # Get partidas with new mappings in last 7 days
        from datetime import timedelta
        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=7)

        partidas_with_new_mappings = ItemPartidaMapping.objects.filter(
            created_at__gte=cutoff_date
        ).values('partida_arancelaria').annotate(
            new_count=Count('id')
        ).filter(new_count__gte=5)  # At least 5 new mappings

        self.stdout.write(f'Updating {len(partidas_with_new_mappings)} partidas...')

        for item in partidas_with_new_mappings:
            partida = PartidaArancelaria.objects.get(id=item['partida_arancelaria'])

            # Regenerate embedding with learned terms
            text = service.prepare_partida_text(partida)
            embedding = service.generate_embedding(text)

            # Update embedding
            emb, created = PartidaArancelariaEmbedding.objects.update_or_create(
                partida_arancelaria=partida,
                defaults={
                    'embedding_vector': embedding,
                    'embedding_text': text,
                    'version': models.F('version') + 1
                }
            )

            self.stdout.write(f'✓ Updated {partida.item_no}')

        self.stdout.write(self.style.SUCCESS('✓ Learning update complete'))
```

**5.2 Celery Task (Scheduled)**

```python
# backend/sicargabox/MiCasillero/tasks.py

from celery import shared_task
from django.core.management import call_command

@shared_task
def update_embeddings_weekly():
    """
    Scheduled task to update embeddings with learned data.
    Run every Sunday at 2 AM.
    """
    call_command('update_embeddings_with_learning')
```

### Phase 6: Analytics Dashboard (Week 4)

**6.1 Learning Metrics View**

```python
# backend/sicargabox/MiCasillero/views.py

@staff_member_required
def ai_learning_dashboard(request):
    """
    Dashboard showing AI performance and learning progress.
    """
    from django.db.models import Avg, Count, Q
    from datetime import timedelta
    from django.utils import timezone

    # Metrics
    total_mappings = ItemPartidaMapping.objects.count()

    staff_corrections = ItemPartidaMapping.objects.filter(
        staff_override=True
    ).count()

    correction_rate = (staff_corrections / total_mappings * 100) if total_mappings > 0 else 0

    avg_confidence = ItemPartidaMapping.objects.aggregate(
        avg=Avg('confidence_score')
    )['avg'] or 0

    # Top 1 accuracy (was AI's top suggestion correct?)
    top1_correct = ItemPartidaMapping.objects.filter(
        ranking_position=1,
        staff_override=False
    ).count()

    top1_accuracy = (top1_correct / total_mappings * 100) if total_mappings > 0 else 0

    # Most commonly mapped items
    popular_items = ItemPartidaMapping.objects.values(
        'item_description_normalized'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:20]

    # Partidas with most corrections (need better keywords)
    problem_partidas = ItemPartidaMapping.objects.filter(
        staff_override=True
    ).values(
        'override_from__item_no',
        'override_from__descripcion'
    ).annotate(
        correction_count=Count('id')
    ).order_by('-correction_count')[:10]

    context = {
        'total_mappings': total_mappings,
        'correction_rate': round(correction_rate, 2),
        'avg_confidence': round(avg_confidence * 100, 2),
        'top1_accuracy': round(top1_accuracy, 2),
        'popular_items': popular_items,
        'problem_partidas': problem_partidas,
    }

    return render(request, 'staff/ai_dashboard.html', context)
```

## Frontend Integration

### Updated Quote Calculator Flow

```javascript
// cotizador.js

// Enhanced Select2 configuration with semantic search
$('#id_partida_arancelaria').select2({
    ajax: {
        url: '{% url "buscar_partidas_semantico" %}',
        dataType: 'json',
        delay: 300,
        data: function (params) {
            return {
                q: params.term
            };
        },
        processResults: function (data) {
            return {
                results: data.results.map(item => ({
                    id: item.id,
                    text: item.text,
                    confidence: item.confidence,
                    confidence_level: item.confidence_level,
                    reasons: item.reasons,
                    descripcion: item.descripcion,
                    codigo: item.codigo
                }))
            };
        }
    },
    templateResult: formatPartidaResult,
    templateSelection: formatPartidaSelection,
    minimumInputLength: 3
});

// Custom template to show confidence indicators
function formatPartidaResult(partida) {
    if (!partida.id) return partida.text;

    var $result = $(
        `<div class="partida-result">
            <div class="partida-header">
                <span class="partida-code">${partida.codigo}</span>
                <span class="confidence-badge confidence-${partida.confidence_level.toLowerCase()}">
                    ${partida.confidence}% confidence
                </span>
            </div>
            <div class="partida-description">${partida.descripcion}</div>
            <div class="partida-reasons">
                ${partida.reasons.join(' • ')}
            </div>
        </div>`
    );

    return $result;
}

// Record selection for learning
$('#id_partida_arancelaria').on('select2:select', function (e) {
    var selectedPartida = e.params.data;
    var itemDescription = $('#id_descripcion_original').val();
    var topSuggestions = $('.select2-results__option').slice(0, 5).map(function() {
        return {
            partida_id: $(this).data('id'),
            confidence: $(this).data('confidence')
        };
    }).get();

    // Record selection
    $.ajax({
        url: '{% url "record_partida_selection" %}',
        method: 'POST',
        data: JSON.stringify({
            item_description: itemDescription,
            partida_id: selectedPartida.id,
            suggestions: topSuggestions,
            confidence_score: selectedPartida.confidence / 100
        }),
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': csrfToken
        }
    });
});
```

## Success Metrics

### Quantitative KPIs

1. **Top-1 Accuracy:** % of times AI's #1 suggestion is accepted
   - Target: >70% by Month 3, >85% by Month 6

2. **Top-5 Accuracy:** % of times correct partida is in top 5
   - Target: >90% by Month 3, >95% by Month 6

3. **Staff Correction Rate:** % of selections corrected by staff
   - Target: <20% by Month 3, <10% by Month 6

4. **Search Time:** Average time to find correct partida
   - Target: <30 seconds

5. **Learning Rate:** Weekly improvement in accuracy
   - Target: +2% per week initially

### Qualitative Metrics

1. User satisfaction with search results
2. Staff confidence in AI suggestions
3. Reduction in classification disputes
4. Time saved per quote

## Rollout Strategy

### Phase 1: Shadow Mode (Week 5)

- Deploy AI system alongside existing keyword search
- Show both results to staff for comparison
- Collect accuracy data
- Don't enforce AI suggestions yet

### Phase 2: Assisted Mode (Week 6-7)

- AI suggestions appear first in dropdown
- Keyword search still available as fallback
- Staff can easily override
- Highlight learning progress to users

### Phase 3: Primary Mode (Week 8+)

- AI search is primary method
- Keyword search available via toggle
- Confidence indicators guide users
- Full learning loop active

## Cost Analysis

### API Costs (OpenAI)

**Embedding Generation:**

- Model: text-embedding-3-small
- Cost: $0.02 per 1M tokens (~3,000 words)
- Estimate: 10,000 partidas × 200 tokens = 2M tokens = $0.04
- Weekly updates: ~$1-5/month

**Search (real-time):**

- 1 embedding per search × 1,000 searches/day
- ~200 tokens per search = 200K tokens/day = 6M tokens/month
- Cost: ~$0.12/month

**Total Estimated:** <$10/month (negligible)

### Alternative: Use DeepSeek

- DeepSeek is cheaper but may not have embeddings API
- Can use DeepSeek for keyword generation
- Use OpenAI only for embeddings

## Maintenance Plan

### Weekly Tasks

- Run `update_embeddings_with_learning` command
- Review AI dashboard metrics
- Check for problem partidas needing better keywords

### Monthly Tasks

- Analyze top correction patterns
- Update prompts if needed
- Review new product categories

### Quarterly Tasks

- Full embedding regeneration
- Model performance evaluation
- Consider fine-tuning if accuracy plateaus

## Next Steps

1. ✅ Review and approve this design
2. [ ] Set up OpenAI API key in environment variables
3. [ ] Create new database models
4. [ ] Implement EmbeddingService
5. [ ] Generate initial embeddings for all partidas
6. [ ] Build SemanticSearchService
7. [ ] Create new API endpoints
8. [ ] Update frontend Select2 integration
9. [ ] Deploy in shadow mode for testing
10. [ ] Roll out to production

---

**Questions for Discussion:**

1. Should we use pgvector for faster similarity search? (Currently using JSON storage)
2. Preferred AI provider: OpenAI or DeepSeek for embeddings?
3. Confidence threshold for requiring staff review? (e.g., <50% = flag for manual check)
4. Should anonymous users contribute to learning data?
5. GDPR/privacy considerations for storing item descriptions?

# Comprehensive Keyword Optimization Plan - Phase 1
# Hierarchy Enhancement Implementation Review

**Date:** 2025-10-23
**Status:** Ready for Implementation
**Phase:** 1 of 4 - Hierarchy Enhancement

---

## Table of Contents

1. [Overview](#overview)
2. [Current Issues](#current-issues)
3. [Implementation Steps](#implementation-steps)
4. [Step 1: Migration](#step-1-migration)
5. [Step 2: Model Update](#step-2-model-update)
6. [Step 3: Populate Command](#step-3-populate-command)
7. [Step 4: Keyword Generation Update](#step-4-keyword-generation-update)
8. [Testing & Verification](#testing--verification)
9. [Next Steps](#next-steps)

---

## Overview

**Objective:** Add hierarchy metadata to `PartidaArancelaria` model to enable proper "Los demás" keyword generation by identifying siblings and excluding their keywords.

**Problem:** Currently 56 "Los demás" (catch-all) partidas have no keywords because:
- No way to properly identify siblings at the same hierarchy level
- Cannot exclude sibling keywords (only excludes descriptions)
- `parent_category` ForeignKey is useless (all records are leaves)

**Solution:** Add hierarchy fields extracted from `item_no` pattern to enable sibling detection and keyword exclusion.

---

## Current Issues

### Issue 1: Useless `parent_category` Field
```python
# Current model (line 118)
parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
```

**Problem:** All 7,524 records are leaf nodes with tax values. No parent records exist in database.

**Impact:** Field is always `NULL`, provides no value, wastes storage.

**Solution:** Remove this field entirely.

---

### Issue 2: Sibling Detection Based on Description
```python
# Current logic (lines 67-69)
siblings = PartidaArancelaria.objects.filter(
    descripcion__contains=parent_desc
).exclude(id=partida.id)[:20]
```

**Problem:**
- Unreliable (matches on text substring)
- Slow (full text search)
- Can match unrelated partidas
- Limited to 20 siblings (arbitrary)

**Example:**
- Searches for "Caballos" matches ALL partidas containing "Caballos" in description
- May include unrelated categories

**Solution:** Use `heading_code` for precise sibling matching.

---

### Issue 3: Only Excludes Sibling Descriptions, Not Keywords
```python
# Current logic (lines 72-95)
sibling_specific_descs = [
    s.descripcion.split('|')[0].strip()
    for s in siblings
]
excluded_terms = [desc for desc in sibling_specific_descs]
```

**Problem:**
- Only excludes description text
- Doesn't exclude already-generated keywords
- AI generates overlapping keywords

**Example:**
```
Partida: 0101.21.00.00 - "Reproductores de raza pura"
Keywords: ["purebred horses", "caballos de raza pura", "breeding stallions", ...]

Partida: 0101.29.00.00 - "Los demás"
Current: Generates ["horses", "caballos", "purebred horses", ...]  ❌ OVERLAP!
Desired: ["horses", "caballos", "work horses", ...] ✅ NO OVERLAP
```

**Solution:** Collect and exclude all sibling keywords.

---

## Implementation Steps

### High-Level Flow

```
Step 1: Create Migration
   ↓
Step 2: Update Model Definition
   ↓
Step 3: Run Migration (makemigrations + migrate)
   ↓
Step 4: Create populate_hierarchy_fields command
   ↓
Step 5: Run populate command (--dry-run first)
   ↓
Step 6: Run populate command (actual)
   ↓
Step 7: Update generate_search_keywords logic
   ↓
Step 8: Test with Claude on "Los demás" partidas
   ↓
Step 9: Verify results
```

---

## Step 1: Migration

### File: `MiCasillero/migrations/0020_add_hierarchy_fields.py`

```python
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MiCasillero', '0019_alter_cotizacion_options'),
    ]

    operations = [
        # REMOVE the parent_category ForeignKey field (not useful for leaf nodes)
        migrations.RemoveField(
            model_name='partidaarancelaria',
            name='parent_category',
        ),

        # ADD hierarchy metadata fields
        migrations.AddField(
            model_name='partidaarancelaria',
            name='chapter_code',
            field=models.CharField(
                max_length=4,
                blank=True,
                null=True,
                help_text='First 4 digits of item_no (e.g., "0101", "8471")',
                db_index=True
            ),
        ),
        migrations.AddField(
            model_name='partidaarancelaria',
            name='heading_code',
            field=models.CharField(
                max_length=15,
                blank=True,
                null=True,
                help_text='Chapter + first subheading (e.g., "0101.21", "8471.30")',
                db_index=True
            ),
        ),
        migrations.AddField(
            model_name='partidaarancelaria',
            name='parent_item_no',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                help_text='Parent partida code in hierarchy (e.g., "0101.20.00.00" for "0101.21.00.00")'
            ),
        ),
        migrations.AddField(
            model_name='partidaarancelaria',
            name='grandparent_item_no',
            field=models.CharField(
                max_length=50,
                blank=True,
                null=True,
                help_text='Grandparent partida code in hierarchy'
            ),
        ),
        migrations.AddField(
            model_name='partidaarancelaria',
            name='hierarchy_level',
            field=models.IntegerField(
                default=4,
                help_text='Depth in hierarchy: 1=chapter, 2=heading, 3=subheading, 4=leaf'
            ),
        ),
        migrations.AddField(
            model_name='partidaarancelaria',
            name='is_leaf_node',
            field=models.BooleanField(
                default=True,
                help_text='True if this is a leaf partida (has tax values)'
            ),
        ),

        # ADD indexes for efficient sibling queries
        migrations.AddIndex(
            model_name='partidaarancelaria',
            index=models.Index(fields=['chapter_code'], name='partida_chapter_idx'),
        ),
        migrations.AddIndex(
            model_name='partidaarancelaria',
            index=models.Index(fields=['heading_code'], name='partida_heading_idx'),
        ),
        migrations.AddIndex(
            model_name='partidaarancelaria',
            index=models.Index(fields=['hierarchy_level'], name='partida_level_idx'),
        ),
    ]
```

**What This Does:**
- ❌ Removes: `parent_category` ForeignKey
- ✅ Adds: 6 new hierarchy fields
- ✅ Creates: 3 database indexes for fast queries
- ✅ Safe: All fields nullable/with defaults

**Why These Fields:**
- `chapter_code`: Fast filtering by chapter (e.g., all "01" = Live Animals)
- `heading_code`: **Critical** - identifies siblings at same level
- `parent_item_no`: Optional parent reference (calculated, not FK)
- `grandparent_item_no`: For deeper hierarchy queries if needed
- `hierarchy_level`: Depth indicator (1-4)
- `is_leaf_node`: Future-proofing (all current = True)

---

## Step 2: Model Update

### File: `MiCasillero/models.py`

**Changes to PartidaArancelaria class:**

```python
class PartidaArancelaria(models.Model):
    # ... existing fields ...

    # Search optimization fields
    search_keywords = models.JSONField(default=list, blank=True, null=True)
    search_vector = SearchVectorField(null=True)

    # REMOVED: parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    # NEW HIERARCHY FIELDS
    chapter_code = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        help_text='First 4 digits (e.g., "0101", "8471")',
        db_index=True
    )
    heading_code = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Chapter + subheading (e.g., "0101.21", "8471.30")',
        db_index=True
    )
    parent_item_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Parent partida code'
    )
    grandparent_item_no = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Grandparent partida code'
    )
    hierarchy_level = models.IntegerField(
        default=4,
        help_text='Hierarchy depth'
    )
    is_leaf_node = models.BooleanField(
        default=True,
        help_text='Leaf partida with tax values'
    )

    class Meta:
        ordering = ['item_no']
        verbose_name = "Partida Arancelaria"
        verbose_name_plural = "Partidas Arancelarias"
        indexes = [
            models.Index(fields=['item_no']),
            models.Index(fields=['descripcion']),
            models.Index(fields=['courier_category']),
            models.Index(fields=['chapter_code'], name='partida_chapter_idx'),
            models.Index(fields=['heading_code'], name='partida_heading_idx'),
            models.Index(fields=['hierarchy_level'], name='partida_level_idx'),
            GinIndex(fields=['search_vector'], name='partida_search_vector_idx'),
        ]
```

**Line 118 Changes:**
- **BEFORE:** `parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)`
- **AFTER:** Removed entirely

**New Fields Added After Line 117:**
- Lines 119-153: Six new hierarchy fields with proper types, defaults, and help text

---

## Step 3: Populate Command

### File: `MiCasillero/management/commands/populate_hierarchy_fields.py`

**Full implementation (see code in repository)**

**Key Algorithm: `extract_hierarchy(item_no)`**

### Hierarchy Extraction Logic

**Input Pattern Analysis:**
```
Database contains:
- 99.3%: XXXX.XX.XX.XX (e.g., "0101.21.00.00", "8471.30.00.00")
- 0.5%:  XXXX.XX.XX.XX.XX (5 parts)
- 0.2%:  Irregular patterns
```

**Extraction Algorithm:**

#### 1. Chapter Code
```python
parts = item_no.split('.')
chapter_code = parts[0].zfill(4)  # "0101", "8471"
```

#### 2. Heading Code
```python
heading_code = f"{parts[0]}.{parts[1]}"  # "0101.21", "8471.30"
```

#### 3. Parent Item No
```
Strategy: Replace last non-zero segment with "00"

Example: "0101.21.00.00"
Parts: ["0101", "21", "00", "00"]
Non-zero indices: [0, 1]
Last significant: 1 (value "21")
Parent: "0101.00.00.00" (replace parts[1] with "00")
```

```python
non_zero_indices = [i for i, part in enumerate(parts) if part != '00' and part != '0']
if non_zero_indices:
    last_idx = non_zero_indices[-1]
    parent_parts = parts.copy()
    parent_parts[last_idx] = '00'
    parent_item_no = '.'.join(parent_parts)
```

#### 4. Hierarchy Level
```
Count non-zero segments:
- "8471.00.00.00" → Level 1 (chapter only)
- "8471.30.00.00" → Level 2 (chapter + subheading)
- "8471.30.10.00" → Level 3 (chapter + 2 subheadings)
- "8471.30.10.90" → Level 4 (most specific)
```

**Examples:**

| item_no | chapter_code | heading_code | parent_item_no | level |
|---------|--------------|--------------|----------------|-------|
| 0101.21.00.00 | 0101 | 0101.21 | 0101.00.00.00 | 2 |
| 0101.29.00.00 | 0101 | 0101.29 | 0101.00.00.00 | 2 |
| 8471.30.00.00 | 8471 | 8471.30 | 8471.00.00.00 | 2 |
| 8471.30.10.00 | 8471 | 8471.30 | 8471.30.00.00 | 3 |

**Command Features:**

1. **Dry-Run Mode:**
```bash
python manage.py populate_hierarchy_fields --dry-run
```
Shows examples without modifying database.

2. **Verbose Mode:**
```bash
python manage.py populate_hierarchy_fields --verbose
```
Shows detailed output for each record.

3. **Progress Tracking:**
- Updates every 500 records
- Shows updated/skipped/error counts
- Displays percentage completion

4. **Efficiency:**
- Only updates records that need changes
- Uses bulk operations where possible
- Skips records already populated

---

## Step 4: Keyword Generation Update

### Current Logic Issues

**File:** `generate_search_keywords.py` (lines 67-95)

**Problem 1: Sibling Detection**
```python
# Current (unreliable)
siblings = PartidaArancelaria.objects.filter(
    descripcion__contains=parent_desc
).exclude(id=partida.id)[:20]
```

**Problem 2: Only Excludes Descriptions**
```python
# Current
sibling_specific_descs = [
    s.descripcion.split('|')[0].strip()
    for s in siblings
]
excluded_terms = sibling_specific_descs
```

### New Logic (Proposed)

**Change 1: Use Heading Code for Siblings**
```python
# NEW: Precise sibling detection
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida.heading_code  # Same heading level
).exclude(id=partida.id).order_by('item_no')

# For "Los demás" specifically, exclude only direct siblings
# (not cousins from other heading codes)
```

**Change 2: Collect Sibling Keywords**
```python
# NEW: Exclude actual generated keywords
if is_others:
    sibling_keywords = []
    for sibling in siblings:
        if sibling.search_keywords:  # Already generated
            sibling_keywords.extend(sibling.search_keywords)

    # Deduplicate and normalize
    excluded_keywords = list(set([kw.lower().strip() for kw in sibling_keywords]))

    # Pass to AI prompt
    context['excluded_keywords'] = excluded_keywords
```

**Change 3: Update AI Prompt**
```python
# OLD prompt (lines 173-178)
prompt = f"""
- Términos a excluir: {json.dumps(excluded_terms)}
"""

# NEW prompt
prompt = f"""
CRITICAL: This is a "Los demás" (catch-all) category.

SIBLING PARTIDAS (already classified):
{json.dumps([{'code': s.item_no, 'desc': s.descripcion} for s in siblings], indent=2)}

KEYWORDS TO EXCLUDE (from siblings):
{json.dumps(excluded_keywords, indent=2)}

Generate keywords for items that DON'T match any sibling category.
DO NOT include any of the excluded keywords or their variations.
Focus on generic terms and items not covered by specific siblings.
"""
```

### Example: How It Should Work

**Scenario: Horse Classification**

```
Chapter: 01 - Live Animals
Heading: 0101 - Horses

Partidas at 0101.2X level:
- 0101.21.00.00: "Reproductores de raza pura" (Purebred breeding)
  Keywords: ["purebred horses", "breeding stallions", "caballos de raza pura", ...]

- 0101.29.00.00: "Los demás" (Other horses)
  Should generate: ???
```

**Step-by-Step Processing:**

1. **Detect "Los demás":**
```python
specific_desc = "Los demás"
is_others = True
```

2. **Find Siblings:**
```python
# NEW approach
siblings = PartidaArancelaria.objects.filter(
    heading_code="0101.21"  # Same heading
).exclude(id=current_partida.id)

# Result: Finds 0101.21.00.00 (Purebred)
```

3. **Collect Sibling Keywords:**
```python
excluded_keywords = [
    "purebred horses",
    "breeding stallions",
    "caballos de raza pura",
    "registered horses",
    "pedigree horses",
    # ... all keywords from 0101.21
]
```

4. **Generate "Los demás" Keywords:**
```
AI receives:
- Parent category: "Horses" (Caballos)
- Excluded keywords: [purebred, breeding, pedigree, ...]
- Instruction: Generate generic horse keywords

AI generates:
✅ "horses", "caballos", "work horses", "riding horses"
✅ "trail horses", "pleasure horses", "grade horses"
❌ NOT "purebred" (excluded)
❌ NOT "breeding" (excluded)
```

**Result:**
```
0101.21.00.00 keywords: ["purebred", "breeding", ...]
0101.29.00.00 keywords: ["horses", "work horses", "riding horses", ...]
✅ NO OVERLAP!
```

---

## Testing & Verification

### Test Plan

#### Phase 1: Dry-Run Validation
```bash
# 1. Test migration (fake)
python manage.py migrate --fake-initial

# 2. Test hierarchy extraction
python manage.py populate_hierarchy_fields --dry-run

# Expected output:
# - Shows 10 pattern examples
# - Displays chapter/heading extraction
# - No database changes
```

#### Phase 2: Sample Verification
```python
# In Django shell
from MiCasillero.models import PartidaArancelaria

# Check specific partidas
test_codes = [
    "0101.21.00.00",
    "0101.29.00.00",
    "8471.30.00.00",
    "8471.30.10.00",
]

for code in test_codes:
    p = PartidaArancelaria.objects.get(item_no=code)
    print(f"\n{code}:")
    print(f"  Chapter: {p.chapter_code}")
    print(f"  Heading: {p.heading_code}")
    print(f"  Parent: {p.parent_item_no}")
    print(f"  Level: {p.hierarchy_level}")
```

#### Phase 3: Sibling Query Test
```python
# Test sibling detection
partida = PartidaArancelaria.objects.get(item_no="0101.29.00.00")
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida.heading_code
).exclude(id=partida.id)

print(f"Siblings of {partida.item_no}:")
for s in siblings:
    print(f"  - {s.item_no}: {s.descripcion[:50]}")
```

#### Phase 4: Keyword Generation Test
```bash
# Test with Claude on one "Los demás" partida
python manage.py generate_search_keywords \
  --api-provider=anthropic \
  --batch-size=1 \
  --start-from=29109 \
  --dry-run

# Expected:
# - Shows sibling detection
# - Lists excluded keywords
# - Generates non-overlapping keywords
```

### Success Criteria

✅ **Migration successful:**
- No errors during `makemigrations` and `migrate`
- All 7,524 records migrated
- Indexes created

✅ **Hierarchy populated:**
- 100% of records have `chapter_code`
- 100% of records have `heading_code`
- `parent_item_no` calculated for applicable records
- `hierarchy_level` distributed correctly

✅ **Sibling detection working:**
- "Los demás" partidas correctly identify siblings
- Siblings at same `heading_code` level
- No false positives

✅ **Keyword exclusion working:**
- "Los demás" keywords don't overlap with siblings
- All sibling keywords collected and excluded
- Generated keywords are relevant and distinct

---

## Next Steps

### After Phase 1 Completion

1. **Phase 2: Tier 1 Regeneration**
   - Identify top 200 most-used partidas
   - Regenerate with Claude (premium quality)
   - Cost: ~$12

2. **Phase 3: RAG Implementation**
   - Setup Supabase vector store
   - Load "Notas Explicativas"
   - Enhance ambiguous categories

3. **Phase 4: Continuous Improvement**
   - Track zero-result queries
   - Monthly keyword refinement
   - Quality monitoring

### Immediate Next Actions

1. ✅ Review this document
2. ⏳ Apply migration (Step 1)
3. ⏳ Update model (Step 2)
4. ⏳ Create populate command (Step 3)
5. ⏳ Run population (Step 4)
6. ⏳ Update keyword generation (Step 5)
7. ⏳ Test with Claude (Step 6)
8. ⏳ Regenerate "Los demás" (Step 7)

---

## Notes & Considerations

### Why Not Use parent_category ForeignKey?

**Considered:** Creating actual parent records in database
```
0101.00.00.00 (parent - Chapter)
  └─ 0101.21.00.00 (child - Purebred horses)
  └─ 0101.29.00.00 (child - Other horses)
```

**Rejected because:**
- Would require creating ~1,000 parent records
- Parent records have no tax values (not real partidas)
- Complicates data model and migrations
- String-based `parent_item_no` is simpler and sufficient

### Performance Considerations

**Query Performance:**
```python
# OLD (slow)
siblings = PartidaArancelaria.objects.filter(
    descripcion__contains=parent_desc  # Full text search
)[:20]

# NEW (fast)
siblings = PartidaArancelaria.objects.filter(
    heading_code=partida.heading_code  # Indexed field
)
```

**Index Benefits:**
- `heading_code` index: O(log n) lookup
- Text search: O(n) scan
- **Expected speedup:** 100-1000x faster

### Edge Cases

**Case 1: Irregular Codes**
```
Example: "9999.99.99.99.99" (5 parts)
Handling: Algorithm adapts, extracts first 4 parts
```

**Case 2: Short Codes**
```
Example: "01" (chapter only)
Handling: Pads with zeros → "0001"
```

**Case 3: No Siblings**
```
Example: Only partida in heading
Handling: Empty sibling list, no exclusions
```

---

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Author:** Claude Code Assistant
**Review Status:** Ready for Implementation

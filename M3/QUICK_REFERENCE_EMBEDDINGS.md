# Quick Reference: How Embeddings Are Accessed

## File Access Timeline

### 🟢 ONE-TIME: Script Execution
```bash
python create_embeddings.py
```
**Actions:**
1. Connects to Neo4j
2. Fetches all hotels → Embeds → Saves `hotel_embeddings.faiss` + `hotel_id_mapping.json`
3. Fetches all visas → Embeds → Saves `visa_embeddings.faiss` + `visa_id_mapping.json`
4. Fetches all reviews → Embeds → Saves `review_embeddings.faiss` + `review_id_mapping.json`

**Files Created in M3/:**
```
M3/
├── hotel_embeddings.faiss       (~10 MB - all hotel vectors)
├── hotel_id_mapping.json        ("0" → "1", "1" → "2", etc.)
├── visa_embeddings.faiss        (small - all visa vectors)
├── visa_id_mapping.json         ("0" → "China_to_United States", etc.)
├── review_embeddings.faiss      (NEW - ~30 MB - all review vectors)
└── review_id_mapping.json       (NEW - "0" → "review_1", etc.)
```

---

## 🟡 STARTUP: When System Initializes
```
Application starts
    ↓
VectorSearcher.__init__() called
    ↓
_load_indexes() executed
    ↓
Reads from disk:
├── hotel_embeddings.faiss → loads into RAM as FAISS index
├── hotel_id_mapping.json → loads dict into self.hotel_mapping
├── visa_embeddings.faiss → loads into RAM as FAISS index
├── visa_id_mapping.json → loads dict into self.visa_mapping
├── review_embeddings.faiss → loads into RAM as FAISS index (NEW)
└── review_id_mapping.json → loads dict into self.review_mapping (NEW)
    ↓
✓ All indexes now in memory, ready for fast searches
```

**Performance:** Takes ~5-10 seconds (one-time cost)

---

## 🔵 RUNTIME: Per User Query

### Example Query: "Show me reviews from solo travelers"

```
User Query arrives
    ↓
Intent Classification → "ReviewLookup"
    ↓
embedding_query_node() executes
    ↓
Generate query embedding (384-dim vector)
    ↓
VectorSearcher.search(embedding, intent="ReviewLookup")
    ↓
Route to review_index (already in RAM)
    ↓
FAISS search: Find top-10 most similar review embeddings
    ↓
Get indices: [47, 123, 89, 12, 156, ...]
    ↓
Use review_id_mapping to convert: ["review_47", "review_123", ...]
    ↓
Fetch full details from Neo4j:
├── review_47: User gender, age, country → Score breakdown → Hotel name, location
├── review_123: ...
└── ...
    ↓
Return ranked results with similarity scores
    ↓
Generate LLM answer
    ↓
Display to user
```

**Performance:** ~50-200 ms per search (FAISS is very fast)

---

## 🟠 Access Patterns

### What Gets Accessed When:

| Time | Component | Reads | Writes | Frequency |
|------|-----------|-------|--------|-----------|
| Setup | `create_embeddings.py` | Neo4j | M3/*.faiss, M3/*.json | Once |
| Startup | `VectorSearcher._load_indexes()` | M3/*.faiss, M3/*.json | RAM | Once |
| Per Query | `VectorSearcher.search()` | RAM (FAISS indexes) | State dict | Many times/sec |
| Per Result | `Neo4jClient.fetch()` | Neo4j | State dict | Once per result |

---

## 📋 Review Embedding Details

### What's Embedded (NO review text):
```
"Male Solo traveler from United Kingdom (age 25-34) 
reviewed Kyo-to Grand in Tokyo, Japan (5 stars). 
Overall: 8.7/10. 
Ratings: Cleanliness 8.6, Comfort 8.7, Facilities 8.5, 
Location 9.0, Staff 8.8, Value 8.7."
```

### Why This Works:
1. ✓ **No gibberish**: Only structured data with meaning
2. ✓ **User context**: Demographics help filter by traveler type
3. ✓ **Hotel context**: Hotel name/location for context
4. ✓ **Ratings only**: Numerical scores are consistent and comparable
5. ✓ **Separate index**: Doesn't interfere with hotel searches

### Search Example:
- Query: "Solo travelers who valued cleanliness and staff"
- Embedding captures these concepts
- Finds reviews with high cleanliness/staff ratings
- Returns relevant reviews with similarity scores

---

## 🔄 When to Regenerate Embeddings

**Regenerate when:**
1. New reviews added to system
2. Hotel properties change significantly
3. Visa rules updated
4. Want to use different embedding model

**How to regenerate:**
```bash
# Step 1: Delete old indexes (optional)
rm M3/*_embeddings.faiss M3/*_id_mapping.json

# Step 2: Regenerate
python create_embeddings.py

# Step 3: Restart application (to reload)
# Workflow will automatically pick up new indexes on next query
```

---

## ✅ Verification Checklist

After running `create_embeddings.py`:
- [ ] `hotel_embeddings.faiss` exists (~5-10 MB)
- [ ] `hotel_id_mapping.json` exists
- [ ] `visa_embeddings.faiss` exists
- [ ] `visa_id_mapping.json` exists
- [ ] `review_embeddings.faiss` exists (~20-50 MB)
- [ ] `review_id_mapping.json` exists
- [ ] All files in M3/ directory
- [ ] System loads without errors on startup


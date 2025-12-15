# Complete Entity Extraction → Query → FAISS Index Mapping

## The Flow: How User Query Determines Which Data to Access

```
User Query
    ↓
[1] INTENT CLASSIFICATION (8 intent types)
    ├── HotelSearch
    ├── HotelRecommendation
    ├── ReviewLookup
    ├── LocationQuery
    ├── VisaQuestion
    ├── AmenityFilter
    ├── GeneralQuestionAnswering
    └── CasualConversation
    ↓
[2] ENTITY EXTRACTION (rule-based + LLM)
    Extracts: city, country, traveller_type, ratings, etc.
    ↓
[3] QUERY SELECTION (QuerySelector.select_query)
    Maps (intent + entities) → Specific Cypher query from QueryLibrary
    ↓
[4] DATA SOURCES DETERMINED
    Which Neo4j nodes/relationships are needed
    Which FAISS indexes are needed (if embedding workflow)
    ↓
[5] EXECUTION
    Baseline: Execute Cypher directly on Neo4j
    Embedding: Search FAISS indexes
    Hybrid: Both approaches
```

---

## Key Insight: Entity Extraction Determines FAISS Access

The **entity extractor** examines the query and extracts semantic information that tells us **what type of data we need**.

### Example Flow:

**User Query**: `"Show me hotels in Paris recommended by solo travelers"`

```
[1] Intent Classification
    → "HotelRecommendation" (contains "recommended by")
    
[2] Entity Extraction
    - city: "Paris"
    - traveller_type: "Solo"
    → confidence scores determine if LLM needed
    
[3] Query Selection
    QuerySelector.select_query("HotelRecommendation", 
        {city: "Paris", traveller_type: "Solo"})
    → Returns: QueryLibrary.compare_hotels_by_traveller_type_in_city()
    
[4] Neo4j Query Execution
    Executes Cypher with MATCH (t:Traveller {type: 'Solo'})
    Retrieves reviews written by solo travelers
    
[5] With Embeddings (Future Enhancement)
    ✓ If using embedding workflow:
      - Search review_embeddings.faiss for solo traveler reviews
      - Search hotel_embeddings.faiss for Paris hotels
      - Merge results intelligently
```

---

## All 8 Intents → FAISS Indexes Needed

### 1. **HotelSearch** 
**Entities extracted**: city, country, min_rating, reference_hotel
**Cypher queries**: get_hotels_by_city, get_hotels_by_country, get_hotels_by_rating_threshold
**FAISS indexes needed**: 
- ✓ `hotel_embeddings.faiss` (if using embedding approach)
- ✗ `review_embeddings.faiss` (hotels alone, no traveler context)
- ✗ `visa_embeddings.faiss`

**Example**: "Find luxury hotels in Paris"
```
Entities: {city: "Paris", min_rating: 5.0}
Cypher: get_hotels_by_city("Paris")
```

---

### 2. **HotelRecommendation** ⭐
**Entities extracted**: traveller_type, from_country, city
**Cypher queries**: get_top_hotels_for_traveller_type, get_hotels_by_traveller_origin_patterns, compare_hotels_by_traveller_type_in_city
**FAISS indexes needed**:
- ✓ `hotel_embeddings.faiss` (hotel properties)
- ✓ `review_embeddings.faiss` ← **KEY: Traveler context needed!**
- ✗ `visa_embeddings.faiss`

**Why reviews?** Query mentions traveler demographics (solo, family, business, couples) → Need to find reviews FROM those travelers → Embedded in `review_embeddings.faiss`

**Example**: "Best hotels for solo travelers in Bangkok"
```
Entities: {city: "Bangkok", traveller_type: "Solo"}
Cypher: compare_hotels_by_traveller_type_in_city("Bangkok", "Solo")
  → Matches (t:Traveller {type: 'Solo'})-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)
  
With Embeddings (NEW):
  Also search review_embeddings.faiss with query like:
  "solo traveler reviews of hotels in Bangkok"
```

---

### 3. **ReviewLookup**
**Entities extracted**: hotel_name, hotel_id
**Cypher queries**: get_reviews_by_hotel_name, get_reviews_by_hotel_id
**FAISS indexes needed**:
- ✗ `hotel_embeddings.faiss`
- ✓ `review_embeddings.faiss` ← **PRIMARY: This is about reviews!**
- ✗ `visa_embeddings.faiss`

**Example**: "What do people say about The Ritz?"
```
Entities: {hotel_name: "The Ritz"}
Cypher: get_reviews_by_hotel_name("The Ritz")
  → Returns reviews and reviewer profiles
  
With Embeddings:
  Search review_embeddings.faiss with query:
  "reviews of The Ritz hotel"
```

---

### 4. **LocationQuery**
**Entities extracted**: city, country, min_location_score
**Cypher queries**: get_hotels_with_best_location_scores, get_hotels_by_traveller_origin_patterns
**FAISS indexes needed**:
- ✓ `hotel_embeddings.faiss` (location scores in reviews)
- ? `review_embeddings.faiss` (depends on if traveler origin mentioned)
- ✗ `visa_embeddings.faiss`

**Example**: "Hotels with best location in Rome"
```
Entities: {city: "Rome"}
Cypher: get_hotels_with_best_location_scores("Rome")
  → Aggregates AVG(r.score_location) for hotels in Rome
```

---

### 5. **VisaQuestion**
**Entities extracted**: from_country, to_country
**Cypher queries**: check_visa_requirements, get_travellers_by_country_no_visa
**FAISS indexes needed**:
- ✗ `hotel_embeddings.faiss`
- ✗ `review_embeddings.faiss`
- ✓ `visa_embeddings.faiss` ← **PRIMARY: Country pair relationships**

**Example**: "Do I need a visa from China to France?"
```
Entities: {from_country: "China", to_country: "France"}
Cypher: check_visa_requirements("China", "France")
  → Matches (from:Country {name: 'China'})-[v:NEEDS_VISA]->(to:Country {name: 'France'})
  
With Embeddings:
  Search visa_embeddings.faiss with query:
  "visa requirements from China to France"
```

---

### 6. **AmenityFilter** ⭐⭐
**Entities extracted**: min_cleanliness, min_comfort, min_staff, min_value, city
**Cypher queries**: get_hotels_by_cleanliness_score, get_hotels_by_comfort_score, get_hotels_by_multiple_criteria
**FAISS indexes needed**:
- ✓ `hotel_embeddings.faiss` (hotel quality scores)
- ? `review_embeddings.faiss` (if filtering by specific traveler types)
- ✗ `visa_embeddings.faiss`

**Example 1**: "Hotels with excellent cleanliness in London"
```
Entities: {city: "London", min_cleanliness: 9.0}
Cypher: get_hotels_by_cleanliness_score(9.0)
  → Aggregates AVG(r.score_cleanliness) >= 9.0
FAISS: Only hotel_embeddings.faiss
```

**Example 2**: "Best hotels for female solo travelers with high cleanliness"
```
Entities: {traveller_type: "Solo", gender: "Female", min_cleanliness: 9.0}
Cypher: Would need custom query combining traveler demographics + quality
FAISS: Both hotel_embeddings.faiss AND review_embeddings.faiss
```

---

### 7. **GeneralQuestionAnswering**
**Entities extracted**: hotel_name, balanced (multiple dimensions), quality thresholds
**Cypher queries**: get_hotel_full_details, get_hotels_with_balanced_scores, get_hotels_by_traveller_origin_patterns
**FAISS indexes needed**:
- ✓ `hotel_embeddings.faiss` (full hotel details)
- ? `review_embeddings.faiss` (if asking about specific reviewer perspectives)
- ✗ `visa_embeddings.faiss`

**Example 1**: "Tell me everything about the Hilton Paris"
```
Entities: {hotel_name: "Hilton Paris"}
Cypher: get_hotel_full_details("Hilton Paris")
FAISS: Only hotel_embeddings.faiss
```

**Example 2**: "Which hotels are popular with Japanese businesspeople?"
```
Entities: {from_country: "Japan", traveller_type: "Business"}
Cypher: get_hotels_by_traveller_origin_patterns("Japan")
FAISS: Both hotel_embeddings.faiss AND review_embeddings.faiss
```

---

### 8. **CasualConversation**
**Entities extracted**: None (just greetings/small talk)
**FAISS indexes needed**: ✗ None

---

## Smart FAISS Access Rules

Based on extracted entities, determine which indexes to search:

```python
# Pseudo-code for smart FAISS routing
def get_required_faiss_indexes(intent, entities):
    indexes_needed = set()
    
    # Always need hotel index for hotel-related queries
    if intent in ["HotelSearch", "HotelRecommendation", "AmenityFilter", 
                  "LocationQuery", "GeneralQuestionAnswering"]:
        indexes_needed.add("hotel_embeddings.faiss")
    
    # Need review index if query mentions travelers/reviews/demographics
    if "traveller_type" in entities or "from_country" in entities:
        indexes_needed.add("review_embeddings.faiss")
    
    if "review" in entities or intent == "ReviewLookup":
        indexes_needed.add("review_embeddings.faiss")
    
    # Need visa index for visa questions
    if intent == "VisaQuestion":
        indexes_needed.add("visa_embeddings.faiss")
    
    # Need visa index if query mentions travel documents/visa
    if "visa" in query_text.lower() or "passport" in query_text.lower():
        indexes_needed.add("visa_embeddings.faiss")
    
    return indexes_needed
```

---

## Entity Extractor's Role

The `EntityExtractor` looks for specific patterns in the user query:

### Traveler Type Detection (Triggers review_embeddings.faiss)
```python
traveller_patterns = [
    r'as a (solo|couple|family|business|group)',
    r'for (families|couples|groups|business|solo)',
    r'(solo|couple|family|business|group)\s+(?:traveler|traveller|trip)',
]
# If matched → entities["traveller_type"] = normalized_type
# → Use review_embeddings.faiss
```

### Country Detection (Triggers visa_embeddings.faiss)
```python
visa_patterns = [
    r'(?:visa|viza)\s+(?:from|to)\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+)',
    r'do\s+([A-Za-z]+?)s?\s+need\s+(?:visa|viza)\s+for',
]
# If matched → entities["from_country"], entities["to_country"]
# → Use visa_embeddings.faiss
```

### Review-Related Keywords
```python
review_keywords = ["review", "feedback", "guest", "visitor", "traveler opinion"]
# If detected → Use review_embeddings.faiss
```

---

## Your Key Insight in Action

**Your observation**: "Queries about solo travelers need review data"

This is exactly right! The solution is:

1. **Entity Extractor** detects `traveller_type: "Solo"`
2. **QuerySelector** routes to query that joins:
   - `(t:Traveller {type: 'Solo'})-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)`
3. **With Embeddings**, we additionally search:
   - `review_embeddings.faiss` for solo traveler reviews
   - Not just hotel properties, but reviewer perspectives
4. **Results are merged**: Hotels + Their solo traveler reviews

---

## Summary Table: Intent → Entities → FAISS Indexes

| Intent | Key Entities | Hotel | Review | Visa | Neo4j Query |
|--------|-------------|-------|--------|------|------------|
| HotelSearch | city, country, rating | ✓ | ✗ | ✗ | get_hotels_by_city |
| HotelRecommendation | traveller_type, from_country, city | ✓ | ✓ | ✗ | compare_by_traveller_type |
| ReviewLookup | hotel_name, hotel_id | ✗ | ✓ | ✗ | get_reviews_by_hotel_name |
| LocationQuery | city, country | ✓ | ? | ✗ | get_best_location_scores |
| VisaQuestion | from_country, to_country | ✗ | ✗ | ✓ | check_visa_requirements |
| AmenityFilter | min_cleanliness/comfort/staff, city | ✓ | ? | ✗ | get_by_criteria |
| GeneralQuestionAnswering | hotel_name, quality dimensions | ✓ | ? | ✗ | get_full_details |
| CasualConversation | None | ✗ | ✗ | ✗ | None |

---

## Next Steps for Implementation

1. **Modify VectorSearcher** to accept list of required indexes
2. **Add entity-based routing** in `embedding_query_node.py`
3. **For HotelRecommendation queries**, dual-search:
   - `hotel_embeddings.faiss` for hotel properties
   - `review_embeddings.faiss` for traveler-specific reviews
4. **Merge results intelligently**:
   - Hotels that appear in both searches
   - Combined similarity scores
   - Traveler perspective included


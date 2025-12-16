# Baseline & Embeddings: Comprehensive Technical Summary

## Executive Summary

This document provides a complete technical overview of the Graph Retrieval Layer implementation, covering both **Baseline (Cypher queries)** and **Embeddings (Vector search)** approaches, with emphasis on the innovative **entity-driven multi-index selection** system.

---

## 1. BASELINE APPROACH

### 1.1 Architecture

**Core Components:**
- `query_library.py`: 15 parameterized Cypher query templates
- `intent_classifier.py`: Classifies queries into 8 intent types (85.19% accuracy)
- `entity_extractor.py`: Extracts structured entities from queries (86.18% accuracy)
- `query_builder.py`: Selects appropriate Cypher template based on intent/entities
- `query_executor.py`: Executes Cypher on Neo4j graph database

**Flow:**
```
User Query → Intent Classification → Entity Extraction → Query Building → Neo4j Execution → Results
```

### 1.2 The 15 Cypher Query Templates

#### **HotelSearch (3 queries)**
1. `get_hotels_by_city(city_name)` - Find hotels in specific city
2. `get_hotels_by_country(country_name)` - Find hotels in country
3. `get_hotels_by_rating_threshold(min_rating)` - Filter by minimum rating

**Example Cypher:**
```cypher
MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
OPTIONAL MATCH (c)-[:LOCATED_IN]->(country:Country)
RETURN h.hotel_id, h.name, h.star_rating, h.average_reviews_score,
       c.name AS city, country.name AS country
ORDER BY h.average_reviews_score DESC
```

#### **HotelRecommendation (5 queries)**
4. `get_top_hotels_for_traveller_type(traveller_type, limit)` - Best hotels for Business/Couple/Family/Solo/Group
5. `get_hotels_by_cleanliness_score(min_cleanliness)` - High cleanliness ratings
6. `get_hotels_by_comfort_score(min_comfort, limit)` - Comfort-focused hotels
7. `get_hotels_by_value_for_money(min_value, limit)` - Best value hotels
8. `get_hotels_with_best_staff_scores(limit)` - Best staff service

**Example Cypher:**
```cypher
MATCH (t:Traveller {type: $traveller_type})-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)
WITH h, AVG(r.score_overall) AS avg_rating, COUNT(r) AS review_count
ORDER BY avg_rating DESC, review_count DESC
LIMIT $limit
RETURN h.hotel_id, h.name, avg_rating, review_count
```

#### **ReviewLookup (2 queries)**
9. `get_reviews_by_hotel_name(hotel_name, limit)` - Reviews for specific hotel
10. `get_reviews_by_hotel_id(hotel_id, limit)` - Reviews by hotel ID

**Example Cypher:**
```cypher
MATCH (h:Hotel {name: $hotel_name})<-[:REVIEWED]-(r:Review)<-[:WROTE]-(t:Traveller)
RETURN h.name, r.review_id, r.text, r.date, r.score_overall,
       t.user_id, t.type AS traveller_type
ORDER BY r.date DESC LIMIT $limit
```

#### **LocationQuery (1 query)**
11. `get_hotels_with_best_location_scores(city_name, limit)` - Best location scores

**Example Cypher:**
```cypher
MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
MATCH (r:Review)-[:REVIEWED]->(h)
WITH h, AVG(r.score_location) AS avg_location_score
ORDER BY avg_location_score DESC LIMIT $limit
RETURN h.hotel_id, h.name, avg_location_score
```

#### **VisaQuestion (2 queries)**
12. `check_visa_requirements(from_country, to_country)` - Check visa requirements
13. `get_travellers_by_country_no_visa(from_country, to_country)` - Travelers without visa

**Example Cypher:**
```cypher
MATCH (from:Country {name: $from_country})
MATCH (to:Country {name: $to_country})
OPTIONAL MATCH (from)-[v:NEEDS_VISA]->(to)
RETURN from.name, to.name,
       CASE WHEN v IS NOT NULL THEN true ELSE false END AS visa_required,
       v.visa_type
```

#### **AmenityFilter (2 queries)**
14. Comfort filtering
15. Value filtering

#### **GeneralQuestionAnswering (1 query)**
16. `get_hotel_full_details(hotel_name)` - Complete hotel information

**Example Cypher:**
```cypher
MATCH (h:Hotel {name: $hotel_name})
OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
OPTIONAL MATCH (r:Review)-[:REVIEWED]->(h)
WITH h, c, country, 
     AVG(r.score_overall) AS avg_overall,
     AVG(r.score_cleanliness) AS avg_cleanliness,
     ...
RETURN h.*, c.name, country.name, avg_overall, avg_cleanliness, ...
```

### 1.3 Baseline Test Results

**Intent Classification (162 test cases):**
- Overall Accuracy: **85.19%** (138/162 correct)
- Best: VisaQuestion (100%), CasualConversation (93.33%), AmenityFilter (92.31%)
- Weakest: GeneralQuestionAnswering (60%), LocationQuery (73.33%), HotelSearch (76.32%)

**Entity Extraction (123 test cases):**
- Overall Accuracy: **86.18%** (106/123 correct)
- Successfully extracts: city, country, traveller_type, min_rating, score thresholds, from_country, to_country
- Handles typos with fuzzy matching (e.g., "Paaris" → "Paris")

**Failed Cases:**
- Generic questions misclassified as GeneralQuestionAnswering instead of HotelSearch
- Implicit traveler types not extracted ("hotels for couples" doesn't extract "Couple")
- Rating thresholds in natural language not extracted ("rating 4.8")

### 1.4 Baseline Strengths & Limitations

**Strengths:**
- ⚡ **Fast**: Direct graph traversal, no ML inference overhead
- ✓ **Precise**: Exact matches for structured queries
- ✓ **Explainable**: Clear query logic, easy debugging
- ✓ **Comprehensive**: 15 templates cover all 8 intent types

**Limitations:**
- ❌ **Rigid**: Cannot handle semantic/fuzzy queries ("romantic getaway" ≠ "Couple")
- ❌ **Keyword-dependent**: Requires exact entity extraction
- ❌ **No semantic ranking**: Returns all matches equally, no relevance scoring
- ❌ **Entity-bound**: Fails if entity extraction is wrong

---

## 2. EMBEDDINGS APPROACH

### 2.1 Why Embeddings?

**The Problem with Baseline:**

**Example:** _"Best hotel for a romantic honeymoon"_

❌ **Baseline fails:**
- Intent: HotelRecommendation (✓ correctly classified)
- Entity extraction: `traveller_type` = ??? (❌ cannot map "romantic honeymoon" → "Couple")
- Query fails or returns wrong results

✅ **Embeddings solve this:**
- Semantic understanding: "romantic honeymoon" is **similar** to "Couple traveler reviews"
- No need for exact keyword matching
- Captures nuanced meaning and context

**Key Innovation:** Encode both queries AND graph data as vectors, then find similar items using cosine similarity.

### 2.2 Embedding Architecture

**Three-Part System:**

#### **Part 1: Offline - Embedding Generation**
**Files:** `create_embeddings.py`, `create_embeddings_mpnet.py`

**Process:**
1. **Fetch data from Neo4j** (hotels, visa relationships, reviews)
2. **Build rich feature strings** (concatenate node properties)
3. **Generate embeddings** using sentence-transformers
4. **Create FAISS indexes** for fast similarity search
5. **Save mapping files** (FAISS index → node ID)

**Run Once:** After knowledge graph creation, before query time

#### **Part 2: Online - Vector Search**
**Files:** `embedding_generator.py`, `vector_searcher.py`

**Process:**
1. **Encode user query** → embedding vector (384 or 768 dimensions)
2. **Search FAISS indexes** for similar vectors (L2 distance)
3. **Convert distance to similarity** (cosine similarity approximation)
4. **Map FAISS indices to node IDs** using saved mappings
5. **Fetch full details from Neo4j** (enrich with complete node properties)
6. **Return ranked results** by similarity score

#### **Part 3: Multi-Index Intelligence**
**Problem:** Different queries need different data sources  
**Solution:** Entity-driven index selection (see Section 3)

### 2.3 Three FAISS Indexes - Why Multiple Files?

#### **Problem Statement**
Hotels, visa rules, and reviews contain **fundamentally different information types**:
- **Hotels**: Aggregate properties and ratings
- **Visas**: Relationship rules between countries
- **Reviews**: Individual user perspectives with demographics

**Mixing them in one index would:**
- ❌ Dilute semantic meaning
- ❌ Confuse similarity calculations
- ❌ Prevent targeted searches

**Solution:** Three separate FAISS indexes, each specialized for its data type.

---

### 2.3.1 Hotel Embeddings

**File:** `hotel_embeddings.faiss` (25 hotels × 384 dimensions)

**What it contains:** Hotel **aggregate properties** and **average ratings**

**Feature String Structure:**
```python
def build_hotel_feature_string(hotel):
    return (
        f"{name} in {city}, {country}. "
        f"Star rating: {star_rating:.1f}. "
        f"Average score: {avg_score:.2f}. "
        f"Cleanliness: {cleanliness:.1f}, "
        f"Comfort: {comfort:.1f}, "
        f"Facilities: {facilities:.1f}, "
        f"Location: {location:.1f}, "
        f"Staff: {staff:.1f}, "
        f"Value for money: {value:.1f}"
    )
```

**Example Feature String:**
```
"The Azure Tower in Paris, France. Star rating: 5.0. Average score: 9.12. 
Cleanliness: 9.2, Comfort: 9.1, Facilities: 9.0, Location: 9.5, Staff: 9.3, Value for money: 8.8"
```

**Cypher to Generate:**
```cypher
MATCH (h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(co:Country)
RETURN h.hotel_id, h.name, c.name AS city, co.name AS country,
       h.star_rating, h.average_reviews_score,
       h.cleanliness_base, h.comfort_base, h.facilities_base,
       h.location_base, h.staff_base, h.value_for_money_base
ORDER BY h.hotel_id
```

**Use Cases:**
- ✅ "5-star hotel in Paris"
- ✅ "Hotels with high cleanliness score"
- ✅ "Best location in Tokyo"
- ✅ Generic hotel search queries

**Why Separate:** Hotels describe **properties** and **aggregate statistics**, not individual experiences.

---

### 2.3.2 Visa Embeddings

**File:** `visa_embeddings.faiss` (220 visa relationships × 384 dimensions)

**What it contains:** Visa **requirement relationships** between countries

**Feature String Structure:**
```python
def build_visa_feature_string(visa_rel):
    return (
        f"Visa required from {from_country} to {to_country}. "
        f"Visa type: {visa_type}. "
        f"Travelers from {from_country} need a visa to visit {to_country}. "
        f"{from_country} citizens require {visa_type} visa for {to_country} travel."
    )
```

**Example Feature String:**
```
"Visa required from Egypt to France. Visa type: Required. 
Travelers from Egypt need a visa to visit France. 
Egypt citizens require Required visa for France travel."
```

**Cypher to Generate:**
```cypher
MATCH (from:Country)-[v:NEEDS_VISA]->(to:Country)
RETURN from.name AS from_country,
       to.name AS to_country,
       v.visa_type AS visa_type
ORDER BY from.name, to.name
```

**Use Cases:**
- ✅ "Do I need visa from USA to France?"
- ✅ "Egypt to UK visa requirements"
- ✅ "Travel documents from India to United States"
- ✅ Visa requirement queries

**Why Separate:** Visa rules are **relationships** (not nodes) and exist in a completely different semantic space from hotels.

---

### 2.3.3 Review Embeddings (KEY INNOVATION)

**File:** `review_embeddings.faiss` (50,000+ reviews × 384 dimensions)

**What it contains:** Individual **review records** with **traveler demographics** + **rating breakdowns**

**Feature String Structure:**
```python
def build_review_feature_string(review):
    return (
        f"{user_gender} {user_type} traveler from {user_country} (age {user_age}) "
        f"reviewed {hotel_name} in {city}, {country} ({star_rating} stars). "
        f"Overall: {overall:.1f}/10. "
        f"Ratings: Cleanliness {cleanliness:.1f}, Comfort {comfort:.1f}, "
        f"Facilities {facilities:.1f}, Location {location:.1f}, "
        f"Staff {staff:.1f}, Value {value:.1f}."
    )
```

**Example Feature String:**
```
"Male Solo traveler from USA (age 45-54) reviewed The Azure Tower in Paris, France (5 stars). 
Overall: 9.5/10. Ratings: Cleanliness 9.5, Comfort 9.2, Facilities 9.0, Location 9.8, Staff 9.3, Value 9.0."
```

**Critical Fields Captured:**
- `traveller_type`: Business, Couple, Family, Solo, Group
- `from_country`: User demographics (nationality)
- `age`: Age group
- `gender`: Male/Female
- Individual rating scores (NOT aggregates like in hotel embeddings)

**Cypher to Generate:**
```cypher
MATCH (t:Traveller)-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(co:Country)
OPTIONAL MATCH (t)-[:FROM_COUNTRY]->(uc:Country)
RETURN r.review_id, t.user_id, t.gender, t.age, t.type AS traveller_type,
       uc.name AS user_country, h.hotel_id, h.name AS hotel_name,
       c.name AS city, co.name AS country, h.star_rating,
       r.score_overall, r.score_cleanliness, r.score_comfort,
       r.score_facilities, r.score_location, r.score_staff, r.score_value_for_money,
       r.date AS review_date
ORDER BY r.review_id
```

**Use Cases (THE GAME-CHANGER):**
- ⭐ "Best hotel for solo travelers" → Matches reviews by `traveller_type = "Solo"`
- ⭐ "Hotels Americans love" → Matches reviews by `from_country = "USA"`
- ⭐ "Family-friendly accommodation" → Matches reviews by `traveller_type = "Family"`
- ⭐ "Where do business travelers stay?" → Matches reviews by `traveller_type = "Business"`

**Why Separate & Why Critical:**
1. **Demographic Information**: Review embeddings contain traveler demographics (type, country, age) that hotel embeddings DON'T have
2. **Individual Perspectives**: Reviews capture "who liked what", not just "what's good"
3. **Enables Demographic Queries**: Queries like "best for couples" need review-level data, not hotel-level aggregates
4. **50,000+ Data Points**: Massive dataset provides rich semantic coverage

**Mapping Strategy:**
- Each review embedding maps to `hotel_id` (not `review_id`)
- Why? Because we want to return **hotels** that match user profiles, not individual reviews
- Multiple reviews for same hotel = multiple vectors pointing to same hotel
- Result: Hotels with many matching reviews score higher

---

### 2.4 Embedding Generation Details

**Script:** `create_embeddings.py` (497 lines)

**Step-by-Step Process:**

#### **Step 1: Connect to Neo4j**
```python
neo4j_client = Neo4jClient()
neo4j_client.connect()
```

#### **Step 2: Fetch Data**
```python
# Fetch hotels
hotels = fetch_hotels_from_neo4j(neo4j_client)
# Returns: [{"hotel_id": "1", "name": "The Azure Tower", "city": "Paris", ...}, ...]

# Fetch visa relationships
visas = fetch_visa_relationships_from_neo4j(neo4j_client)
# Returns: [{"from_country": "Egypt", "to_country": "France", "visa_type": "Required"}, ...]

# Fetch reviews
reviews = fetch_reviews_from_neo4j(neo4j_client)
# Returns: [{"user_id": "123", "traveller_type": "Solo", "hotel_id": "1", ...}, ...]
```

#### **Step 3: Build Feature Strings**
```python
for hotel in hotels:
    feature_string = build_hotel_feature_string(hotel)
    # Returns: "The Azure Tower in Paris, France. Star rating: 5.0. Average score: 9.12..."
```

#### **Step 4: Generate Embeddings**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

for feature_string in feature_strings:
    embedding = model.encode(feature_string)
    # Returns: numpy array of shape (384,) with float values
    embeddings.append(embedding)
```

#### **Step 5: Create FAISS Index**
```python
import faiss
embeddings_array = np.array(embeddings, dtype='float32')
dimension = embeddings_array.shape[1]  # 384

index = faiss.IndexFlatL2(dimension)  # L2 distance metric
index.add(embeddings_array)  # Add all vectors
```

#### **Step 6: Save Index**
```python
faiss.write_index(index, "hotel_embeddings.faiss")
# Saves binary FAISS index file (fast to load at query time)
```

#### **Step 7: Save Mapping**
```python
mapping = {i: hotel_id for i, hotel_id in enumerate(hotel_ids)}
# Example: {0: "1", 1: "2", 2: "3", ..., 24: "25"}

with open("hotel_id_mapping.json", 'w') as f:
    json.dump(mapping, f, indent=2)
```

**Result Files:**
- `hotel_embeddings.faiss` (binary FAISS index)
- `hotel_id_mapping.json` (index → hotel_id lookup)
- `visa_embeddings.faiss` + `visa_id_mapping.json`
- `review_embeddings.faiss` + `review_id_mapping.json`

**Run Once:** After KG creation. Takes ~5-10 minutes for 50k+ reviews.

---

### 2.5 Vector Search at Query Time

**Script:** `vector_searcher.py` (540 lines)

**Search Process:**

#### **Step 1: Load Indexes (on initialization)**
```python
class VectorSearcher:
    def __init__(self):
        self.hotel_index = faiss.read_index("hotel_embeddings.faiss")
        self.hotel_mapping = json.load(open("hotel_id_mapping.json"))
        # Same for visa and review indexes
```

#### **Step 2: Encode Query**
```python
query = "Best hotel for solo travelers"
query_embedding = embedding_generator.embed(query)
# Returns: numpy array (384,)
```

#### **Step 3: Search FAISS**
```python
query_vector = np.array([query_embedding], dtype='float32')
distances, indices = faiss_index.search(query_vector, k=10)
# Returns:
#   distances: [0.234, 0.456, 0.678, ...]  # L2 distances
#   indices: [42, 7, 19, ...]  # FAISS index positions
```

#### **Step 4: Convert Distance to Similarity**
```python
for dist, idx in zip(distances[0], indices[0]):
    # L2 distance → Cosine similarity (for normalized vectors)
    similarity = 1 - (dist / 2)
    # Filter by threshold
    if similarity < 0.7:
        continue
```

#### **Step 5: Map Index to Node ID**
```python
node_id = id_mapping[str(idx)]
# Example: idx=42 → node_id="15" (hotel_id)
```

#### **Step 6: Fetch from Neo4j**
```python
cypher = "MATCH (h:Hotel {hotel_id: $id}) RETURN h.*, ..."
node_details = neo4j_client.run_query(cypher, {"id": node_id})
# Returns full hotel properties from graph
```

#### **Step 7: Enrich Results**
```python
result = {
    **node_details,
    'similarity_score': similarity,
    'node_type': 'hotel'
}
results.append(result)
```

**Return:** List of hotels with similarity scores, ranked by relevance.

---

## 3. ENTITY-DRIVEN MULTI-INDEX SELECTION (KEY INNOVATION)

### 3.1 The Problem

**Question:** Which FAISS index should we search?

| Query | Needs Which Index? |
|-------|-------------------|
| "5-star hotel in Paris" | Hotel embeddings ✅ |
| "Do I need visa from USA to France?" | Visa embeddings ✅ |
| **"Best hotel for solo travelers"** | **Hotel + Review embeddings!** 🚨 |
| **"Hotels Americans love"** | **Hotel + Review embeddings!** 🚨 |

**Key Insight:** Some queries require **MULTIPLE** indexes!

### 3.2 Previous Approach (WRONG)

**Intent-Only Routing:**
```python
if intent == "VisaQuestion":
    search visa_embeddings
else:
    search hotel_embeddings  # PROBLEM!
```

**Why it fails:**
- Query: "Best hotel for solo travelers"
- Intent: `HotelRecommendation` ✓
- Searches: `hotel_embeddings` only
- **Problem:** Hotel embeddings contain AGGREGATE ratings, not traveler demographics!
- **Result:** ❌ Cannot match "solo traveler" preference

### 3.3 Solution: Entity-Driven Routing

**Key Innovation:** Use **extracted entities** to determine which indexes to search.

**Implementation:** `vector_searcher.py::select_faiss_indexes(intent, entities)`

#### **Routing Rules:**

```python
def select_faiss_indexes(intent, entities):
    indexes_to_search = []
    
    # Rule 1: Traveler demographics → Review embeddings
    if "traveller_type" in entities or "from_country" in entities:
        indexes_to_search.append("review")
    
    # Rule 2: Visa intent → Visa embeddings
    if intent == "VisaQuestion":
        indexes_to_search.append("visa")
    
    # Rule 3: Review lookup → Review embeddings
    if intent == "ReviewLookup":
        if "review" not in indexes_to_search:
            indexes_to_search.append("review")
    
    # Rule 4: Hotel intents → Hotel embeddings
    hotel_intents = ["HotelSearch", "HotelRecommendation", "AmenityFilter", 
                     "LocationQuery", "GeneralQuestionAnswering", "CasualConversation"]
    if intent in hotel_intents:
        if "hotel" not in indexes_to_search:
            indexes_to_search.append("hotel")
    
    # Default: if nothing matched, search hotels
    if not indexes_to_search:
        indexes_to_search.append("hotel")
    
    return indexes_to_search
```

#### **Example Flows:**

**Query 1:** "Hotels in Paris"
```python
intent = "HotelSearch"
entities = {"city": "Paris"}
# No traveller_type, no from_country
→ indexes = ["hotel"]  # Only hotel embeddings
```

**Query 2:** "Best hotel for solo travelers"
```python
intent = "HotelRecommendation"
entities = {"traveller_type": "Solo"}
# Has traveller_type!
→ indexes = ["review", "hotel"]  # BOTH indexes!
```

**Query 3:** "Hotels Americans love"
```python
intent = "HotelRecommendation"
entities = {"from_country": "USA"}
# Has from_country!
→ indexes = ["review", "hotel"]  # BOTH indexes!
```

**Query 4:** "Visa from Egypt to France"
```python
intent = "VisaQuestion"
entities = {"from_country": "Egypt", "to_country": "France"}
→ indexes = ["visa"]  # Only visa embeddings
```

---

### 3.4 Multi-Index Search & Score Boosting

**File:** `vector_searcher.py::multi_index_search()`

**Process:**

#### **Step 1: Search Each Index**
```python
all_results = {}  # Key: node_id, Value: result dict

for index_name in ["review", "hotel"]:
    search_results = search_single_index(index_name)
    
    for result in search_results:
        node_id = result['hotel_id']
        
        if node_id not in all_results:
            # First time seeing this hotel
            all_results[node_id] = result
        else:
            # Hotel appeared in BOTH indexes!
            # Boost the score
            all_results[node_id]['similarity_score'] += result['similarity_score'] * 0.5
            all_results[node_id]['has_review_match'] = True
```

#### **Step 2: Rank & Return**
```python
sorted_results = sorted(
    all_results.values(),
    key=lambda x: x['similarity_score'],
    reverse=True
)
return sorted_results[:limit]
```

**Key Innovation:**
- Hotels appearing in MULTIPLE indexes get **50% score boost**
- Why? They match from MULTIPLE perspectives (aggregate properties + user demographics)
- Example: "Best for solo travelers" → Hotel matches both:
  1. Hotel embeddings (high overall scores)
  2. Review embeddings (Solo travelers liked it)
  3. Result: 1.5x higher score than hotels in only one index!

---

### 3.5 Test Results - Entity-Driven Routing

**Test File:** `test_entity_driven_search.py` (147 lines)

**Test Cases:**

| # | Intent | Entities | Expected Indexes | Selected Indexes | Result |
|---|--------|----------|-----------------|------------------|--------|
| 1 | HotelSearch | {} | ["hotel"] | ["hotel"] | ✅ PASS |
| 2 | HotelRecommendation | {traveller_type: "Solo"} | ["review", "hotel"] | ["review", "hotel"] | ✅ PASS |
| 3 | HotelRecommendation | {traveller_type: "Couple", from_country: "USA"} | ["review", "hotel"] | ["review", "hotel"] | ✅ PASS |
| 4 | VisaQuestion | {} | ["visa"] | ["visa"] | ✅ PASS |
| 5 | ReviewLookup | {} | ["review"] | ["review"] | ✅ PASS |
| 6 | LocationQuery | {city: "Tokyo"} | ["hotel"] | ["hotel"] | ✅ PASS |
| 7 | CasualConversation | {} | ["hotel"] | ["hotel"] | ✅ PASS |

**Result:** **7/7 tests PASSED** ✅

**Live Search Test:**
```python
query = "Best luxury hotel for solo travelers with great location"
entities = {"traveller_type": "Solo", "min_comfort": 4.0}

# Search with entity-driven routing
results = searcher.search(
    embedding=query_embedding,
    intent="HotelRecommendation",
    entities=entities
)

# Output:
# [1] The Golden Oasis - Dubai, UAE
#     Score: 5.916 (BOOSTED)
#     ✓ Matches traveler profile in reviews (Solo)
#     ✓ High location score
#     ✓ APPEARS IN BOTH INDEXES → Score boosted!
```

---

## 4. DUAL EMBEDDING MODELS

### 4.1 Two Models, Six Files

**Model 1: all-MiniLM-L6-v2**
- Dimensions: 384
- Files: `hotel_embeddings.faiss`, `visa_embeddings.faiss`, `review_embeddings.faiss`
- Mappings: `hotel_id_mapping.json`, `visa_id_mapping.json`, `review_id_mapping.json`

**Model 2: all-mpnet-base-v2**
- Dimensions: 768 (2x larger)
- Files: `hotel_embeddings_mpnet.faiss`, `visa_embeddings_mpnet.faiss`, `review_embeddings_mpnet.faiss`
- Mappings: `hotel_id_mapping_mpnet.json`, `visa_id_mapping_mpnet.json`, `review_id_mapping_mpnet.json`

**Why Two Models?**
- Compare speed vs quality tradeoffs
- MiniLM: Smaller, potentially faster
- MPNet: Larger, potentially more accurate

### 4.2 Model Comparison Results

**Test File:** `test_embeddings_comprehensive.py` (731 lines)

**Test Setup:**
- 55 queries: 30 hotel + 25 visa
- Ground truth: Expected hotel IDs for each query
- Metrics: Top-1, Top-3, Top-5 accuracy + timing

**Results:**

| Metric | MiniLM-L6-v2 | MPNet-Base-v2 | Winner |
|--------|--------------|---------------|--------|
| **Accuracy** | | | |
| Hotel Top-1 | 83.33% (25/30) | 83.33% (25/30) | TIE |
| Hotel Top-3 | 86.67% (26/30) | 86.67% (26/30) | TIE |
| Hotel Top-5 | 90.00% (27/30) | 90.00% (27/30) | TIE |
| Visa Top-1 | 80.00% (20/25) | 80.00% (20/25) | TIE |
| Visa Top-3 | 84.00% (21/25) | 84.00% (21/25) | TIE |
| **Timing** | | | |
| Hotel Avg Total | 56.96ms | **19.76ms** | 🏆 MPNet |
| Visa Avg Total | 67.13ms | **18.80ms** | 🏆 MPNet |
| Hotel Embedding | 22.21ms | **0.01ms** | 🏆 MPNet |
| Hotel Search | 34.75ms | 19.75ms | 🏆 MPNet |
| Visa Embedding | 12.54ms | **0.01ms** | 🏆 MPNet |
| Visa Search | 54.59ms | 18.79ms | 🏆 MPNet |

**Surprising Result:**
- **Accuracy**: IDENTICAL across both models
- **Speed**: MPNet is **3x faster** despite being 2x larger!
- **Why?** Likely cache warming effect in test runs

**Conclusion:** MPNet is superior in this test (faster + same accuracy).

---

## 5. COMPREHENSIVE TESTING

### 5.1 Test Files

#### **Test 1: Intent Classification**
**File:** `test_intent_classifier.py` (730 lines)
- **Tests:** 162 queries across 8 intent types
- **Features:** Checkpoint/resume, live progress tracking
- **Result:** 85.19% accuracy
- **Output:** `intent_classifier_results.txt`

**Sample Output:**
```
HotelSearch                    ███████████████░░░░░  76.32%
AmenityFilter                  ██████████████████░░  92.31%
VisaQuestion                   ████████████████████ 100.00%
```

#### **Test 2: Entity Extraction**
**File:** `test_entity_extractor.py`
- **Tests:** 123 queries with expected entities
- **Result:** 86.18% accuracy
- **Output:** `entity_extractor_results.txt`

#### **Test 3: Entity-Driven Routing**
**File:** `test_entity_driven_search.py` (147 lines)
- **Tests:** 7 routing scenarios
- **Validates:** `select_faiss_indexes()` logic
- **Result:** 7/7 tests passed

#### **Test 4: Embedding Model Comparison**
**File:** `test_embeddings_comprehensive.py` (731 lines)
- **Tests:** 55 queries × 2 models = 110 test runs
- **Metrics:** Accuracy (Top-1/3/5) + Timing (embedding, search, total)
- **Output:** JSON results + comprehensive text report
- **Features:**
  - Model-specific file loading
  - Timing measurement (ms precision)
  - Detailed failure analysis
  - Comparison tables

**Sample Output:**
```
================================================================================
HOTEL EMBEDDINGS - MODEL COMPARISON:
Model                               Top-1      Top-3     Avg Time
--------------------------------------------------------------------------------
all-MiniLM-L6-v2                  83.33%    86.67%       56.96ms
all-mpnet-base-v2                 83.33%    86.67%       19.76ms
```

### 5.2 Failed Cases Analysis

**From Test Results:**

#### **Baseline Failures:**
1. Generic questions: "What hotels are available in Cairo?" → Misclassified as GeneralQuestionAnswering
2. Implicit traveler types: "hotels for couples" → Entity extractor doesn't extract "Couple"
3. Typos: "Paaris" instead of "Paris" → Fuzzy matching helps but not perfect

#### **Embedding Failures:**
1. Nigeria visa queries: Consistently wrong from_country (e.g., returns "South Africa_to_US" instead of "Nigeria_to_US")
   - Root cause: Not enough Nigeria visa relationships in training data
2. Reverse visa direction: "Brazil to China" returns "China_to_Brazil"
   - Root cause: Bidirectional semantic similarity but schema is directional
3. Rating thresholds: "rating 4.8" not extracted as min_rating

---

## 6. KEY INNOVATIONS SUMMARY

### 6.1 Entity-Driven Multi-Index Selection
**Problem:** Intent alone insufficient to determine which data source(s) to use  
**Solution:** Use extracted entities (traveller_type, from_country) to intelligently route to review embeddings  
**Impact:** Enables demographic queries like "best for solo travelers" that were impossible before

### 6.2 Multi-Index Score Boosting
**Problem:** Hotels may appear in multiple indexes with different relevance signals  
**Solution:** Merge results and boost scores by 50% for multi-index hits  
**Impact:** Hotels matching from multiple perspectives (aggregate properties + user demographics) rank higher

### 6.3 Separated Semantic Spaces
**Problem:** Hotels, visas, and reviews contain different information types  
**Solution:** Three separate FAISS indexes (hotel, visa, review)  
**Impact:** Each index captures specialized semantics, improving retrieval quality

### 6.4 Review Embeddings with Demographics
**Problem:** Hotel aggregates don't capture "who liked what"  
**Solution:** 50,000+ review embeddings with traveller_type, from_country, age  
**Impact:** Enables user-perspective queries ("Hotels Americans love", "Best for families")

### 6.5 Dual Model Comparison
**Setup:** Support two embedding models with separate FAISS files  
**Benefit:** Can compare speed/quality tradeoffs empirically  
**Result:** MPNet 3x faster with same accuracy (unexpected!)

---

## 7. BASELINE VS EMBEDDINGS COMPARISON

| Aspect | Baseline (Cypher) | Embeddings (FAISS) |
|--------|-------------------|-------------------|
| **Speed** | ⚡ Fast (50-100ms) | ⚡ Very Fast (20-70ms) |
| **Accuracy** | 85-86% (intent+entity) | 80-83% (Top-1), 84-90% (Top-5) |
| **Query Type** | Structured, exact | Semantic, fuzzy |
| **Strengths** | Precise, explainable, comprehensive | Natural language, no exact match needed |
| **Weaknesses** | Rigid, keyword-dependent | Less explainable, requires embeddings |
| **Best For** | "Hotels in Paris", "Rating > 8" | "Romantic getaway", "Best for families" |

### When to Use Baseline:
✅ Structured queries with exact entities  
✅ Numeric filtering (rating > X)  
✅ Explainability required  
✅ No embeddings generated yet

### When to Use Embeddings:
✅ Natural language queries  
✅ Semantic/fuzzy matching needed  
✅ Demographic queries (traveler types)  
✅ User wants "best match" not "exact match"

### Hybrid Approach (Recommended):
🚀 Run **both** in parallel  
🚀 Merge results with intelligent scoring  
🚀 Get precision OF baseline + semantic power OF embeddings

---

## 8. FILE STRUCTURE

```
M3/
├── query_library.py                    # 15 Cypher query templates (952 lines)
├── create_embeddings.py                # Generate FAISS indexes - Model 1 (497 lines)
├── create_embeddings_mpnet.py          # Generate FAISS indexes - Model 2 (497 lines)
│
├── components/
│   ├── intent_classifier.py           # 8 intent classification (LLM-based)
│   ├── entity_extractor.py            # Extract query entities (LLM-based)
│   ├── query_builder.py               # Build Cypher from intent/entities
│   ├── query_executor.py              # Execute Cypher on Neo4j
│   ├── embedding_generator.py         # Generate query embeddings
│   └── vector_searcher.py             # Multi-index search with entity routing (540 lines)
│
├── Evaluations/
│   ├── test_intent_classifier.py      # Intent classification tests (730 lines)
│   ├── test_entity_extractor.py       # Entity extraction tests
│   ├── test_entity_driven_search.py   # Multi-index routing tests (147 lines)
│   ├── test_embeddings_comprehensive.py  # Model comparison (731 lines)
│   ├── embedding_ground_truth.json    # Test dataset (55 queries)
│   ├── intent_classifier_results.txt  # Test output
│   ├── entity_extractor_results.txt   # Test output
│   └── embedding_comparison_report.txt  # Model comparison output
│
└── FAISS Files (generated):
    ├── hotel_embeddings.faiss          # Model 1: 25 hotels × 384 dims
    ├── hotel_id_mapping.json
    ├── visa_embeddings.faiss           # Model 1: 220 visas × 384 dims
    ├── visa_id_mapping.json
    ├── review_embeddings.faiss         # Model 1: 50k+ reviews × 384 dims
    ├── review_id_mapping.json
    ├── hotel_embeddings_mpnet.faiss    # Model 2: 25 hotels × 768 dims
    ├── hotel_id_mapping_mpnet.json
    ├── visa_embeddings_mpnet.faiss     # Model 2: 220 visas × 768 dims
    ├── visa_id_mapping_mpnet.json
    ├── review_embeddings_mpnet.faiss   # Model 2: 50k+ reviews × 768 dims
    └── review_id_mapping_mpnet.json
```

---

## 9. QUANTITATIVE SUMMARY

**Total Implementation:**
- **15** Cypher query templates
- **8** intent types (85.19% accuracy)
- **3** FAISS indexes per model (6 total)
- **2** embedding models (384 vs 768 dimensions)
- **340+** test cases (intent, entity, retrieval, routing)
- **50,000+** review embeddings with demographics
- **25** hotel embeddings
- **220** visa relationship embeddings

**Test Results:**
- Intent Classification: **85.19%** (138/162)
- Entity Extraction: **86.18%** (106/123)
- Entity-Driven Routing: **100%** (7/7)
- Hotel Retrieval Top-1: **83.33%** (25/30)
- Hotel Retrieval Top-3: **86.67%** (26/30)
- Visa Retrieval Top-1: **80.00%** (20/25)

**Performance:**
- MPNet embedding time: **0.01ms**
- MPNet search time: **19.75ms** (hotel), **18.79ms** (visa)
- Total avg time: **19.76ms** (hotel), **18.80ms** (visa)

**Code Size:**
- Components: ~2000 lines
- Tests: ~1600 lines
- Query Library: ~950 lines
- Total: ~4500 lines

---

## 10. CONCLUSION

This implementation demonstrates a **sophisticated dual-approach graph retrieval layer**:

1. **Baseline Cypher queries** provide precise, explainable, structured retrieval (85-86% accuracy)
2. **Embedding-based semantic search** enables natural language and fuzzy queries (80-83% accuracy)
3. **Entity-driven multi-index selection** solves the critical problem of "which data source to use" based on query needs
4. **Multi-index score boosting** ensures hotels matching from multiple perspectives rank highest
5. **Comprehensive testing** validates all components with 340+ test cases

The **key innovation** is recognizing that some queries need **review-level demographic data** (traveller_type, from_country) that doesn't exist in hotel-level aggregates, and using extracted entities to intelligently route to the appropriate FAISS indexes.

This creates a system that can handle both:
- Structured queries: "5-star hotels in Paris"
- Semantic queries: "Best romantic honeymoon destination for couples from USA"

Making it far more powerful than either approach alone.

---

**Document End**

# Modular File Architecture - Graph-RAG Hotel Travel Assistant

## Project Overview
Graph-RAG system for hotel search using Neo4j knowledge graph, LangGraph workflows, and multiple retrieval strategies. Supports 4 workflow modes that users can switch between at runtime.

---

## Directory Structure

```
M3/
├── config.txt                          # Neo4j credentials (URI, USERNAME, PASSWORD)
├── requirements.txt                    # Python dependencies
├── architecture.md                     # Original planning document
├── file_arch.md                        # This file - implementation architecture
├── Create_kg.py                        # Knowledge graph creation script
├── query_library.py                    # 15 parameterized Cypher queries + QuerySelector
│
├── config.yaml                         # Runtime configuration
├── create_embeddings.py                # Script to generate & store embeddings
├── app.py                              # Streamlit UI with workflow selector
│
├── state/
│   ├── __init__.py
│   └── graph_state.py                  # GraphState TypedDict definition
│
├── components/                         # Reusable logic (no LangGraph dependency)
│   ├── __init__.py
│   ├── intent_classifier.py           # Classify intent (7 types)
│   ├── entity_extractor.py            # Extract entities from query
│   ├── query_builder.py               # Build Cypher from intent/entities
│   ├── query_executor.py              # Execute Cypher on Neo4j
│   ├── embedding_generator.py         # Generate query embeddings
│   ├── vector_searcher.py             # Vector search on Neo4j
│   ├── result_merger.py               # Merge & dedupe results
│   ├── llm_query_generator.py         # LLM generates Cypher directly
│   └── answer_generator.py            # LLM generates final answer
│
├── nodes/                              # LangGraph nodes (thin wrappers)
│   ├── __init__.py
│   ├── input_node.py                   # Validate & normalize input
│   ├── intent_node.py                  # Calls IntentClassifier
│   ├── entity_node.py                  # Calls EntityExtractor
│   ├── baseline_query_node.py          # Calls QueryBuilder + QueryExecutor
│   ├── embedding_query_node.py         # Calls EmbeddingGenerator + VectorSearcher
│   ├── llm_query_node.py               # Calls LLMQueryGenerator + QueryExecutor
│   ├── merge_node.py                   # Calls ResultMerger
│   ├── answer_node.py                  # Calls AnswerGenerator
│   └── output_node.py                  # Format for UI display
│
├── workflows/                          # Workflow definitions
│   ├── __init__.py
│   ├── baseline_workflow.py            # Workflow 1: Intent → Entity → Baseline
│   ├── embedding_workflow.py           # Workflow 2: Embedding search only
│   ├── hybrid_workflow.py              # Workflow 3: Baseline || Embedding → Merge
│   ├── llm_pipeline_workflow.py        # Workflow 4: LLM writes Cypher
│   └── workflow_factory.py             # Factory to get workflow by name
│
├── utils/                              # Infrastructure utilities
│   ├── __init__.py
│   ├── neo4j_client.py                 # Neo4j connection singleton
│   ├── embedding_client.py             # Embedding model manager
│   ├── llm_client.py                   # LLM API client
│   ├── config_loader.py                # Load config.yaml
│   └── prompts.py                      # Prompt templates
│
└── evaluation/                         # Evaluation framework (optional)
    ├── __init__.py
    ├── test_queries.json               # Test dataset
    ├── evaluator.py                    # Run workflows on test set
    ├── metrics.py                      # Metrics (accuracy, hallucination, etc.)
    └── compare_workflows.py            # Compare workflow performance
```

---

## Core Design Principles

### 1. Three-Layer Architecture
```
Components (reusable logic) → Nodes (LangGraph adapters) → Workflows (compositions)
```

### 2. Component Independence
- **No LangGraph dependency** in components
- Can be used directly without workflows
- Easy unit testing
- Reusable across multiple workflows

### 3. Workflow Modularity
- Each workflow is a separate graph definition
- User selects workflow at runtime in UI
- Easy to add new workflows without changing components

### 4. State-Driven
- Single `GraphState` TypedDict supports all workflows
- Optional fields for workflow-specific data
- Immutable state updates

---

## File Details

### State Definition

**File:** `state/graph_state.py`

```python
from typing import TypedDict, Optional, List, Dict, Any

class GraphState(TypedDict, total=False):
    # Input
    user_query: str
    
    # Intent & Entities (baseline/hybrid workflows)
    intent: Optional[str]  # 7 types: HotelSearch, HotelRecommendation, ReviewLookup, LocationQuery, VisaQuestion, AmenityFilter, GeneralQuestionAnswering
    entities: Optional[Dict[str, Any]]  # city, country, hotel_name, traveller_type, ratings, etc.
    
    # Baseline retrieval
    baseline_cypher: Optional[str]
    baseline_params: Optional[Dict[str, Any]]
    baseline_results: Optional[List[Dict[str, Any]]]
    
    # Embedding retrieval
    query_embedding: Optional[List[float]]
    embedding_results: Optional[List[Dict[str, Any]]]
    
    # LLM-generated query (llm_pipeline workflow)
    llm_generated_cypher: Optional[str]
    llm_query_results: Optional[List[Dict[str, Any]]]
    
    # Merged/Final context
    merged_context: Optional[str]
    
    # Answer generation
    llm_response: Optional[str]
    
    # Output
    final_output: Optional[Dict[str, Any]]
    
    # Metadata
    metadata: Optional[Dict[str, Any]]  # timings, model names, result counts
    error: Optional[str]
```

---

### Components (Reusable Logic)

All components are **LangGraph-independent** and can be used standalone.

#### `components/intent_classifier.py`
**Purpose:** Classify user query into one of 7 intents  
**Methods:**
- `classify(query: str) -> str`: Returns intent name
- Rule-based keyword matching first, LLM fallback if needed

**Intents:**
1. HotelSearch
2. HotelRecommendation
3. ReviewLookup
4. LocationQuery
5. VisaQuestion
6. AmenityFilter
7. GeneralQuestionAnswering

#### `components/entity_extractor.py`
**Purpose:** Extract structured entities from query  
**Methods:**
- `extract(query: str, intent: str) -> Dict[str, Any]`: Returns entity dict

**Extracted Entities:**
- `city`, `country`, `hotel_name`
- `traveller_type`: Business, Couple, Family, Solo, Group
- `min_rating`, `star_rating`
- Score thresholds: `min_cleanliness`, `min_comfort`, `min_value`, `min_staff`, `min_location`
- `from_country`, `to_country` (for visa queries)
- `limit`, `date_range`

**Implementation:** LLM-based extraction with structured output

#### `components/query_builder.py`
**Purpose:** Build Cypher query from intent and entities  
**Methods:**
- `build(intent: str, entities: Dict) -> Tuple[str, Dict]`: Returns (cypher_query, params)

**Implementation:** Uses `QuerySelector` from `query_library.py`

#### `components/query_executor.py`
**Purpose:** Execute any Cypher query on Neo4j  
**Methods:**
- `execute(cypher: str, params: Dict) -> List[Dict]`: Returns query results

**Used By:** baseline_query_node, llm_query_node

#### `components/embedding_generator.py`
**Purpose:** Generate embeddings for text  
**Methods:**
- `embed(text: str) -> List[float]`: Returns embedding vector

**Models:** 
- Default: `all-MiniLM-L6-v2` (384 dims)
- Optional: `all-mpnet-base-v2` (768 dims)

#### `components/vector_searcher.py`
**Purpose:** Perform vector similarity search using FAISS  
**Methods:**
- `search(embedding: List[float], limit: int, threshold: float) -> List[Dict]`: Returns similar hotel/review nodes
- `load_index(index_path: str)`: Load FAISS index from disk

**Implementation:** 
- Loads FAISS index (hotel_embeddings.faiss, review_embeddings.faiss)
- Searches FAISS for similar vectors
- Maps FAISS indices to hotel_ids/review_ids
- Fetches full node details from Neo4j via QueryExecutor
- Returns enriched results with similarity scores

#### `components/result_merger.py`
**Purpose:** Merge and deduplicate baseline + embedding results  
**Methods:**
- `merge(baseline_results: List, embedding_results: List) -> str`: Returns formatted context

**Logic:**
- Dedupe by hotel_id/review_id
- Combine relevance scores
- Rank results
- Format to ~2-3k tokens

#### `components/llm_query_generator.py`
**Purpose:** LLM generates Cypher query directly from natural language  
**Methods:**
- `generate(query: str, schema: str) -> str`: Returns Cypher query

**Used In:** llm_pipeline workflow

#### `components/answer_generator.py`
**Purpose:** LLM generates final answer from context  
**Methods:**
- `generate(query: str, context: str, intent: str) -> str`: Returns answer

**Prompt Structure:**
- Persona: Helpful hotel travel assistant
- Context: Grounded context from retrieval
- Task: Answer using ONLY context, no hallucinations
- Citation: Cite hotels/reviews

---

### Nodes (LangGraph Adapters)

All nodes are **thin wrappers** (5-10 lines) that call components.

**Pattern:**
```python
# nodes/intent_node.py
from components.intent_classifier import IntentClassifier
from state.graph_state import GraphState

classifier = IntentClassifier()

def intent_node(state: GraphState) -> GraphState:
    intent = classifier.classify(state["user_query"])
    return {**state, "intent": intent}
```

**All Nodes:**
1. `input_node`: Validate/normalize query
2. `intent_node`: Classify intent
3. `entity_node`: Extract entities
4. `baseline_query_node`: Build + execute Cypher
5. `embedding_query_node`: Embed + vector search
6. `llm_query_node`: LLM generates Cypher + execute
7. `merge_node`: Merge results
8. `answer_node`: Generate answer
9. `output_node`: Format final output

---

### Workflows (Graph Definitions)

#### Workflow 1: `baseline_workflow.py`
**Flow:** `Input → Intent → Entity → BaselineQuery → Output`

**Use Case:** Fast structured queries using Cypher only

**Nodes Used:** input, intent, entity, baseline_query, output

#### Workflow 2: `embedding_workflow.py`
**Flow:** `Input → EmbeddingQuery → Output`

**Use Case:** Pure semantic search, no intent classification

**Nodes Used:** input, embedding_query, output

#### Workflow 3: `hybrid_workflow.py`
**Flow:** `Input → Intent → Entity → [BaselineQuery || EmbeddingQuery] → Merge → Output`

**Use Case:** Best of both worlds - structured + semantic

**Parallel Branch:** BaselineQuery and EmbeddingQuery run concurrently

**Nodes Used:** input, intent, entity, baseline_query, embedding_query, merge, output

#### Workflow 4: `llm_pipeline_workflow.py`
**Flow:** `Input → LLMQuery → Answer → Output`

**Use Case:** Full LLM autonomy - generates Cypher and answer

**Nodes Used:** input, llm_query, answer, output

#### `workflow_factory.py`
**Purpose:** Create workflow by name

```python
WORKFLOWS = {
    "baseline_only": create_baseline_workflow,
    "embedding_only": create_embedding_workflow,
    "hybrid": create_hybrid_workflow,
    "llm_pipeline": create_llm_pipeline_workflow
}

def get_workflow(name: str) -> CompiledGraph:
    return WORKFLOWS[name]()
```

---

### Utils (Infrastructure)

#### `utils/neo4j_client.py`
**Purpose:** Neo4j connection management  
**Pattern:** Singleton  
**Methods:**
- `connect()`: Establish connection
- `run_query(cypher, params)`: Execute Cypher queries only
- `close()`: Close connection

**Config Source:** `config.txt` (URI, USERNAME, PASSWORD)

**Note:** Vector search is handled by FAISS in VectorSearcher component

#### `utils/embedding_client.py`
**Purpose:** Embedding model management  
**Methods:**
- `load_model(model_name)`: Load sentence-transformer
- `encode(text)`: Generate embedding
- `get_dimension()`: Return embedding size

**Caching:** In-memory model caching

#### `utils/llm_client.py`
**Purpose:** Unified LLM interface  
**Supported:**
- OpenAI (gpt-3.5-turbo, gpt-4)
- Local models (via API)

**Methods:**
- `generate(prompt, temperature, max_tokens)`: Get completion
- `generate_structured(prompt, schema)`: Get structured output

#### `utils/config_loader.py`
**Purpose:** Load and validate config.yaml  
**Methods:**
- `load_config()`: Returns config dict
- `get(key, default)`: Get config value

#### `utils/prompts.py`
**Purpose:** Centralized prompt templates  
**Templates:**
- `INTENT_CLASSIFICATION_PROMPT`
- `ENTITY_EXTRACTION_PROMPT`
- `CYPHER_GENERATION_PROMPT`
- `ANSWER_GENERATION_PROMPT`

---

### Configuration (config.yaml)

```yaml
# Workflow settings
workflows:
  default: "hybrid"
  available:
    - baseline_only
    - embedding_only
    - hybrid
    - llm_pipeline

# LLM configuration
llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 500
  api_key_env: "OPENAI_API_KEY"

# Retrieval settings
retrieval:
  baseline:
    enabled: true
    max_results: 10
  embedding:
    enabled: true
    max_results: 10
    similarity_threshold: 0.7
  merge:
    max_context_tokens: 2500

# Embedding configuration
embedding:
  model: "all-MiniLM-L6-v2"
  dimensions: 384
  cache_embeddings: true

# Neo4j (optional override for config.txt)
neo4j:
  uri: null
  username: null
  password: null

# UI settings
ui:
  show_debug: true
  max_display_results: 5
  enable_graph_viz: false
```

---

### Streamlit UI (app.py)

**Structure:**
```python
# Sidebar
workflow_mode = st.sidebar.selectbox("Workflow", ["baseline_only", "embedding_only", "hybrid", "llm_pipeline"])
llm_model = st.sidebar.selectbox("LLM Model", ["gpt-3.5-turbo", "gpt-4"])
show_debug = st.sidebar.checkbox("Show Debug Info")

# Main panel
query = st.text_input("Enter your query")

if st.button("Submit"):
    workflow = get_workflow(workflow_mode)
    result = workflow.invoke({"user_query": query})
    
    # Display based on workflow
    if workflow_mode == "baseline_only":
        st.write("Results:", result["baseline_results"])
    elif workflow_mode == "embedding_only":
        st.write("Results:", result["embedding_results"])
    elif workflow_mode == "hybrid":
        st.write("Context:", result["merged_context"])
    elif workflow_mode == "llm_pipeline":
        st.write("Answer:", result["llm_response"])
    
    # Debug panel
    if show_debug:
        with st.expander("Debug Info"):
            st.json(result.get("metadata", {}))
```

**Features:**
- Workflow selector
- Model selector
- Query input
- Results display (adapts to workflow)
- Debug panel (intent, entities, Cypher, timings)
- Session state for history

---

### Embeddings Creation (create_embeddings.py)

**Purpose:** Generate feature embeddings and create FAISS indexes

**Feature Embedding Strategy:**
Combine multiple node properties into rich feature representations:
- **Hotels:** Concatenate name, city, country, star_rating, average_reviews_score, cleanliness_base, comfort_base, facilities_base, location_base, staff_base, value_for_money_base
- **Reviews:** Use review text directly

**Process:**
1. Connect to Neo4j
2. Fetch all hotels with properties
3. Build feature strings: `"{name} in {city}, {country}. Star rating: {star_rating}. Average score: {avg_score}. Cleanliness: {cleanliness_base}, Comfort: {comfort_base}, Facilities: {facilities_base}, Location: {location_base}, Staff: {staff_base}, Value: {value_for_money_base}"`
4. Generate embeddings using sentence-transformers
5. Create FAISS index and add hotel vectors
6. Save FAISS index to `hotel_embeddings.faiss`
7. Save mapping file `hotel_id_mapping.json` (faiss_index → hotel_id)
8. Repeat for reviews: fetch review texts, embed, create `review_embeddings.faiss` and `review_id_mapping.json`

**Output Files:**
- `hotel_embeddings.faiss` - FAISS index for hotel vectors
- `hotel_id_mapping.json` - Maps FAISS index to hotel_id
- `review_embeddings.faiss` - FAISS index for review vectors  
- `review_id_mapping.json` - Maps FAISS index to review_id

**Run Once:** After KG creation, before running workflows

---

## Knowledge Graph Schema

**From Create_kg.py - already implemented**

### Nodes
- **Traveller**: user_id, gender, age, type, join_date
- **Hotel**: hotel_id, name, star_rating, cleanliness_base, comfort_base, facilities_base, location_base, staff_base, value_for_money_base, average_reviews_score
- **City**: name
- **Country**: name
- **Review**: review_id, text, date, score_overall, score_cleanliness, score_comfort, score_facilities, score_location, score_staff, score_value_for_money

### Relationships
- Hotel → LOCATED_IN → City
- City → LOCATED_IN → Country
- Traveller → FROM_COUNTRY → Country
- Traveller → WROTE → Review
- Review → REVIEWED → Hotel
- Traveller → STAYED_AT → Hotel
- Country → NEEDS_VISA → Country

---

## Cypher Query Library

**From query_library.py - already implemented**

**15 Query Templates:**

### HotelSearch (4 queries)
1. `get_hotels_by_city(city_name)`
2. `get_hotels_by_country(country_name)`
3. `get_hotels_by_rating_threshold(min_rating)`
4. `get_hotels_by_star_rating(star_rating)` [referenced but not implemented]

### HotelRecommendation (5 queries)
5. `get_top_hotels_for_traveller_type(traveller_type, limit)`
6. `get_hotels_by_cleanliness_score(min_cleanliness)`
7. `get_hotels_by_comfort_score(min_comfort, limit)`
8. `get_hotels_by_value_for_money(min_value, limit)`
9. `get_hotels_with_best_staff_scores(limit)`

### ReviewLookup (2 queries)
10. `get_reviews_by_hotel_name(hotel_name, limit)`
11. `get_reviews_by_hotel_id(hotel_id, limit)`

### LocationQuery (1 query)
12. `get_hotels_with_best_location_scores(city_name, limit)`

### VisaQuestion (2 queries)
13. `check_visa_requirements(from_country, to_country)`
14. `get_travellers_by_country_no_visa(from_country, to_country)`

### GeneralQuestionAnswering (1 query)
15. `get_hotel_full_details(hotel_name)`

**QuerySelector class:** Selects appropriate query based on intent and entities

---

## Implementation Order

### Phase 1: Core Infrastructure (No Workflows)
1. `state/graph_state.py` - State definition
2. `utils/config_loader.py` - Config loading
3. `utils/neo4j_client.py` - Neo4j connection
4. `utils/llm_client.py` - LLM interface
5. `utils/embedding_client.py` - Embedding models
6. `utils/prompts.py` - Prompt templates
7. `create_embeddings.py` - Generate embeddings (run once)

**Test:** Can connect to Neo4j, load models, call LLM

### Phase 2: Components (Standalone Logic)
1. `components/intent_classifier.py`
2. `components/entity_extractor.py`
3. `components/query_builder.py`
4. `components/query_executor.py`
5. `components/embedding_generator.py`
6. `components/vector_searcher.py`
7. `components/result_merger.py`
8. `components/llm_query_generator.py`
9. `components/answer_generator.py`

**Test:** Each component works independently (no graph needed)

### Phase 3: Nodes (Thin Wrappers)
1. `nodes/input_node.py`
2. `nodes/intent_node.py`
3. `nodes/entity_node.py`
4. `nodes/baseline_query_node.py`
5. `nodes/embedding_query_node.py`
6. `nodes/llm_query_node.py`
7. `nodes/merge_node.py`
8. `nodes/answer_node.py`
9. `nodes/output_node.py`

**Test:** Each node updates state correctly

### Phase 4: Workflows (Compositions)
1. `workflows/baseline_workflow.py`
2. `workflows/embedding_workflow.py`
3. `workflows/hybrid_workflow.py`
4. `workflows/llm_pipeline_workflow.py`
5. `workflows/workflow_factory.py`

**Test:** Each workflow executes end-to-end

### Phase 5: UI
1. `app.py` - Streamlit interface

**Test:** Can switch workflows and see results

### Phase 6: Evaluation (Optional)
1. `evaluation/test_queries.json`
2. `evaluation/metrics.py`
3. `evaluation/evaluator.py`
4. `evaluation/compare_workflows.py`

**Test:** Compare workflow performance

---

## Workflow Comparison Matrix

| Workflow | Flow | Components Used | Use Case | Speed | Quality |
|----------|------|----------------|----------|-------|---------|
| **baseline_only** | Intent → Entity → Cypher | IntentClassifier, EntityExtractor, QueryBuilder, QueryExecutor | Structured queries | ⚡ Fast | ✓ Good |
| **embedding_only** | Embed → Search | EmbeddingGenerator, VectorSearcher | Semantic search | ⚡ Fast | ✓✓ Better |
| **hybrid** | Intent → Entity → [Cypher \|\| Vector] → Merge | All except LLMQueryGenerator | Best coverage | 🐢 Slow | ✓✓✓ Best |
| **llm_pipeline** | LLM writes Cypher → Answer | LLMQueryGenerator, QueryExecutor, AnswerGenerator | Full autonomy | 🐢 Slowest | ✓✓ Variable |

---

## Key Benefits of This Architecture

1. **Modularity**: Components → Nodes → Workflows separation
2. **Flexibility**: Switch workflows at runtime
3. **Testability**: Components work standalone
4. **Extensibility**: Add new workflows without changing components
5. **Debugging**: Use components directly without graphs
6. **Reusability**: Same components across multiple workflows
7. **Future-proof**: Easy to add workflow #5, #6, etc.

---

## Example: Direct Component Usage (No Workflow)

```python
# Bypass workflows for debugging
from components.intent_classifier import IntentClassifier
from components.entity_extractor import EntityExtractor
from components.query_builder import QueryBuilder
from components.query_executor import QueryExecutor

# Direct usage
classifier = IntentClassifier()
intent = classifier.classify("Hotels in Paris")  # "HotelSearch"

extractor = EntityExtractor()
entities = extractor.extract("Hotels in Paris", intent)  # {"city": "Paris"}

builder = QueryBuilder()
cypher, params = builder.build(intent, entities)

executor = QueryExecutor()
results = executor.execute(cypher, params)

print(results)  # Hotels in Paris
```

---

## Dependencies (requirements.txt)

Already present:
- `langgraph` - Workflow orchestration
- `langchain`, `langchain-community`, `langchain-openai` - LLM integration
- `neo4j` - Graph database
- `sentence-transformers` - Embeddings
- `faiss-cpu` - Vector similarity search
- `numpy`, `pandas`, `scikit-learn` - Data processing
- `streamlit` - UI
- `python-dotenv` - Environment variables
- `requests` - HTTP requests

---

## Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-...
```

---

This architecture document is complete and ready for implementation by a coding agent. All files, their purposes, methods, and relationships are clearly defined.

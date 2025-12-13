# Embedding Evaluation Documentation

## Overview
This directory contains comprehensive tests for evaluating the performance of both hotel and visa embedding models using known ground truth data.

## Files

### 1. `embedding_ground_truth.json`
Contains 55 test cases with known correct answers:
- **30 Hotel Queries**: Tests covering hotel name matching, location queries, amenity-based searches, and specific feature requests
- **25 Visa Queries**: Tests covering visa requirements between various country pairs

Each test case includes:
- `id`: Unique identifier
- `query`: Natural language query to test
- `expected_top1`: The correct result that should rank #1
- `expected_top3`: List of acceptable results in top 3 (for queries with multiple valid answers)
- `description`: Explanation of why this is the correct answer

### 2. `test_embeddings_comprehensive.py`
Main evaluation script that:
- Tests hotel embedding retrieval against 30 test queries
- Tests visa embedding retrieval against 25 test queries
- Calculates Top-1, Top-3, and Top-5 accuracy metrics
- Compares performance between hotel and visa embeddings
- Generates detailed results with similarity scores
- Saves comprehensive JSON report

## Ground Truth Data

### Hotel Test Cases

The hotel dataset contains 25 hotels across major cities worldwide. Test cases include:

1. **Name-based queries** (20 cases): Direct hotel name matches or landmark references
   - Example: "find the Royal Compass hotel in London" → Hotel ID 2
   - Example: "hotel near the Colosseum in Rome" → Hotel ID 14

2. **Location-based queries** (5 cases): City/country specific searches
   - Example: "luxury hotel in New York" → Hotel ID 1
   - Example: "accommodation in Berlin Germany" → Hotel ID 9

3. **Amenity-based queries** (5 cases): Searches for specific ratings/features
   - Example: "5 star hotel with best cleanliness rating" → Hotel ID 4 (cleanliness: 9.6)
   - Example: "hotel with amazing location score above 9.5" → Hotel ID 7 (location: 9.8)

### Visa Test Cases

The visa dataset contains 114 visa relationships where visas are required. Test cases cover:

1. **China visa requirements** (8 cases): Chinese citizens traveling abroad
   - Example: "do I need a visa from China to United States" → Tourist Visa required
   - Example: "China to Singapore visa" → Tourist Visa required

2. **India visa requirements** (6 cases): Indian citizens traveling abroad
   - Example: "visa from India to Japan" → Tourist Visa / eVisa required
   - Example: "India to Dubai UAE visa" → Tourist Visa / eVisa required

3. **Egypt visa requirements** (3 cases): Egyptian citizens traveling abroad
   - Example: "Egypt to Australia visa" → Tourist Visa / eVisa required

4. **Other countries** (8 cases): Nigeria, Russia, South Africa, Thailand, Brazil
   - Example: "Nigeria to UK visa requirements" → Tourist Visa required
   - Example: "Russia to China visa" → Tourist Visa / eVisa required

## Evaluation Metrics

### Top-K Accuracy
- **Top-1 Accuracy**: Percentage of queries where the correct answer is ranked #1
  - This is the PRIMARY metric - strict evaluation of retrieval quality
  - Target: >80% for high-quality embeddings

- **Top-3 Accuracy**: Percentage of queries where a correct answer appears in top 3
  - Acceptable for queries with multiple valid answers
  - Target: >90% for acceptable performance

- **Top-5 Accuracy**: Percentage of queries where a correct answer appears in top 5
  - Fallback metric for edge cases
  - Target: >95% minimum

### Similarity Scores
- Cosine similarity converted from L2 distances: `similarity = 1 - (distance² / 2)`
- Range: 0.0 to 1.0 (higher is better)
- Typical good matches: >0.7

## Running the Tests

### Prerequisites
```bash
cd M3
python create_embeddings.py  # Generate FAISS indexes (if not already done)
```

This creates:
- `hotel_embeddings.faiss` (25 hotel vectors)
- `hotel_id_mapping.json` (FAISS index → hotel_id)
- `visa_embeddings.faiss` (114 visa relationship vectors)
- `visa_id_mapping.json` (FAISS index → visa_id)

### Execute Tests
```bash
cd M3/Evaluations
python test_embeddings_comprehensive.py
```

### Output
1. **Console Output**: Real-time progress with detailed results for each query
2. **JSON Report**: `embedding_evaluation_results.json` with complete metrics

## Expected Results

### Perfect Retrieval Scenarios
Queries where Top-1 accuracy should be 100%:
- Exact hotel name matches: "Royal Compass hotel in London"
- Direct visa queries: "visa from China to United States"
- Landmark-based hotel searches: "hotel near the Colosseum in Rome"

### Challenging Scenarios
Queries that may have lower Top-1 accuracy:
- Generic feature queries: "hotel with best cleanliness" (multiple hotels have high cleanliness)
- Ambiguous locations: "luxury hotel" without city specification
- Synonym variations: "accommodation" vs "hotel" vs "stay"

## Interpreting Results

### High Performance (Top-1 >80%)
- Embedding model captures semantic meaning well
- Feature strings in `create_embeddings.py` are well-designed
- FAISS indexing working correctly

### Medium Performance (Top-1 60-80%)
- Model may need tuning or different embedding model
- Consider enhancing feature strings with more context
- Check if query phrasing differs significantly from embedded text

### Low Performance (Top-1 <60%)
- Embedding model may be inappropriate for this domain
- Feature engineering needed in `create_embeddings.py`
- Consider alternative models (e.g., all-mpnet-base-v2 vs all-MiniLM-L6-v2)

## Comparison: Hotel vs Visa Embeddings

### Expected Performance Differences

**Hotel Embeddings** typically perform better because:
- Rich feature strings with multiple attributes (location, ratings, amenities)
- More natural language variation in queries
- Diverse entities (25 distinct hotels)

**Visa Embeddings** may be more challenging because:
- Structured country-to-country relationships
- Less semantic variation in queries
- Many similar relationships (e.g., China requires visa for most countries)

### Benchmark Targets
- **Hotel Top-1**: >75%
- **Hotel Top-3**: >90%
- **Visa Top-1**: >70%
- **Visa Top-3**: >85%

## Test Case Design Principles

1. **Known Ground Truth**: Every query has a verifiable correct answer from CSV data
2. **Diverse Coverage**: Tests cover all hotel/visa types and query patterns
3. **Realistic Queries**: Natural language phrasing that real users might type
4. **Multiple Difficulty Levels**: Mix of easy (exact match) and hard (semantic similarity) cases
5. **Accept Multiple Answers**: Some queries legitimately have multiple correct answers (Top-3)

## Troubleshooting

### Low Accuracy Issues
1. Check if FAISS indexes exist and loaded correctly
2. Verify Neo4j database has all hotel/visa data
3. Review feature string construction in `create_embeddings.py`
4. Test with different embedding models

### Missing Results
1. Ensure `create_embeddings.py` was run successfully
2. Check that Neo4j contains all 25 hotels and 114 visa relationships
3. Verify CSV data matches Neo4j data

### Inconsistent Similarity Scores
1. Embeddings may not be normalized (check `normalize=True` in embedding generation)
2. L2 to cosine conversion may need adjustment
3. Feature strings may be too short or too long

## Future Enhancements

1. **Model Comparison**: Test multiple embedding models (MiniLM vs MPNet vs BERT)
2. **Feature Ablation**: Test impact of removing specific features from strings
3. **Query Variations**: Add synonyms and paraphrases of existing queries
4. **Threshold Tuning**: Find optimal similarity thresholds for filtering
5. **Cross-Lingual**: Add queries in different languages

## References

- Embedding Model: `all-MiniLM-L6-v2` (384 dimensions, sentence-transformers)
- FAISS Index Type: Flat L2 (exact search, no approximation)
- Dataset: 25 hotels, 114 visa relationships requiring visas
- Query Types: Natural language questions about hotels and visa requirements

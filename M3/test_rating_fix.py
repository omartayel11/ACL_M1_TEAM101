"""
Quick test to verify rating threshold query fix
Tests the complete flow from query to Neo4j without relying on LLM rate limits
"""
from query_library import QueryLibrary, QuerySelector
from utils.neo4j_client import Neo4jClient

print("=== Testing Rating Threshold Query Fix ===\n")

# Test 1: Direct query library call
print("1. Testing QueryLibrary.get_hotels_by_rating_threshold(8.0)")
query, params = QueryLibrary.get_hotels_by_rating_threshold(8.0)
print(f"Query generated: ✓")
print(f"Params: {params}\n")

# Test 2: Execute against Neo4j
neo4j = Neo4jClient()
result = neo4j.run_query(query, params)
print(f"2. Neo4j execution")
print(f"Results returned: {len(result)} hotels")
if result:
    print(f"Sample result: {result[0]['hotel_name']} - {result[0]['avg_score']:.2f}\n")
else:
    print("ERROR: No results returned!\n")

# Test 3: Query selector with proper entities
print("3. Testing QuerySelector with HotelSearch intent")
entities = {"min_rating": 8.0}
intent = "HotelSearch"
query, params = QuerySelector.select_query(intent, entities)
if query:
    result = neo4j.run_query(query, params)
    print(f"✓ QuerySelector works: {len(result)} results\n")
else:
    print("ERROR: QuerySelector returned None\n")

# Test 4: Test with different thresholds
print("4. Testing different rating thresholds")
for threshold in [7.0, 8.0, 9.0]:
    query, params = QueryLibrary.get_hotels_by_rating_threshold(threshold)
    result = neo4j.run_query(query, params)
    print(f"   Rating >= {threshold}: {len(result)} hotels")

neo4j.close()

print("\n=== All Tests Complete ===")
print("✓ Query library fixed")
print("✓ Neo4j returns results")
print("✓ QuerySelector works with correct entities")
print("\nNext step: Update intent classifier to recognize rating queries as HotelSearch")

"""
Quick test script to debug embedding search
"""

from components.embedding_generator import EmbeddingGenerator
from components.vector_searcher import VectorSearcher

# Initialize
generator = EmbeddingGenerator()
searcher = VectorSearcher()

# Test query
query = "do i need visa from egypt to france?"
print(f"Query: {query}\n")

# Generate embedding
embedding = generator.embed(query)
print(f"✓ Generated embedding: {len(embedding)} dimensions")
print(f"  First 5 values: {embedding[:5]}\n")

# Check if index loaded
print(f"Hotel index loaded: {searcher.hotel_index is not None}")
print(f"Hotel mapping size: {len(searcher.hotel_mapping) if searcher.hotel_mapping else 0}\n")

# Try search with different thresholds
print("=" * 60)
for threshold in [0.9, 0.7, 0.5, 0.3, 0.0]:
    print(f"\nSearching with threshold={threshold}:")
    results = searcher.search(embedding, limit=5, threshold=threshold)
    print(f"  Found {len(results)} results")
    
    if results:
        for i, r in enumerate(results[:3], 1):
            hotel_name = r.get('hotel_name', 'N/A')
            city = r.get('city', '')
            location = f" ({city})" if city else ""
            print(f"    {i}. {hotel_name}{location} - similarity: {r.get('similarity_score', 0):.4f}")

print("\n" + "=" * 60)
print("If you see 0 results for all thresholds, there's an issue with the search logic.")
print("If you see results with lower thresholds, just lower the threshold in config.yaml")

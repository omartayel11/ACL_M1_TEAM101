"""
Test script for entity-driven FAISS index selection
Verifies that extracted entities correctly drive which FAISS indexes are searched
"""

from components.vector_searcher import VectorSearcher
from components.embedding_generator import EmbeddingGenerator

def test_entity_driven_index_selection():
    """Test that entities drive FAISS index selection"""
    
    print("=" * 70)
    print("TESTING ENTITY-DRIVEN FAISS INDEX SELECTION")
    print("=" * 70)
    
    searcher = VectorSearcher()
    generator = EmbeddingGenerator()
    
    # Test cases with different intents and entities
    test_cases = [
        {
            "name": "Hotel Search (no entities)",
            "intent": "HotelSearch",
            "entities": {},
            "expected_indexes": ["hotel"]
        },
        {
            "name": "Hotel Recommendation for solo traveler",
            "intent": "HotelRecommendation",
            "entities": {"traveller_type": "Solo", "city": "Paris"},
            "expected_indexes": ["review", "hotel"]  # Should include review due to traveller_type
        },
        {
            "name": "Hotel Recommendation for couples from USA",
            "intent": "HotelRecommendation",
            "entities": {"traveller_type": "Couples", "from_country": "USA"},
            "expected_indexes": ["review", "hotel"]  # Should include review due to traveller_type and from_country
        },
        {
            "name": "Visa Question",
            "intent": "VisaQuestion",
            "entities": {},
            "expected_indexes": ["visa"]
        },
        {
            "name": "Review Lookup",
            "intent": "ReviewLookup",
            "entities": {},
            "expected_indexes": ["review"]
        },
        {
            "name": "Location Query",
            "intent": "LocationQuery",
            "entities": {"city": "Tokyo"},
            "expected_indexes": ["hotel"]  # No traveller_type, so just hotel
        },
        {
            "name": "Casual Conversation",
            "intent": "CasualConversation",
            "entities": {},
            "expected_indexes": ["hotel"]
        }
    ]
    
    # Run tests
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"  Intent: {test['intent']}")
        print(f"  Entities: {test['entities']}")
        
        selected = searcher.select_faiss_indexes(test['intent'], test['entities'])
        expected = test['expected_indexes']
        
        print(f"  Selected indexes: {selected}")
        print(f"  Expected indexes: {expected}")
        
        # Check if selection matches expectation
        if set(selected) == set(expected):
            print("  ✓ PASS")
        else:
            print("  ✗ FAIL")
            all_passed = False
    
    # Test actual search with entities
    print("\n" + "=" * 70)
    print("TESTING MULTI-INDEX SEARCH WITH ENTITIES")
    print("=" * 70)
    
    if searcher.hotel_index is not None:
        test_query = "Best luxury hotel for solo travelers with great location"
        embedding = generator.embed(test_query)
        
        print(f"\nTest Query: {test_query}")
        print(f"Embedding dimension: {len(embedding)}")
        
        # Simulate entities extracted from the query
        entities = {
            "traveller_type": "Solo",
            "min_comfort": 4.0,
            "hotel_name": None
        }
        
        print(f"Simulated extracted entities: {entities}")
        
        # Search with entities
        results = searcher.search(
            embedding=embedding,
            limit=5,
            threshold=0.5,
            intent="HotelRecommendation",
            entities=entities
        )
        
        if results:
            print(f"\n✓ Retrieved {len(results)} results")
            print("\nTop 3 results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  [{i}] {result.get('hotel_name')} - {result.get('city')}, {result.get('country')}")
                print(f"      Score: {result.get('similarity_score', 0):.3f}")
                if result.get('has_review_match'):
                    print(f"      ✓ Matches traveler profile in reviews")
        else:
            print("\n✗ No results found")
            all_passed = False
    else:
        print("\n⚠ Hotel index not loaded. Run create_embeddings.py first.")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = test_entity_driven_index_selection()
    sys.exit(0 if success else 1)

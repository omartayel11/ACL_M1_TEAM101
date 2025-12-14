"""
Quick test to verify entity extraction fixes
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from components.entity_extractor import EntityExtractor
from components.intent_classifier import IntentClassifier

def test_fixes():
    extractor = EntityExtractor()
    classifier = IntentClassifier()
    
    test_cases = [
        # Star rating tests
        ("5 star hotels in Paris", {"city": "Paris", "star_rating": 5.0}),
        ("find 4 star hotels in London", {"city": "London", "star_rating": 4.0}),
        
        # Country vs city
        ("hotels in France", {"country": "France"}),
        ("hotels in Spain", {"country": "Spain"}),
        ("hotels in Paris", {"city": "Paris"}),
        
        # Visa patterns
        ("do I need a visa from USA to France", {"from_country": "United States", "to_country": "France"}),
        ("do Americans need visa for Japan", {"from_country": "United States", "to_country": "Japan"}),
        
        # Rating extraction
        ("hotels with rating 4.8", {"min_rating": 4.8}),
        ("hotels with rating 4.7 or higher", {"min_rating": 4.7}),
        
        # Quality scores without defaults
        ("hotels with cleanliness score above 9.0", {"min_cleanliness": 9.0}),
        ("show me hotels with comfort score 9.2", {"min_comfort": 9.2}),
        ("hotels with staff score above 9.0", {"min_staff": 9.0}),
        
        # No greedy city matching
        ("I want to see some reviews", {}),
        ("what do people say about Mandarin Oriental", {"hotel_name": "Mandarin Oriental"}),
    ]
    
    print("="*80)
    print("ENTITY EXTRACTION FIX VERIFICATION")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for query, expected in test_cases:
        intent = classifier.classify(query)
        extracted = extractor.extract(query, intent)
        
        # Check if extracted matches expected
        match = True
        for key, value in expected.items():
            if key not in extracted:
                match = False
                break
            if isinstance(value, float):
                if abs(extracted[key] - value) > 0.01:
                    match = False
                    break
            elif extracted[key] != value:
                match = False
                break
        
        status = "✅" if match else "❌"
        if match:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Query: \"{query}\"")
        print(f"   Expected: {expected}")
        print(f"   Extracted: {extracted}")
    
    print("\n" + "="*80)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*80)

if __name__ == "__main__":
    test_fixes()

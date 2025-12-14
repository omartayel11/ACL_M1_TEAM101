"""
Test typo handling with LLM validation
"""

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from components.entity_extractor import EntityExtractor
from components.intent_classifier import IntentClassifier

def test_typo_fixes():
    extractor = EntityExtractor(debug=True)
    classifier = IntentClassifier()
    
    # Test cases that failed due to typos
    test_cases = [
        ("find hotels in Paaris", {"city": "Paris"}),
        ("hotels in Londan", {"city": "London"}),
        ("visa from UK to Span", {"from_country": "United Kingdom", "to_country": "Spain"}),
        ("visa from Canda to Italy", {"from_country": "Canada", "to_country": "Italy"}),
        ("visa from USA to Japn", {"from_country": "United States", "to_country": "Japan"}),
        ("hotels with ratng above 4.5", {"min_rating": 4.5}),
        ("best hotels for my honeymoon", {"traveller_type": "Couple"}),
        ("find hotels with friendly staff score 9.5", {"min_staff": 9.5}),
    ]
    
    print("="*80)
    print("TYPO HANDLING TEST WITH LLM VALIDATION")
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
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("="*80)

if __name__ == "__main__":
    test_typo_fixes()

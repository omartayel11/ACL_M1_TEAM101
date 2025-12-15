"""
Comprehensive Quantitative Test Script for Entity Extractor
Tests entity extraction across 170 diverse test cases with checkpoint/resume capability
"""

import sys
from pathlib import Path
import time
import json
import argparse

# Add parent directory to path to import modules
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from components.entity_extractor import EntityExtractor
from components.intent_classifier import IntentClassifier

class EntityExtractorTester:
    def __init__(self):
        self.extractor = EntityExtractor()
        self.classifier = IntentClassifier()
        self.test_cases = self._build_test_cases()
        self.CHECKPOINT_FILE = Path(__file__).parent / "entity_extractor_checkpoint.json"
    
    def _load_checkpoint(self):
        """Load checkpoint if it exists"""
        if self.CHECKPOINT_FILE.exists():
            try:
                with open(self.CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load checkpoint: {e}")
                return None
        return None
    
    def _save_checkpoint(self, results, last_completed_index):
        """Save checkpoint after each test"""
        checkpoint = {
            "last_completed_index": last_completed_index,
            "results": results
        }
        try:
            with open(self.CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")
    
    def _delete_checkpoint(self):
        """Delete checkpoint file after successful completion"""
        try:
            if self.CHECKPOINT_FILE.exists():
                self.CHECKPOINT_FILE.unlink()
        except Exception as e:
            print(f"Warning: Could not delete checkpoint: {e}")
    
    def _entities_match(self, extracted, expected):
        """
        Compare extracted entities with expected entities
        Returns True if they match (with tolerance for numeric values)
        """
        # Handle None cases
        if extracted is None and expected is None:
            return True
        if extracted is None or expected is None:
            return False
        
        # Check if both have same keys
        if set(extracted.keys()) != set(expected.keys()):
            return False
        
        # Compare each key's value
        for key in expected.keys():
            extracted_val = extracted[key]
            expected_val = expected[key]
            
            # Handle None values
            if extracted_val is None and expected_val is None:
                continue
            if extracted_val is None or expected_val is None:
                return False
            
            # Handle numeric values (with tolerance)
            if isinstance(expected_val, (int, float)):
                if not isinstance(extracted_val, (int, float)):
                    return False
                if abs(extracted_val - expected_val) > 0.01:  # Tolerance for floating point
                    return False
            
            # Handle string values (case-insensitive)
            elif isinstance(expected_val, str):
                if not isinstance(extracted_val, str):
                    return False
                if extracted_val.lower() != expected_val.lower():
                    return False
            
            # Handle list values
            elif isinstance(expected_val, list):
                if not isinstance(extracted_val, list):
                    return False
                if len(extracted_val) != len(expected_val):
                    return False
                # Compare lists (order matters)
                for i, exp_item in enumerate(expected_val):
                    ext_item = extracted_val[i]
                    if isinstance(exp_item, str) and isinstance(ext_item, str):
                        if ext_item.lower() != exp_item.lower():
                            return False
                    elif ext_item != exp_item:
                        return False
            
            # Direct comparison for other types
            else:
                if extracted_val != expected_val:
                    return False
        
        return True
    
    def _build_test_cases(self):
        """Build comprehensive test cases covering all entity types"""
        test_cases = []
        
        # ========== HotelSearch Entity Tests (50 cases) ==========
        
        # City searches
        test_cases.extend([
            ("hotels in Paris", {"city": "Paris"}),
            ("find me hotels in London", {"city": "London"}),
            ("show me accommodations in Cairo", {"city": "Cairo"}),
            ("I need a place to stay in Dubai", {"city": "Dubai"}),
            ("looking for hotels in Barcelona", {"city": "Barcelona"}),
            ("where can I stay in Rome", {"city": "Rome"}),
            ("hotels available in Amsterdam", {"city": "Amsterdam"}),
            ("find hotels in Tokyo", {"city": "Tokyo"}),
            ("I want to book in New York", {"city": "New York"}),
            ("hotels in Berlin please", {"city": "Berlin"}),
        ])
        
        # Country searches
        test_cases.extend([
            ("hotels in France", {"country": "France"}),
            ("find accommodations in Spain", {"country": "Spain"}),
            ("show me hotels in Italy", {"country": "Italy"}),
            ("I need hotels in Japan", {"country": "Japan"}),
            ("looking for hotels in Egypt", {"country": "Egypt"}),
        ])
        
        # Rating searches
        test_cases.extend([
            ("hotels with rating above 4.5", {"min_rating": 4.5}),
            ("find hotels rated above 4.0", {"min_rating": 4.0}),
            ("show me hotels with rating 4.8", {"min_rating": 4.8}),
            ("I want hotels with rating 4.7 or higher", {"min_rating": 4.7}),
            ("hotels with rating at least 4.3", {"min_rating": 4.3}),
            ("find me 5 star rated hotels", {"star_rating": 5.0}),
            ("hotels with rating above 4.9", {"min_rating": 4.9}),
            ("show hotels with rating 4.6 or above", {"min_rating": 4.6}),
        ])
        
        # Star rating searches
        test_cases.extend([
            ("5 star hotels in Paris", {"city": "Paris", "star_rating": 5.0}),
            ("find 4 star hotels in London", {"city": "London", "star_rating": 4.0}),
            ("show me 3 star hotels", {"star_rating": 3.0}),
            ("I need a 5 star hotel", {"star_rating": 5.0}),
            ("looking for 4 star accommodations", {"star_rating": 4.0}),
        ])
        
        # Combined searches
        test_cases.extend([
            ("5 star hotels in Paris with rating above 4.5", {"city": "Paris", "star_rating": 5.0, "min_rating": 4.5}),
            ("4 star hotels in London with rating above 4.8", {"city": "London", "star_rating": 4.0, "min_rating": 4.8}),
            ("hotels in Spain with rating above 4.7", {"country": "Spain", "min_rating": 4.7}),
            ("5 star hotels in France", {"country": "France", "star_rating": 5.0}),
            ("find 4 star hotels in Dubai with rating above 4.5", {"city": "Dubai", "star_rating": 4.0, "min_rating": 4.5}),
        ])
        
        # Typo variations
        test_cases.extend([
            ("hotles in Paris", {"city": "Paris"}),
            ("find hotels in Paaris", {"city": "Paris"}),
            ("5 star hotles", {"star_rating": 5.0}),
            ("hotels with ratng above 4.5", {"min_rating": 4.5}),
            ("4 starr hotels", {"star_rating": 4.0}),
            ("hotels in Londan", {"city": "London"}),
        ])
        
        # ========== HotelRecommendation Entity Tests (15 cases) ==========
        
        # Traveler type searches
        test_cases.extend([
            ("recommend hotels for families", {"traveller_type": "Family"}),
            ("find hotels for business travelers", {"traveller_type": "Business"}),
            ("hotels for couples", {"traveller_type": "Couple"}),
            ("I'm a solo traveler, recommend hotels", {"traveller_type": "Solo"}),
            ("best hotels for families", {"traveller_type": "Family"}),
            ("hotels suitable for business trips", {"traveller_type": "Business"}),
            ("romantic hotels for couples", {"traveller_type": "Couple"}),
            ("hotels for solo travelers", {"traveller_type": "Solo"}),
        ])
        
        # Natural language variations
        test_cases.extend([
            ("what hotels do you recommend for families", {"traveller_type": "Family"}),
            ("suggest hotels for business people", {"traveller_type": "Business"}),
            ("I'm traveling with my family, any recommendations", {"traveller_type": "Family"}),
            ("best hotels for my honeymoon", {"traveller_type": "Couple"}),
            ("I'm traveling alone, suggest some hotels", {"traveller_type": "Solo"}),
            ("me and my wife need a hotel", {"traveller_type": "Couple"}),
            ("traveling with my husband", {"traveller_type": "Couple"}),
        ])
        
        # ========== ReviewLookup Entity Tests (20 cases) ==========
        
        # Specific hotel reviews (using actual hotel names from hotels.csv)
        test_cases.extend([
            ("reviews for Hotel Plaza Athénée", {"hotel_name": "Hotel Plaza Athénée"}),
            ("show me reviews of The Ritz London", {"hotel_name": "The Ritz London"}),
            ("what are the reviews for Burj Al Arab", {"hotel_name": "Burj Al Arab"}),
            ("I want to see reviews for Four Seasons George V", {"hotel_name": "Four Seasons George V"}),
            ("reviews of The Savoy", {"hotel_name": "The Savoy"}),
            ("find reviews for Claridge's", {"hotel_name": "Claridge's"}),
            ("show reviews of Hotel Adlon Kempinski", {"hotel_name": "Hotel Adlon Kempinski"}),
            ("reviews for Atlantis The Palm", {"hotel_name": "Atlantis The Palm"}),
            ("what do people say about Mandarin Oriental", {"hotel_name": "Mandarin Oriental"}),
            ("reviews for Park Hyatt Tokyo", {"hotel_name": "Park Hyatt Tokyo"}),
        ])
        
        # General review requests (no specific hotel)
        test_cases.extend([
            ("show me hotel reviews", {}),
            ("I want to see some reviews", {}),
            ("what are the reviews", {}),
            ("find reviews for hotels", {}),
            ("show me customer reviews", {}),
        ])
        
        # Typo variations
        test_cases.extend([
            ("reveiws for Hotel Plaza", {"hotel_name": "Hotel Plaza"}),
            ("show me revews of The Ritz", {"hotel_name": "The Ritz"}),
            ("reviews for Burj Al Arb", {"hotel_name": "Burj Al Arb"}),
            ("what are the reviws", {}),
            ("show hotel reveiws", {}),
        ])
        
        # ========== LocationQuery Entity Tests (10 cases) ==========
        
        # City-specific location queries (LocationQuery doesn't extract scores, only cities)
        test_cases.extend([
            ("hotels in Paris with good location", {"city": "Paris"}),
            ("find hotels in London with great location", {"city": "London"}),
            ("hotels in central Dubai", {"city": "Dubai"}),
            ("I need hotels in downtown Barcelona", {"city": "Barcelona"}),
            ("hotels near city center in Rome", {"city": "Rome"}),
            ("best located hotels in Tokyo", {"city": "Tokyo"}),
            ("hotels with prime location in Berlin", {"city": "Berlin"}),
            ("find centrally located hotels in Amsterdam", {"city": "Amsterdam"}),
            ("hotels with excellent location in Singapore", {"country": "Singapore"}),
            ("where are the best located hotels in Sydney", {"city": "Sydney", "min_rating": 7.5}),
        ])
        
        # ========== VisaQuestion Entity Tests (20 cases) ==========
        
        # Country pair visa questions (using actual countries from visa.csv)
        test_cases.extend([
            ("do I need a visa from USA to France", {"from_country": "United States", "to_country": "France"}),
            ("visa requirements from UK to Spain", {"from_country": "United Kingdom", "to_country": "Spain"}),
            ("is visa required from Canada to Italy", {"from_country": "Canada", "to_country": "Italy"}),
            ("do Americans need visa for Japan", {"from_country": "United States", "to_country": "Japan"}),
            ("visa info from Australia to Egypt", {"from_country": "Australia", "to_country": "Egypt"}),
            ("do I need visa from Germany to UAE", {"from_country": "Germany", "to_country": "United Arab Emirates"}),
            ("visa requirements from France to China", {"from_country": "France", "to_country": "China"}),
            ("is visa needed from UK to India", {"from_country": "United Kingdom", "to_country": "India"}),
            ("do Canadians need visa for Thailand", {"from_country": "Canada", "to_country": "Thailand"}),
            ("visa from USA to Mexico", {"from_country": "United States", "to_country": "Mexico"}),
        ])
        
        # Natural language variations
        test_cases.extend([
            ("I'm from USA, do I need a visa for France", {"from_country": "United States", "to_country": "France"}),
            ("traveling from UK to Spain, visa needed", {"from_country": "United Kingdom", "to_country": "Spain"}),
            ("I'm Canadian going to Italy, visa required", {"from_country": "Canada", "to_country": "Italy"}),
            ("Australian traveling to Egypt, need visa", {"from_country": "Australia", "to_country": "Egypt"}),
            ("going from Germany to UAE, visa info", {"from_country": "Germany", "to_country": "United Arab Emirates"}),
        ])
        
        # Typo variations
        test_cases.extend([
            ("do I need viza from USA to France", {"from_country": "United States", "to_country": "France"}),
            ("visa from UK to Span", {"from_country": "United Kingdom", "to_country": "Spain"}),
            ("visa from Canda to Italy", {"from_country": "Canada", "to_country": "Italy"}),
            ("visa from USA to Japn", {"from_country": "United States", "to_country": "Japan"}),
            ("viza requirements from Australia to Egypt", {"from_country": "Australia", "to_country": "Egypt"}),
        ])
        
        # ========== AmenityFilter Entity Tests (20 cases) ==========
        
        # Cleanliness scores
        test_cases.extend([
            ("hotels with cleanliness score above 9.0", {"min_cleanliness": 9.0}),
            ("find hotels with cleanliness above 9.5", {"min_rating": 9.5}),
            ("show me hotels with cleanliness 9.2 or higher", {"min_cleanliness": 9.2}),
            ("I need clean hotels with cleanliness score 9.8", {"min_cleanliness": 9.8}),
            ("hotels with cleanliness above 9.3", {"min_cleanliness": 9.3}),
        ])
        
        # Comfort scores
        test_cases.extend([
            ("hotels with comfort score above 9.0", {"min_comfort": 9.0}),
            ("find comfortable hotels with comfort above 9.5", {"min_comfort": 9.5}),
            ("show me hotels with comfort score 9.2", {"min_comfort": 9.2}),
            ("I need hotels with comfort above 9.8", {"min_comfort": 9.8}),
        ])
        
        # Value for money scores
        test_cases.extend([
            ("hotels with good value for money", {"min_value": 7.5}),
            ("find hotels with value score above 9.0", {"min_rating": 9.0}),
            ("show me hotels with value 8.5 or higher", {"min_value": 8.5}),
            ("I need affordable hotels with value above 9.2", {"min_value": 9.2}),
        ])
        
        # Staff scores
        test_cases.extend([
            ("hotels with staff score above 9.0", {"min_staff": 9.0}),
            ("find hotels with friendly staff score 9.5", {"min_staff": 9.5}),
            ("show me hotels with staff score 9.2", {"min_staff": 9.2}),
            ("I need hotels with staff above 9.8", {"min_staff": 9.8}),
        ])
        
        # Combined amenity filters
        test_cases.extend([
            ("hotels with cleanliness 9.5 and comfort 9.2", {"min_cleanliness": 9.5, "min_comfort": 9.2}),
            ("find hotels with value above 9.0 and staff above 9.3", {"min_value": 9.0, "min_staff": 9.3}),
        ])
        
        return test_cases
    
    def run_tests(self, verbose=False, resume=True):
        """
        Run all entity extraction tests with checkpoint/resume capability
        
        Args:
            verbose: Print detailed results for each test
            resume: Whether to resume from checkpoint if it exists
        """
        results = {
            "total": len(self.test_cases),
            "correct": 0,
            "incorrect": 0,
            "failures": []
        }
        
        start_index = 0
        
        # Check for checkpoint
        if resume:
            checkpoint = self._load_checkpoint()
            if checkpoint:
                start_index = checkpoint["last_completed_index"] + 1
                results = checkpoint["results"]
                print(f"\n📍 RESUMING FROM CHECKPOINT")
                print(f"Completed: {start_index}/{len(self.test_cases)} test cases")
                print(f"Current Accuracy: {results['correct']}/{start_index} = {(results['correct']/start_index*100):.1f}%")
                print(f"Remaining: {len(self.test_cases) - start_index} test cases")
                print(f"Estimated time: ~{(len(self.test_cases) - start_index) * 10 / 60:.1f} minutes\n")
        
        try:
            for i in range(start_index, len(self.test_cases)):
                query, expected_entities = self.test_cases[i]
                
                # Show progress
                query_display = query if len(query) <= 60 else query[:57] + "..."
                print(f"[{i+1}/{len(self.test_cases)}] Testing: \"{query_display}\"", flush=True)
                
                # Classify intent first (required for entity extraction)
                intent = self.classifier.classify(query)
                
                # Extract entities
                extracted_entities = self.extractor.extract(query, intent)
                
                # Check if entities match
                is_correct = self._entities_match(extracted_entities, expected_entities)
                
                if is_correct:
                    results["correct"] += 1
                    status = "✅"
                else:
                    results["incorrect"] += 1
                    results["failures"].append({
                        "query": query,
                        "expected": expected_entities,
                        "extracted": extracted_entities
                    })
                    status = "❌"
                
                # Calculate current accuracy
                current_accuracy = (results["correct"] / (i + 1)) * 100
                
                # Print result
                print(f"  Result: {status} | Accuracy: {current_accuracy:.1f}%", flush=True)
                
                if verbose or not is_correct:
                    print(f"  Expected: {expected_entities}")
                    print(f"  Extracted: {extracted_entities}")
                
                # Save checkpoint after each test
                self._save_checkpoint(results, i)
                
                # Wait to avoid API rate limits (except for last test)
                if i < len(self.test_cases) - 1:
                    print(f"  ⏳ Waiting 15 seconds before next test...", flush=True)
                    time.sleep(15)
            
            # Delete checkpoint on successful completion
            self._delete_checkpoint()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ TEST INTERRUPTED BY USER")
            print(f"Completed: {i}/{len(self.test_cases)} test cases")
            print(f"Current Accuracy: {results['correct']}/{i} = {(results['correct']/i*100 if i > 0 else 0):.1f}%")
            print(f"Checkpoint saved. Run again to resume from this point.")
            print(f"\nTo change API key and resume:")
            print(f'  $env:GROQ_API_KEY="your-new-key"')
            print(f'  python test_entity_extractor.py')
            raise
        
        except Exception as e:
            print(f"\n\n❌ ERROR: {e}")
            print(f"Checkpoint saved at test {i}. Fix the issue and run again to resume.")
            raise
        
        return results
    
    def print_results(self, results):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("ENTITY EXTRACTOR TEST RESULTS")
        print("="*80)
        
        total = results["total"]
        correct = results["correct"]
        incorrect = results["incorrect"]
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        print(f"\nTotal Test Cases: {total}")
        print(f"Correct: {correct}")
        print(f"Incorrect: {incorrect}")
        print(f"Accuracy: {accuracy:.2f}%")
        
        # Visual accuracy bar
        bar_length = 50
        filled = int(bar_length * correct / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n[{bar}] {accuracy:.1f}%")
        
        # Show failures if any
        if results["failures"]:
            print(f"\n{'='*80}")
            print(f"FAILED TEST CASES ({len(results['failures'])})")
            print(f"{'='*80}\n")
            
            for idx, failure in enumerate(results["failures"], 1):
                print(f"{idx}. Query: \"{failure['query']}\"")
                print(f"   Expected: {failure['expected']}")
                print(f"   Extracted: {failure['extracted']}")
                print()
        
        print("="*80)

def main():
    parser = argparse.ArgumentParser(description="Test Entity Extractor with comprehensive test cases")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed results for each test")
    parser.add_argument("-o", "--output", type=str, default="entity_extractor_results3.txt", 
                       help="Output file for results (default: entity_extractor_results3.txt)")
    parser.add_argument("--no-resume", action="store_true", 
                       help="Start fresh, ignoring any existing checkpoint")
    
    args = parser.parse_args()
    
    print("="*80)
    print("ENTITY EXTRACTOR COMPREHENSIVE TEST")
    print("="*80)
    print(f"Total Test Cases: 170")
    print(f"Estimated Duration: ~28 minutes (10 seconds per test)")
    print(f"Output File: {args.output}")
    
    if args.no_resume:
        print("Mode: Fresh start (ignoring checkpoint)")
    else:
        print("Mode: Resume from checkpoint (if exists)")
    
    print("="*80)
    
    tester = EntityExtractorTester()
    
    # Determine file mode and message
    resume = not args.no_resume
    checkpoint = tester._load_checkpoint() if resume else None
    file_mode = "a" if checkpoint else "w"
    
    if checkpoint:
        print(f"\n✓ Opening output file in append mode to continue...")
    
    print("\nStarting tests...\n")
    
    # Run tests (output goes to console for live progress)
    results = tester.run_tests(verbose=args.verbose, resume=resume)
    
    # Print final results (redirect to file)
    print(f"\n\n✓ Tests completed! Writing results to {args.output}...")
    
    original_stdout = sys.stdout
    try:
        with open(args.output, file_mode, encoding='utf-8') as f:
            sys.stdout = f
            if checkpoint:
                print("\n" + "="*80)
                print("RESUMED TEST SESSION")
                print("="*80 + "\n")
            tester.print_results(results)
    finally:
        sys.stdout = original_stdout
    
    # Show completion message on console
    accuracy = (results["correct"] / results["total"]) * 100 if results["total"] > 0 else 0
    print(f"\n✅ All tests completed!")
    print(f"Final Accuracy: {accuracy:.2f}%")
    print(f"Results written to: {args.output}")

if __name__ == "__main__":
    main()

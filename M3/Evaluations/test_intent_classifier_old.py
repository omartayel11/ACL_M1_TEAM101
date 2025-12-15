#!/usr/bin/env python3
"""
Comprehensive Quantitative Test for OLD Intent Classifier (LLM-Only)
Tests the old LLM-only intent classifier with diverse real-world queries including typos and variations
WITH CHECKPOINT AND LIVE PROGRESS SUPPORT
"""

import sys
import time
import json
from pathlib import Path

# Add M3 directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the OLD classifier
from components.intent_classifier_old_LLM_only import IntentClassifier


class IntentClassifierTester:
    """
    Comprehensive tester for OLD intent classification with accuracy metrics
    Supports checkpoint/resume and live progress display
    """
    
    CHECKPOINT_FILE = "intent_classifier_old_checkpoint.json"
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.test_cases = self._build_test_cases()
    
    def _load_checkpoint(self):
        """Load checkpoint if exists"""
        checkpoint_path = Path(__file__).parent / self.CHECKPOINT_FILE
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Could not load checkpoint: {e}")
        return None
    
    def _save_checkpoint(self, results, last_completed_index):
        """Save checkpoint after each test case"""
        checkpoint_path = Path(__file__).parent / self.CHECKPOINT_FILE
        checkpoint = {
            "last_completed_index": last_completed_index,
            "results": results
        }
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save checkpoint: {e}")
    
    def _delete_checkpoint(self):
        """Delete checkpoint file after successful completion"""
        checkpoint_path = Path(__file__).parent / self.CHECKPOINT_FILE
        if checkpoint_path.exists():
            try:
                checkpoint_path.unlink()
            except Exception as e:
                print(f"⚠️ Warning: Could not delete checkpoint: {e}")
    
    def _build_test_cases(self):
        """Build comprehensive test cases covering all intents with multiple variations"""
        return [
            # ========== HotelSearch (40 test cases) ==========
            {"query": "Find hotels in Paris", "expected": "HotelSearch"},
            {"query": "Show me hotels in Tokyo", "expected": "HotelSearch"},
            {"query": "I need hotels in New York", "expected": "HotelSearch"},
            {"query": "hotels in Dubai", "expected": "HotelSearch"},
            {"query": "Looking for hotels in London", "expected": "HotelSearch"},
            {"query": "What hotels are available in Cairo?", "expected": "HotelSearch"},
            {"query": "Can you find me hotels in Sydney", "expected": "HotelSearch"},
            {"query": "I want to stay in Bangkok", "expected": "HotelSearch"},
            {"query": "Find hotels in France", "expected": "HotelSearch"},
            {"query": "Show me hotels in Japan", "expected": "HotelSearch"},
            {"query": "hotels in the United States", "expected": "HotelSearch"},
            {"query": "accommodation in Egypt", "expected": "HotelSearch"},
            {"query": "places to stay in Italy", "expected": "HotelSearch"},
            {"query": "Find hotels with rating above 8", "expected": "HotelSearch"},
            {"query": "Show me highly rated hotels", "expected": "HotelSearch"},
            {"query": "I need hotels with good ratings", "expected": "HotelSearch"},
            {"query": "hotels rated 9 or higher", "expected": "HotelSearch"},
            {"query": "top rated hotels", "expected": "HotelSearch"},
            {"query": "hotels with rating above 8.5", "expected": "HotelSearch"},
            {"query": "Find me hotels with excellent ratings", "expected": "HotelSearch"},
            {"query": "5-star hotels in Paris", "expected": "HotelSearch"},
            {"query": "Find 5 star hotels", "expected": "HotelSearch"},
            {"query": "I want a five-star hotel", "expected": "HotelSearch"},
            {"query": "Show me 4-star hotels in London", "expected": "HotelSearch"},
            {"query": "luxury 5-star accommodation", "expected": "HotelSearch"},
            {"query": "Find 5-star hotels in Dubai with rating above 9", "expected": "HotelSearch"},
            {"query": "I need highly rated hotels in Tokyo", "expected": "HotelSearch"},
            {"query": "Show me top hotels in Singapore", "expected": "HotelSearch"},
            {"query": "find hoteks in cairo", "expected": "HotelSearch"},
            {"query": "hotels in Pari", "expected": "HotelSearch"},
            {"query": "show me hotles in london", "expected": "HotelSearch"},
            {"query": "Where can I stay in Rome?", "expected": "HotelSearch"},
            {"query": "I'm looking for a place to stay in Barcelona", "expected": "HotelSearch"},
            {"query": "What are my accommodation options in Amsterdam?", "expected": "HotelSearch"},
            {"query": "I need somewhere to stay in Berlin", "expected": "HotelSearch"},
            {"query": "Find me a hotel in Moscow", "expected": "HotelSearch"},
            {"query": "I'm traveling to Istanbul, where should I stay?", "expected": "HotelSearch"},
            {"query": "Looking for accommodation in Singapore", "expected": "HotelSearch"},
            
            # ========== HotelRecommendation (18 test cases) ==========
            {"query": "Best hotels for couples", "expected": "HotelRecommendation"},
            {"query": "Top hotels for families", "expected": "HotelRecommendation"},
            {"query": "Recommend hotels for business travelers", "expected": "HotelRecommendation"},
            {"query": "What are the best hotels for solo travelers?", "expected": "HotelRecommendation"},
            {"query": "Hotels suitable for families with kids", "expected": "HotelRecommendation"},
            {"query": "I'm traveling for business, what hotels do you recommend?", "expected": "HotelRecommendation"},
            {"query": "Best romantic hotels for couples", "expected": "HotelRecommendation"},
            {"query": "Top rated hotels for group travel", "expected": "HotelRecommendation"},
            {"query": "Where should a couple stay?", "expected": "HotelRecommendation"},
            {"query": "Recommend me hotels for a family vacation", "expected": "HotelRecommendation"},
            {"query": "Best hotels for couples in Paris", "expected": "HotelRecommendation"},
            {"query": "Top family-friendly hotels in Tokyo", "expected": "HotelRecommendation"},
            {"query": "Recommend business hotels in London with high ratings", "expected": "HotelRecommendation"},
            {"query": "What's the best hotel for a romantic getaway?", "expected": "HotelRecommendation"},
            {"query": "I need a hotel recommendation for families", "expected": "HotelRecommendation"},
            {"query": "Suggest a hotel for my business trip", "expected": "HotelRecommendation"},
            {"query": "Where do couples usually stay?", "expected": "HotelRecommendation"},
            {"query": "Recommend hotels for solo travelers", "expected": "HotelRecommendation"},
            
            # ========== ReviewLookup (20 test cases) ==========
            {"query": "Show me reviews for The Azure Tower", "expected": "ReviewLookup"},
            {"query": "What are the reviews for The Royal Compass?", "expected": "ReviewLookup"},
            {"query": "Reviews for L'Étoile Palace", "expected": "ReviewLookup"},
            {"query": "Tell me about reviews for The Golden Oasis", "expected": "ReviewLookup"},
            {"query": "I want to see reviews for Marina Bay Zenith", "expected": "ReviewLookup"},
            {"query": "Show reviews for Copacabana Lux", "expected": "ReviewLookup"},
            {"query": "What do people say about The Maple Grove?", "expected": "ReviewLookup"},
            {"query": "Reviews for Nile Grandeur", "expected": "ReviewLookup"},
            {"query": "Find reviews for The Bosphorus Inn", "expected": "ReviewLookup"},
            {"query": "Show me hotel reviews", "expected": "ReviewLookup"},
            {"query": "What do guests say about this hotel?", "expected": "ReviewLookup"},
            {"query": "I want to read customer feedback", "expected": "ReviewLookup"},
            {"query": "Can I see guest reviews?", "expected": "ReviewLookup"},
            {"query": "What's the feedback for hotels in Paris?", "expected": "ReviewLookup"},
            {"query": "What are guests saying about The Orchid Palace?", "expected": "ReviewLookup"},
            {"query": "Customer reviews for Gaudi's Retreat", "expected": "ReviewLookup"},
            {"query": "Tell me what people think about Canal House Grand", "expected": "ReviewLookup"},
            {"query": "Any feedback on The Kiwi Grand?", "expected": "ReviewLookup"},
            {"query": "reviews for The Azur Tower", "expected": "ReviewLookup"},
            {"query": "show me reveiws for hotels", "expected": "ReviewLookup"},
            
            # ========== LocationQuery (15 test cases) ==========
            {"query": "Hotels with best location scores", "expected": "LocationQuery"},
            {"query": "Which hotels have the best location?", "expected": "LocationQuery"},
            {"query": "Find hotels with excellent location", "expected": "LocationQuery"},
            {"query": "Show me hotels with good location ratings", "expected": "LocationQuery"},
            {"query": "I need hotels with high location scores", "expected": "LocationQuery"},
            {"query": "Hotels in the best locations", "expected": "LocationQuery"},
            {"query": "Which hotel has the highest location score?", "expected": "LocationQuery"},
            {"query": "Hotels with best location in London", "expected": "LocationQuery"},
            {"query": "Find hotels with great location in Paris", "expected": "LocationQuery"},
            {"query": "Best located hotels in Tokyo", "expected": "LocationQuery"},
            {"query": "Hotels with top location scores in Dubai", "expected": "LocationQuery"},
            {"query": "Where are the best located hotels?", "expected": "LocationQuery"},
            {"query": "I want a hotel in a prime location", "expected": "LocationQuery"},
            {"query": "Hotels with convenient locations", "expected": "LocationQuery"},
            {"query": "Show me centrally located hotels", "expected": "LocationQuery"},
            
            # ========== VisaQuestion (20 test cases) ==========
            {"query": "Do I need a visa from USA to France?", "expected": "VisaQuestion"},
            {"query": "Visa requirements from United Kingdom to Japan", "expected": "VisaQuestion"},
            {"query": "Is a visa required from Germany to Egypt?", "expected": "VisaQuestion"},
            {"query": "Do I need visa to travel from China to United States?", "expected": "VisaQuestion"},
            {"query": "Visa requirements from India to United Kingdom", "expected": "VisaQuestion"},
            {"query": "Check visa from Canada to Australia", "expected": "VisaQuestion"},
            {"query": "Do citizens of Brazil need visa for Singapore?", "expected": "VisaQuestion"},
            {"query": "Is visa needed from Russia to France?", "expected": "VisaQuestion"},
            {"query": "Visa requirements from Egypt to Germany", "expected": "VisaQuestion"},
            {"query": "Do I need a visa from South Africa to Italy?", "expected": "VisaQuestion"},
            {"query": "Can I travel from USA to Japan without a visa?", "expected": "VisaQuestion"},
            {"query": "What are the visa requirements from Mexico to Spain?", "expected": "VisaQuestion"},
            {"query": "I'm from Thailand, do I need visa for United Arab Emirates?", "expected": "VisaQuestion"},
            {"query": "Traveling from South Korea to Canada, need visa?", "expected": "VisaQuestion"},
            {"query": "Check if I need travel documents from Australia to United Kingdom", "expected": "VisaQuestion"},
            {"query": "Do I need a passport visa from France to Italy?", "expected": "VisaQuestion"},
            {"query": "Travel document requirements from United States to Mexico", "expected": "VisaQuestion"},
            {"query": "visa requiremnts from USA to UK", "expected": "VisaQuestion"},
            {"query": "do i need viza from Germany to Spain", "expected": "VisaQuestion"},
            {"query": "visa from Fance to Japan", "expected": "VisaQuestion"},
            
            # ========== AmenityFilter (25 test cases) ==========
            {"query": "Hotels with high cleanliness", "expected": "AmenityFilter"},
            {"query": "Find hotels with cleanliness score above 9", "expected": "AmenityFilter"},
            {"query": "I need hotels with excellent cleanliness", "expected": "AmenityFilter"},
            {"query": "Show me the cleanest hotels", "expected": "AmenityFilter"},
            {"query": "Hotels known for cleanliness", "expected": "AmenityFilter"},
            {"query": "Find hotels with high cleanliness scores", "expected": "AmenityFilter"},
            {"query": "Hotels with high comfort score", "expected": "AmenityFilter"},
            {"query": "Find comfortable hotels", "expected": "AmenityFilter"},
            {"query": "I want hotels with excellent comfort", "expected": "AmenityFilter"},
            {"query": "Show me hotels with good comfort ratings", "expected": "AmenityFilter"},
            {"query": "Most comfortable hotels available", "expected": "AmenityFilter"},
            {"query": "Good value for money", "expected": "AmenityFilter"},
            {"query": "Hotels with best value for money", "expected": "AmenityFilter"},
            {"query": "I need hotels with high value", "expected": "AmenityFilter"},
            {"query": "Find hotels with great value for money scores", "expected": "AmenityFilter"},
            {"query": "Best value hotels", "expected": "AmenityFilter"},
            {"query": "Hotels with excellent value for money", "expected": "AmenityFilter"},
            {"query": "Hotels with excellent staff", "expected": "AmenityFilter"},
            {"query": "Find hotels with great staff service", "expected": "AmenityFilter"},
            {"query": "I need hotels with high staff scores", "expected": "AmenityFilter"},
            {"query": "Show me hotels with friendly staff", "expected": "AmenityFilter"},
            {"query": "Hotels with best staff ratings", "expected": "AmenityFilter"},
            {"query": "Hotels with high cleanliness and comfort", "expected": "AmenityFilter"},
            {"query": "Find hotels with good value and excellent staff", "expected": "AmenityFilter"},
            {"query": "I need clean hotels with comfortable rooms", "expected": "AmenityFilter"},
            {"query": "Show me hotels with great cleanliness and staff scores", "expected": "AmenityFilter"},
            
            # ========== CasualConversation (15 test cases) ==========
            {"query": "Hi", "expected": "CasualConversation"},
            {"query": "Hello", "expected": "CasualConversation"},
            {"query": "Hey there", "expected": "CasualConversation"},
            {"query": "Good morning", "expected": "CasualConversation"},
            {"query": "Thanks", "expected": "CasualConversation"},
            {"query": "Thank you", "expected": "CasualConversation"},
            {"query": "Thanks a lot", "expected": "CasualConversation"},
            {"query": "Help", "expected": "CasualConversation"},
            {"query": "What can you do?", "expected": "CasualConversation"},
            {"query": "How can you help me?", "expected": "CasualConversation"},
            {"query": "What are your capabilities?", "expected": "CasualConversation"},
            {"query": "Bye", "expected": "CasualConversation"},
            {"query": "Goodbye", "expected": "CasualConversation"},
            {"query": "See you later", "expected": "CasualConversation"},
            {"query": "Have a nice day", "expected": "CasualConversation"},
            
            # ========== GeneralQuestionAnswering (10 test cases) ==========
            {"query": "Tell me about The Azure Tower", "expected": "GeneralQuestionAnswering"},
            {"query": "What do you know about hotels in general?", "expected": "GeneralQuestionAnswering"},
            {"query": "Give me information about The Royal Compass", "expected": "GeneralQuestionAnswering"},
            {"query": "Describe The Golden Oasis", "expected": "GeneralQuestionAnswering"},
            {"query": "What are the facilities at Marina Bay Zenith?", "expected": "GeneralQuestionAnswering"},
            {"query": "Tell me everything about Copacabana Lux", "expected": "GeneralQuestionAnswering"},
            {"query": "Information about The Maple Grove hotel", "expected": "GeneralQuestionAnswering"},
            {"query": "What can you tell me about Nile Grandeur?", "expected": "GeneralQuestionAnswering"},
            {"query": "Details about The Bosphorus Inn", "expected": "GeneralQuestionAnswering"},
            {"query": "I want comprehensive information about The Orchid Palace", "expected": "GeneralQuestionAnswering"},
        ]
    
    def run_tests(self, verbose=False, resume=True):
        """
        Run all test cases and calculate accuracy metrics
        
        Args:
            verbose: If True, print detailed results for each test case (to file)
            resume: If True, resume from checkpoint if available
        
        Returns:
            dict: Test results with accuracy metrics
        """
        # Try to load checkpoint
        start_index = 0
        
        if resume:
            checkpoint = self._load_checkpoint()
            if checkpoint:
                start_index = checkpoint["last_completed_index"] + 1
                results = checkpoint["results"]
                print("=" * 80)
                print("📁 RESUMING FROM CHECKPOINT")
                print("=" * 80)
                print(f"Resuming from test case #{start_index + 1}/{len(self.test_cases)}")
                print(f"Completed so far: {start_index}/{len(self.test_cases)}")
                print(f"Current accuracy: {results.get('accuracy', 0):.2f}%")
                print("=" * 80)
                print()
            else:
                results = {
                    "total": len(self.test_cases),
                    "correct": 0,
                    "incorrect": 0,
                    "by_intent": {},
                    "failures": []
                }
                
                # Initialize per-intent tracking
                for intent in self.classifier.INTENTS:
                    results["by_intent"][intent] = {
                        "total": 0,
                        "correct": 0,
                        "incorrect": 0,
                        "accuracy": 0.0
                    }
        else:
            results = {
                "total": len(self.test_cases),
                "correct": 0,
                "incorrect": 0,
                "by_intent": {},
                "failures": []
            }
            
            # Initialize per-intent tracking
            for intent in self.classifier.INTENTS:
                results["by_intent"][intent] = {
                    "total": 0,
                    "correct": 0,
                    "incorrect": 0,
                    "accuracy": 0.0
                }
        
        if start_index == 0:
            print("=" * 80)
            print("OLD INTENT CLASSIFIER (LLM-ONLY) QUANTITATIVE TEST")
            print("=" * 80)
            print(f"Total test cases: {results['total']}")
            print("=" * 80)
            print()
        
        # Run each test case
        try:
            for i in range(start_index, len(self.test_cases)):
                test_case = self.test_cases[i]
                query = test_case["query"]
                expected = test_case["expected"]
                
                # Print progress to console (always visible)
                query_display = query if len(query) <= 50 else query[:50] + "..."
                progress_msg = f"[{i+1}/{len(self.test_cases)}] Testing: \"{query_display}\""
                print(progress_msg, flush=True)
                
                # Classify query
                try:
                    predicted = self.classifier.classify(query)
                except Exception as e:
                    error_msg = str(e).lower()
                    # Check if it's a rate limit error
                    if 'rate_limit' in error_msg or 'rate limit' in error_msg or '429' in error_msg:
                        print(f"\n⚠️  RATE LIMIT REACHED")
                        print(f"   Checkpoint saved at test case {i}/{len(self.test_cases)}")
                        print(f"   Current accuracy: {(results['correct'] / max(i, 1)) * 100:.2f}%")
                        print(f"   Run the script again to resume from this point")
                        self._save_checkpoint(results, i - 1)  # Save at previous index to retry this one
                        raise Exception("Rate limit reached. Please wait and run again to resume.")
                    else:
                        # For other errors, re-raise
                        raise
                
                # Check if correct
                is_correct = (predicted == expected)
                
                # Update results
                if is_correct:
                    results["correct"] += 1
                    results["by_intent"][expected]["correct"] += 1
                else:
                    results["incorrect"] += 1
                    results["by_intent"][expected]["incorrect"] += 1
                    results["failures"].append({
                        "query": query,
                        "expected": expected,
                        "predicted": predicted
                    })
                
                results["by_intent"][expected]["total"] += 1
                
                # Calculate current accuracy
                current_accuracy = (results["correct"] / (i + 1)) * 100
                
                # Print result to console
                status = "✅ PASS" if is_correct else "❌ FAIL"
                console_msg = f"  Result: {status} | Expected: {expected} | Predicted: {predicted} | Accuracy: {current_accuracy:.1f}%"
                print(console_msg, flush=True)
                
                # Print if verbose or incorrect (to file)
                if verbose or not is_correct:
                    status = "✅ PASS" if is_correct else "❌ FAIL"
                    print(f"[{i+1}/{results['total']}] {status}")
                    print(f"  Query: \"{query}\"")
                    print(f"  Expected: {expected}")
                    print(f"  Predicted: {predicted}")
                    if not is_correct:
                        print(f"  ⚠️  MISMATCH")
                    print()
                
                # Save checkpoint after each test
                results["accuracy"] = current_accuracy
                self._save_checkpoint(results, i)
                
                # Wait 10 seconds between LLM calls to avoid API quota limits
                if i < len(self.test_cases) - 1:
                    print(f"  ⏳ Waiting 15 seconds...", flush=True)
                    time.sleep(15)
                print()
            
            # Calculate per-intent accuracy
            for intent in results["by_intent"]:
                intent_data = results["by_intent"][intent]
                if intent_data["total"] > 0:
                    intent_data["accuracy"] = (intent_data["correct"] / intent_data["total"]) * 100
            
            # Calculate overall accuracy
            results["accuracy"] = (results["correct"] / results["total"]) * 100
            
            # Delete checkpoint on successful completion
            self._delete_checkpoint()
            
        except KeyboardInterrupt:
            print("\n" + "=" * 80)
            print("⚠️  TEST INTERRUPTED BY USER")
            print("=" * 80)
            print(f"Completed: {i}/{len(self.test_cases)} test cases")
            print(f"Current accuracy: {(results['correct'] / max(i, 1)) * 100:.2f}%")
            print("\nCheckpoint saved. Run again to resume from this point.")
            print("=" * 80)
            raise
        except Exception as e:
            print(f"\n⚠️  ERROR: {e}")
            print(f"Checkpoint saved at test case {i}")
            raise
        
        return results
    
    def print_results(self, results):
        """Print comprehensive test results with accuracy metrics"""
        print()
        print("=" * 80)
        print("TEST RESULTS SUMMARY - OLD CLASSIFIER (LLM-ONLY)")
        print("=" * 80)
        print()
        
        # Overall accuracy
        print(f"📊 OVERALL ACCURACY: {results['accuracy']:.2f}%")
        print(f"   ✅ Correct: {results['correct']}/{results['total']}")
        print(f"   ❌ Incorrect: {results['incorrect']}/{results['total']}")
        print()
        
        # Per-intent accuracy
        print("=" * 80)
        print("ACCURACY BY INTENT")
        print("=" * 80)
        print()
        
        sorted_intents = sorted(
            results["by_intent"].items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        for intent, data in sorted_intents:
            if data["total"] > 0:
                accuracy_bar = "█" * int(data["accuracy"] / 5) + "░" * (20 - int(data["accuracy"] / 5))
                print(f"{intent:30s} {accuracy_bar} {data['accuracy']:6.2f}%")
                print(f"{'':30s} ({data['correct']}/{data['total']} correct)")
                print()
        
        # Failures
        if results["failures"]:
            print("=" * 80)
            print("FAILED TEST CASES")
            print("=" * 80)
            print()
            
            for i, failure in enumerate(results["failures"], 1):
                print(f"❌ Failure #{i}")
                print(f"   Query: \"{failure['query']}\"")
                print(f"   Expected: {failure['expected']}")
                print(f"   Predicted: {failure['predicted']}")
                print()
        else:
            print("=" * 80)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 80)
            print()


def main():
    """Main entry point for quantitative testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantitative test for OLD intent classifier (LLM-only)")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed results for each test case (default: only failures)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="intent_classifier_old_results.txt",
        help="Output file for results (default: intent_classifier_old_results.txt)"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start from beginning, ignore checkpoint"
    )
    
    args = parser.parse_args()
    
    # Open output file in append mode if resuming
    resume = not args.no_resume
    checkpoint_path = Path(__file__).parent / IntentClassifierTester.CHECKPOINT_FILE
    checkpoint_exists = checkpoint_path.exists()
    mode = 'a' if (resume and checkpoint_exists) else 'w'
    
    original_stdout = sys.stdout
    
    try:
        with open(args.output, mode, encoding='utf-8') as f:
            # Redirect detailed output to file, keep progress on console
            sys.stdout = f
            
            # Create tester and run tests
            tester = IntentClassifierTester()
            
            # Restore stdout temporarily for test execution (console progress)
            sys.stdout = original_stdout
            results = tester.run_tests(verbose=args.verbose, resume=resume)
            
            # Redirect back to file for results
            sys.stdout = f
            tester.print_results(results)
    
    finally:
        # Restore stdout
        sys.stdout = original_stdout
    
    # Print completion message to console
    print("\n" + "=" * 80)
    print("✅ OLD intent classifier test completed!")
    print(f"📄 Results saved to: {args.output}")
    print(f"📊 Overall accuracy: {results['accuracy']:.2f}%")
    print("=" * 80)
    
    # Exit with appropriate code
    exit_code = 0 if results["accuracy"] == 100.0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

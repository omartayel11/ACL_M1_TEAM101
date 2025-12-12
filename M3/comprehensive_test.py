"""
Comprehensive Test Suite for Graph-RAG Hotel Travel Assistant
Tests all workflows with various query types to identify failure points
"""
import sys
from pathlib import Path
import time
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))

from chatbot import HotelChatbot
from utils.neo4j_client import Neo4jClient

# Test cases organized by category - Covering all 15 queries in query_library.py
TEST_CASES = [
    # Query 3: get_hotels_by_rating_threshold - TESTING: decimal extraction
    {
        "category": "Query3-RatingThreshold",
        "query": "Hotels with rating above 8.5",
        "expected": "Should use get_hotels_by_rating_threshold query"
    },
    
    # Query 5: get_top_hotels_for_traveller_type - TESTING: context formatting
    {
        "category": "Query5-TravellerType",
        "query": "Recommend hotels for families",
        "expected": "Should use get_top_hotels_for_traveller_type (Family)"
    },
    {
        "category": "Query5-TravellerType",
        "query": "Best hotels for business travelers",
        "expected": "Should use get_top_hotels_for_traveller_type (Business)"
    },
    {
        "category": "Query5-TravellerType",
        "query": "Hotels for solo travelers",
        "expected": "Should use get_top_hotels_for_traveller_type (Solo)"
    },
    
    # Query 6: get_hotels_by_cleanliness_score - TESTING
    {
        "category": "Query6-Cleanliness",
        "query": "Find hotels with good cleanliness",
        "expected": "Should use get_hotels_by_cleanliness_score query"
    },
    
    # Query 10: check_visa_requirements - TESTING: context formatting
    {
        "category": "Query10-VisaCheck",
        "query": "Do I need a visa from USA to Dubai?",
        "expected": "Should use check_visa_requirements query"
    },
    
    # Query 11: get_travellers_by_country_no_visa - TESTING: context formatting
    {
        "category": "Query11-TravellersNoVisa",
        "query": "How many travellers from USA stayed in Egypt without needing a visa?",
        "expected": "Should use get_travellers_by_country_no_visa query"
    },
    
    # Query 12: get_hotels_by_comfort_score - TESTING
    {
        "category": "Query12-Comfort",
        "query": "Show me hotels with good comfort",
        "expected": "Should use get_hotels_by_comfort_score query"
    },
    
    # Query 13: get_hotels_by_value_for_money - TESTING: "affordable" keyword
    {
        "category": "Query13-ValueForMoney",
        "query": "Show me affordable quality hotels",
        "expected": "Should use get_hotels_by_value_for_money query"
    },
    
    # Query 14: get_hotels_with_best_staff_scores - TESTING: "excellent" keyword
    {
        "category": "Query14-BestStaff",
        "query": "Hotels with excellent staff",
        "expected": "Should use get_hotels_with_best_staff_scores query"
    },
    {
        "category": "Query14-BestStaff",
        "query": "Which hotels have the best service?",
        "expected": "Should use get_hotels_with_best_staff_scores query"
    },
    
    # Edge cases
    {
        "category": "Edge-case",
        "query": "Show me 10-star hotels",
        "expected": "Should handle invalid rating gracefully"
    },
]

WORKFLOWS = [
    "baseline_only",
    "embedding_only",
    "hybrid",
    "conversational_hybrid",
    "llm_pipeline"
]


class TestResult:
    """Store test result information"""
    def __init__(self, workflow: str, test_case: Dict, response: Dict, error: str = None):
        self.workflow = workflow
        self.test_case = test_case
        self.response = response
        self.error = error
        self.success = error is None and response.get('result_count', 0) > 0
        self.has_results = response.get('result_count', 0) > 0 if response else False


def check_neo4j_data():
    """Check if Neo4j has data"""
    print("\n" + "="*70)
    print("📊 CHECKING NEO4J DATA")
    print("="*70)
    
    try:
        neo4j = Neo4jClient()
        
        # Count hotels
        hotel_count = neo4j.run_query("MATCH (h:Hotel) RETURN count(h) as count", {})
        print(f"✓ Hotels in database: {hotel_count[0]['count'] if hotel_count else 0}")
        
        # Count cities
        city_count = neo4j.run_query("MATCH (c:City) RETURN count(c) as count", {})
        print(f"✓ Cities in database: {city_count[0]['count'] if city_count else 0}")
        
        # Count reviews
        review_count = neo4j.run_query("MATCH (r:Review) RETURN count(r) as count", {})
        print(f"✓ Reviews in database: {review_count[0]['count'] if review_count else 0}")
        
        # Sample hotel names
        sample_hotels = neo4j.run_query(
            "MATCH (h:Hotel)-[:LOCATED_IN]->(c:City) RETURN h.name as name, c.name as city LIMIT 5",
            {}
        )
        if sample_hotels:
            print("\n📍 Sample hotels in database:")
            for hotel in sample_hotels:
                print(f"   - {hotel['name']} in {hotel['city']}")
        
        neo4j.close()
        return True
    except Exception as e:
        print(f"✗ Error checking Neo4j: {str(e)}")
        return False


def run_test(workflow: str, test_case: Dict, test_num: int, total: int, detailed_log_file: str) -> TestResult:
    """Run a single test case"""
    def log_detailed(message):
        """Write detailed logs to file"""
        with open(detailed_log_file, 'a') as f:
            f.write(message + '\n')
    
    try:
        print(f"\n[{test_num}/{total}] Testing: {workflow} | {test_case['category']}")
        print(f"Query: '{test_case['query']}'")
        
        # Log to detailed file
        log_detailed("\n" + "="*80)
        log_detailed(f"TEST #{test_num}/{total}")
        log_detailed(f"Workflow: {workflow}")
        log_detailed(f"Category: {test_case['category']}")
        log_detailed(f"Query: {test_case['query']}")
        log_detailed(f"Expected: {test_case['expected']}")
        log_detailed("="*80)
        
        # Create chatbot for this workflow
        bot = HotelChatbot(workflow_mode=workflow)
        
        # Run query
        start_time = time.time()
        response = bot.chat(test_case['query'])
        elapsed = time.time() - start_time
        
        # Analyze response
        result_count = response.get('result_count', 0)
        answer_length = len(response.get('answer', ''))
        answer = response.get('answer', 'No answer generated')
        
        print(f"⏱️  Time: {elapsed:.2f}s | Results: {result_count} | Answer length: {answer_length} chars")
        
        # Log detailed results
        log_detailed(f"\n⏱️  Execution Time: {elapsed:.2f}s")
        log_detailed(f"📊 Results Count: {result_count}")
        log_detailed(f"📝 Answer Length: {answer_length} characters")
        
        # Log baseline results if present
        if 'baseline_results' in response:
            baseline = response['baseline_results']
            log_detailed(f"\n🔍 BASELINE RESULTS: {len(baseline) if baseline else 0} results")
            if baseline:
                for i, result in enumerate(baseline[:3], 1):  # Show first 3
                    log_detailed(f"   {i}. {result}")
        
        # Log embedding results if present
        if 'embedding_results' in response:
            embedding = response['embedding_results']
            log_detailed(f"\n🧠 EMBEDDING RESULTS: {len(embedding) if embedding else 0} results")
            if embedding:
                for i, result in enumerate(embedding[:3], 1):  # Show first 3
                    log_detailed(f"   {i}. {result}")
        
        # Log the final answer
        log_detailed(f"\n💬 FINAL ANSWER:")
        log_detailed("-" * 80)
        log_detailed(answer)
        log_detailed("-" * 80)
        
        if result_count > 0:
            print(f"✓ SUCCESS - Retrieved {result_count} results")
            log_detailed(f"\n✓ TEST RESULT: SUCCESS - Retrieved {result_count} results")
        else:
            print(f"⚠️  NO RESULTS - No data retrieved from graph")
            log_detailed(f"\n⚠️  TEST RESULT: NO RESULTS - No data retrieved from graph")
        
        return TestResult(workflow, test_case, response)
        
    except Exception as e:
        print(f"✗ ERROR - {str(e)}")
        log_detailed(f"\n❌ ERROR: {str(e)}")
        log_detailed(f"Full traceback: {e.__class__.__name__}: {str(e)}")
        return TestResult(workflow, test_case, {}, error=str(e))


def analyze_results(results: List[TestResult], summary_file: str):
    """Analyze and report test results"""
    def log(message):
        """Print and write to file"""
        print(message)
        with open(summary_file, 'a') as f:
            f.write(message + '\n')
    
    log("\n" + "="*70)
    log("📊 TEST RESULTS ANALYSIS")
    log("="*70)
    
    # Overall statistics
    total_tests = len(results)
    tests_with_results = sum(1 for r in results if r.has_results)
    tests_with_errors = sum(1 for r in results if r.error)
    
    log(f"\n📈 Overall Statistics:")
    log(f"   Total tests run: {total_tests}")
    log(f"   Tests with results: {tests_with_results} ({tests_with_results/total_tests*100:.1f}%)")
    log(f"   Tests with errors: {tests_with_errors} ({tests_with_errors/total_tests*100:.1f}%)")
    log(f"   Tests with no results: {total_tests - tests_with_results - tests_with_errors}")
    
    # Results by workflow
    log(f"\n📊 Results by Workflow:")
    for workflow in WORKFLOWS:
        workflow_results = [r for r in results if r.workflow == workflow]
        if workflow_results:
            with_results = sum(1 for r in workflow_results if r.has_results)
            with_errors = sum(1 for r in workflow_results if r.error)
            log(f"\n   {workflow}:")
            log(f"      Tests: {len(workflow_results)}")
            log(f"      With results: {with_results} ({with_results/len(workflow_results)*100:.1f}%)")
            log(f"      With errors: {with_errors}")
    
    # Results by category
    log(f"\n📊 Results by Query Category:")
    categories = set(r.test_case['category'] for r in results)
    for category in sorted(categories):
        cat_results = [r for r in results if r.test_case['category'] == category]
        with_results = sum(1 for r in cat_results if r.has_results)
        log(f"   {category}: {with_results}/{len(cat_results)} successful")
    
    # Failure analysis
    log(f"\n🔍 Failure Analysis:")
    failures = [r for r in results if not r.has_results and not r.error]
    if failures:
        log(f"\n   {len(failures)} tests returned no results:")
        
        # Group by workflow
        for workflow in WORKFLOWS:
            workflow_failures = [f for f in failures if f.workflow == workflow]
            if workflow_failures:
                log(f"\n   {workflow} ({len(workflow_failures)} failures):")
                for f in workflow_failures[:3]:  # Show first 3
                    log(f"      - [{f.test_case['category']}] {f.test_case['query']}")
    
    # Error analysis
    errors = [r for r in results if r.error]
    if errors:
        log(f"\n❌ Errors ({len(errors)} total):")
        for err in errors[:5]:  # Show first 5 errors
            log(f"   - {err.workflow}: {err.error[:100]}")
    
    # Identify weakest areas
    log(f"\n⚠️  Weakest Areas:")
    category_success_rates = {}
    for category in categories:
        cat_results = [r for r in results if r.test_case['category'] == category]
        success_rate = sum(1 for r in cat_results if r.has_results) / len(cat_results)
        category_success_rates[category] = success_rate
    
    worst_categories = sorted(category_success_rates.items(), key=lambda x: x[1])[:3]
    for category, rate in worst_categories:
        log(f"   - {category}: {rate*100:.1f}% success rate")
    
    # Best performing workflow
    log(f"\n🏆 Best Performing Workflow:")
    workflow_success = {}
    for workflow in WORKFLOWS:
        workflow_results = [r for r in results if r.workflow == workflow]
        if workflow_results:
            success_rate = sum(1 for r in workflow_results if r.has_results) / len(workflow_results)
            workflow_success[workflow] = success_rate
    
    if workflow_success:
        best_workflow = max(workflow_success.items(), key=lambda x: x[1])
        log(f"   {best_workflow[0]}: {best_workflow[1]*100:.1f}% success rate")


def main():
    """Run comprehensive test suite"""
    # Output files
    summary_file = "test_results_summary.txt"
    detailed_file = "test_results_detailed.txt"
    
    def log(message):
        """Print and write to summary file"""
        print(message)
        with open(summary_file, 'a') as f:
            f.write(message + '\n')
    
    # Clear previous results
    with open(summary_file, 'w') as f:
        f.write("")
    with open(detailed_file, 'w') as f:
        f.write("COMPREHENSIVE GRAPH-RAG SYSTEM TEST - DETAILED OUTPUT\n")
        f.write("="*80 + "\n")
        f.write("This file contains the complete output of each test including queries and responses\n")
        f.write("="*80 + "\n\n")
    
    log("="*70)
    log("🧪 COMPREHENSIVE GRAPH-RAG SYSTEM TEST")
    log("="*70)
    
    # Check Neo4j data first
    if not check_neo4j_data():
        log("\n⚠️  Warning: Could not verify Neo4j data. Tests may fail.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run tests
    log("\n" + "="*70)
    log("🚀 STARTING TESTS")
    log("="*70)
    log(f"Total test cases: {len(TEST_CASES)}")
    log(f"Workflows to test: {len(WORKFLOWS)}")
    log(f"Total tests: {len(TEST_CASES) * len(WORKFLOWS)}")
    
    all_results = []
    test_num = 0
    total_tests = len(TEST_CASES) * len(WORKFLOWS)
    
    for workflow in WORKFLOWS:
        log(f"\n{'='*70}")
        log(f"Testing Workflow: {workflow.upper()}")
        log(f"{'='*70}")
        
        for test_case in TEST_CASES:
            test_num += 1
            result = run_test(workflow, test_case, test_num, total_tests, detailed_file)
            all_results.append(result)
            
            # 10-second delay between requests to avoid rate limits
            log(f"⏳ Waiting 10 seconds before next test (rate limit protection)...")
            time.sleep(15)
    
    # Analyze results
    analyze_results(all_results, summary_file)
    
    log("\n" + "="*70)
    log("✅ TEST SUITE COMPLETE")
    log(f"📄 Summary saved to: {summary_file}")
    log(f"📄 Detailed output saved to: {detailed_file}")
    log("="*70)


if __name__ == "__main__":
    main()

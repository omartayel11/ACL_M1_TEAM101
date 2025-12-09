"""
Test the embedding workflow end-to-end
"""
import sys
from pathlib import Path

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent))

from workflows.workflow_factory import get_workflow

def main():
    print("Testing Embedding Workflow")
    print("="*60)
    
    # Get the embedding workflow
    workflow = get_workflow("embedding_only")
    print("✓ Loaded embedding_only workflow\n")
    
    # Test query
    query = "Luxury hotels with great location"
    print(f"Query: {query}\n")
    
    # Run workflow
    initial_state = {
        "user_query": query,
        "intent": None,
        "entities": {},
        "cypher_query": None,
        "baseline_results": [],
        "embedding_results": [],
        "merged_context": "",
        "llm_query_results": [],
        "answer": "",
        "error": None
    }
    
    print("Running workflow...")
    result = workflow.invoke(initial_state)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n📊 Embedding Results: {len(result.get('embedding_results', []))} hotels found")
        
        for i, hotel in enumerate(result.get('embedding_results', [])[:5], 1):
            print(f"\n{i}. {hotel.get('hotel_name', 'N/A')}")
            print(f"   Location: {hotel.get('city', 'N/A')}, {hotel.get('country', 'N/A')}")
            print(f"   Star Rating: {hotel.get('star_rating', 'N/A')}")
            print(f"   Overall Score: {hotel.get('avg_score', 'N/A')}")
            print(f"   Similarity: {hotel.get('similarity_score', 0):.4f}")
        
        print(f"\n💬 Answer:\n{result.get('answer', 'No answer generated')}")

if __name__ == "__main__":
    main()

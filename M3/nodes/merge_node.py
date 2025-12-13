"""
Merge Node - Merge baseline and embedding results
"""

from state.graph_state import GraphState
from components.result_merger import ResultMerger

# Initialize merger once
merger = ResultMerger()


def merge_node(state: GraphState) -> GraphState:
    """
    Merge and deduplicate baseline + embedding results
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with merged context
    """
    baseline_results = state.get("baseline_results", [])
    embedding_results = state.get("embedding_results", [])
    
    # Merge results into formatted context
    merged_context = merger.merge(baseline_results, embedding_results)
    
    # Print merged context for visibility
    print(f"\n📋 [MERGED CONTEXT FOR LLM]")
    print(f"Baseline results: {len(baseline_results)} | Embedding results: {len(embedding_results)}")
    print(f"Context length: {len(merged_context)} characters")
    print(f"\nFull merged context:\n{'-'*60}")
    print(merged_context)
    print(f"{'-'*60}")
    
    # Return only changed fields
    return {"merged_context": merged_context}


if __name__ == "__main__":
    # Test merge node
    test_state: GraphState = {
        "baseline_results": [
            {
                "hotel_id": "h1",
                "hotel_name": "Hotel Paris",
                "city": "Paris",
                "avg_score": 8.5
            }
        ],
        "embedding_results": [
            {
                "hotel_id": "h2",
                "hotel_name": "London Inn",
                "city": "London",
                "avg_score": 7.8,
                "similarity_score": 0.92
            }
        ]
    }
    
    result = merge_node(test_state)
    print("Merge Node Test:")
    print(f"Baseline count: {len(test_state['baseline_results'])}")
    print(f"Embedding count: {len(test_state['embedding_results'])}")
    print(f"\nMerged Context:\n{result.get('merged_context', 'None')[:300]}...")

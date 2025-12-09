"""
Output Node - Format final output for UI display
"""

from state.graph_state import GraphState


def output_node(state: GraphState) -> GraphState:
    """
    Format final output for user display
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with formatted output
    """
    # Determine which workflow was used based on available state fields
    workflow_type = "unknown"
    
    if state.get("llm_generated_cypher"):
        workflow_type = "llm_pipeline"
    elif state.get("merged_context"):
        workflow_type = "hybrid"
    elif state.get("embedding_results"):
        workflow_type = "embedding_only"
    elif state.get("baseline_results"):
        workflow_type = "baseline_only"
    
    # Build output
    final_output = {
        "query": state.get("user_query", ""),
        "workflow": workflow_type,
        "answer": state.get("llm_response"),
        "results": {
            "baseline": state.get("baseline_results"),
            "embedding": state.get("embedding_results"),
            "llm_query": state.get("llm_query_results")
        },
        "metadata": {
            "intent": state.get("intent"),
            "entities": state.get("entities"),
            "baseline_count": len(state.get("baseline_results", [])),
            "embedding_count": len(state.get("embedding_results", [])),
            **state.get("metadata", {})
        }
    }
    
    # Return only changed fields
    return {"final_output": final_output}


if __name__ == "__main__":
    # Test output node
    test_state: GraphState = {
        "user_query": "Find hotels in Paris",
        "intent": "HotelSearch",
        "entities": {"city": "Paris"},
        "baseline_results": [{"hotel_name": "Hotel Paris"}],
        "embedding_results": [{"hotel_name": "Paris Inn"}],
        "merged_context": "Hotels found...",
        "llm_response": "Based on the data, Hotel Paris is a great choice.",
        "metadata": {"query_length": 20}
    }
    
    result = output_node(test_state)
    print("Output Node Test:")
    print(f"Workflow: {result['final_output']['workflow']}")
    print(f"Query: {result['final_output']['query']}")
    print(f"Answer: {result['final_output']['answer']}")
    print(f"Metadata: {result['final_output']['metadata']}")

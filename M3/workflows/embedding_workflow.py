"""
Embedding Workflow - Pure Semantic Search
Embedding-only retrieval without intent classification
"""

from langgraph.graph import StateGraph, END
from state.graph_state import GraphState
from nodes import (
    input_node,
    intent_node,
    entity_node,
    embedding_query_node,
    merge_node,  # Format embedding results
    answer_node,
    output_node,
    casual_conversation_node
)


def create_embedding_workflow():
    """
    Create embedding-only workflow graph
    
    Flow: Input → EmbeddingQuery → Output
    
    Use Case: Pure semantic search
    - No intent classification needed
    - Direct embedding generation
    - FAISS vector similarity search
    - Returns similar hotels/reviews
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("entity", entity_node)
    workflow.add_node("casual", casual_conversation_node)
    workflow.add_node("embedding_query", embedding_query_node)
    workflow.add_node("merge", merge_node)  # Format results
    workflow.add_node("answer", answer_node)
    workflow.add_node("output", output_node)
    
    # Routing function
    def route_after_intent(state: GraphState) -> str:
        intent = state.get("intent", "GeneralQuestionAnswering")
        if intent == "CasualConversation":
            return "casual"
        return "embedding"
    
    # Define edges
    workflow.set_entry_point("input")
    workflow.add_edge("input", "intent")
    workflow.add_edge("intent", "entity")  # Extract entities after intent
    
    # Conditional routing after entity extraction
    workflow.add_conditional_edges(
        "entity",
        route_after_intent,
        {
            "casual": "casual",
            "embedding": "embedding_query"
        }
    )
    
    # Casual path
    workflow.add_edge("casual", "output")
    
    # Embedding path
    workflow.add_edge("embedding_query", "merge")  # Format results
    workflow.add_edge("merge", "answer")
    workflow.add_edge("answer", "output")
    workflow.add_edge("output", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test embedding workflow
    workflow = create_embedding_workflow()
    
    test_query = "Luxury hotels with great location and cleanliness"
    print(f"Testing Embedding Workflow with query: '{test_query}'")
    print("=" * 60)
    
    result = workflow.invoke({"user_query": test_query})
    
    print("\n=== Results ===")
    print(f"Query embedding dimension: {len(result.get('query_embedding', []))}")
    print(f"Embedding results count: {len(result.get('embedding_results', []))}")
    
    final_output = result.get('final_output', {})
    print(f"\nWorkflow: {final_output.get('workflow')}")
    
    # Get embedding results
    embedding_results = final_output.get('results', {}).get('embedding', [])
    print(f"Total embedding results: {len(embedding_results)}")
    
    # Show first few results if available
    if embedding_results:
        print(f"\nTop 3 results:")
        for i, item in enumerate(embedding_results[:3], 1):
            # Get name (hotel_name for hotels, review_text for reviews)
            name = item.get('hotel_name') or item.get('name') or item.get('review_text', '')[:50]
            similarity = item.get('similarity_score', 0)
            node_type = item.get('node_type', 'unknown')
            
            # Show additional info for hotels
            if node_type == 'hotel':
                city = item.get('city', 'N/A')
                star = item.get('star_rating', 'N/A')
                print(f"  {i}. {name} - {city} ({star}★) (similarity: {similarity:.3f})")
            else:
                print(f"  {i}. [{node_type}] {name} (similarity: {similarity:.3f})")
    else:
        print("\nNo results found. Try lowering the similarity threshold in config.yaml")

"""
Hybrid Workflow - Structured + Semantic Search
Combines baseline Cypher queries with embedding search, then merges results
"""

from langgraph.graph import StateGraph, END
from state.graph_state import GraphState
from nodes import (
    input_node,
    intent_node,
    entity_node,
    baseline_query_node,
    embedding_query_node,
    merge_node,
    answer_node,
    output_node,
    casual_conversation_node
)


def create_hybrid_workflow():
    """
    Create hybrid workflow graph with parallel retrieval
    
    Flow: Input → Intent → Entity → [BaselineQuery || EmbeddingQuery] → Merge → Output
    
    Use Case: Best of both worlds
    - Intent classification + entity extraction
    - Parallel execution of:
        * Structured Cypher queries (baseline)
        * Semantic vector search (embedding)
    - Result merging and deduplication
    - Highest quality, slower performance
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("casual", casual_conversation_node)
    workflow.add_node("entity", entity_node)
    workflow.add_node("baseline_query", baseline_query_node)
    workflow.add_node("embedding_query", embedding_query_node)
    workflow.add_node("merge", merge_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("output", output_node)
    
    # Routing function
    def route_after_intent(state: GraphState) -> str:
        intent = state.get("intent", "GeneralQuestionAnswering")
        if intent == "CasualConversation":
            return "casual"
        return "entity"
    
    # Define edges
    workflow.set_entry_point("input")
    workflow.add_edge("input", "intent")
    
    # Conditional routing after intent
    workflow.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "casual": "casual",
            "entity": "entity"
        }
    )
    
    # Casual path goes straight to output
    workflow.add_edge("casual", "output")
    
    # Retrieval path: parallel branching
    workflow.add_edge("entity", "baseline_query")
    workflow.add_edge("entity", "embedding_query")
    
    # Both branches converge at merge
    workflow.add_edge("baseline_query", "merge")
    workflow.add_edge("embedding_query", "merge")
    
    # Answer generation and output
    workflow.add_edge("merge", "answer")
    workflow.add_edge("answer", "output")
    workflow.add_edge("output", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test hybrid workflow
    workflow = create_hybrid_workflow()
    
    test_query = "Find luxury hotels in Paris with excellent cleanliness"
    print(f"Testing Hybrid Workflow with query: '{test_query}'")
    print("=" * 60)
    
    result = workflow.invoke({"user_query": test_query})
    
    print("\n=== Results ===")
    print(f"Intent: {result.get('intent')}")
    print(f"Entities: {result.get('entities')}")
    print(f"Baseline results: {len(result.get('baseline_results', []))}")
    print(f"Embedding results: {len(result.get('embedding_results', []))}")
    print(f"Merged context length: {len(result.get('merged_context', ''))} chars")
    
    final_output = result.get('final_output', {})
    print(f"\nWorkflow: {final_output.get('workflow')}")
    print(f"Total results: {len(final_output.get('results', []))}")
    
    # Show metadata
    metadata = final_output.get('metadata', {})
    print(f"\nMetadata:")
    print(f"  Baseline count: {metadata.get('baseline_count', 0)}")
    print(f"  Embedding count: {metadata.get('embedding_count', 0)}")
    print(f"  Merged count: {metadata.get('merged_count', 0)}")

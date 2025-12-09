"""
Baseline Workflow - Intent → Entity → Cypher Query
Fast structured queries using rule-based intent classification and Cypher execution
"""

from langgraph.graph import StateGraph, END
from state.graph_state import GraphState
from nodes import (
    input_node,
    intent_node,
    entity_node,
    baseline_query_node,
    merge_node,  # Use merge_node to format results
    answer_node,
    output_node,
    casual_conversation_node
)


def create_baseline_workflow():
    """
    Create baseline workflow graph
    
    Flow: Input → Intent → Entity → BaselineQuery → Output
    
    Use Case: Fast structured Cypher queries
    - Intent classification (7 types)
    - Entity extraction
    - Query building from query_library.py
    - Direct Neo4j execution
    
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
    workflow.add_node("merge", merge_node)  # Format results into context
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
    
    # Retrieval path
    workflow.add_edge("entity", "baseline_query")
    workflow.add_edge("baseline_query", "merge")  # Format results
    workflow.add_edge("merge", "answer")
    workflow.add_edge("answer", "output")
    workflow.add_edge("output", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test baseline workflow
    workflow = create_baseline_workflow()
    
    test_query = "Find hotels in Paris"
    print(f"Testing Baseline Workflow with query: '{test_query}'")
    print("=" * 60)
    
    result = workflow.invoke({"user_query": test_query})
    
    print("\n=== Results ===")
    print(f"Intent: {result.get('intent')}")
    print(f"Entities: {result.get('entities')}")
    print(f"Cypher: {result.get('baseline_cypher', '')[:100]}...")
    print(f"Results count: {len(result.get('baseline_results', []))}")
    
    final_output = result.get('final_output', {})
    print(f"\nWorkflow: {final_output.get('workflow')}")
    
    # Show baseline results
    baseline_results = final_output.get('results', {}).get('baseline', [])
    print(f"Total baseline results: {len(baseline_results)}")
    
    if baseline_results:
        print(f"\nFirst result:")
        first = baseline_results[0]
        for key, value in list(first.items())[:5]:  # Show first 5 fields
            print(f"  {key}: {value}")

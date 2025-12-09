"""
Conversational Hybrid Workflow - Full LangGraph with Memory
Hybrid workflow with integrated conversation management and query rewriting
"""

from langgraph.graph import StateGraph, END
from state.graph_state import GraphState
from nodes import (
    conversational_input_node,
    intent_node,
    entity_node,
    baseline_query_node,
    embedding_query_node,
    merge_node,
    conversation_context_node,
    answer_node,
    conversation_update_node,
    output_node,
    casual_conversation_node  # New: for casual chat
)


def create_conversational_hybrid_workflow():
    """
    Create conversational hybrid workflow with integrated memory
    
    Flow: 
        Input → QueryRewriter → Intent → Entity → 
        [BaselineQuery || EmbeddingQuery] → Merge → 
        ConversationContext → Answer → ConversationUpdate → Output
    
    Features:
    - Query rewriting using chat history
    - Parallel baseline + embedding retrieval
    - Conversation context for answer generation
    - Automatic history update
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("input", conversational_input_node)
    workflow.add_node("intent", intent_node)
    workflow.add_node("casual", casual_conversation_node)  # New: casual chat
    workflow.add_node("entity", entity_node)
    workflow.add_node("baseline_query", baseline_query_node)
    workflow.add_node("embedding_query", embedding_query_node)
    workflow.add_node("merge", merge_node)
    workflow.add_node("conversation_context", conversation_context_node)
    workflow.add_node("answer", answer_node)
    workflow.add_node("conversation_update", conversation_update_node)
    workflow.add_node("output", output_node)
    
    # Routing function: casual vs retrieval
    def route_after_intent(state: GraphState) -> str:
        """Route to casual node or entity extraction based on intent"""
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
    
    # Casual path: skip retrieval, go straight to conversation update
    workflow.add_edge("casual", "conversation_update")
    
    # Retrieval path: parallel baseline + embedding
    workflow.add_edge("entity", "baseline_query")
    workflow.add_edge("entity", "embedding_query")
    
    # Both paths converge at merge
    workflow.add_edge("baseline_query", "merge")
    workflow.add_edge("embedding_query", "merge")
    
    # Add conversation context before answer
    workflow.add_edge("merge", "conversation_context")
    workflow.add_edge("conversation_context", "answer")
    
    # Update conversation history
    workflow.add_edge("answer", "conversation_update")
    workflow.add_edge("conversation_update", "output")
    workflow.add_edge("output", END)
    
    # Compile and return
    return workflow.compile()


if __name__ == "__main__":
    # Test conversational hybrid workflow
    workflow = create_conversational_hybrid_workflow()
    
    # Simulate conversation
    print("="*60)
    print("TEST: Conversational Hybrid Workflow")
    print("="*60)
    
    # First query
    state1 = {
        "user_query": "Find luxury hotels in Dubai",
        "chat_history": []
    }
    
    print("\nQuery 1: Find luxury hotels in Dubai")
    result1 = workflow.invoke(state1)
    
    print(f"Intent: {result1.get('intent')}")
    print(f"Entities: {result1.get('entities')}")
    print(f"Baseline results: {len(result1.get('baseline_results', []))}")
    print(f"Embedding results: {len(result1.get('embedding_results', []))}")
    print(f"Answer: {result1.get('llm_response', '')[:200]}...")
    print(f"History length: {len(result1.get('chat_history', []))}")
    
    # Second query with reference
    state2 = {
        "user_query": "What about 5-star hotels there?",
        "chat_history": result1.get("chat_history", [])
    }
    
    print("\n" + "="*60)
    print("Query 2: What about 5-star hotels there? (with history)")
    result2 = workflow.invoke(state2)
    
    print(f"Original query: {state2['user_query']}")
    print(f"Rewritten: {result2.get('metadata', {}).get('query_rewritten', False)}")
    print(f"Intent: {result2.get('intent')}")
    print(f"Entities: {result2.get('entities')}")
    print(f"History length: {len(result2.get('chat_history', []))}")
    
    print("\n✓ Conversational workflow test complete!")

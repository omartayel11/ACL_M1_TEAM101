"""
Conversational Input Node - Input processing with query rewriting
Used only in conversational_hybrid_workflow
"""

from state.graph_state import GraphState
from components.query_rewriter import QueryRewriter

# Initialize query rewriter
rewriter = QueryRewriter()


def conversational_input_node(state: GraphState) -> GraphState:
    """
    Validate, normalize, and rewrite input query using chat history
    
    This node is specifically for conversational workflows where query
    rewriting based on chat history is needed.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with normalized/rewritten query
    """
    query = state.get("user_query", "")
    chat_history = state.get("chat_history", [])
    
    # Step 1: Normalize query
    query = query.strip()
    
    # Step 2: Query rewriting if chat history exists
    query_rewritten = False
    original_query = query
    
    if chat_history and rewriter.needs_rewriting(query):
        # Format history context
        context = _format_history(chat_history)
        # Extract last entities
        last_entities = _extract_last_entities(chat_history)
        
        # Rewrite query
        rewritten = rewriter.rewrite_with_context(query, context, last_entities)
        
        if rewritten != query:
            print(f"[Input Node] Query Rewriting: '{query}' → '{rewritten}'")
            query = rewritten
            query_rewritten = True
    
    # Return only changes
    return {
        "user_query": query,
        "metadata": {
            "query_length": len(query),
            "query_rewritten": query_rewritten,
            "original_query": original_query if query_rewritten else None
        }
    }


def _format_history(chat_history: list, last_n: int = 4) -> str:
    """Format chat history for context"""
    recent = chat_history[-last_n:] if last_n > 0 else chat_history
    if not recent:
        return ""
    
    lines = ["Previous conversation:"]
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


def _extract_last_entities(chat_history: list) -> dict:
    """Extract entities from recent messages"""
    entities = {}
    for msg in reversed(chat_history):
        if msg.get("role") == "user" and "entities" in msg.get("metadata", {}):
            for key, value in msg["metadata"]["entities"].items():
                if key not in entities and value:
                    entities[key] = value
    return entities


if __name__ == "__main__":
    # Test conversational input node
    test_state: GraphState = {
        "user_query": "  What about 5-star hotels there?  ",
        "chat_history": [
            {
                "role": "user",
                "content": "Find hotels in Dubai",
                "metadata": {"entities": {"city": "Dubai"}}
            },
            {
                "role": "assistant",
                "content": "Found 5 hotels in Dubai."
            }
        ]
    }
    
    result = conversational_input_node(test_state)
    print("Conversational Input Node Test:")
    print(f"Original: '{test_state['user_query']}'")
    print(f"Processed: '{result.get('user_query')}'")
    print(f"Rewritten: {result.get('metadata', {}).get('query_rewritten')}")

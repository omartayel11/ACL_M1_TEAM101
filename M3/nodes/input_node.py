"""
Input Node - Validate, normalize, and rewrite user query
Integrated query rewriting for conversation context
"""

from state.graph_state import GraphState
from components.query_rewriter import QueryRewriter

# Initialize query rewriter
rewriter = QueryRewriter()


def input_node(state: GraphState) -> GraphState:
    """
    Validate and normalize input query
    
    NOTE: Query rewriting is handled separately in conversational_hybrid_workflow.
    This node should only do basic validation and normalization.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with normalized query
    """
    query = state.get("user_query", "")
    
    # Normalize query
    query = query.strip()
    
    # Return only changes
    return {
        "user_query": query,
        "metadata": {
            "query_length": len(query)
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
    # Test input node
    test_state: GraphState = {
        "user_query": "  i want the hotels than have cleanliness score greater than 8   "
    }
    
    result = input_node(test_state)
    print("Input Node Test:")
    print(f"Original: '{test_state['user_query']}'")
    print(f"Normalized: '{result['user_query']}'")
    print(f"Metadata: {result.get('metadata')}")

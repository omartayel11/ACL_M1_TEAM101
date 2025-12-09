"""
Conversation History Node - Manage chat history in state
LangGraph node that updates conversation history after processing
"""

from state.graph_state import GraphState
from datetime import datetime


def conversation_update_node(state: GraphState) -> GraphState:
    """
    Update conversation history with current query and response
    This node should be called at the end of workflows
    
    Args:
        state: Current graph state after processing
        
    Returns:
        Updated state with new messages added to chat_history
    """
    user_query = state.get("user_query", "")
    llm_response = state.get("llm_response", "")
    intent = state.get("intent")
    entities = state.get("entities", {})
    
    # Get existing history or initialize
    chat_history = state.get("chat_history", []).copy()
    
    # Add user message
    if user_query:
        user_message = {
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "intent": intent,
                "entities": entities,
                "query_rewritten": state.get("metadata", {}).get("query_rewritten", False)
            }
        }
        chat_history.append(user_message)
    
    # Add assistant message
    if llm_response:
        assistant_message = {
            "role": "assistant",
            "content": llm_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "workflow": state.get("metadata", {}).get("workflow"),
                "result_count": len(state.get("baseline_results", [])) + len(state.get("embedding_results", []))
            }
        }
        chat_history.append(assistant_message)
    
    # Trim history to last 20 messages (10 turns)
    max_messages = 20
    if len(chat_history) > max_messages:
        chat_history = chat_history[-max_messages:]
    
    # Return only changed fields
    return {
        "chat_history": chat_history,
        "metadata": {
            **state.get("metadata", {}),
            "conversation_length": len(chat_history)
        }
    }


def conversation_context_node(state: GraphState) -> GraphState:
    """
    Format conversation history as context string for LLM
    Adds conversation_context to state for answer generation
    
    Args:
        state: Current graph state with chat_history
        
    Returns:
        Updated state with conversation_context string
    """
    chat_history = state.get("chat_history", [])
    
    if not chat_history:
        return {}  # No changes if no history
    
    # Format last few messages
    recent = chat_history[-6:]  # Last 3 turns (6 messages)
    context_lines = ["Recent conversation:"]
    
    for msg in recent:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = msg.get("content", "")
        # Truncate long messages
        if len(content) > 150:
            content = content[:150] + "..."
        context_lines.append(f"{role}: {content}")
    
    conversation_context = "\n".join(context_lines)
    
    # Return only changed fields
    return {
        "conversation_context": conversation_context
    }


if __name__ == "__main__":
    # Test conversation nodes
    test_state: GraphState = {
        "user_query": "Find hotels in Paris",
        "intent": "HotelSearch",
        "entities": {"city": "Paris"},
        "llm_response": "I found 5 hotels in Paris.",
        "baseline_results": [{"hotel": "A"}, {"hotel": "B"}],
        "chat_history": []
    }
    
    # Test update node
    result = conversation_update_node(test_state)
    print(f"History length: {len(result['chat_history'])}")
    print(f"Messages:")
    for msg in result['chat_history']:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Test context node
    result2 = conversation_context_node(result)
    print(f"\nConversation context:\n{result2.get('conversation_context')}")

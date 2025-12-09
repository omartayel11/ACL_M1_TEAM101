"""
Answer Node - Generate final answer from context using LLM
"""

from state.graph_state import GraphState
from components.answer_generator import AnswerGenerator

# Initialize generator once
generator = AnswerGenerator()


def answer_node(state: GraphState) -> GraphState:
    """
    Generate final answer from query and context
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with LLM response
    """
    query = state.get("user_query", "")
    intent = state.get("intent")
    
    # Get context - use merged_context if available, otherwise format llm_query_results
    context = state.get("merged_context", "")
    
    if not context:
        # Format llm_query_results as context
        results = state.get("llm_query_results", [])
        if results:
            context = "=== QUERY RESULTS ===\n\n"
            for i, result in enumerate(results, 1):
                context += f"{i}. "
                for key, value in result.items():
                    context += f"{key}: {value}, "
                context = context.rstrip(", ") + "\n"
    
    print(f"\n💬 [ANSWER GENERATION]")
    print(f"Query: {query}")
    print(f"Intent: {intent}")
    print(f"Context length: {len(context)} characters")
    
    # Generate answer
    answer = generator.generate(query, context, intent)
    
    print(f"✓ Generated answer ({len(answer)} characters)")
    
    # Return only changed fields
    return {"llm_response": answer}


if __name__ == "__main__":
    # Test answer node
    test_context = """=== HOTELS ===

1. Hotel Paris
   Location: Paris, France
   Star Rating: 4
   Average Score: 8.50
   Relevance: 1.00
"""
    
    test_state: GraphState = {
        "user_query": "What hotels are available in Paris?",
        "intent": "HotelSearch",
        "merged_context": test_context
    }
    
    result = answer_node(test_state)
    print("Answer Node Test:")
    print(f"Query: {test_state['user_query']}")
    print(f"Intent: {test_state['intent']}")
    print(f"\nAnswer:\n{result.get('llm_response', 'None')}")

"""
Intent Node - Classify user query intent
"""

from state.graph_state import GraphState
from components.intent_classifier import IntentClassifier

# Initialize classifier once
classifier = IntentClassifier()


def intent_node(state: GraphState) -> GraphState:
    """
    Classify user query into intent
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with intent
    """
    query = state.get("user_query", "")
    intent = classifier.classify(query)
    
    # Return only changed fields
    return {"intent": intent}


if __name__ == "__main__":
    # Test intent node
    test_state: GraphState = {
        "user_query": "Find hotels in Paris"
    }
    
    result = intent_node(test_state)
    print("Intent Node Test:")
    print(f"Query: {test_state['user_query']}")
    print(f"Intent: {result.get('intent')}")

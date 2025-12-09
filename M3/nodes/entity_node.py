"""
Entity Node - Extract entities from query
"""

from state.graph_state import GraphState
from components.entity_extractor import EntityExtractor

# Initialize extractor once
extractor = EntityExtractor()


def entity_node(state: GraphState) -> GraphState:
    """
    Extract entities from user query based on intent
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with entities
    """
    query = state.get("user_query", "")
    intent = state.get("intent", "GeneralQuestionAnswering")
    
    entities = extractor.extract(query, intent)
    
    # Return only changed fields
    return {"entities": entities}


if __name__ == "__main__":
    # Test entity node
    test_state: GraphState = {
        "user_query": "Find hotels in Paris",
        "intent": "HotelSearch"
    }
    
    result = entity_node(test_state)
    print("Entity Node Test:")
    print(f"Query: {test_state['user_query']}")
    print(f"Intent: {test_state['intent']}")
    print(f"Entities: {result.get('entities')}")

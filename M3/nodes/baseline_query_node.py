"""
Baseline Query Node - Build and execute Cypher query
"""

from state.graph_state import GraphState
from components.query_builder import QueryBuilder
from components.query_executor import QueryExecutor

# Initialize components once
builder = QueryBuilder()
executor = QueryExecutor()


def baseline_query_node(state: GraphState) -> GraphState:
    """
    Build Cypher query from intent/entities and execute on Neo4j
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with baseline results
    """
    intent = state.get("intent", "")
    entities = state.get("entities", {})
    
    # Build Cypher query
    cypher, params = builder.build(intent, entities)
    
    # Execute query
    results = []
    if cypher:
        try:
            print(f"\n🔍 [BASELINE RETRIEVAL]")
            print(f"Generated Cypher: {cypher}")
            if params:
                print(f"Parameters: {params}")
            results = executor.execute(cypher, params)
            print(f"✓ Retrieved {len(results)} results from graph database")
            if results:
                print(f"Sample: {results[0] if len(results) > 0 else 'N/A'}")
        except Exception as e:
            print(f"❌ Baseline query execution failed: {e}")
            results = []
    
    # Return only changed fields
    return {
        "baseline_cypher": cypher,
        "baseline_params": params,
        "baseline_results": results
    }


if __name__ == "__main__":
    # Test baseline query node
    test_state: GraphState = {
        "user_query": "Find hotels in Paris",
        "intent": "HotelSearch",
        "entities": {"city": "Paris"}
    }
    
    result = baseline_query_node(test_state)
    print("Baseline Query Node Test:")
    print(f"Intent: {test_state['intent']}")
    print(f"Entities: {test_state['entities']}")
    print(f"Cypher: {result.get('baseline_cypher', '')[:100]}...")
    print(f"Params: {result.get('baseline_params')}")
    print(f"Results count: {len(result.get('baseline_results', []))}")

"""
LLM Query Node - LLM generates Cypher and executes it
"""

from state.graph_state import GraphState
from components.llm_query_generator import LLMQueryGenerator
from components.query_executor import QueryExecutor

# Initialize components once
generator = LLMQueryGenerator()
executor = QueryExecutor()


def llm_query_node(state: GraphState) -> GraphState:
    """
    Use LLM to generate Cypher query and execute it
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with LLM-generated query results
    """
    query = state.get("user_query", "")
    
    # Generate Cypher with LLM
    cypher = ""
    results = []
    
    try:
        cypher = generator.generate(query)
        
        print(f"\n🤖 [LLM QUERY GENERATION]")
        print(f"User Query: {query}")
        print(f"Generated Cypher:\n{cypher}\n")
        
        # Execute generated query
        if cypher:
            results = executor.execute(cypher, {})
            print(f"✓ Retrieved {len(results)} results from Neo4j")
            
            # Print all LLM query results
            if results:
                print(f"\n📊 [LLM QUERY RESULTS] ({len(results)} total):")
                for i, result in enumerate(results, 1):
                    print(f"  [{i}] {result}")
            else:
                print("  (No results found)")
    except Exception as e:
        print(f"❌ LLM query generation/execution failed: {e}")
        cypher = ""
        results = []
    
    return {
        **state,
        "llm_generated_cypher": cypher,
        "llm_query_results": results
    }


if __name__ == "__main__":
    # Test LLM query node
    test_state: GraphState = {
        "user_query": "Find top 5 hotels in Paris"
    }
    
    result = llm_query_node(test_state)
    print("LLM Query Node Test:")
    print(f"Query: {test_state['user_query']}")
    print(f"Generated Cypher:\n{result.get('llm_generated_cypher', 'None')}")
    print(f"Results count: {len(result.get('llm_query_results', []))}")

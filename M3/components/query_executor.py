"""
Query Executor for Graph-RAG Hotel Travel Assistant
Executes Cypher queries on Neo4j database
"""

from typing import List, Dict, Any, Optional
from utils.neo4j_client import Neo4jClient


class QueryExecutor:
    """
    Execute Cypher queries on Neo4j.
    Thin wrapper around Neo4jClient for component layer.
    """
    
    def __init__(self):
        """Initialize query executor"""
        self.neo4j_client = Neo4jClient()
        self.neo4j_client.connect()
    
    def execute(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results
        
        Args:
            cypher: Cypher query string
            params: Query parameters dictionary
            
        Returns:
            List of result records as dictionaries
            
        Raises:
            Exception: If query execution fails
        """
        if not cypher:
            return []
        
        params = params or {}
        
        try:
            results = self.neo4j_client.run_query(cypher, params)
            return results
            
        except Exception as e:
            print(f"Query execution failed: {e}")
            print(f"Query: {cypher[:200]}...")
            print(f"Params: {params}")
            raise


if __name__ == "__main__":
    # Test query executor
    executor = QueryExecutor()
    
    print("=== Query Executor Test ===\n")
    
    # Test 1: Simple count query
    print("Test 1: Count all nodes")
    try:
        results = executor.execute("MATCH (n) RETURN count(n) AS total")
        print(f"Total nodes: {results[0]['total']}\n")
    except Exception as e:
        print(f"Test failed: {e}\n")
    
    # Test 2: Parameterized query
    print("Test 2: Find hotels in Paris")
    try:
        cypher = """
        MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
        RETURN h.name AS hotel_name, h.average_reviews_score AS score
        LIMIT 3
        """
        results = executor.execute(cypher, {"city_name": "Paris"})
        for r in results:
            print(f"  - {r['hotel_name']}: {r['score']}")
    except Exception as e:
        print(f"Test failed: {e}")

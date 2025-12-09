"""
Query Builder for Graph-RAG Hotel Travel Assistant
Builds Cypher queries from intent and entities
"""

from typing import Dict, Tuple, Optional, Any
from query_library import QuerySelector

class QueryBuilder:
    """
    Build Cypher queries from intent and extracted entities.
    Uses QuerySelector from query_library.py
    """
    
    def __init__(self):
        """Initialize query builder"""
        self.query_selector = QuerySelector()
    
    def build(self, intent: str, entities: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Build Cypher query from intent and entities
        
        Args:
            intent: Classified intent (e.g., "HotelSearch")
            entities: Extracted entities dictionary
            
        Returns:
            Tuple of (cypher_query, parameters) or (None, None) if no match
        """
        if not intent:
            return None, None
        
        # Use QuerySelector to select appropriate query
        cypher, params = self.query_selector.select_query(intent, entities)
        
        return cypher, params


if __name__ == "__main__":
    # Test query builder
    builder = QueryBuilder()
    
    print("=== Query Builder Test ===\n")
    
    # Test 1: HotelSearch by city
    print("Test 1: HotelSearch by city")
    intent = "HotelSearch"
    entities = {"city": "Paris"}
    cypher, params = builder.build(intent, entities)
    print(f"Intent: {intent}")
    print(f"Entities: {entities}")
    print(f"Query: {cypher[:100]}..." if cypher else "None")
    print(f"Params: {params}\n")
    
    # Test 2: HotelRecommendation by traveller type
    print("Test 2: HotelRecommendation by traveller type")
    intent = "HotelRecommendation"
    entities = {"traveller_type": "Family", "limit": 5}
    cypher, params = builder.build(intent, entities)
    print(f"Intent: {intent}")
    print(f"Entities: {entities}")
    print(f"Query: {cypher[:100]}..." if cypher else "None")
    print(f"Params: {params}\n")
    
    # Test 3: VisaQuestion
    print("Test 3: VisaQuestion")
    intent = "VisaQuestion"
    entities = {"from_country": "USA", "to_country": "France"}
    cypher, params = builder.build(intent, entities)
    print(f"Intent: {intent}")
    print(f"Entities: {entities}")
    print(f"Query: {cypher[:100]}..." if cypher else "None")
    print(f"Params: {params}")

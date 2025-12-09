"""
LLM Query Generator for Graph-RAG Hotel Travel Assistant
LLM generates Cypher queries directly from natural language
"""

from typing import Optional
from utils.llm_client import LLMClient
import re


class LLMQueryGenerator:
    """
    Generate Cypher queries using LLM.
    For the llm_pipeline workflow - full LLM autonomy.
    """
    
    # Neo4j schema from Create_kg.py
    SCHEMA = """Neo4j Graph Schema:

Nodes:
- Hotel: hotel_id, name, star_rating, cleanliness_base, comfort_base, facilities_base,
         location_base, staff_base, value_for_money_base, average_reviews_score
- Review: review_id, text, date, score_overall, score_cleanliness, score_comfort,
          score_facilities, score_location, score_staff, score_value_for_money
- Traveller: user_id, gender, age, type (Business|Couple|Family|Solo|Group), join_date
- City: name
- Country: name

Relationships:
- (Hotel)-[:LOCATED_IN]->(City)
- (City)-[:LOCATED_IN]->(Country)
- (Traveller)-[:FROM_COUNTRY]->(Country)
- (Traveller)-[:WROTE]->(Review)
- (Review)-[:REVIEWED]->(Hotel)
- (Traveller)-[:STAYED_AT]->(Hotel)
- (Country)-[:NEEDS_VISA]->(Country)

Common Query Patterns:
1. Find hotels by location: MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
2. Get reviews: MATCH (r:Review)-[:REVIEWED]->(h:Hotel {name: $hotel_name})
3. Filter by traveller type: MATCH (t:Traveller {type: $traveller_type})-[:STAYED_AT]->(h:Hotel)
4. Check visa: MATCH (from:Country {name: $from})-[v:NEEDS_VISA]->(to:Country {name: $to})
"""
    
    def __init__(self):
        """Initialize LLM query generator"""
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client for query generation: {e}")
    
    def generate(self, query: str, schema: Optional[str] = None) -> str:
        """
        Generate Cypher query from natural language
        
        Args:
            query: Natural language query
            schema: Optional custom schema (uses default if not provided)
            
        Returns:
            Cypher query string
        """
        schema = schema or self.SCHEMA
        
        prompt = f"""You are a Neo4j Cypher query expert. Generate a valid Cypher query for the following natural language question.

{schema}

Natural Language Query: "{query}"

Requirements:
- Generate ONLY the Cypher query, no explanations
- DO NOT use parameters ($param) - embed values directly in the query using single quotes for strings
- Include RETURN clause with relevant fields
- Add LIMIT clause if asking for "top" or "best" (use specific number from query or default LIMIT 10)
- Use OPTIONAL MATCH for relationships that might not exist
- Order results by relevance (ratings, scores, etc.)

Example: For "Find hotels in Paris", use: MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {{name: 'Paris'}})

Cypher Query:"""

        try:
            response = self.llm_client.generate(prompt, temperature=0.0, max_tokens=500)
            
            # Extract Cypher from response
            cypher = self._extract_cypher(response)
            
            return cypher
            
        except Exception as e:
            print(f"Error generating Cypher query: {e}")
            raise
    
    def _extract_cypher(self, response: str) -> str:
        """
        Extract Cypher query from LLM response
        
        Args:
            response: LLM response text
            
        Returns:
            Clean Cypher query
        """
        # Remove markdown code blocks
        if "```cypher" in response:
            response = response.split("```cypher")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        # Clean up
        response = response.strip()
        
        # Remove any leading/trailing quotes
        response = response.strip('"').strip("'")
        
        return response


if __name__ == "__main__":
    # Test LLM query generator
    generator = LLMQueryGenerator()
    
    print("=== LLM Query Generator Test ===\n")
    
    test_queries = [
        "Find all hotels in Paris",
        "What are the top 5 hotels for families?",
        "Show me reviews for hotels with good cleanliness scores",
        "Do I need a visa from USA to France?"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        try:
            cypher = generator.generate(query)
            print(f"Generated Cypher:\n{cypher}\n")
        except Exception as e:
            print(f"Error: {e}\n")

"""
Query Rewriter - Resolve references using conversation history
Handles context-dependent queries like "What about that hotel?" or "Show me 5-star hotels there"
"""

from typing import Dict, Any, Optional
from utils.llm_client import LLMClient
from utils.config_loader import ConfigLoader


class QueryRewriter:
    """
    Rewrite queries to resolve references using conversation context
    """
    
    def __init__(self):
        """Initialize query rewriter with LLM client"""
        self.llm_client = LLMClient()
        self.config = ConfigLoader()
    
    def needs_rewriting(self, query: str) -> bool:
        """
        Check if query contains references that need resolution
        
        Args:
            query: User query
            
        Returns:
            True if query contains pronouns/references
        """
        # Reference words that indicate context dependency
        reference_words = [
            " it ", " that ", " this ", " these ", " those ",
            " there", " here",
            "what about", "how about",
        ]
        
        query_lower = " " + query.lower() + " "
        return any(ref in query_lower for ref in reference_words)
    
    def rewrite_with_context(
        self,
        query: str,
        conversation_history: str,
        last_entities: Dict[str, Any]
    ) -> str:
        """
        Rewrite query to be context-independent using conversation history
        
        Args:
            query: Current user query (may contain references)
            conversation_history: Formatted string of recent conversation
            last_entities: Previously extracted entities (city, hotel_name, etc.)
            
        Returns:
            Rewritten query with resolved references
        """
        # If no references detected, return original query
        if not self.needs_rewriting(query):
            return query
        
        # Build prompt for LLM to rewrite query
        prompt = f"""You are a query rewriter that ONLY replaces reference words with their actual values.

{conversation_history}

Previously mentioned entities:
{self._format_entities(last_entities)}

Current user query: "{query}"

Task: Replace ONLY reference words (pronouns like "it", "that", "there", "this") with the specific entities from conversation history.

CRITICAL RULES:
1. ONLY replace reference words - do NOT add any new information
2. ONLY substitute "there" → "Paris", "that hotel" → "specific hotel name", etc.
3. Do NOT add context that wasn't in the original query
4. If the query has no references to replace, return it EXACTLY as-is
5. Keep all other words identical to the original

Examples:
- "What about hotels there?" + (city: Paris) → "What about hotels in Paris?"
- "Tell me about that hotel" + (hotel: Ritz) → "Tell me about Ritz"  
- "best hotels for cleanliness" + (city: Cairo) → "best hotels for cleanliness" (NO CHANGE - no references!)

Return ONLY the rewritten query with references replaced:"""

        try:
            rewritten = self.llm_client.generate(
                prompt=prompt,
                temperature=0.3,  # Low temperature for consistent rewriting
                max_tokens=100
            )
            
            # Clean up response
            rewritten = rewritten.strip()
            
            # If LLM returns something reasonable, use it
            if rewritten and len(rewritten) > 3:
                print(f"[Query Rewriter] Original: '{query}' → Rewritten: '{rewritten}'")
                return rewritten
            else:
                # Fallback: use simple entity substitution
                return self._simple_rewrite(query, last_entities)
                
        except Exception as e:
            print(f"[Query Rewriter] LLM rewriting failed: {e}, using simple substitution")
            return self._simple_rewrite(query, last_entities)
    
    def _simple_rewrite(self, query: str, entities: Dict[str, Any]) -> str:
        """
        Simple rule-based rewriting as fallback
        
        Args:
            query: Original query
            entities: Last known entities
            
        Returns:
            Query with simple entity substitution
        """
        rewritten = query
        
        # Replace common references
        if entities.get("city") and ("there" in query.lower() or "that city" in query.lower()):
            rewritten = rewritten.replace("there", f"in {entities['city']}")
            rewritten = rewritten.replace("There", f"In {entities['city']}")
            rewritten = rewritten.replace("that city", entities['city'])
        
        if entities.get("hotel_name") and ("that hotel" in query.lower() or "this hotel" in query.lower()):
            rewritten = rewritten.replace("that hotel", entities['hotel_name'])
            rewritten = rewritten.replace("this hotel", entities['hotel_name'])
        
        if entities.get("country") and "that country" in query.lower():
            rewritten = rewritten.replace("that country", entities['country'])
        
        return rewritten
    
    def _format_entities(self, entities: Dict[str, Any]) -> str:
        """Format entities dictionary for prompt"""
        if not entities:
            return "None"
        
        lines = []
        for key, value in entities.items():
            if value:
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines) if lines else "None"


if __name__ == "__main__":
    # Test query rewriter
    rewriter = QueryRewriter()
    
    # Test 1: Simple reference
    query1 = "What about 5-star hotels there?"
    entities1 = {"city": "Paris", "country": "France"}
    history1 = "User: Find hotels in Paris\nAssistant: I found 3 hotels in Paris."
    
    print("Test 1:")
    print(f"Original: {query1}")
    print(f"Rewritten: {rewriter.rewrite_with_context(query1, history1, entities1)}")
    
    # Test 2: No rewriting needed
    query2 = "Find hotels in Tokyo"
    print("\nTest 2:")
    print(f"Original: {query2}")
    print(f"Needs rewriting: {rewriter.needs_rewriting(query2)}")

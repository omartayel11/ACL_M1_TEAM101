"""
Intent Classifier for Graph-RAG Hotel Travel Assistant
Classifies user queries into one of 7 intent types using LLM-based classification
"""

from typing import Optional
from utils.llm_client import LLMClient


class IntentClassifier:
    """
    Classify user query into one of 7 intents using LLM.
    Strategy: Pure LLM-based classification with knowledge of available query types.
    """
    
    # 8 intent types (added Casual conversation)
    INTENTS = [
        "HotelSearch",
        "HotelRecommendation", 
        "ReviewLookup",
        "LocationQuery",
        "VisaQuestion",
        "AmenityFilter",
        "GeneralQuestionAnswering",
        "CasualConversation"  # New: for greetings and small talk
    ]
    
    # Map intents to available query types from query_library.py
    INTENT_QUERY_CAPABILITIES = {
        "HotelSearch": [
            "Find hotels by city name",
            "Find hotels by country",
            "Filter hotels by minimum rating threshold",
            "Filter hotels by star rating"
        ],
        "HotelRecommendation": [
            "Get top hotels for specific traveller type (Business, Couple, Family, Solo, Group)",
            "Get hotels by cleanliness score",
            "Get hotels by comfort score",
            "Get hotels by value for money",
            "Get hotels with best staff scores"
        ],
        "ReviewLookup": [
            "Get reviews by hotel name",
            "Get reviews by hotel ID"
        ],
        "LocationQuery": [
            "Get hotels with best location scores (optionally filtered by city)"
        ],
        "VisaQuestion": [
            "Check visa requirements between two countries",
            "Get travellers from country who stayed without visa"
        ],
        "AmenityFilter": [
            "Filter hotels by cleanliness score",
            "Filter hotels by comfort score", 
            "Filter hotels by value for money",
            "Filter hotels by staff scores"
        ],
        "GeneralQuestionAnswering": [
            "Get comprehensive details about a specific hotel"
        ]
    }
    
    def __init__(self):
        """
        Initialize LLM-based intent classifier
        """
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client for intent classification: {e}")
    
    def classify(self, query: str) -> str:
        """
        Classify user query into one of 7 intents using LLM
        
        Args:
            query: User query string
            
        Returns:
            Intent name (one of 7 types)
        """
        if not query or not query.strip():
            return "GeneralQuestionAnswering"
        
        intent = self._classify_by_llm(query)
        
        if intent and intent in self.INTENTS:
            return intent
        
        # Default fallback
        return "GeneralQuestionAnswering"
    
    def _classify_by_llm(self, query: str) -> Optional[str]:
        """
        LLM-based classification with knowledge of query library capabilities
        
        Args:
            query: User query string
            
        Returns:
            Intent name or None if LLM call fails
        """
        try:
            # Build capabilities description from query library
            capabilities_desc = ""
            for intent, capabilities in self.INTENT_QUERY_CAPABILITIES.items():
                capabilities_desc += f"\n{intent}:\n"
                for cap in capabilities:
                    capabilities_desc += f"  - {cap}\n"
            
            prompt = f"""You are an intent classifier. Classify this query into ONE category.

Categories:
1. HotelSearch - Finding hotels in a city/country
   Examples: "hotels in Cairo", "find hotels in Paris", "show me hotels in Egypt"

2. HotelRecommendation - Asking for best/top hotels by traveler type
   Examples: "best hotels for couples", "top hotels for families", "recommended hotels for business travelers"

3. ReviewLookup - Requesting reviews/feedback for hotels
   Examples: "reviews for Hilton", "what do guests say about this hotel", "show me feedback"

4. LocationQuery - Asking about location scores/quality
   Examples: "hotels with best location score", "which hotels have good location", "find hotels with best location"

5. VisaQuestion - Visa requirements between countries
   Examples: "do I need visa from USA to France", "visa requirements from Egypt to UK"

6. AmenityFilter - Filtering by quality scores (cleanliness, comfort, value, staff)
   Examples: "hotels with high cleanliness", "best comfort score", "good value for money"

7. CasualConversation - Greetings, bot capabilities, small talk
   Examples: "hi", "what can you do", "thank you", "goodbye"

8. GeneralQuestionAnswering - Everything else

MATCHING RULES:
- City/country + hotels = HotelSearch
- "best"/"top" + traveler type (couples/families/business) = HotelRecommendation
- "location score"/"best location" = LocationQuery
- "reviews"/"feedback"/"ratings" = ReviewLookup
- Cleanliness/comfort/value/staff scores = AmenityFilter

Query: "{query}"

Answer with ONLY the category name (e.g., "LocationQuery")."""

            response = self.llm_client.generate(prompt, temperature=0.0, max_tokens=50)
            
            # Extract intent from response
            intent = response.strip().strip('"').strip("'")
            
            # Validate intent is one of the 7 types
            if intent in self.INTENTS:
                return intent
            
            # Try to find intent in response if LLM added explanation
            for valid_intent in self.INTENTS:
                if valid_intent in response:
                    return valid_intent
            
            return None
            
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            return None
    
    def get_available_intents(self) -> list:
        """Get list of all available intent types"""
        return self.INTENTS.copy()


# Test the classifier
if __name__ == "__main__":
    print("Testing LLM-based Intent Classifier\n")
    print("Note: This classifier uses the query library structure from query_library.py")
    print("Supporting 15 Cypher query templates across 7 intent categories\n")
    
    classifier = IntentClassifier()
    
    test_queries = [
        "Find hotels in Paris",
        "What are the best hotels for families?",
        "Show me reviews for Hotel California",
        "Which hotels have the best location in London?",
        "Do I need a visa to travel from USA to France?",
        "Hotels with cleanliness score above 8",
        "Tell me about accommodation options"
    ]
    
    print("=== Intent Classifier Test ===\n")
    for query in test_queries:
        intent = classifier.classify(query)
        print(f"Query: {query}")
        print(f"Intent: {intent}\n")

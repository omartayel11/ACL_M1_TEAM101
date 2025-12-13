"""
Intent Classifier for Graph-RAG Hotel Travel Assistant
Classifies user queries into one of 7 intent types using hybrid rule-based + LLM classification
"""

from typing import Optional, Tuple
import re
from utils.llm_client import LLMClient


class IntentClassifier:
    """
    Classify user query into one of 7 intents using hybrid approach.
    Strategy: Rule-based pre-classification for high-confidence cases, LLM for ambiguous queries.
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
    
    # Rule-based patterns and weights for confidence calculation
    EXACT_MATCHES = {
        "CasualConversation": {"hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye", "help"}
    }
    
    KEYWORD_WEIGHTS = {
        "VisaQuestion": {
            "visa": 0.6,
            "travel document": 0.5,
            "passport": 0.3
        },
        "LocationQuery": {
            "location score": 0.7,
            "location rating": 0.7,
            "best location": 0.6,
            "good location": 0.5
        },
        "AmenityFilter": {
            "cleanliness": 0.5,
            "comfort": 0.5,
            "staff": 0.5,
            "value for money": 0.5,
            "value": 0.4
        },
        "HotelSearch": {
            "hotels in": 0.6,
            "find hotels": 0.6,
            "rating above": 0.5,
            "star": 0.3
        },
        "ReviewLookup": {
            "review": 0.5,
            "feedback": 0.5,
            "what do guests say": 0.7
        },
        "HotelRecommendation": {
            "couples": 0.5,
            "families": 0.5,
            "business": 0.5,
            "solo": 0.5,
            "for": 0.2
        }
    }
    
    PATTERNS = {
        "VisaQuestion": [
            (r'\bfrom\s+\w+\s+to\s+\w+\b', 0.4),
        ],
        "ReviewLookup": [
            (r'\breview(?:s)?\s+(?:for|of|about)\s+', 0.7),
            (r'\bfeedback\s+(?:for|about)\s+', 0.6),
        ],
        "HotelRecommendation": [
            (r'\b(?:best|top)\s+(?:hotels?\s+)?for\s+(couples?|families|business|solo)', 0.9),
        ],
        "HotelSearch": [
            (r'\brating\s+above\s+[\d.]+', 0.8),
            (r'\b\d+[- ]star\b', 0.7),
        ]
    }
    
    # Negative indicators - if these appear, reduce confidence for that intent
    NEGATIVE_INDICATORS = {
        "LocationQuery": ["cleanliness", "comfort", "staff", "value"],
        "HotelSearch": ["review", "feedback"],
    }
    
    def __init__(self):
        """
        Initialize hybrid intent classifier with rule-based and LLM components
        """
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client for intent classification: {e}")
    
    def classify(self, query: str) -> str:
        """
        Classify user query using hybrid approach: rule-based first, then LLM if needed
        
        Args:
            query: User query string
            
        Returns:
            Intent name (one of 7 types)
        """
        if not query or not query.strip():
            return "GeneralQuestionAnswering"
        
        # Stage 1: Try rule-based classification
        rule_intent, confidence = self._classify_by_rules(query)
        
        # High confidence (>= 0.9) - use rule result directly
        if confidence >= 0.9:
            return rule_intent
        
        # Medium confidence (0.5-0.9) - use LLM with hint
        if confidence >= 0.5:
            intent = self._classify_by_llm(query, hint_intent=rule_intent, hint_confidence=confidence)
            if intent and intent in self.INTENTS:
                return intent
            # LLM failed, use rule result
            return rule_intent
        
        # Low confidence (< 0.5) - pure LLM classification
        intent = self._classify_by_llm(query)
        if intent and intent in self.INTENTS:
            return intent
        
        # All failed - use rule result if available, otherwise fallback
        if rule_intent:
            return rule_intent
        return "GeneralQuestionAnswering"
    
    def _classify_by_rules(self, query: str) -> Tuple[Optional[str], float]:
        """
        Rule-based classification with confidence scoring
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (intent, confidence) where confidence is 0.0-1.0
        """
        query_lower = query.lower().strip()
        intent_scores = {}
        
        # Check exact matches first
        for intent, matches in self.EXACT_MATCHES.items():
            if query_lower in matches:
                return (intent, 1.0)
        
        # Check keyword weights
        for intent, keywords in self.KEYWORD_WEIGHTS.items():
            score = 0.0
            for keyword, weight in keywords.items():
                if keyword in query_lower:
                    score += weight
            if score > 0:
                intent_scores[intent] = min(score, 1.0)
        
        # Check pattern matches
        for intent, patterns in self.PATTERNS.items():
            for pattern, weight in patterns:
                if re.search(pattern, query_lower):
                    current_score = intent_scores.get(intent, 0.0)
                    intent_scores[intent] = max(current_score, weight)
        
        # Apply negative indicators
        for intent, negative_words in self.NEGATIVE_INDICATORS.items():
            if intent in intent_scores:
                for neg_word in negative_words:
                    if neg_word in query_lower:
                        intent_scores[intent] = max(0.0, intent_scores[intent] - 0.3)
        
        # No matches found
        if not intent_scores:
            return (None, 0.0)
        
        # Get best match
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]
        
        # Check for conflicts (multiple similar scores)
        sorted_scores = sorted(intent_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            if sorted_scores[0] - sorted_scores[1] < 0.3:
                # Close competition, reduce confidence
                best_score = max(0.3, best_score - 0.3)
        
        return (best_intent, best_score)
    
    def _classify_by_llm(self, query: str, hint_intent: Optional[str] = None, hint_confidence: Optional[float] = None) -> Optional[str]:
        """
        LLM-based classification with optional rule-based hints
        
        Args:
            query: User query string
            hint_intent: Optional intent suggestion from rules
            hint_confidence: Optional confidence score from rules
            
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
            
            # Add hint information if provided
            hint_text = ""
            if hint_intent and hint_confidence:
                hint_text = f"\n\nNOTE: Rule-based pre-classification suggests '{hint_intent}' with {hint_confidence:.0%} confidence. Consider this hint but make your own judgment based on the full query context.\n"
            
            prompt = f"""You are an intent classifier. Classify this query into ONE category.{hint_text}

Categories:
1. HotelSearch - Finding hotels in a city/country OR filtering by rating/stars
   Examples: "hotels in Cairo", "find hotels in Paris", "show me hotels in Egypt", "hotels with rating above 8", "highly rated hotels", "5-star hotels"

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
- Rating/stars + hotels = HotelSearch (e.g., "rating above 8", "highly rated", "5-star")
- "best"/"top" + traveler type (couples/families/business) = HotelRecommendation
- "location score"/"best location" = LocationQuery
- "reviews"/"feedback"/"ratings" = ReviewLookup
- Cleanliness/comfort/value/staff scores = AmenityFilter

- IMPORTANT: Do NOT classify based on literal example matching. Always classify based on the meaning (semantics) of the query, even if wording, phrasing, synonyms, or structure are different. Consider paraphrases and similar intent patterns.
- ANY query involving cleanliness score, comfort score, value for money score, staff score, or any hotel quality metric MUST be classified as AmenityFilter, even if phrasing or wording is different (e.g., "high comfort score", "good value", "great staff reviews", "value for money", "good comfort"). This ALWAYS maps to AmenityFilter.


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
    print("=" * 80)
    print("HYBRID INTENT CLASSIFIER TEST")
    print("=" * 80)
    print("This classifier uses a two-stage approach:")
    print("  1. Rule-based pre-classification (keywords, patterns, exact matches)")
    print("  2. LLM classification (for ambiguous cases or as fallback)")
    print("\nConfidence Thresholds:")
    print("  • High (≥0.9): Use rule result immediately")
    print("  • Medium (0.5-0.9): Use LLM with hint from rules")
    print("  • Low (<0.5): Pure LLM classification")
    print("=" * 80)
    print()
    
    classifier = IntentClassifier()
    
    test_queries = [
        "Find hotels in Paris",
        "What are the best hotels for families?",
        "Show me reviews for Hotel California",
        "Which hotels have the best location in London?",
        "Do I need a visa to travel from USA to France?",
        "Hotels with cleanliness score above 8",
        "Tell me about accommodation options",
        "good value for money",
        "i need hotels with good value for money",
        "i need hotels with high cleanliness",
        "i need hotels with high cleanliness scores",
        "i need hotels with high comfort score",
        "find hoteks in cairo"  # Typo test
    ]
    
    print(f"Testing {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"TEST CASE #{i}")
        print("=" * 80)
        print(f"Query: \"{query}\"")
        print()
        
        # Get rule-based classification with details
        rule_intent, confidence = classifier._classify_by_rules(query)
        
        print("📊 STAGE 1: Rule-Based Classification")
        print("-" * 80)
        if rule_intent:
            print(f"  Rule Intent: {rule_intent}")
            print(f"  Confidence: {confidence:.2f} ({confidence*100:.0f}%)")
            
            # Determine what happens next
            if confidence >= 0.9:
                print(f"  Decision: ✅ HIGH CONFIDENCE - Use rule result immediately")
            elif confidence >= 0.5:
                print(f"  Decision: ⚠️  MEDIUM CONFIDENCE - Consult LLM with hint")
            else:
                print(f"  Decision: ❌ LOW CONFIDENCE - Pure LLM classification")
        else:
            print(f"  Rule Intent: None")
            print(f"  Confidence: 0.00 (0%)")
            print(f"  Decision: ❌ NO MATCH - Pure LLM classification")
        print()
        
        # Get final classification
        print("🤖 STAGE 2: LLM Classification")
        print("-" * 80)
        
        if confidence >= 0.9:
            print(f"  Skipped (high confidence in rules)")
            final_intent = rule_intent
        elif confidence >= 0.5:
            print(f"  Mode: LLM with hint ('{rule_intent}' @ {confidence:.0%})")
            final_intent = classifier._classify_by_llm(query, hint_intent=rule_intent, hint_confidence=confidence)
            if final_intent:
                print(f"  LLM Result: {final_intent}")
            else:
                print(f"  LLM Result: Failed - using rule result")
                final_intent = rule_intent
        else:
            print(f"  Mode: Pure LLM (no hints)")
            final_intent = classifier._classify_by_llm(query)
            if final_intent:
                print(f"  LLM Result: {final_intent}")
            else:
                print(f"  LLM Result: Failed - using fallback")
                final_intent = rule_intent if rule_intent else "GeneralQuestionAnswering"
        print()
        
        print("✨ FINAL CLASSIFICATION")
        print("-" * 80)
        print(f"  Intent: {final_intent}")
        print(f"  Source: {'Rules' if confidence >= 0.9 else 'LLM with hint' if confidence >= 0.5 else 'LLM'}")
        print()
        print()

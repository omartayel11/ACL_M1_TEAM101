"""
Entity Extractor for Graph-RAG Hotel Travel Assistant
Extracts structured entities from user queries using LLM
"""

from typing import Dict, Any, Optional
from utils.llm_client import LLMClient


class EntityExtractor:
    """
    Extract structured entities from user queries.
    Uses LLM with structured output based on intent.
    """
    
    # Valid values for entity validation
    TRAVELLER_TYPES = ["Business", "Couple", "Family", "Solo", "Group"]
    
    def __init__(self, debug: bool = False):
        """Initialize entity extractor
        
        Args:
            debug: If True, print LLM responses for debugging
        """
        self.debug = debug
        try:
            self.llm_client = LLMClient()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM client for entity extraction: {e}")
    
    def extract(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from query based on intent
        
        Args:
            query: User query string
            intent: Classified intent
            
        Returns:
            Dictionary of extracted entities
        """
        if not query or not query.strip():
            return {}
        
        # Use LLM to extract entities
        entities = self._extract_with_llm(query, intent)
        
        # Validate and normalize entities
        entities = self._validate_entities(entities)
        
        return entities
    
    def _extract_with_llm(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Use LLM to extract entities with intent-specific guidance
        
        Args:
            query: User query string
            intent: Classified intent
            
        Returns:
            Dictionary of extracted entities
        """
        # Build intent-specific entity schema
        schema = self._get_entity_json_schema_for_intent(intent)
        
        prompt = f"""Extract entities from this hotel query: "{query}"

Intent: {intent}

Instructions:
- Extract ONLY entities explicitly mentioned
- Use null for missing values
- For traveller types: use singular form (Family not families, Couple not couples)
- For scores: extract numeric values mentioned (e.g., "above 8.5" → 8.5)
- Score types: cleanliness, comfort, value, staff, location, facilities

Extract the entities now."""

        try:
            # Use structured generation for better JSON output
            entities = self.llm_client.generate_structured(prompt, schema, temperature=0.0)
            
            if self.debug:
                print(f"DEBUG - Extracted entities: {entities}")
            
            return entities if entities else {}
            
        except Exception as e:
            if self.debug:
                print(f"DEBUG - LLM extraction failed: {e}")
            # Return empty dict on failure - LLM only, no fallback
            return {}
    
    def _get_entity_json_schema_for_intent(self, intent: str) -> Dict[str, str]:
        """Get JSON schema for structured extraction based on intent"""
        schemas = {
            "HotelSearch": {
                "city": "string or null",
                "country": "string or null",
                "min_rating": "number or null",
                "star_rating": "number or null",
                "limit": "number or null"
            },
            "HotelRecommendation": {
                "traveller_type": "string or null",
                "min_cleanliness": "number or null",
                "min_comfort": "number or null",
                "min_value": "number or null",
                "city": "string or null",
                "limit": "number or null"
            },
            "ReviewLookup": {
                "hotel_name": "string or null",
                "hotel_id": "string or null",
                "limit": "number or null"
            },
            "LocationQuery": {
                "city": "string or null",
                "limit": "number or null"
            },
            "VisaQuestion": {
                "from_country": "string or null",
                "to_country": "string or null"
            },
            "AmenityFilter": {
                "min_cleanliness": "number or null",
                "min_comfort": "number or null",
                "min_value": "number or null",
                "min_staff": "number or null",
                "min_location": "number or null",
                "min_facilities": "number or null",
                "limit": "number or null"
            },
            "GeneralQuestionAnswering": {
                "hotel_name": "string or null",
                "city": "string or null",
                "country": "string or null"
            }
        }
        return schemas.get(intent, {})
    
    def _validate_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize extracted entities"""
        validated = {}
        
        for key, value in entities.items():
            if value is None or value == "null" or value == "":
                continue
            
            # Normalize traveller type
            if key == "traveller_type":
                value = str(value).capitalize()
                # Handle plural forms
                if value == "Families":
                    value = "Family"
                elif value == "Couples":
                    value = "Couple"
                if value in self.TRAVELLER_TYPES:
                    validated[key] = value
            
            # Convert numeric fields
            elif key in ["min_rating", "star_rating", "min_cleanliness", "min_comfort", 
                        "min_value", "min_staff", "min_location", "min_facilities"]:
                try:
                    validated[key] = float(value)
                except (ValueError, TypeError):
                    pass
            
            # Convert limit to int
            elif key == "limit":
                try:
                    validated[key] = int(value)
                except (ValueError, TypeError):
                    validated[key] = 10  # Default
            
            # String fields - just clean whitespace
            else:
                validated[key] = str(value).strip()
        
        return validated


if __name__ == "__main__":
    # Test entity extractor
    extractor = EntityExtractor(debug=True)  # Enable debug mode
    
    print("=== Entity Extractor Test ===\n")
    
    test_cases = [
        ("Find hotels in Paris", "HotelSearch"),
        ("Best hotels for families in London", "HotelRecommendation"),
        ("Show me reviews for Hotel California", "ReviewLookup"),
        ("Hotels with location score above 8.5", "AmenityFilter"),
        ("Do I need a visa from USA to France?", "VisaQuestion")
    ]
    
    for query, intent in test_cases:
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        entities = extractor.extract(query, intent)
        print(f"Entities: {entities}\n")

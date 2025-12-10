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
    
    # Valid cities from hotels.csv
    VALID_CITIES = [
        "New York", "London", "Paris", "Tokyo", "Dubai", "Singapore", "Sydney",
        "Rio de Janeiro", "Berlin", "Toronto", "Shanghai", "Mexico City", "Mumbai",
        "Rome", "Cape Town", "Seoul", "Moscow", "Cairo", "Barcelona", "Bangkok",
        "Istanbul", "Amsterdam", "Buenos Aires", "Lagos", "Wellington"
    ]
    
    # Valid countries from hotels.csv
    VALID_COUNTRIES = [
        "United States", "United Kingdom", "France", "Japan", "United Arab Emirates",
        "Singapore", "Australia", "Brazil", "Germany", "Canada", "China", "Mexico",
        "India", "Italy", "South Africa", "South Korea", "Russia", "Egypt", "Spain",
        "Thailand", "Turkey", "Netherlands", "Argentina", "Nigeria", "New Zealand"
    ]
    
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
- If query mentions "me and my wife/husband/partner", set traveller_type to "Couple"
- For scores: extract numeric values mentioned (e.g., "above 8.5" → 8.5)
- If user says "high" without a specific number, use 8.0 as the threshold
- If user says "good" or "best" without a number, use 7.5 as the threshold
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
            
            # Validate and normalize city names
            elif key == "city":
                normalized_city = self._normalize_city(str(value).strip())
                if normalized_city:
                    validated[key] = normalized_city
            
            # Validate and normalize country names
            elif key in ["country", "from_country", "to_country"]:
                normalized_country = self._normalize_country(str(value).strip())
                if normalized_country:
                    validated[key] = normalized_country
            
            # Other string fields - just clean whitespace
            else:
                validated[key] = str(value).strip()
        
        return validated
    
    def _normalize_city(self, city_input: str) -> Optional[str]:
        """
        Normalize city name to match valid cities from database.
        Uses fuzzy matching to handle typos and variations.
        
        Args:
            city_input: User's city input (may have typos)
            
        Returns:
            Normalized city name or None if no match
        """
        if not city_input:
            return None
        
        city_lower = city_input.lower().strip()
        
        # Exact match (case-insensitive)
        for valid_city in self.VALID_CITIES:
            if city_lower == valid_city.lower():
                return valid_city
        
        # Fuzzy match: check if input is contained in valid city or vice versa
        for valid_city in self.VALID_CITIES:
            valid_lower = valid_city.lower()
            # Handle common patterns: "new york" matches "New York", "rio" matches "Rio de Janeiro"
            if city_lower in valid_lower or valid_lower in city_lower:
                return valid_city
        
        # No match found - return title case version as fallback
        return city_input.title()
    
    def _normalize_country(self, country_input: str) -> Optional[str]:
        """
        Normalize country name to match valid countries from database.
        Uses fuzzy matching to handle typos and variations.
        
        Args:
            country_input: User's country input (may have typos)
            
        Returns:
            Normalized country name or None if no match
        """
        if not country_input:
            return None
        
        country_lower = country_input.lower().strip()
        
        # Exact match (case-insensitive)
        for valid_country in self.VALID_COUNTRIES:
            if country_lower == valid_country.lower():
                return valid_country
        
        # Fuzzy match: check if input is contained in valid country or vice versa
        for valid_country in self.VALID_COUNTRIES:
            valid_lower = valid_country.lower()
            if country_lower in valid_lower or valid_lower in country_lower:
                return valid_country
        
        # Common aliases
        aliases = {
            "usa": "United States",
            "america": "United States",
            "us": "United States",
            "uk": "United Kingdom",
            "uae": "United Arab Emirates",
            "korea": "South Korea",
            "south korea": "South Korea"
        }
        
        if country_lower in aliases:
            return aliases[country_lower]
        
        # No match found - return title case version as fallback
        return country_input.title()


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

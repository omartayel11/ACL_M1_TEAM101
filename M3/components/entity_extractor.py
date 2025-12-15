"""
Entity Extractor for Graph-RAG Hotel Travel Assistant
Extracts structured entities from user queries using LLM
"""

import re
import difflib
from typing import Dict, Any, Optional, List, Tuple
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
    
    # Valid hotels - will be populated from database at runtime
    VALID_HOTELS = []
    
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
        
        # Load valid hotels from database on first initialization
        # This helps with fuzzy matching for hotel names
        if not EntityExtractor.VALID_HOTELS:
            self._load_valid_hotels()
    
    def _load_valid_hotels(self):
        """Load valid hotel names from the database"""
        try:
            from utils.config_loader import ConfigLoader
            from neo4j import GraphDatabase
            config = ConfigLoader()
            uri = config.get('neo4j.uri')
            username = config.get('neo4j.username')
            password = config.get('neo4j.password')
            
            if not uri or not username or not password:
                print(f"⚠ Neo4j configuration incomplete, skipping hotel list loading")
                EntityExtractor.VALID_HOTELS = []
                return
            
            driver = GraphDatabase.driver(uri, auth=(username, password))
            with driver.session() as session:
                result = session.run("MATCH (h:Hotel) RETURN h.name AS name ORDER BY h.name")
                EntityExtractor.VALID_HOTELS = [record["name"] for record in result if record["name"]]
                print(f"✓ Successfully loaded {len(EntityExtractor.VALID_HOTELS)} hotel names from database")
                if self.debug and EntityExtractor.VALID_HOTELS:
                    print(f"  Sample hotels: {EntityExtractor.VALID_HOTELS[:5]}")
            driver.close()
        except Exception as e:
            print(f"⚠ Could not load hotel names from database: {e}")
            EntityExtractor.VALID_HOTELS = []
    
    def extract(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from query based on intent using hybrid approach:
        Rule-based first → LLM with hint (like intent classifier)
        
        Args:
            query: User query string
            intent: Classified intent
            
        Returns:
            Dictionary of extracted entities
        """
        if not query or not query.strip():
            return {}
        
        # Stage 1: Rule-based extraction with confidence scoring
        rule_entities, confidence = self._extract_by_rules_with_confidence(query, intent)
        
        # High confidence (>= 0.9) - use rule results directly (only very obvious patterns)
        if confidence >= 0.9:
            validated = self._validate_entities(rule_entities)
            return validated
        
        # Medium confidence (0.5-0.9) - use LLM with hint from rules
        if confidence >= 0.5:
            llm_entities = self._extract_with_llm(query, intent, hint_entities=rule_entities, hint_confidence=confidence)
            # Merge: rule results first, LLM only adds/overrides non-None values
            merged = {**rule_entities}
            if llm_entities:
                for key, value in llm_entities.items():
                    if value is not None and value != "null":
                        merged[key] = value
            validated = self._validate_entities(merged)
            return validated
        
        # Low confidence (< 0.5) - pure LLM extraction
        llm_entities = self._extract_with_llm(query, intent)
        validated = self._validate_entities(llm_entities) if llm_entities else {}
        return validated
    
    def _extract_by_rules_with_confidence(self, query: str, intent: str) -> tuple:
        """
        Rule-based extraction with confidence scoring
        Returns both entities AND confidence score (0.0-1.0)
        
        Args:
            query: User query string
            intent: Classified intent
            
        Returns:
            Tuple of (entities_dict, confidence_score)
        """
        entities = {}
        confidence_scores = []
        query_lower = query.lower()
        
        # Extract traveller type (solo, couple, family, business, group)
        # Lower confidence to let LLM help with ambiguous cases
        traveller_patterns = [
            (r'as a (solo|couple|family|business|group)', 0.85),
            (r'as (solo|couple|family|business|group)', 0.75),
            (r'for (families|couples|groups|business|solo)', 0.8),  # "for families", "for couples"
            (r'(solo|couple|family|business|group)\s+(?:traveler|traveller|trip)', 0.7),
            (r'(solo|couple|family|business|group)\s+(?:travelers?|travellers?)', 0.65),
            (r'or as a (solo|couple|family|business|group)', 0.8),
        ]
        for pattern, pattern_conf in traveller_patterns:
            match = re.search(pattern, query_lower)
            if match:
                traveller_type = match.group(1).strip()
                # Map plural forms to singular
                type_map = {
                    'families': 'Family',
                    'couples': 'Couple',
                    'groups': 'Group',
                    'business': 'Business',
                    'solo': 'Solo'
                }
                # Handle both singular and plural
                normalized = type_map.get(traveller_type.lower(), traveller_type.capitalize())
                if normalized in self.TRAVELLER_TYPES:
                    entities["traveller_type"] = normalized
                    confidence_scores.append(pattern_conf)
                    break
        
        # Extract star rating (5 star, 4 star hotels)
        star_patterns = [
            (r'(\d)\s*star\s+hotel', 0.85),
            (r'(\d)\s*star', 0.8),
        ]
        for pattern, pattern_conf in star_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    star_rating = float(match.group(1))
                    if 1.0 <= star_rating <= 5.0:
                        entities["star_rating"] = star_rating
                        confidence_scores.append(pattern_conf)
                        break
                except ValueError:
                    pass
        
        # Extract reference hotel (similar to X hotel)
        similar_pattern = r'similar\s+(?:to|with)\s+(?:(?:the|a)\s+)?([^,\n]+?)(?:\s+(?:in|from|for|that|which|where)|$)'
        match = re.search(similar_pattern, query_lower)
        if match:
            hotel_name = match.group(1).strip()
            hotel_name = re.sub(r'\s+(?:in|from|for|hotel)?$', '', hotel_name)
            if hotel_name and len(hotel_name) > 2:
                entities["reference_hotel"] = hotel_name
                confidence_scores.append(0.95)
        
        # Extract visa-related entities (from_country and to_country)
        # Check for visa patterns first (they're more specific)
        visa_patterns = [
            (r'(?:visa|viza)\s+(?:from|requirements from|needed? from|required from)\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|\?|\.|$)', 0.95),
            (r'(?:from|I\'m from)\s+([A-Za-z\s]+?)(?:,|\s+).*(?:visa|viza)\s+(?:for|to)\s+([A-Za-z\s]+?)(?:\s|\?|\.|$)', 0.9),
            (r'do\s+([A-Za-z]+?)s?\s+need\s+(?:visa|viza)\s+for\s+([A-Za-z\s]+?)(?:\s|\?|\.|$)', 0.9),
        ]
        for pattern, pattern_conf in visa_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                from_country = match.group(1).strip()
                to_country = match.group(2).strip()
                if from_country and to_country:
                    # Normalize country names (e.g., "Americans" -> "United States")
                    from_country_normalized = self._normalize_country_name(from_country)
                    to_country_normalized = self._normalize_country_name(to_country)
                    entities["from_country"] = from_country_normalized
                    entities["to_country"] = to_country_normalized
                    confidence_scores.append(pattern_conf)
                    break
        
        # Extract from_country (travelers from X country / popular among X people) - only if not already extracted from visa
        if "from_country" not in entities:
            from_country_patterns = [
                (r'popular\s+among\s+(?:travelers?|guests?|people)\s+from\s+([A-Za-z\s]+?)(?:\s+to|\s+in|[\?\.]|$)', 0.85),
            ]
            for pattern, pattern_conf in from_country_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    country_name = match.group(1).strip()
                    if country_name and len(country_name) >= 2:
                        entities["from_country"] = country_name
                        confidence_scores.append(pattern_conf)
                        break
        
        # Extract city/country name (in X, go to X, visit X)
        # Skip if this is a visa query or review query
        if "to_country" not in entities and "visa" not in query_lower and "review" not in query_lower:
            location_patterns = [
                (r'(?:hotels?|accommodations?)\s+in\s+([a-zA-Z\s]+?)(?:\s+(?:with|and|or|for|,)|[,?!.]|$)', 0.85),
                (r'\sin\s+([a-zA-Z\s]+?)(?:\s+(?:with|and|or|for|,)|[,?!.]|$)', 0.75),
                (r'(?:go|travel|visit|explore)\s+to\s+([a-zA-Z\s]+?)(?:\s+(?:and|or|with|,)|[,?!.]|$)', 0.8),
            ]
            for pattern, pattern_conf in location_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    location_name = match.group(1).strip()
                    # Clean up common noise words
                    location_name = re.sub(r'\s+(and|or|with|the|a)$', '', location_name)
                    if location_name and len(location_name) >= 3:
                        # Normalize to title case
                        location_name = location_name.title()
                        
                        # Check if it's a known country first
                        if location_name in self.VALID_COUNTRIES or self._normalize_country_name(location_name) in self.VALID_COUNTRIES:
                            entities["country"] = self._normalize_country_name(location_name)
                            confidence_scores.append(pattern_conf)
                        else:
                            # Assume it's a city
                            entities["city"] = location_name
                            confidence_scores.append(pattern_conf * 0.9)  # Slightly lower confidence for cities
                        break
        
        # Extract quality dimensions with numeric thresholds for AmenityFilter/GeneralQuestionAnswering
        if intent in ["AmenityFilter", "GeneralQuestionAnswering"]:
            quality_matches = []
            extracted_numbers = set()  # Track which numbers we've used
            
            # Look for patterns like "cleanliness more than 8" or "cleanliness above 8.5" or "cleanliness score 9.2"
            cleanliness_pattern = r'(?:cleanliness|clean)\s+(?:score\s+)?(?:more than|above|greater than|at least|minimum|of)?\s*([\d.]+)'
            match = re.search(cleanliness_pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    entities["min_cleanliness"] = value
                    extracted_numbers.add(value)
                    quality_matches.append(0.85)  # Lower confidence
                except ValueError:
                    pass
            
            comfort_pattern = r'(?:comfort|comfortable)\s+(?:score\s+)?(?:more than|above|greater than|at least|minimum|of)?\s*([\d.]+)'
            match = re.search(comfort_pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    entities["min_comfort"] = value
                    extracted_numbers.add(value)
                    quality_matches.append(0.85)
                except ValueError:
                    pass
            
            # Improved staff pattern - must include 'staff' keyword
            staff_pattern = r'(?:staff|service)\s+(?:score\s+)?(?:more than|above|greater than|at least|minimum|of)?\s*([\d.]+)'
            # Also check for 'friendly staff score X' pattern
            staff_pattern_2 = r'(?:friendly|helpful|good|excellent)\s+(?:staff|service)\s+(?:score\s+)?(?:more than|above|at least)?\s*([\d.]+)'
            match = re.search(staff_pattern, query_lower)
            if not match:
                match = re.search(staff_pattern_2, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    entities["min_staff"] = value
                    extracted_numbers.add(value)
                    quality_matches.append(0.85)
                except ValueError:
                    pass
        
            value_pattern = r'(?:value|affordable)\s+(?:score\s+)?(?:more than|above|greater than|at least|minimum|of)?\s*([\d.]+)'
            match = re.search(value_pattern, query_lower)
            if match:
                try:
                    value = float(match.group(1))
                    entities["min_value"] = value
                    extracted_numbers.add(value)
                    quality_matches.append(0.85)
                except ValueError:
                    pass
            
            # Special handling for "good value for money" without number
            if 'value for money' in query_lower or ('value' in query_lower and 'good' in query_lower):
                if "min_value" not in entities:
                    entities["min_value"] = 7.5
                    quality_matches.append(0.8)
            
            if 'balanced' in query_lower or 'balance' in query_lower or 'all dimensions' in query_lower or 'across all' in query_lower or 'all the scores' in query_lower:
                entities["balanced"] = True
                quality_matches.append(0.95)
            
            # Add quality match confidence
            if quality_matches:
                confidence_scores.append(max(quality_matches))
        
        # Extract trend signals
        if 'trend' in query_lower or 'improving' in query_lower or 'getting better' in query_lower or 'improve' in query_lower:
            entities["is_trending"] = True
            confidence_scores.append(0.9)
        
        # Extract rating (with, above, rating X) - but ONLY if not already extracted quality dimensions
        # This must come AFTER quality extraction to avoid conflicts
        if not any(key in entities for key in ["min_cleanliness", "min_comfort", "min_staff", "min_value"]):
            rating_patterns = [
                (r'(?:rating|rated|ratng)\s+(?:of\s+)?([\d.]+)', 0.95),  # 'ratng' typo support
                (r'with\s+(?:rating|ratng)\s+([\d.]+)', 0.95),
                (r'(?:rating|ratng)\s+(?:above|more than|at least)\s+([\d.]+)', 0.9),
            ]
            for pattern, pattern_conf in rating_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Skip if quality dimension keywords are present
                    if any(word in query_lower for word in ['staff', 'service', 'friendly', 'cleanliness', 'clean', 'comfort', 'value', 'affordable']):
                        continue
                    try:
                        rating_value = float(match.group(1))
                        # Only extract if this number wasn't already used for quality dimensions
                        if "extracted_numbers" in locals() and rating_value not in extracted_numbers:
                            entities["min_rating"] = rating_value
                            confidence_scores.append(pattern_conf)
                            break
                        elif "extracted_numbers" not in locals():
                            # If we haven't extracted quality dimensions, we can use this
                            entities["min_rating"] = rating_value
                            confidence_scores.append(pattern_conf)
                            break
                    except ValueError:
                        pass
        
        # Calculate overall confidence
        if not confidence_scores:
            overall_confidence = 0.0
        else:
            # Average confidence, but weight towards high confidence
            avg_conf = sum(confidence_scores) / len(confidence_scores)
            # Boost slightly for multiple matches
            if len(confidence_scores) > 1:
                avg_conf = min(1.0, avg_conf + 0.1)
            overall_confidence = avg_conf
        
        return entities, overall_confidence
    
    def _extract_with_llm(self, query: str, intent: str, hint_entities: Dict[str, Any] = None, hint_confidence: float = None) -> Dict[str, Any]:
        """
        Route to intent-specific LLM extraction function.
        Each intent has its own focused prompt and schema.
        
        Args:
            query: User query string
            intent: Classified intent
            hint_entities: Optional entities extracted from rules
            hint_confidence: Optional confidence score from rules
            
        Returns:
            Dictionary of extracted entities
        """
        # Route to intent-specific extraction
        extractors = {
            "HotelSearch": self._extract_hotel_search_llm,
            "HotelRecommendation": self._extract_hotel_recommendation_llm,
            "ReviewLookup": self._extract_review_lookup_llm,
            "VisaQuestion": self._extract_visa_question_llm,
            "AmenityFilter": self._extract_amenity_filter_llm,
            "GeneralQuestionAnswering": self._extract_general_qa_llm,
        }
        
        extractor_func = extractors.get(intent)
        if not extractor_func:
            # Fallback for unknown intents
            return {}
        
        try:
            return extractor_func(query, hint_entities, hint_confidence)
        except Exception as e:
            if self.debug:
                print(f"DEBUG - LLM extraction failed for {intent}: {e}")
            return {}
    
    def _extract_hotel_search_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for HotelSearch intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract location and filters from: "{query}"{hint_text}

Return JSON with:
- city: city name if mentioned (e.g., "Paris", "London")
- country: country name if no city specified
- min_rating: minimum rating if mentioned (e.g., "above 4.5" → 4.5)
- star_rating: star rating if mentioned (e.g., "5 star" → 5)
- limit: number of results if specified

Use null for missing values.'''

        schema = {
            "city": "string or null",
            "country": "string or null",
            "min_rating": "number or null",
            "star_rating": "number or null",
            "limit": "number or null"
        }
        
        return self._call_llm_structured(prompt, schema)
    
    def _extract_hotel_recommendation_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for HotelRecommendation intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract traveler preferences from: "{query}"{hint_text}

Return JSON with:
- traveller_type: "Family", "Couple", "Solo", "Business", or "Group" if mentioned
  (e.g., "honeymoon" → "Couple", "family trip" → "Family")
- reference_hotel: hotel name if asking for similar hotels
- from_country: country name if asking about travelers from a specific country
- city: city name if mentioned
- min_cleanliness/min_comfort/min_value: scores if quality mentioned (default 7.5 if just keyword)

Use null for missing values.'''

        schema = {
            "traveller_type": "string or null",
            "reference_hotel": "string or null",
            "from_country": "string or null",
            "min_cleanliness": "number or null",
            "min_comfort": "number or null",
            "min_value": "number or null",
            "city": "string or null"
        }
        
        return self._call_llm_structured(prompt, schema)
    
    def _extract_review_lookup_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for ReviewLookup intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract hotel name from: "{query}"{hint_text}

Return JSON with:
- hotel_name: name of the hotel if mentioned

Use null if no specific hotel mentioned.'''

        schema = {"hotel_name": "string or null"}
        return self._call_llm_structured(prompt, schema)
    
    def _extract_visa_question_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for VisaQuestion intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract visa-related countries from: "{query}"{hint_text}

Return JSON with:
- from_country: origin country (where person is from)
- to_country: destination country (where person wants to go)

Examples:
- "visa from USA to France" → from_country: "United States", to_country: "France"
- "do Americans need visa for Japan" → from_country: "United States", to_country: "Japan"

Use null for missing values.'''

        schema = {
            "from_country": "string or null",
            "to_country": "string or null"
        }
        
        return self._call_llm_structured(prompt, schema)
    
    def _extract_amenity_filter_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for AmenityFilter intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract quality scores and filters from: "{query}"{hint_text}

Return JSON with quality scores (extract actual numbers or use 7.5 for keywords):
- min_cleanliness: if "clean" or "cleanliness" mentioned
- min_comfort: if "comfort" or "comfortable" mentioned  
- min_staff: if "staff" or "service" mentioned
- min_value: if "value" or "affordable" mentioned
- city: city name if specified
- reference_hotel: hotel name if comparing to another hotel

Use null for missing values.'''

        schema = {
            "city": "string or null",
            "min_cleanliness": "number or null",
            "min_comfort": "number or null",
            "min_value": "number or null",
            "min_staff": "number or null",
            "reference_hotel": "string or null"
        }
        
        return self._call_llm_structured(prompt, schema)
    
    def _extract_general_qa_llm(self, query: str, hints: Dict = None, confidence: float = None) -> Dict:
        """Extract entities for GeneralQuestionAnswering intent"""
        hint_text = self._build_hint_text(hints, confidence) if hints else ""
        
        prompt = f'''Extract any relevant entities from: "{query}"{hint_text}

Return JSON (use null for missing):
- city/country: location if mentioned
- from_country: if asking about travelers from a country
- traveller_type: if asking about specific traveler types
- balanced: true if asking about balanced/consistent scores across dimensions
- is_trending: true if asking about improving/trending hotels
- reference_hotel: hotel name if mentioned
- min_cleanliness/min_comfort/min_staff/min_value: quality scores if mentioned

Use null for missing values.'''

        schema = {
            "city": "string or null",
            "country": "string or null",
            "from_country": "string or null",
            "traveller_type": "string or null",
            "balanced": "boolean or null",
            "is_trending": "boolean or null",
            "reference_hotel": "string or null",
            "min_cleanliness": "number or null",
            "min_comfort": "number or null",
            "min_staff": "number or null",
            "min_value": "number or null"
        }
        
        return self._call_llm_structured(prompt, schema)
    
    def _build_hint_text(self, hints: Dict, confidence: float) -> str:
        """Build hint text from rule-based extraction"""
        if not hints:
            return ""
        hints_str = ", ".join([f"{k}={v}" for k, v in hints.items()])
        return f"\n\nHint from rules ({confidence:.0%} confidence): {hints_str}"
    
    def _call_llm_structured(self, prompt: str, schema: Dict) -> Dict:
        """Call LLM with structured output"""
        try:
            result = self.llm_client.generate_structured(prompt, schema, temperature=0.0)
            if self.debug:
                print(f"DEBUG - LLM extracted: {result}")
            return result if result else {}
        except Exception as e:
            if self.debug:
                print(f"DEBUG - LLM call failed: {e}")
            return {}
    
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
                elif value == "Solos":
                    value = "Solo"
                # Handle "solo travelers" -> "Solo"
                if "solo" in value.lower():
                    value = "Solo"
                elif "couple" in value.lower():
                    value = "Couple"
                elif "famil" in value.lower():
                    value = "Family"
                elif "business" in value.lower():
                    value = "Business"
                elif "group" in value.lower():
                    value = "Group"
                if value in self.TRAVELLER_TYPES:
                    validated[key] = value
            
            # Convert numeric fields (including new ones for TrendAnalysis)
            elif key in ["min_rating", "star_rating", "min_cleanliness", "min_comfort", 
                        "min_value", "min_staff", "min_location", "min_facilities",
                        "min_recent_score", "min_improvement", "min_value_score"]:
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
            
            # Hotel names and reference hotels - validate against known hotels
            elif key in ["hotel_name", "reference_hotel"]:
                normalized_hotel = self._normalize_hotel_name(str(value).strip())
                if normalized_hotel:
                    validated[key] = normalized_hotel
                else:
                    # If normalization fails, keep the original (fuzzy matching may not work offline)
                    validated[key] = str(value).strip()
            
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
        
        # Check for potential typos using edit distance + LLM validation
        closest_match = self._find_closest_match_with_llm(city_input, self.VALID_CITIES, "city")
        if closest_match:
            return closest_match
        
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
        
        # Check for potential typos using edit distance + LLM validation
        closest_match = self._find_closest_match_with_llm(country_input, self.VALID_COUNTRIES, "country")
        if closest_match:
            return closest_match
        
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
    
    def _normalize_hotel_name(self, hotel_input: str) -> Optional[str]:
        """
        Normalize hotel name to match valid hotels from database.
        Uses fuzzy matching to handle missing/extra "The", typos, etc.
        
        Args:
            hotel_input: User's hotel input (may have typos or missing articles)
            
        Returns:
            Normalized hotel name or None if no match
        """
        if not hotel_input:
            return None
        
        hotel_lower = hotel_input.lower().strip()
        
        # If we have hotel list loaded, try to match against it
        if EntityExtractor.VALID_HOTELS and len(EntityExtractor.VALID_HOTELS) > 0:
            # Exact match (case-insensitive)
            for valid_hotel in EntityExtractor.VALID_HOTELS:
                if hotel_lower == valid_hotel.lower():
                    return valid_hotel
            
            # Fuzzy match: remove "the" from both and compare
            hotel_no_the = hotel_lower.replace("the ", "").strip()
            for valid_hotel in EntityExtractor.VALID_HOTELS:
                valid_no_the = valid_hotel.lower().replace("the ", "").strip()
                if hotel_no_the == valid_no_the:
                    return valid_hotel
            
            # Substring match (handles partial names)
            for valid_hotel in EntityExtractor.VALID_HOTELS:
                valid_lower = valid_hotel.lower()
                if hotel_lower in valid_lower or valid_lower in hotel_lower:
                    return valid_hotel
            
            # If still no match, use fuzzy matching with LLM for typo correction
            closest_match = self._find_closest_match_with_llm(hotel_input, EntityExtractor.VALID_HOTELS, "hotel")
            if closest_match:
                return closest_match
        
        # No match found or hotel list not loaded - return original as title case
        return hotel_input.title()
    
    def _find_closest_match_with_llm(self, user_input: str, valid_options: List[str], entity_type: str) -> Optional[str]:
        """
        Find closest match for potential typo using edit distance + LLM validation.
        Only calls LLM when edit distance suggests a likely typo.
        
        Args:
            user_input: User's input (potentially misspelled)
            valid_options: List of valid values (VALID_CITIES or VALID_COUNTRIES)
            entity_type: 'city' or 'country' for better LLM prompting
            
        Returns:
            Corrected value if LLM confirms typo, None otherwise
        """
        user_lower = user_input.lower().strip()
        
        # Find closest matches by edit distance
        matches_with_distance = []
        for valid_option in valid_options:
            # Calculate similarity ratio (0.0 to 1.0)
            similarity = difflib.SequenceMatcher(None, user_lower, valid_option.lower()).ratio()
            matches_with_distance.append((valid_option, similarity))
        
        # Sort by similarity (highest first)
        matches_with_distance.sort(key=lambda x: x[1], reverse=True)
        
        # If best match has high similarity (0.7-0.95), it's likely a typo
        best_match, best_similarity = matches_with_distance[0]
        
        # Perfect match already handled by earlier checks
        if best_similarity >= 0.95:
            return None
        
        # If similarity is between 0.7 and 0.95, likely a typo - ask LLM
        if 0.7 <= best_similarity < 0.95:
            return self._validate_typo_with_llm(user_input, best_match, entity_type)
        
        # Too different, probably not a typo
        return None
    
    def _validate_typo_with_llm(self, user_input: str, suggested_correction: str, entity_type: str) -> Optional[str]:
        """
        Ask LLM to validate if user_input is a typo of suggested_correction.
        
        Args:
            user_input: User's input (potentially misspelled)
            suggested_correction: Suggested correct spelling
            entity_type: 'city' or 'country'
            
        Returns:
            suggested_correction if LLM confirms typo, None otherwise
        """
        try:
            prompt = f'''Is "{user_input}" a typo or misspelling of the {entity_type} name "{suggested_correction}"?

Answer with ONLY "yes" or "no".

Examples:
- "Paaris" vs "Paris" → yes
- "Londan" vs "London" → yes  
- "Span" vs "Spain" → yes
- "Canda" vs "Canada" → yes
- "Berlin" vs "London" → no
- "Tokyo" vs "Paris" → no

Your answer (yes/no):'''
            
            # Use LLM client to generate response
            response = self.llm_client._client.chat.completions.create(
                model=self.llm_client._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Deterministic
                max_tokens=50  # Increased from 10 to allow full response
            )
            
            # Handle response - some models use 'content', others use 'reasoning'
            message = response.choices[0].message
            content = message.content
            
            # If content is empty, check reasoning field (for models like gpt-oss-120b)
            if not content and hasattr(message, 'reasoning') and message.reasoning:
                content = message.reasoning
            
            if self.debug:
                print(f"Typo validation: '{user_input}' vs '{suggested_correction}'")
                print(f"  LLM response: {content}")
            
            # Handle None or empty content
            if not content:
                if self.debug:
                    print(f"  Result: LLM returned no content")
                return None
            
            answer = content.strip().lower()
            
            if "yes" in answer:
                if self.debug:
                    print(f"  Result: YES - correcting to '{suggested_correction}'")
                return suggested_correction
            else:
                if self.debug:
                    print(f"  Result: NO - keeping '{user_input}'")
                return None
                
        except Exception as e:
            if self.debug:
                print(f"LLM typo validation failed: {e}")
            # On error, be conservative and don't correct
            return None
    
    def _normalize_country_name(self, country_input: str) -> str:
        """
        Normalize country name or nationality adjective to full country name.
        Handles cases like "Americans" -> "United States", "UK" -> "United Kingdom"
        
        Args:
            country_input: Country name or nationality adjective
            
        Returns:
            Normalized full country name
        """
        if not country_input:
            return country_input
        
        country_lower = country_input.lower().strip()
        
        # Nationality adjectives to country names
        nationality_map = {
            "american": "United States",
            "americans": "United States",
            "british": "United Kingdom",
            "french": "France",
            "japanese": "Japan",
            "german": "Germany",
            "canadian": "Canada",
            "canadians": "Canada",
            "australian": "Australia",
            "australians": "Australia",
            "spanish": "Spain",
            "italian": "Italy",
            "chinese": "China",
            "mexican": "Mexico",
            "indian": "India",
            "brazilian": "Brazil",
            "russian": "Russia",
            "egyptian": "Egypt",
            "thai": "Thailand",
            "turkish": "Turkey",
            "dutch": "Netherlands",
            "korean": "South Korea",
            "south korean": "South Korea",
            "emirati": "United Arab Emirates",
            "singaporean": "Singapore",
        }
        
        if country_lower in nationality_map:
            return nationality_map[country_lower]
        
        # Common country name variations and abbreviations
        country_aliases = {
            "usa": "United States",
            "us": "United States",
            "america": "United States",
            "uk": "United Kingdom",
            "uae": "United Arab Emirates",
            "korea": "South Korea",
        }
        
        if country_lower in country_aliases:
            return country_aliases[country_lower]
        
        # Check against valid countries
        for valid_country in self.VALID_COUNTRIES:
            if country_lower == valid_country.lower():
                return valid_country
        
        # Return title case as fallback
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

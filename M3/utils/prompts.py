"""
Prompt templates for Graph-RAG Hotel Travel Assistant
Centralized repository of all prompts used in the system
"""


class PromptTemplates:
    """
    Collection of prompt templates for different components.
    All prompts are designed for hotel/travel domain and Neo4j graph schema.
    """
    
    # =========================================================================
    # INTENT CLASSIFICATION
    # =========================================================================
    
    INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a hotel search system.

Analyze the user's query and classify it into ONE of these intents:

1. HotelSearch - User wants to find hotels by location or basic criteria
2. HotelRecommendation - User wants recommendations based on traveler type or quality scores
3. ReviewLookup - User wants to see reviews for specific hotels
4. LocationQuery - User asks about best locations or areas
5. VisaQuestion - User asks about visa requirements
6. AmenityFilter - User wants to filter by specific amenities or quality aspects
7. GeneralQuestionAnswering - General questions about a hotel

Examples:
- "Hotels in Paris" → HotelSearch
- "Best hotels for families" → HotelRecommendation
- "Show me reviews for Hilton Paris" → ReviewLookup
- "Do I need a visa from USA to France?" → VisaQuestion
- "Hotels with high cleanliness scores" → AmenityFilter

User query: {query}

Respond with ONLY the intent name (e.g., "HotelSearch")."""
    
    # =========================================================================
    # ENTITY EXTRACTION
    # =========================================================================
    
    ENTITY_EXTRACTION_PROMPT = """You are an entity extractor for a hotel search system.

Extract structured entities from the user's query based on the intent.

Intent: {intent}
Query: {query}

Extract these entities (return null if not found):
- city: City name (string)
- country: Country name (string)
- hotel_name: Specific hotel name (string)
- traveller_type: One of: Business, Couple, Family, Solo, Group (string)
- min_rating: Minimum rating threshold (number, 0-10)
- star_rating: Star rating (number, 1-5)
- min_cleanliness: Minimum cleanliness score (number, 0-10)
- min_comfort: Minimum comfort score (number, 0-10)
- min_location: Minimum location score (number, 0-10)
- min_staff: Minimum staff score (number, 0-10)
- min_value: Minimum value for money score (number, 0-10)
- from_country: Origin country for visa queries (string)
- to_country: Destination country for visa queries (string)
- limit: Number of results requested (number, default: 10)

Examples:
Query: "Hotels in Paris"
Entities: {{"city": "Paris", "country": null, "limit": 10}}

Query: "Top 5 hotels for families with cleanliness above 8"
Entities: {{"traveller_type": "Family", "min_cleanliness": 8, "limit": 5}}

Query: "Do I need a visa from USA to France?"
Entities: {{"from_country": "USA", "to_country": "France"}}

Respond with ONLY valid JSON containing the extracted entities."""
    
    # =========================================================================
    # CYPHER QUERY GENERATION (for LLM pipeline workflow)
    # =========================================================================
    
    CYPHER_GENERATION_PROMPT = """You are a Cypher query generator for a Neo4j hotel database.

Database Schema:
Nodes:
- Hotel: hotel_id, name, star_rating, average_reviews_score, cleanliness_base, comfort_base, facilities_base, location_base, staff_base, value_for_money_base
- City: name
- Country: name
- Review: review_id, text, date, score_overall, score_cleanliness, score_comfort, score_facilities, score_location, score_staff, score_value_for_money
- Traveller: user_id, gender, age, type (Business/Couple/Family/Solo/Group), join_date

Relationships:
- (Hotel)-[:LOCATED_IN]->(City)
- (City)-[:LOCATED_IN]->(Country)
- (Review)-[:REVIEWED]->(Hotel)
- (Traveller)-[:WROTE]->(Review)
- (Traveller)-[:STAYED_AT]->(Hotel)
- (Traveller)-[:FROM_COUNTRY]->(Country)
- (Country)-[:NEEDS_VISA]->(Country)

User query: {query}

Generate a Cypher query to answer this question. Return ONLY the Cypher query, no explanations.

Guidelines:
- Use OPTIONAL MATCH for relationships that might not exist
- Always include hotel location (city, country)
- Use ORDER BY for ranking results
- Add LIMIT clause (default 10)
- Use aggregate functions (AVG, COUNT) when appropriate
- For review queries, join Review->Hotel->City->Country
- For traveller preferences, filter by Traveller.type

Cypher query:"""
    
    # =========================================================================
    # ANSWER GENERATION
    # =========================================================================
    
    ANSWER_GENERATION_PROMPT = """You are a helpful hotel travel assistant. 

Generate a natural, conversational answer to the user's question using ONLY the provided context.

CRITICAL RULES:
1. Use ONLY information from the context below
2. Do NOT make up or hallucinate information
3. If the context doesn't contain enough information, say "I don't have enough information to answer that"
4. Cite specific hotels, cities, or review details when relevant
5. Be concise but informative
6. Use bullet points for multiple hotels
7. Include relevant scores and ratings

Intent: {intent}
User query: {query}

Context:
{context}

Provide a helpful answer:"""
    
    # =========================================================================
    # SPECIALIZED PROMPTS
    # =========================================================================
    
    HOTEL_COMPARISON_PROMPT = """Compare these hotels based on the provided information:

Hotels:
{hotels}

Compare them on:
- Location and accessibility
- Overall ratings and reviews
- Quality scores (cleanliness, comfort, staff, etc.)
- Value for money
- Best suited for which type of traveler

Provide a balanced comparison with recommendations."""
    
    REVIEW_SUMMARIZATION_PROMPT = """Summarize these hotel reviews:

Hotel: {hotel_name}
Reviews:
{reviews}

Provide:
1. Overall sentiment (Positive/Mixed/Negative)
2. Key strengths (3-5 points)
3. Common complaints (if any)
4. Best for which travelers
5. Summary in 2-3 sentences"""
    
    VISA_ADVICE_PROMPT = """Provide visa information for travel between countries:

From: {from_country}
To: {to_country}
Visa Required: {visa_required}
Visa Type: {visa_type}

Provide:
1. Clear yes/no answer
2. Type of visa if required
3. Brief advice on what to prepare
4. Reminder to check official sources"""
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    @staticmethod
    def format_intent_prompt(query: str) -> str:
        """Format intent classification prompt"""
        return PromptTemplates.INTENT_CLASSIFICATION_PROMPT.format(query=query)
    
    @staticmethod
    def format_entity_prompt(query: str, intent: str) -> str:
        """Format entity extraction prompt"""
        return PromptTemplates.ENTITY_EXTRACTION_PROMPT.format(
            query=query,
            intent=intent
        )
    
    @staticmethod
    def format_cypher_prompt(query: str) -> str:
        """Format Cypher generation prompt"""
        return PromptTemplates.CYPHER_GENERATION_PROMPT.format(query=query)
    
    @staticmethod
    def format_answer_prompt(query: str, context: str, intent: str) -> str:
        """Format answer generation prompt"""
        return PromptTemplates.ANSWER_GENERATION_PROMPT.format(
            query=query,
            context=context,
            intent=intent
        )
    
    @staticmethod
    def format_review_summary_prompt(hotel_name: str, reviews: str) -> str:
        """Format review summarization prompt"""
        return PromptTemplates.REVIEW_SUMMARIZATION_PROMPT.format(
            hotel_name=hotel_name,
            reviews=reviews
        )
    
    @staticmethod
    def format_visa_prompt(
        from_country: str,
        to_country: str,
        visa_required: bool,
        visa_type: str = None
    ) -> str:
        """Format visa advice prompt"""
        return PromptTemplates.VISA_ADVICE_PROMPT.format(
            from_country=from_country,
            to_country=to_country,
            visa_required="Yes" if visa_required else "No",
            visa_type=visa_type or "N/A"
        )
    
    @staticmethod
    def get_system_prompt() -> str:
        """Get default system prompt for LLM"""
        return """You are a knowledgeable hotel travel assistant with expertise in:
- Hotel recommendations and search
- Travel planning and logistics
- Visa requirements and regulations
- Accommodation quality assessment

Always be helpful, accurate, and concise. Use only provided information."""


if __name__ == "__main__":
    # Test prompt templates
    print("=== Prompt Templates Test ===\n")
    
    print("1. Intent Classification:")
    print(PromptTemplates.format_intent_prompt("Hotels in Paris"))
    print("\n" + "="*60 + "\n")
    
    print("2. Entity Extraction:")
    print(PromptTemplates.format_entity_prompt(
        "Top 5 hotels for families",
        "HotelRecommendation"
    ))
    print("\n" + "="*60 + "\n")
    
    print("3. Answer Generation:")
    print(PromptTemplates.format_answer_prompt(
        "Hotels in Paris",
        "Hotel A: 5-star, rating 9.2\nHotel B: 4-star, rating 8.5",
        "HotelSearch"
    ))

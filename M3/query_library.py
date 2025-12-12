#!/usr/bin/env python3
"""
query_library.py
Contains parameterized Cypher query templates for hotel-related intents.
These queries will be selected based on intent classification and populated with extracted entities.

Schema reminder from Create_kg.py:
- Nodes: Traveller, Hotel, City, Country, Review
- Hotel properties: hotel_id, name, star_rating, cleanliness_base, comfort_base, facilities_base, 
  location_base, staff_base, value_for_money_base, average_reviews_score
- Review properties: review_id, text, date, score_overall, score_cleanliness, score_comfort, 
  score_facilities, score_location, score_staff, score_value_for_money
- Traveller properties: user_id, gender, age, type, join_date
- Relationships: LOCATED_IN, FROM_COUNTRY, WROTE, REVIEWED, STAYED_AT, NEEDS_VISA
"""

class QueryLibrary:
    """
    Centralized library of Cypher query templates for Graph-RAG retrieval.
    Each query is parameterized and will be populated with extracted entities.
    """
    
    # =========================================================================
    # INTENT: HotelSearch
    # =========================================================================
    
    @staticmethod
    def get_hotels_by_city(city_name):
        """
        Query 1: Get all hotels in a specific city with their ratings and location info.
        Parameters: city_name (str)
        """
        return """
        MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
        OPTIONAL MATCH (c)-[:LOCATED_IN]->(country:Country)
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               h.average_reviews_score AS avg_score,
               c.name AS city,
               country.name AS country
        ORDER BY h.average_reviews_score DESC
        """, {"city_name": city_name}
    
    @staticmethod
    def get_hotels_by_country(country_name):
        """
        Query 2: Get all hotels in a specific country.
        Parameters: country_name (str)
        """
        return """
        MATCH (h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(co:Country {name: $country_name})
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               h.average_reviews_score AS avg_score,
               c.name AS city,
               co.name AS country
        ORDER BY h.average_reviews_score DESC
        """, {"country_name": country_name}
    
    @staticmethod
    def get_hotels_by_rating_threshold(min_rating):
        """
        Query 3: Get hotels with average review score above a threshold.
        Parameters: min_rating (float)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_overall) AS avg_score
        WHERE avg_score >= $min_rating
        ORDER BY avg_score DESC
        LIMIT 10
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_score,
               c.name AS city,
               country.name AS country
        """, {"min_rating": min_rating}
    
    
    
    # =========================================================================
    # INTENT: HotelRecommendation
    # =========================================================================
    
    @staticmethod
    def get_top_hotels_for_traveller_type(traveller_type, limit=5):
        """
        Query 5: Get top-rated hotels based on reviews from specific traveller type.
        Parameters: traveller_type (str) - e.g., 'Business', 'Couple', 'Family', 'Solo', 'Group'
                    limit (int) - number of results
        """
        return """
        MATCH (t:Traveller {type: $traveller_type})-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_overall) AS avg_rating, COUNT(r) AS review_count
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_rating,
               review_count,
               c.name AS city,
               country.name AS country
        """, {"traveller_type": traveller_type, "limit": limit}
    
    @staticmethod
    def get_hotels_by_cleanliness_score(min_cleanliness):
        """
        Query 6: Get hotels with high cleanliness scores.
        Parameters: min_cleanliness (float)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_cleanliness) AS avg_cleanliness
        WHERE avg_cleanliness >= $min_cleanliness
        ORDER BY avg_cleanliness DESC
        LIMIT 10
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_cleanliness,
               c.name AS city,
               country.name AS country
        """, {"min_cleanliness": min_cleanliness}
    
    # =========================================================================
    # INTENT: ReviewLookup
    # =========================================================================
    
    @staticmethod
    def get_reviews_by_hotel_name(hotel_name, limit=10):
        """
        Query 7: Get recent reviews for a specific hotel.
        Parameters: hotel_name (str), limit (int)
        """
        return """
        MATCH (h:Hotel {name: $hotel_name})<-[:REVIEWED]-(r:Review)<-[:WROTE]-(t:Traveller)
        RETURN r.review_id AS review_id,
               r.text AS review_text,
               r.date AS review_date,
               r.score_overall AS score_overall,
               r.score_cleanliness AS score_cleanliness,
               r.score_comfort AS score_comfort,
               r.score_facilities AS score_facilities,
               r.score_location AS score_location,
               r.score_staff AS score_staff,
               r.score_value_for_money AS score_value_for_money,
               t.user_id AS user_id,
               t.type AS traveller_type,
               t.gender AS gender
        ORDER BY r.date DESC
        LIMIT $limit
        """, {"hotel_name": hotel_name, "limit": limit}
    
    @staticmethod
    def get_reviews_by_hotel_id(hotel_id, limit=10):
        """
        Query 8: Get recent reviews for a hotel by ID.
        Parameters: hotel_id (str), limit (int)
        """
        return """
        MATCH (h:Hotel {hotel_id: $hotel_id})<-[:REVIEWED]-(r:Review)<-[:WROTE]-(t:Traveller)
        RETURN r.review_id AS review_id,
               r.text AS review_text,
               r.date AS review_date,
               r.score_overall AS score_overall,
               r.score_cleanliness AS score_cleanliness,
               r.score_comfort AS score_comfort,
               r.score_facilities AS score_facilities,
               r.score_location AS score_location,
               r.score_staff AS score_staff,
               r.score_value_for_money AS score_value_for_money,
               t.user_id AS user_id,
               t.type AS traveller_type,
               t.gender AS gender
        ORDER BY r.date DESC
        LIMIT $limit
        """, {"hotel_id": hotel_id, "limit": limit}
    
    # =========================================================================
    # INTENT: LocationQuery
    # =========================================================================
    
    @staticmethod
    def get_hotels_with_best_location_scores(city_name=None, limit=5):
        """
        Query 9: Get hotels with highest location scores (optionally filtered by city).
        Parameters: city_name (str or None), limit (int)
        """
        if city_name:
            return """
            MATCH (h:Hotel)-[:LOCATED_IN]->(c:City {name: $city_name})
            MATCH (r:Review)-[:REVIEWED]->(h)
            OPTIONAL MATCH (c)-[:LOCATED_IN]->(country:Country)
            WITH h, c, country, AVG(r.score_location) AS avg_location_score
            ORDER BY avg_location_score DESC
            LIMIT $limit
            RETURN h.hotel_id AS hotel_id,
                   h.name AS hotel_name,
                   h.star_rating AS star_rating,
                   avg_location_score,
                   c.name AS city,
                   country.name AS country
            """, {"city_name": city_name, "limit": limit}
        else:
            return """
            MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
            OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
            WITH h, c, country, AVG(r.score_location) AS avg_location_score
            ORDER BY avg_location_score DESC
            LIMIT $limit
            RETURN h.hotel_id AS hotel_id,
                   h.name AS hotel_name,
                   h.star_rating AS star_rating,
                   avg_location_score,
                   c.name AS city,
                   country.name AS country
            """, {"limit": limit}
    
    # =========================================================================
    # INTENT: VisaQuestion
    # =========================================================================
    
    @staticmethod
    def check_visa_requirements(from_country, to_country):
        """
        Query 10: Check if visa is required between two countries.
        Parameters: from_country (str), to_country (str)
        """
        return """
        MATCH (from:Country {name: $from_country})
        MATCH (to:Country {name: $to_country})
        OPTIONAL MATCH (from)-[v:NEEDS_VISA]->(to)
        RETURN from.name AS from_country,
               to.name AS to_country,
               CASE WHEN v IS NOT NULL THEN true ELSE false END AS visa_required,
               v.visa_type AS visa_type
        """, {"from_country": from_country, "to_country": to_country}
    
    @staticmethod
    def get_travellers_by_country_no_visa(from_country, to_country):
        """
        Query 11: Get count of travellers from country who stayed at hotels in destination 
        country without visa requirements.
        Parameters: from_country (str), to_country (str)
        """
        return """
        MATCH (t:Traveller)-[:FROM_COUNTRY]->(fromCountry:Country {name: $from_country})
        MATCH (t)-[:STAYED_AT]->(h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(toCountry:Country {name: $to_country})
        WHERE NOT (fromCountry)-[:NEEDS_VISA]->(toCountry)
        RETURN COUNT(DISTINCT t) AS traveller_count,
               fromCountry.name AS from_country,
               toCountry.name AS to_country
        """, {"from_country": from_country, "to_country": to_country}
    
    # =========================================================================
    # INTENT: AmenityFilter / Quality Filter
    # =========================================================================
    
    @staticmethod
    def get_hotels_by_comfort_score(min_comfort, limit=10):
        """
        Query 12: Get hotels with high comfort scores from reviews.
        Parameters: min_comfort (float), limit (int)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_comfort) AS avg_comfort
        WHERE avg_comfort >= $min_comfort
        ORDER BY avg_comfort DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_comfort,
               c.name AS city,
               country.name AS country
        """, {"min_comfort": min_comfort, "limit": limit}
    
    @staticmethod
    def get_hotels_by_value_for_money(min_value, limit=10):
        """
        Query 13: Get hotels with best value for money scores.
        Parameters: min_value (float), limit (int)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_value_for_money) AS avg_value
        WHERE avg_value >= $min_value
        ORDER BY avg_value DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_value,
               c.name AS city,
               country.name AS country
        """, {"min_value": min_value, "limit": limit}
    
    @staticmethod
    def get_hotels_with_best_staff_scores(limit=10):
        """
        Query 14: Get hotels with highest staff service scores.
        Parameters: limit (int)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country, AVG(r.score_staff) AS avg_staff_score
        WHERE avg_staff_score IS NOT NULL
        ORDER BY avg_staff_score DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_staff_score,
               c.name AS city,
               country.name AS country
        """, {"limit": limit}
    
    # =========================================================================
    # INTENT: GeneralQuestionAnswering
    # =========================================================================
    
    @staticmethod
    def get_hotel_full_details(hotel_name):
        """
        Query 15: Get comprehensive details about a specific hotel including all attributes.
        Parameters: hotel_name (str)
        """
        return """
        MATCH (h:Hotel {name: $hotel_name})
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        OPTIONAL MATCH (r:Review)-[:REVIEWED]->(h)
        WITH h, c, country, 
             AVG(r.score_overall) AS avg_overall,
             AVG(r.score_cleanliness) AS avg_cleanliness,
             AVG(r.score_comfort) AS avg_comfort,
             AVG(r.score_facilities) AS avg_facilities,
             AVG(r.score_location) AS avg_location,
             AVG(r.score_staff) AS avg_staff,
             AVG(r.score_value_for_money) AS avg_value,
             COUNT(r) AS total_reviews
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               h.average_reviews_score AS overall_avg_score,
               h.cleanliness_base AS cleanliness_base,
               h.comfort_base AS comfort_base,
               h.facilities_base AS facilities_base,
               h.location_base AS location_base,
               h.staff_base AS staff_base,
               h.value_for_money_base AS value_base,
               c.name AS city,
               country.name AS country,
               avg_overall,
               avg_cleanliness,
               avg_comfort,
               avg_facilities,
               avg_location,
               avg_staff,
               avg_value,
               total_reviews
        """, {"hotel_name": hotel_name}


# =========================================================================
# Query Selection Helper
# =========================================================================

class QuerySelector:
    """
    Helper class to select appropriate query based on intent and extracted entities.
    """
    
    INTENT_QUERY_MAP = {
        "HotelSearch": [
            "get_hotels_by_city",
            "get_hotels_by_country",
            "get_hotels_by_rating_threshold",
            "get_hotels_by_star_rating"
        ],
        "HotelRecommendation": [
            "get_top_hotels_for_traveller_type",
            "get_hotels_by_cleanliness_score",
            "get_hotels_by_comfort_score",
            "get_hotels_by_value_for_money",
            "get_hotels_with_best_staff_scores"
        ],
        "ReviewLookup": [
            "get_reviews_by_hotel_name",
            "get_reviews_by_hotel_id"
        ],
        "LocationQuery": [
            "get_hotels_with_best_location_scores"
        ],
        "VisaQuestion": [
            "check_visa_requirements",
            "get_travellers_by_country_no_visa"
        ],
        "AmenityFilter": [
            "get_hotels_by_cleanliness_score",
            "get_hotels_by_comfort_score",
            "get_hotels_by_value_for_money",
            "get_hotels_with_best_staff_scores"
        ],
        "GeneralQuestionAnswering": [
            "get_hotel_full_details"
        ]
    }
    
    @staticmethod
    def select_query(intent, entities):
        """
        Select the most appropriate query template based on intent and available entities.
        
        Args:
            intent (str): Classified intent
            entities (dict): Extracted entities from user query
        
        Returns:
            tuple: (cypher_query, parameters) or (None, None) if no match
        """
        if intent not in QuerySelector.INTENT_QUERY_MAP:
            return None, None
        
        # Simple rule-based selection based on available entities
        if intent == "HotelSearch":
            if "city" in entities:
                return QueryLibrary.get_hotels_by_city(entities["city"])
            elif "country" in entities:
                return QueryLibrary.get_hotels_by_country(entities["country"])
            elif "min_rating" in entities:
                return QueryLibrary.get_hotels_by_rating_threshold(entities["min_rating"])
            # star_rating queries not implemented - fall through to return None
        
        elif intent == "HotelRecommendation":
            if "traveller_type" in entities:
                return QueryLibrary.get_top_hotels_for_traveller_type(
                    entities["traveller_type"], 
                    entities.get("limit", 5)
                )
            elif "min_cleanliness" in entities:
                return QueryLibrary.get_hotels_by_cleanliness_score(entities["min_cleanliness"])
            elif "min_comfort" in entities:
                return QueryLibrary.get_hotels_by_comfort_score(entities["min_comfort"])
            elif "min_value" in entities:
                return QueryLibrary.get_hotels_by_value_for_money(entities["min_value"])
            elif "min_staff" in entities:
                return QueryLibrary.get_hotels_with_best_staff_scores(entities.get("limit", 10))
            # Fallback: if no specific score provided, default to cleanliness with 8.0 threshold
            else:
                return QueryLibrary.get_hotels_by_cleanliness_score(8.0)
        
        elif intent == "ReviewLookup":
            if "hotel_name" in entities:
                return QueryLibrary.get_reviews_by_hotel_name(
                    entities["hotel_name"],
                    entities.get("limit", 10)
                )
            elif "hotel_id" in entities:
                return QueryLibrary.get_reviews_by_hotel_id(
                    entities["hotel_id"],
                    entities.get("limit", 10)
                )
        
        elif intent == "LocationQuery":
            return QueryLibrary.get_hotels_with_best_location_scores(
                entities.get("city"),
                entities.get("limit", 5)
            )
        
        elif intent == "VisaQuestion":
            if "from_country" in entities and "to_country" in entities:
                return QueryLibrary.check_visa_requirements(
                    entities["from_country"],
                    entities["to_country"]
                )
        
        elif intent == "AmenityFilter":
            # Handle quality score filters (cleanliness, comfort, value, staff)
            if "min_cleanliness" in entities:
                return QueryLibrary.get_hotels_by_cleanliness_score(entities["min_cleanliness"])
            elif "min_comfort" in entities:
                return QueryLibrary.get_hotels_by_comfort_score(
                    entities["min_comfort"],
                    entities.get("limit", 10)
                )
            elif "min_value" in entities:
                return QueryLibrary.get_hotels_by_value_for_money(
                    entities["min_value"],
                    entities.get("limit", 10)
                )
            elif "min_staff" in entities:
                return QueryLibrary.get_hotels_with_best_staff_scores(entities.get("limit", 10))
            # Fallback: if just asking about cleanliness/comfort/staff without threshold
            # Use default threshold of 8.0 for cleanliness
            else:
                return QueryLibrary.get_hotels_by_cleanliness_score(8.0)
        
        elif intent == "GeneralQuestionAnswering":
            if "hotel_name" in entities:
                return QueryLibrary.get_hotel_full_details(entities["hotel_name"])
        
        return None, None


if __name__ == "__main__":
    # Test: print all available queries
    print("=== Hotel Graph-RAG Query Library ===\n")
    print("Total query templates: 15\n")
    
    # Example usage
    print("Example 1: Search hotels in Paris")
    query, params = QueryLibrary.get_hotels_by_city("Paris")
    print(f"Query:\n{query}")
    print(f"Parameters: {params}\n")
    
    print("Example 2: Get top hotels for Business travelers")
    query, params = QueryLibrary.get_top_hotels_for_traveller_type("Business", 5)
    print(f"Query:\n{query}")
    print(f"Parameters: {params}\n")
    
    print("Example 3: Check visa requirements")
    query, params = QueryLibrary.check_visa_requirements("USA", "France")
    print(f"Query:\n{query}")
    print(f"Parameters: {params}\n")

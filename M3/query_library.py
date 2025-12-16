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
    def get_hotels_by_city(city_name): #done
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
    def get_hotels_by_country(country_name): #done
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
    def get_hotels_by_rating_threshold(min_rating): #done
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
    def get_top_hotels_for_traveller_type(traveller_type, limit=5): #DONE
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
    def get_hotels_by_cleanliness_score(min_cleanliness): #DONE
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
    def get_reviews_by_hotel_name(hotel_name, limit=10): #DONE
        """
        Query 7: Get recent reviews for a specific hotel.
        Parameters: hotel_name (str), limit (int)
        """
        return """
        MATCH (h:Hotel {name: $hotel_name})<-[:REVIEWED]-(r:Review)<-[:WROTE]-(t:Traveller)
        RETURN h.name AS hotel_name,
               r.review_id AS review_id,
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
        RETURN h.name AS hotel_name,
               r.review_id AS review_id,
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
    def get_hotels_with_best_location_scores(city_name=None, limit=5): #DONE
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
    def check_visa_requirements(from_country, to_country): #DONE
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
    
    # =========================================================================
    # INTENT: AmenityFilter / Quality Filter
    # =========================================================================
    
    @staticmethod
    def get_hotels_by_comfort_score(min_comfort, limit=10): #DONE
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
    def get_hotels_by_value_for_money(min_value, limit=10): #DONE
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
    def get_hotels_with_best_staff_scores(limit=10): #DONE
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
    def get_hotel_full_details(hotel_name): # hotel name issue
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
    # COMPLEX QUERIES - Multi-Criteria & Advanced Analytics
    # =========================================================================
    
    @staticmethod
    def get_hotels_by_multiple_criteria(city_name=None, min_cleanliness=None, min_comfort=None, 
                                        min_staff=None, min_value=None, limit=10):
        """
        Query 16: Advanced multi-criteria filtering with all quality dimensions.
        Finds hotels matching multiple quality thresholds (only those specified are applied).
        Parameters: city_name (str or None), min_cleanliness (float or None), min_comfort (float or None),
                    min_staff (float or None), min_value (float or None), limit (int)
        """
        where_clauses = ["avg_cleanliness IS NOT NULL"]
        params = {"limit": limit}
        
        if min_cleanliness is not None:
            where_clauses.append("avg_cleanliness >= $min_cleanliness")
            params["min_cleanliness"] = min_cleanliness
        if min_comfort is not None:
            where_clauses.append("avg_comfort >= $min_comfort")
            params["min_comfort"] = min_comfort
        if min_staff is not None:
            where_clauses.append("avg_staff >= $min_staff")
            params["min_staff"] = min_staff
        if min_value is not None:
            where_clauses.append("avg_value >= $min_value")
            params["min_value"] = min_value
        
        city_filter = ""
        if city_name:
            city_filter = "MATCH (h)-[:LOCATED_IN]->(c:City {name: $city_name})\n"
            params["city_name"] = city_name
        else:
            city_filter = "MATCH (h)-[:LOCATED_IN]->(c:City)\n"
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        {city_filter}
        OPTIONAL MATCH (c)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country,
             AVG(r.score_cleanliness) AS avg_cleanliness,
             AVG(r.score_comfort) AS avg_comfort,
             AVG(r.score_staff) AS avg_staff,
             AVG(r.score_value_for_money) AS avg_value,
             AVG(r.score_overall) AS avg_overall,
             COUNT(r) AS review_count
        WHERE {where_clause}
        ORDER BY avg_overall DESC, review_count DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_overall,
               avg_cleanliness,
               avg_comfort,
               avg_staff,
               avg_value,
               review_count,
               c.name AS city,
               country.name AS country
        """
        return query, params
    
    @staticmethod
    def compare_hotels_by_traveller_type_in_city(city_name, traveller_type=None, limit_per_type=3):
        """
        Query 17: Comparative analysis - Top hotels for each traveller type in a city.
        Shows which hotels are best for Business, Couple, Family, Solo, Group travelers.
        Parameters: city_name (str), traveller_type (str, optional), limit_per_type (int)
        """
        if traveller_type:
            # Single traveller type - filter by both city and traveller type
            return """
        MATCH (c:City {name: $city_name})<-[:LOCATED_IN]-(h:Hotel)
        MATCH (t:Traveller {type: $traveller_type})-[:WROTE]->(r:Review)-[:REVIEWED]->(h)
        WITH h, 
             AVG(r.score_overall) AS avg_rating,
             COUNT(r) AS review_count
        ORDER BY avg_rating DESC, review_count DESC
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_rating,
               review_count
        LIMIT $limit_per_type
        """, {"city_name": city_name, "traveller_type": traveller_type, "limit_per_type": limit_per_type}
        else:
            # No specific traveller type - compare all types in city
            return """
        MATCH (c:City {name: $city_name})<-[:LOCATED_IN]-(h:Hotel)
        MATCH (t:Traveller)-[:WROTE]->(r:Review)-[:REVIEWED]->(h)
        WITH t.type AS traveller_type,
             h, 
             AVG(r.score_overall) AS avg_rating,
             COUNT(r) AS review_count
        ORDER BY traveller_type, avg_rating DESC
        WITH traveller_type, COLLECT({hotel_name: h.name, 
                                       hotel_id: h.hotel_id,
                                       rating: avg_rating,
                                       reviews: review_count})[0..$limit_per_type] AS top_hotels
        RETURN traveller_type, top_hotels
        """, {"city_name": city_name, "limit_per_type": limit_per_type}
    
    @staticmethod
    def get_hotels_with_balanced_scores(min_balance_score=7.0, limit=10):
        """
        Query 18: Find hotels with balanced quality across all dimensions.
        Returns hotels where cleanliness, comfort, staff, location, and value are all high and similar.
        Parameters: min_balance_score (float) - minimum score for all dimensions, limit (int)
        """
        return """
        MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
        WITH h, c, country,
             AVG(r.score_cleanliness) AS avg_clean,
             AVG(r.score_comfort) AS avg_comfort,
             AVG(r.score_staff) AS avg_staff,
             AVG(r.score_location) AS avg_location,
             AVG(r.score_value_for_money) AS avg_value,
             AVG(r.score_overall) AS avg_overall,
             COUNT(r) AS review_count
        WHERE avg_clean >= $min_score AND avg_comfort >= $min_score AND 
              avg_staff >= $min_score AND avg_location >= $min_score AND avg_value >= $min_score
        WITH h, c, country, avg_overall, review_count,
             (avg_clean + avg_comfort + avg_staff + avg_location + avg_value) / 5.0 AS balance_score,
             abs(avg_clean - avg_comfort) + abs(avg_comfort - avg_staff) + 
             abs(avg_staff - avg_location) + abs(avg_location - avg_value) AS dimension_variance
        ORDER BY dimension_variance ASC, balance_score DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               balance_score,
               avg_overall,
               dimension_variance,
               review_count,
               c.name AS city,
               country.name AS country
        """, {"min_score": min_balance_score, "limit": limit}
    
    @staticmethod
    def get_hotels_by_traveller_origin_patterns(from_country, limit=8):
        """
        Query 19: Find hotels that are popular among travelers from a specific country.
        Shows which hotels have the most positive reviews from travelers from that origin.
        Parameters: from_country (str), limit (int)
        """
        return """
        MATCH (t:Traveller)-[:FROM_COUNTRY]->(origin:Country {name: $from_country})
        MATCH (t)-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)
        OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(dest:Country)
        WITH h, c, dest, 
             AVG(r.score_overall) AS avg_rating,
             COUNT(r) AS review_count,
             AVG(r.score_comfort) AS avg_comfort,
             AVG(r.score_value_for_money) AS avg_value
        ORDER BY review_count DESC, avg_rating DESC
        LIMIT $limit
        RETURN h.hotel_id AS hotel_id,
               h.name AS hotel_name,
               h.star_rating AS star_rating,
               avg_rating,
               review_count,
               avg_comfort,
               avg_value,
               c.name AS city,
               dest.name AS destination_country
        """, {"from_country": from_country, "limit": limit}
    
    # @staticmethod
    # def get_hotels_similar_to_reference(reference_hotel_name, similarity_threshold=6.5, limit=5): #might remove
    #     """
    #     Query 20: Find hotels similar to a reference hotel based on quality profile.
    #     Similarity is based on matching review score patterns (same profile of strengths/weaknesses).
    #     Parameters: reference_hotel_name (str), similarity_threshold (float), limit (int)
    #     """
    #     return """
    #     MATCH (ref:Hotel {name: $ref_name})<-[:REVIEWED]-(r_ref:Review)
    #     WITH ref,
    #          AVG(r_ref.score_cleanliness) AS ref_clean,
    #          AVG(r_ref.score_comfort) AS ref_comfort,
    #          AVG(r_ref.score_staff) AS ref_staff,
    #          AVG(r_ref.score_location) AS ref_location,
    #          AVG(r_ref.score_value_for_money) AS ref_value
    #     MATCH (h:Hotel)<-[:REVIEWED]-(r:Review)
    #     WHERE h.name <> $ref_name
    #     WITH h, ref,
    #          ref_clean, ref_comfort, ref_staff, ref_location, ref_value,
    #          AVG(r.score_cleanliness) AS h_clean,
    #          AVG(r.score_comfort) AS h_comfort,
    #          AVG(r.score_staff) AS h_staff,
    #          AVG(r.score_location) AS h_location,
    #          AVG(r.score_value_for_money) AS h_value,
    #          COUNT(r) AS review_count
    #     WITH h, ref, review_count,
    #          abs(h_clean - ref_clean) + abs(h_comfort - ref_comfort) + 
    #          abs(h_staff - ref_staff) + abs(h_location - ref_location) + 
    #          abs(h_value - ref_value) AS profile_distance,
    #          (h_clean + h_comfort + h_staff + h_location + h_value) / 5.0 AS avg_score
    #     WHERE profile_distance <= $distance_threshold AND review_count >= 5
    #     OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
    #     ORDER BY profile_distance ASC
    #     LIMIT $limit
    #     RETURN h.hotel_id AS hotel_id,
    #            h.name AS hotel_name,
    #            h.star_rating AS star_rating,
    #            avg_score,
    #            profile_distance,
    #            review_count,
    #            c.name AS city,
    #            country.name AS country
    #     """, {"ref_name": reference_hotel_name, "distance_threshold": similarity_threshold, "limit": limit}
    
    # @staticmethod
    # def get_hotels_with_specialist_strength(strength_type, min_score=8.0, limit=10):
    #     """
    #     Query 21: Find hotels with a specific specialist strength (e.g., best for comfort but may lack value).
    #     Parameters: strength_type (str) - one of: 'cleanliness', 'comfort', 'staff', 'location', 'value', 'facilities'
    #                 min_score (float), limit (int)
    #     """
    #     dimension_map = {
    #         "cleanliness": "score_cleanliness",
    #         "comfort": "score_comfort",
    #         "staff": "score_staff",
    #         "location": "score_location",
    #         "value": "score_value_for_money",
    #         "facilities": "score_facilities"
    #     }
        
    #     score_field = dimension_map.get(strength_type.lower(), "score_overall")
        
    #     return f"""
    #     MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
    #     OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
    #     WITH h, c, country,
    #          AVG(r.{score_field}) AS specialty_score,
    #          AVG(r.score_overall) AS avg_overall,
    #          COUNT(r) AS review_count
    #     WHERE specialty_score >= $min_score
    #     ORDER BY specialty_score DESC, review_count DESC
    #     LIMIT $limit
    #     RETURN h.hotel_id AS hotel_id,
    #            h.name AS hotel_name,
    #            h.star_rating AS star_rating,
    #            specialty_score,
    #            avg_overall,
    #            review_count,
    #            c.name AS city,
    #            country.name AS country
    #     """, {"min_score": min_score, "limit": limit}
    
    # @staticmethod
    # def find_best_value_hotels(max_price_category=None, min_value_score=8.0, limit=10):
    #     """
    #     Query 23: Find hotels offering best value for money.
    #     Parameters: max_price_category (str or None) - filter by implicit price tier, 
    #                 min_value_score (float), limit (int)
    #     """
    #     return """
    #     MATCH (r:Review)-[:REVIEWED]->(h:Hotel)
    #     OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
    #     WITH h, c, country,
    #          AVG(r.score_value_for_money) AS avg_value,
    #          AVG(r.score_overall) AS avg_overall,
    #          COUNT(r) AS review_count
    #     WHERE avg_value >= $min_value_score
    #     ORDER BY avg_value DESC, review_count DESC
    #     LIMIT $limit
    #     RETURN h.hotel_id AS hotel_id,
    #            h.name AS hotel_name,
    #            h.star_rating AS star_rating,
    #            avg_value,
    #            avg_overall,
    #            review_count,
    #            c.name AS city,
    #            country.name AS country
    #     """, {"min_value_score": min_value_score, "limit": limit}


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
            "get_top_hotels_for_traveller_type"
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
            if "from_country" in entities:
                # Popular among travelers from specific country
                return QueryLibrary.get_hotels_by_traveller_origin_patterns(
                    from_country=entities["from_country"],
                    limit=entities.get("limit", 8)
                )
            elif "traveller_type" in entities and "city" in entities:
                # Traveller type recommendation filtered by city
                return QueryLibrary.compare_hotels_by_traveller_type_in_city(
                    city_name=entities["city"],
                    traveller_type=entities["traveller_type"],
                    limit_per_type=entities.get("limit", 3)
                )
            elif "traveller_type" in entities:
                # Standard traveller type recommendation (no city filter)
                return QueryLibrary.get_top_hotels_for_traveller_type(
                    entities["traveller_type"], 
                    entities.get("limit", 5)
                )
        
        elif intent == "ReviewLookup":
            # Query 22 (trending hotels) disabled due to Cypher syntax error
            # if entities.get("is_trending"):
            #     return QueryLibrary.get_hotels_trending_up(...)
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
            # Check for trend analysis signals even for LocationQuery
            if "from_country" in entities:
                # Traveler origin pattern analysis
                return QueryLibrary.get_hotels_by_traveller_origin_patterns(
                    from_country=entities["from_country"],
                    limit=entities.get("limit", 8)
                )
            else:
                # Standard location query
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
            # Check if multiple criteria are specified (escalate to multi-criteria)
            criteria_count = sum(1 for k in ["min_cleanliness", "min_comfort", "min_staff", "min_value", "min_location", "min_facilities"] if k in entities)
            
            if criteria_count >= 2:
                # Multiple criteria detected - use advanced multi-criteria query
                return QueryLibrary.get_hotels_by_multiple_criteria(
                    city_name=entities.get("city"),
                    min_cleanliness=entities.get("min_cleanliness"),
                    min_comfort=entities.get("min_comfort"),
                    min_staff=entities.get("min_staff"),
                    min_value=entities.get("min_value"),
                    limit=entities.get("limit", 10)
                )
            # Single criterion - use simple filter
            elif "min_cleanliness" in entities:
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
            # Check for complex scenarios even in general Q&A
            if "from_country" in entities:
                # Hotels popular among travelers from specific country
                return QueryLibrary.get_hotels_by_traveller_origin_patterns(
                    from_country=entities["from_country"],
                    limit=entities.get("limit", 8)
                )
            elif entities.get("balanced"):
                # Balanced quality across dimensions
                return QueryLibrary.get_hotels_with_balanced_scores(
                    min_balance_score=7.0,
                    limit=entities.get("limit", 10)
                )
            # Check for multiple quality dimensions mentioned
            elif any(k in entities for k in ["min_cleanliness", "min_comfort", "min_staff", "min_value"]):
                criteria_count = sum(1 for k in ["min_cleanliness", "min_comfort", "min_staff", "min_value"] if k in entities)
                if criteria_count >= 2:
                    # Multiple dimensions - use balanced query
                    return QueryLibrary.get_hotels_with_balanced_scores(
                        min_balance_score=min((v for k, v in entities.items() if k.startswith("min_") and isinstance(v, (int, float))), default=7.0),
                        limit=entities.get("limit", 10)
                    )
            # Standard general question
            elif "reference_hotel" in entities:
                return QueryLibrary.get_hotel_full_details(entities["reference_hotel"])
            elif "hotel_name" in entities:
                return QueryLibrary.get_hotel_full_details(entities["hotel_name"])
        
        return None, None


if __name__ == "__main__":
    # Test: print all available queries
    print("=== Hotel Graph-RAG Query Library ===\n")
    print("Total query templates: 23\n")
    
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
    query, params = QueryLibrary.check_visa_requirements("United States", "France")
    print(f"Query:\n{query}")
    print(f"Parameters: {params}\n")
    
    print("Example 4: Multi-criteria filtering (Clean AND Comfortable AND Good Staff)")
    query, params = QueryLibrary.get_hotels_by_multiple_criteria(
        city_name="London",
        min_cleanliness=8.0,
        min_comfort=7.5,
        min_staff=8.5,
        limit=5
    )
    print(f"Query:\n{query[:200]}...\n")
    print(f"Parameters: {params}\n")

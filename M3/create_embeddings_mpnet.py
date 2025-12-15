"""
Create Embeddings Script - Generate FAISS indexes for all-mpnet-base-v2 model
Run this to generate embeddings using the second embedding model
Files are saved with _mpnet suffix to coexist with all-MiniLM-L6-v2 embeddings
"""

import json
import os
from typing import List, Dict, Tuple
import numpy as np
import faiss
from utils.neo4j_client import Neo4jClient
from utils.embedding_client import EmbeddingClient


def fetch_hotels_from_neo4j(neo4j_client: Neo4jClient) -> List[Dict]:
    """
    Fetch all hotels with their properties and visa requirements from Neo4j
    
    Returns:
        List of hotel dicts with all properties including visa info
    """
    cypher = """
    MATCH (h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(co:Country)
    OPTIONAL MATCH (co)-[needs:NEEDS_VISA]->(:Country)
    WITH h, c, co, 
         count(needs) > 0 AS requires_visa_to_some,
         collect(DISTINCT needs.visa_type) AS visa_types
    RETURN h.hotel_id AS hotel_id,
           h.name AS name,
           c.name AS city,
           co.name AS country,
           h.star_rating AS star_rating,
           h.average_reviews_score AS average_reviews_score,
           h.cleanliness_base AS cleanliness_base,
           h.comfort_base AS comfort_base,
           h.facilities_base AS facilities_base,
           h.location_base AS location_base,
           h.staff_base AS staff_base,
           h.value_for_money_base AS value_for_money_base,
           requires_visa_to_some AS has_visa_requirements,
           visa_types
    ORDER BY h.hotel_id
    """
    
    results = neo4j_client.run_query(cypher, {})
    print(f"✓ Fetched {len(results)} hotels from Neo4j")
    return results


def build_hotel_feature_string(hotel: Dict) -> str:
    """
    Build rich feature string for hotel embedding (hotel attributes only)
    
    Args:
        hotel: Hotel dict with all properties
        
    Returns:
        Feature string combining all hotel attributes without visa info
    """
    # Handle None values with defaults
    name = hotel.get('name') or 'Unknown Hotel'
    city = hotel.get('city') or 'Unknown City'
    country = hotel.get('country') or 'Unknown Country'
    star_rating = hotel.get('star_rating') or 0.0
    avg_score = hotel.get('average_reviews_score') or 0.0
    cleanliness = hotel.get('cleanliness_base') or 0.0
    comfort = hotel.get('comfort_base') or 0.0
    facilities = hotel.get('facilities_base') or 0.0
    location = hotel.get('location_base') or 0.0
    staff = hotel.get('staff_base') or 0.0
    value = hotel.get('value_for_money_base') or 0.0
    
    # Build feature string (hotel properties only, no visa info)
    feature_string = (
        f"{name} in {city}, {country}. "
        f"Star rating: {star_rating:.1f}. "
        f"Average score: {avg_score:.2f}. "
        f"Cleanliness: {cleanliness:.1f}, "
        f"Comfort: {comfort:.1f}, "
        f"Facilities: {facilities:.1f}, "
        f"Location: {location:.1f}, "
        f"Staff: {staff:.1f}, "
        f"Value for money: {value:.1f}"
    )
    
    return feature_string


def create_hotel_embeddings(
    neo4j_client: Neo4jClient,
    embedding_client: EmbeddingClient,
    output_dir: str = "."
) -> Tuple[str, str]:
    """
    Create FAISS index and mapping for hotels
    
    Args:
        neo4j_client: Neo4j connection
        embedding_client: Embedding model
        output_dir: Directory to save files
        
    Returns:
        Tuple of (faiss_path, mapping_path)
    """
    print("\n=== Creating Hotel Embeddings (all-mpnet-base-v2) ===")
    
    # Fetch hotels
    hotels = fetch_hotels_from_neo4j(neo4j_client)
    
    if not hotels:
        print("✗ No hotels found in Neo4j")
        return None, None
    
    # Build feature strings and generate embeddings
    print("Generating embeddings...")
    hotel_ids = []
    embeddings = []
    
    for i, hotel in enumerate(hotels):
        hotel_id = hotel['hotel_id']
        feature_string = build_hotel_feature_string(hotel)
        
        # Generate embedding
        embedding = embedding_client.encode(feature_string)
        
        hotel_ids.append(hotel_id)
        embeddings.append(embedding)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(hotels)} hotels...")
    
    print(f"✓ Generated embeddings for {len(embeddings)} hotels")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings, dtype='float32')
    dimension = embeddings_array.shape[1]
    
    print(f"  Embedding dimension: {dimension}")
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"✓ Created FAISS index with {index.ntotal} vectors")
    
    # Save FAISS index with _mpnet suffix
    faiss_path = os.path.join(output_dir, "hotel_embeddings_mpnet.faiss")
    faiss.write_index(index, faiss_path)
    print(f"✓ Saved FAISS index to {faiss_path}")
    
    # Create mapping: faiss_index -> hotel_id
    mapping = {i: hotel_id for i, hotel_id in enumerate(hotel_ids)}
    mapping_path = os.path.join(output_dir, "hotel_id_mapping_mpnet.json")
    
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Saved mapping to {mapping_path}")
    
    return faiss_path, mapping_path


def fetch_visa_relationships_from_neo4j(neo4j_client: Neo4jClient) -> List[Dict]:
    """
    Fetch all visa relationships from Neo4j
    
    Returns:
        List of visa relationship dicts
    """
    cypher = """
    MATCH (from:Country)-[v:NEEDS_VISA]->(to:Country)
    RETURN from.name AS from_country,
           to.name AS to_country,
           v.visa_type AS visa_type,
           id(v) AS relationship_id
    ORDER BY from.name, to.name
    """
    
    results = neo4j_client.run_query(cypher, {})
    print(f"✓ Fetched {len(results)} visa relationships from Neo4j")
    return results


def build_visa_feature_string(visa_rel: Dict) -> str:
    """
    Build feature string for visa relationship embedding
    
    Args:
        visa_rel: Visa relationship dict
        
    Returns:
        Feature string describing visa requirement
    """
    from_country = visa_rel.get('from_country', 'Unknown')
    to_country = visa_rel.get('to_country', 'Unknown')
    visa_type = visa_rel.get('visa_type', 'Required')
    
    # Build natural language description
    feature_string = (
        f"Visa required from {from_country} to {to_country}. "
        f"Visa type: {visa_type}. "
        f"Travelers from {from_country} need a visa to visit {to_country}. "
        f"{from_country} citizens require {visa_type} visa for {to_country} travel."
    )
    
    return feature_string


def create_visa_embeddings(
    neo4j_client: Neo4jClient,
    embedding_client: EmbeddingClient,
    output_dir: str = "."
) -> Tuple[str, str]:
    """
    Create FAISS index and mapping for visa relationships
    
    Args:
        neo4j_client: Neo4j connection
        embedding_client: Embedding model
        output_dir: Directory to save files
        
    Returns:
        Tuple of (faiss_path, mapping_path)
    """
    print("\n=== Creating Visa Embeddings (all-mpnet-base-v2) ===")
    
    # Fetch visa relationships
    visa_rels = fetch_visa_relationships_from_neo4j(neo4j_client)
    
    if not visa_rels:
        print("✗ No visa relationships found in Neo4j")
        return None, None
    
    # Build feature strings and generate embeddings
    print("Generating embeddings...")
    visa_ids = []
    embeddings = []
    
    for i, visa_rel in enumerate(visa_rels):
        # Create unique ID from country pair
        visa_id = f"{visa_rel['from_country']}_to_{visa_rel['to_country']}"
        feature_string = build_visa_feature_string(visa_rel)
        
        # Generate embedding
        embedding = embedding_client.encode(feature_string)
        
        visa_ids.append(visa_id)
        embeddings.append(embedding)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(visa_rels)} visa relationships...")
    
    print(f"✓ Generated embeddings for {len(embeddings)} visa relationships")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings, dtype='float32')
    dimension = embeddings_array.shape[1]
    
    print(f"  Embedding dimension: {dimension}")
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"✓ Created FAISS index with {index.ntotal} vectors")
    
    # Save FAISS index with _mpnet suffix
    faiss_path = os.path.join(output_dir, "visa_embeddings_mpnet.faiss")
    faiss.write_index(index, faiss_path)
    print(f"✓ Saved FAISS index to {faiss_path}")
    
    # Create mapping: faiss_index -> visa_id
    mapping = {i: visa_id for i, visa_id in enumerate(visa_ids)}
    mapping_path = os.path.join(output_dir, "visa_id_mapping_mpnet.json")
    
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Saved mapping to {mapping_path}")
    
    return faiss_path, mapping_path


def fetch_reviews_from_neo4j(neo4j_client: Neo4jClient) -> List[Dict]:
    """
    Fetch all reviews with traveller and hotel details from Neo4j
    
    Returns:
        List of review dicts with traveller, hotel, and ratings
    """
    cypher = """
    MATCH (t:Traveller)-[:WROTE]->(r:Review)-[:REVIEWED]->(h:Hotel)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(co:Country)
    OPTIONAL MATCH (t)-[:FROM_COUNTRY]->(uc:Country)
    RETURN r.review_id AS review_id,
           t.user_id AS user_id,
           t.gender AS user_gender,
           t.age AS user_age_group,
           t.type AS user_traveller_type,
           uc.name AS user_country,
           h.hotel_id AS hotel_id,
           h.name AS hotel_name,
           c.name AS city,
           co.name AS country,
           h.star_rating AS hotel_star_rating,
           r.score_overall AS review_overall_score,
           r.score_cleanliness AS review_cleanliness,
           r.score_comfort AS review_comfort,
           r.score_facilities AS review_facilities,
           r.score_location AS review_location,
           r.score_staff AS review_staff,
           r.score_value_for_money AS review_value_for_money,
           r.date AS review_date
    ORDER BY r.review_id
    """
    
    results = neo4j_client.run_query(cypher, {})
    print(f"✓ Fetched {len(results)} reviews from Neo4j")
    return results


def build_review_feature_string(review: Dict) -> str:
    """
    Build feature string for review embedding (no review text, only structured data)
    
    Args:
        review: Review dict with user, hotel, and rating details
        
    Returns:
        Feature string combining review context and ratings
    """
    # User profile
    user_gender = review.get('user_gender', 'Unknown')
    user_age = review.get('user_age_group', 'Unknown')
    user_type = review.get('user_traveller_type', 'Unknown')
    user_country = review.get('user_country', 'Unknown')
    
    # Hotel info
    hotel_name = review.get('hotel_name', 'Unknown Hotel')
    city = review.get('city', 'Unknown City')
    country = review.get('country', 'Unknown Country')
    star_rating = review.get('hotel_star_rating', 0.0)
    
    # Review ratings
    overall = review.get('review_overall_score', 0.0)
    cleanliness = review.get('review_cleanliness', 0.0)
    comfort = review.get('review_comfort', 0.0)
    facilities = review.get('review_facilities', 0.0)
    location = review.get('review_location', 0.0)
    staff = review.get('review_staff', 0.0)
    value = review.get('review_value_for_money', 0.0)
    
    # Build rich feature string
    feature_string = (
        f"{user_gender} {user_type} traveler from {user_country} (age {user_age}) "
        f"reviewed {hotel_name} in {city}, {country} ({star_rating} stars). "
        f"Overall: {overall:.1f}/10. "
        f"Ratings: Cleanliness {cleanliness:.1f}, Comfort {comfort:.1f}, "
        f"Facilities {facilities:.1f}, Location {location:.1f}, "
        f"Staff {staff:.1f}, Value {value:.1f}."
    )
    
    return feature_string


def create_review_embeddings(
    neo4j_client: Neo4jClient,
    embedding_client: EmbeddingClient,
    output_dir: str = "."
) -> Tuple[str, str]:
    """
    Create FAISS index and mapping for reviews
    
    Args:
        neo4j_client: Neo4j connection
        embedding_client: Embedding model
        output_dir: Directory to save files
        
    Returns:
        Tuple of (faiss_path, mapping_path)
    """
    print("\n=== Creating Review Embeddings (all-mpnet-base-v2) ===")
    
    # Fetch reviews
    reviews = fetch_reviews_from_neo4j(neo4j_client)
    
    if not reviews:
        print("✗ No reviews found in Neo4j")
        return None, None
    
    # Build feature strings and generate embeddings
    print("Generating embeddings...")
    hotel_ids = []  # Map each review embedding to its hotel_id
    embeddings = []
    
    for i, review in enumerate(reviews):
        hotel_id = review['hotel_id']  # Map to hotel_id, not review_id
        feature_string = build_review_feature_string(review)
        
        # Generate embedding
        embedding = embedding_client.encode(feature_string)
        
        hotel_ids.append(hotel_id)
        embeddings.append(embedding)
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(reviews)} reviews...")
    
    print(f"✓ Generated embeddings for {len(embeddings)} reviews")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings, dtype='float32')
    dimension = embeddings_array.shape[1]
    
    print(f"  Embedding dimension: {dimension}")
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    
    print(f"✓ Created FAISS index with {index.ntotal} vectors")
    
    # Save FAISS index with _mpnet suffix
    faiss_path = os.path.join(output_dir, "review_embeddings_mpnet.faiss")
    faiss.write_index(index, faiss_path)
    print(f"✓ Saved FAISS index to {faiss_path}")
    
    # Create mapping: faiss_index -> hotel_id (each review maps back to its hotel for result retrieval)
    mapping = {i: hotel_id for i, hotel_id in enumerate(hotel_ids)}
    mapping_path = os.path.join(output_dir, "review_id_mapping_mpnet.json")
    
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Saved mapping to {mapping_path}")
    
    return faiss_path, mapping_path


def main():
    """Main execution"""
    print("=" * 60)
    print("FAISS Embedding Generation Script")
    print("Model: all-mpnet-base-v2 (768 dimensions)")
    print("=" * 60)
    
    # Initialize clients with mpnet model
    print("\nInitializing clients with all-mpnet-base-v2 model...")
    neo4j_client = Neo4jClient()
    neo4j_client.connect()
    
    embedding_client = EmbeddingClient(model_name="all-mpnet-base-v2")
    
    try:
        # Create hotel embeddings
        hotel_faiss, hotel_mapping = create_hotel_embeddings(
            neo4j_client,
            embedding_client
        )
        
        # Create visa embeddings
        visa_faiss, visa_mapping = create_visa_embeddings(
            neo4j_client,
            embedding_client
        )
        
        # Create review embeddings
        review_faiss, review_mapping = create_review_embeddings(
            neo4j_client,
            embedding_client
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("✓ EMBEDDING GENERATION COMPLETE (all-mpnet-base-v2)")
        print("=" * 60)
        print("\nGenerated files:")
        if hotel_faiss:
            print(f"  • {hotel_faiss}")
            print(f"  • {hotel_mapping}")
        if visa_faiss:
            print(f"  • {visa_faiss}")
            print(f"  • {visa_mapping}")
        if review_faiss:
            print(f"  • {review_faiss}")
            print(f"  • {review_mapping}")
        
        print("\nBoth embedding models are now ready!")
        print("UI can switch between:")
        print("  • all-MiniLM-L6-v2 (384 dims, faster)")
        print("  • all-mpnet-base-v2 (768 dims, higher quality)")
        print("=" * 60)
        
    finally:
        # Cleanup
        neo4j_client.close()


if __name__ == "__main__":
    main()
"""
Create Embeddings Script - Generate FAISS indexes for hotels and reviews
Run this once after creating the knowledge graph to enable semantic search
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
    Build rich feature string for hotel embedding
    
    Args:
        hotel: Hotel dict with all properties
        
    Returns:
        Feature string combining all hotel attributes including visa info
    """
    # Handle None values
    name = hotel.get('name', 'Unknown')
    city = hotel.get('city', 'Unknown')
    country = hotel.get('country', 'Unknown')
    star_rating = hotel.get('star_rating', 0.0)
    avg_score = hotel.get('average_reviews_score', 0.0)
    cleanliness = hotel.get('cleanliness_base', 0.0)
    comfort = hotel.get('comfort_base', 0.0)
    facilities = hotel.get('facilities_base', 0.0)
    location = hotel.get('location_base', 0.0)
    staff = hotel.get('staff_base', 0.0)
    value = hotel.get('value_for_money_base', 0.0)
    has_visa_reqs = hotel.get('has_visa_requirements', False)
    visa_types = hotel.get('visa_types', [])
    
    # Build feature string with visa information
    if has_visa_reqs and visa_types:
        # Filter out None values
        valid_types = [vt for vt in visa_types if vt]
        visa_text = f"{country} requires visa for travel" if valid_types else f"{country} destination"
    else:
        visa_text = f"{country} destination"
    
    feature_string = (
        f"{name} in {city}, {country}. {visa_text}. "
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
    print("\n=== Creating Hotel Embeddings ===")
    
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
    
    # Save FAISS index
    faiss_path = os.path.join(output_dir, "hotel_embeddings.faiss")
    faiss.write_index(index, faiss_path)
    print(f"✓ Saved FAISS index to {faiss_path}")
    
    # Create mapping: faiss_index -> hotel_id
    mapping = {i: hotel_id for i, hotel_id in enumerate(hotel_ids)}
    mapping_path = os.path.join(output_dir, "hotel_id_mapping.json")
    
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Saved mapping to {mapping_path}")
    
    return faiss_path, mapping_path





def main():
    """Main execution"""
    print("=" * 60)
    print("FAISS Embedding Generation Script")
    print("=" * 60)
    
    # Initialize clients
    print("\nInitializing clients...")
    neo4j_client = Neo4jClient()
    neo4j_client.connect()
    
    embedding_client = EmbeddingClient()
    
    try:
        # Create hotel embeddings (with visa information)
        hotel_faiss, hotel_mapping = create_hotel_embeddings(
            neo4j_client,
            embedding_client
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("✓ EMBEDDING GENERATION COMPLETE")
        print("=" * 60)
        print("\nGenerated files:")
        if hotel_faiss:
            print(f"  • {hotel_faiss}")
            print(f"  • {hotel_mapping}")
        
        print("\nYou can now run embedding_workflow and hybrid_workflow!")
        print("=" * 60)
        
    finally:
        # Cleanup
        neo4j_client.close()


if __name__ == "__main__":
    main()
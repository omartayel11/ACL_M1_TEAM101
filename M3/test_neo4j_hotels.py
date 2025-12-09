"""
Test script to check what hotels exist in Neo4j
"""
import sys
from pathlib import Path

# Add M3 to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import ConfigLoader
from utils.neo4j_client import Neo4jClient
from components.query_executor import QueryExecutor

def main():
    # Load config
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    print(f"✓ Configuration loaded")
    
    # Connect to Neo4j
    query_executor = QueryExecutor()
    print(f"✓ Connected to Neo4j")
    
    # Query 1: Get all hotel_ids
    cypher = "MATCH (h:Hotel) RETURN h.hotel_id AS hotel_id ORDER BY h.hotel_id"
    results = query_executor.execute(cypher)
    print(f"\n✓ Found {len(results)} hotels in Neo4j")
    print(f"Hotel IDs: {[r['hotel_id'] for r in results[:30]]}")
    
    # Query 2: Try to fetch hotel with ID 5
    print("\n" + "="*60)
    print("Testing fetch of hotel_id=5:")
    cypher = """
    MATCH (h:Hotel {hotel_id: $hotel_id})
    OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
    RETURN h.hotel_id AS hotel_id,
           h.name AS hotel_name,
           h.star_rating AS star_rating,
           c.name AS city,
           country.name AS country
    """
    results = query_executor.execute(cypher, {"hotel_id": 5})
    print(f"Results: {results}")
    
    # Query 3: Check what properties Hotel nodes have
    print("\n" + "="*60)
    print("Checking Hotel node properties:")
    cypher = "MATCH (h:Hotel) RETURN h LIMIT 1"
    results = query_executor.execute(cypher)
    if results:
        print(f"Sample hotel properties: {list(results[0]['h'].keys())}")
        print(f"Sample hotel data: {dict(results[0]['h'])}")
    
    query_executor.neo4j_client.close()
    print("\n✓ Neo4j connection closed")

if __name__ == "__main__":
    main()

"""
Vector Searcher for Graph-RAG Hotel Travel Assistant
Performs vector similarity search using FAISS indexes
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import faiss
from components.query_executor import QueryExecutor


class VectorSearcher:
    """
    Perform vector similarity search using FAISS.
    Loads FAISS indexes for hotels and reviews, searches for similar vectors,
    and enriches results with full node data from Neo4j.
    """
    
    def __init__(self, index_dir: Optional[str] = None):
        """
        Initialize vector searcher
        
        Args:
            index_dir: Directory containing FAISS indexes and mappings (default: M3/)
        """
        if index_dir is None:
            # Default to M3 directory
            index_dir = Path(__file__).parent.parent
        else:
            index_dir = Path(index_dir)
        
        self.index_dir = index_dir
        self.hotel_index = None
        self.review_index = None
        self.hotel_mapping = None
        self.review_mapping = None
        self.query_executor = QueryExecutor()
        
        # Try to load indexes on initialization
        self._load_indexes()
    
    def _load_indexes(self):
        """Load FAISS indexes and ID mappings from disk"""
        try:
            # Load hotel index
            hotel_index_path = self.index_dir / "hotel_embeddings.faiss"
            hotel_mapping_path = self.index_dir / "hotel_id_mapping.json"
            
            if hotel_index_path.exists() and hotel_mapping_path.exists():
                self.hotel_index = faiss.read_index(str(hotel_index_path))
                with open(hotel_mapping_path, 'r') as f:
                    self.hotel_mapping = json.load(f)
                print(f"✓ Loaded hotel index: {self.hotel_index.ntotal} vectors")
            else:
                print(f"Warning: Hotel FAISS index not found at {hotel_index_path}")
            
            # Load review index
            review_index_path = self.index_dir / "review_embeddings.faiss"
            review_mapping_path = self.index_dir / "review_id_mapping.json"
            
            if review_index_path.exists() and review_mapping_path.exists():
                self.review_index = faiss.read_index(str(review_index_path))
                with open(review_mapping_path, 'r') as f:
                    self.review_mapping = json.load(f)
                print(f"✓ Loaded review index: {self.review_index.ntotal} vectors")
            else:
                print(f"Warning: Review FAISS index not found at {review_index_path}")
                
        except Exception as e:
            print(f"Error loading FAISS indexes: {e}")
            print("Run create_embeddings.py to generate indexes")
    
    def load_index(self, index_path: str):
        """
        Load a specific FAISS index from disk
        
        Args:
            index_path: Path to FAISS index file
        """
        try:
            if "hotel" in index_path.lower():
                self.hotel_index = faiss.read_index(index_path)
                print(f"✓ Loaded hotel index from {index_path}")
            elif "review" in index_path.lower():
                self.review_index = faiss.read_index(index_path)
                print(f"✓ Loaded review index from {index_path}")
        except Exception as e:
            print(f"Error loading index from {index_path}: {e}")
            raise
    
    def search(
        self,
        embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7,
        search_type: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in FAISS index
        
        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)
            search_type: "hotels", "reviews", or "both"
            
        Returns:
            List of similar nodes with similarity scores and full details from Neo4j
        """
        results = []
        
        # Convert embedding to numpy array
        query_vector = np.array([embedding], dtype=np.float32)
        
        # Search hotels
        if search_type in ["hotels", "both"] and self.hotel_index is not None:
            hotel_results = self._search_index(
                self.hotel_index,
                self.hotel_mapping,
                query_vector,
                limit,
                threshold,
                "hotel"
            )
            results.extend(hotel_results)
        
        # Search reviews
        if search_type in ["reviews", "both"] and self.review_index is not None:
            review_results = self._search_index(
                self.review_index,
                self.review_mapping,
                query_vector,
                limit,
                threshold,
                "review"
            )
            results.extend(review_results)
        
        # Sort by similarity score
        results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Limit total results
        return results[:limit]
    
    def _search_index(
        self,
        index: faiss.Index,
        mapping: Dict[str, str],
        query_vector: np.ndarray,
        limit: int,
        threshold: float,
        node_type: str
    ) -> List[Dict[str, Any]]:
        """
        Search a specific FAISS index
        
        Args:
            index: FAISS index
            mapping: Mapping from FAISS index to node IDs
            query_vector: Query embedding
            limit: Max results
            threshold: Similarity threshold
            node_type: "hotel" or "review"
            
        Returns:
            List of search results with Neo4j node details
        """
        try:
            # FAISS returns L2 distances, convert to cosine similarity
            # Search with more results to filter by threshold
            distances, indices = index.search(query_vector, limit * 2)
            
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                # Convert L2 distance to cosine similarity (approximate)
                # For normalized vectors: similarity = 1 - (distance^2 / 2)
                similarity = 1 - (dist / 2)
                
                if similarity < threshold:
                    continue
                
                # Get node ID from mapping
                node_id = mapping.get(str(idx))
                if not node_id:
                    continue
                
                # Fetch full node details from Neo4j
                node_details = self._fetch_node_from_neo4j(node_id, node_type)
                
                if node_details:
                    node_details['similarity_score'] = float(similarity)
                    node_details['node_type'] = node_type
                    results.append(node_details)
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            print(f"Error searching {node_type} index: {e}")
            return []
    
    def _fetch_node_from_neo4j(self, node_id: str, node_type: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full node details from Neo4j
        
        Args:
            node_id: Node ID (hotel_id or review_id)
            node_type: "hotel" or "review"
            
        Returns:
            Node details dictionary or None
        """
        try:
            if node_type == "hotel":
                cypher = """
                MATCH (h:Hotel {hotel_id: $hotel_id})
                OPTIONAL MATCH (h)-[:LOCATED_IN]->(c:City)-[:LOCATED_IN]->(country:Country)
                RETURN h.hotel_id AS hotel_id,
                       h.name AS hotel_name,
                       h.star_rating AS star_rating,
                       h.average_reviews_score AS avg_score,
                       h.cleanliness_base AS cleanliness,
                       h.comfort_base AS comfort,
                       h.facilities_base AS facilities,
                       h.location_base AS location,
                       h.staff_base AS staff,
                       h.value_for_money_base AS value,
                       c.name AS city,
                       country.name AS country
                """
                params = {"hotel_id": node_id}
            else:  # review
                cypher = """
                MATCH (r:Review {review_id: $review_id})
                OPTIONAL MATCH (r)-[:REVIEWED]->(h:Hotel)
                RETURN r.review_id AS review_id,
                       r.text AS review_text,
                       r.score_overall AS score,
                       r.date AS date,
                       h.hotel_id AS hotel_id,
                       h.name AS hotel_name
                """
                params = {"review_id": node_id}
            
            results = self.query_executor.execute(cypher, params)
            return results[0] if results else None
            
        except Exception as e:
            print(f"Error fetching {node_type} {node_id} from Neo4j: {e}")
            return None
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded indexes"""
        return {
            'hotel_index_loaded': self.hotel_index is not None,
            'review_index_loaded': self.review_index is not None,
            'hotel_vectors': self.hotel_index.ntotal if self.hotel_index else 0,
            'review_vectors': self.review_index.ntotal if self.review_index else 0
        }


if __name__ == "__main__":
    # Test vector searcher
    from components.embedding_generator import EmbeddingGenerator
    
    print("=== Vector Searcher Test ===\n")
    
    searcher = VectorSearcher()
    print(f"Index stats: {searcher.get_index_stats()}\n")
    
    if searcher.hotel_index is not None or searcher.review_index is not None:
        # Generate test embedding
        generator = EmbeddingGenerator()
        test_query = "luxury hotels with great location"
        embedding = generator.embed(test_query)
        
        print(f"Test query: {test_query}")
        print(f"Embedding dimension: {len(embedding)}\n")
        
        # Search
        results = searcher.search(
            embedding=embedding,
            limit=5,
            threshold=0.5,
            search_type="both"
        )
        
        print(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Type: {result.get('node_type')}")
            print(f"   Similarity: {result.get('similarity_score', 0):.4f}")
            if result.get('node_type') == 'hotel':
                print(f"   Hotel: {result.get('hotel_name')} ({result.get('city')})")
                print(f"   Score: {result.get('avg_score')}")
            else:
                print(f"   Review: {result.get('review_text', '')[:100]}...")
            print()
    else:
        print("No FAISS indexes loaded. Run create_embeddings.py first.")

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
    Loads FAISS index for hotels, searches for similar vectors,
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
        self.hotel_mapping = None
        self.visa_index = None
        self.visa_mapping = None
        self.review_index = None
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
            
            # Load visa index
            visa_index_path = self.index_dir / "visa_embeddings.faiss"
            visa_mapping_path = self.index_dir / "visa_id_mapping.json"
            
            if visa_index_path.exists() and visa_mapping_path.exists():
                self.visa_index = faiss.read_index(str(visa_index_path))
                with open(visa_mapping_path, 'r') as f:
                    self.visa_mapping = json.load(f)
                print(f"✓ Loaded visa index: {self.visa_index.ntotal} vectors")
            else:
                print(f"Warning: Visa FAISS index not found at {visa_index_path}")
            
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
    
    def _load_model_indexes(self, model_suffix: str = ''):
        """
        Load FAISS indexes for a specific embedding model
        
        Args:
            model_suffix: Suffix for model-specific files ('' for MiniLM, '_mpnet' for MPNet)
        """
        try:
            # Load hotel index
            hotel_index_path = self.index_dir / f"hotel_embeddings{model_suffix}.faiss"
            hotel_mapping_path = self.index_dir / f"hotel_id_mapping{model_suffix}.json"
            
            if hotel_index_path.exists() and hotel_mapping_path.exists():
                self.hotel_index = faiss.read_index(str(hotel_index_path))
                with open(hotel_mapping_path, 'r') as f:
                    self.hotel_mapping = json.load(f)
                print(f"✓ Loaded hotel index ({model_suffix or 'default'}): {self.hotel_index.ntotal} vectors")
            else:
                print(f"Warning: Hotel FAISS index not found for {model_suffix or 'default'} model")
            
            # Load visa index
            visa_index_path = self.index_dir / f"visa_embeddings{model_suffix}.faiss"
            visa_mapping_path = self.index_dir / f"visa_id_mapping{model_suffix}.json"
            
            if visa_index_path.exists() and visa_mapping_path.exists():
                self.visa_index = faiss.read_index(str(visa_index_path))
                with open(visa_mapping_path, 'r') as f:
                    self.visa_mapping = json.load(f)
                print(f"✓ Loaded visa index ({model_suffix or 'default'}): {self.visa_index.ntotal} vectors")
            else:
                print(f"Warning: Visa FAISS index not found for {model_suffix or 'default'} model")
            
            # Load review index
            review_index_path = self.index_dir / f"review_embeddings{model_suffix}.faiss"
            review_mapping_path = self.index_dir / f"review_id_mapping{model_suffix}.json"
            
            if review_index_path.exists() and review_mapping_path.exists():
                self.review_index = faiss.read_index(str(review_index_path))
                with open(review_mapping_path, 'r') as f:
                    self.review_mapping = json.load(f)
                print(f"✓ Loaded review index ({model_suffix or 'default'}): {self.review_index.ntotal} vectors")
            else:
                print(f"Warning: Review FAISS index not found for {model_suffix or 'default'} model")
                
        except Exception as e:
            print(f"Error loading FAISS indexes for {model_suffix or 'default'} model: {e}")
    
    def load_index(self, index_path: str):
        """
        Load hotel FAISS index from disk
        
        Args:
            index_path: Path to hotel FAISS index file
        """
        try:
            self.hotel_index = faiss.read_index(index_path)
            print(f"✓ Loaded hotel index from {index_path}")
        except Exception as e:
            print(f"Error loading index from {index_path}: {e}")
            raise
    
    def search(
        self,
        embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7,
        intent: str = None,
        entities: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar items in FAISS indexes based on intent and entities.
        
        This is the main search entry point that:
        1. Uses select_faiss_indexes() to determine which indexes to search
        2. Uses multi_index_search() to search them and merge results
        3. Falls back to intent-only routing for backward compatibility
        
        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)
            intent: Query intent to determine which index to search
            entities: Extracted entities dict (city, traveller_type, from_country, etc.)
            
        Returns:
            List of similar items with similarity scores and full details from Neo4j
        """
        if entities is None:
            entities = {}
        
        results = []
        
        # Convert embedding to numpy array
        query_vector = np.array([embedding], dtype=np.float32)
        
        # NEW: Use entity-driven index selection
        if entities:
            # Intelligent routing: use both intent and entities
            indexes_to_search = self.select_faiss_indexes(intent, entities)
            
            if indexes_to_search:
                # Search selected indexes with multi-index merge
                results = self.multi_index_search(
                    embedding,
                    indexes_to_search,
                    limit,
                    threshold
                )
        
        # FALLBACK: If no entities or no results, use intent-based routing (backward compatible)
        if not results:
            if intent == "VisaQuestion" and self.visa_index is not None:
                # Search visa index for visa questions
                results = self._search_index(
                    self.visa_index,
                    self.visa_mapping,
                    query_vector,
                    limit,
                    threshold,
                    "visa"
                )
            elif self.hotel_index is not None:
                # Search hotel index for all other queries
                results = self._search_index(
                    self.hotel_index,
                    self.hotel_mapping,
                    query_vector,
                    limit,
                    threshold,
                    "hotel"
                )
        
        return results
    
    def select_faiss_indexes(self, intent: str, entities: Dict[str, Any] = None) -> List[str]:
        """
        Select which FAISS indexes to search based on intent and extracted entities.
        
        This is the core of entity-driven index selection:
        - Entities like traveller_type or from_country trigger review embeddings
        - Intent VisaQuestion triggers visa embeddings
        - Hotel-related intents trigger hotel embeddings
        
        Args:
            intent: Query intent (e.g., "HotelRecommendation", "VisaQuestion")
            entities: Extracted entities dict with keys like traveller_type, from_country, city, etc.
            
        Returns:
            List of index names to search: ["hotel"], ["visa"], ["review"], or combinations
        """
        if entities is None:
            entities = {}
        
        indexes_to_search = []
        
        # Rule 1: If traveller_type or from_country present, search review embeddings
        # These entities indicate user demographic info relevant to reviews
        if "traveller_type" in entities or "from_country" in entities:
            if self.review_index is not None:
                indexes_to_search.append("review")
        
        # Rule 2: If intent is VisaQuestion, search visa embeddings
        if intent == "VisaQuestion":
            if self.visa_index is not None:
                indexes_to_search.append("visa")
        
        # Rule 3: If intent is ReviewLookup, search review embeddings
        if intent == "ReviewLookup":
            if self.review_index is not None and "review" not in indexes_to_search:
                indexes_to_search.append("review")
        
        # Rule 4: For all other intents (hotel search, recommendation, etc.), search hotel embeddings
        # Hotel-related intents: HotelSearch, HotelRecommendation, AmenityFilter, LocationQuery, GeneralQuestionAnswering, CasualConversation
        hotel_intents = ["HotelSearch", "HotelRecommendation", "AmenityFilter", "LocationQuery", 
                        "GeneralQuestionAnswering", "CasualConversation"]
        if intent in hotel_intents or intent not in ["VisaQuestion", "ReviewLookup"]:
            if self.hotel_index is not None and "hotel" not in indexes_to_search:
                indexes_to_search.append("hotel")
        
        # Default: if no intent matched and no entities, search hotels
        if not indexes_to_search and self.hotel_index is not None:
            indexes_to_search.append("hotel")
        
        return indexes_to_search
    
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
        Search a FAISS index
        
        Args:
            index: FAISS index
            mapping: Mapping from FAISS index to node IDs
            query_vector: Query embedding
            limit: Max results
            threshold: Similarity threshold
            node_type: "hotel" or "visa"
            
        Returns:
            List of search results with Neo4j details
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
    
    def multi_index_search(
        self,
        embedding: List[float],
        indexes: List[str],
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search multiple FAISS indexes and merge results intelligently.
        
        Hotels appearing in multiple indexes (e.g., both hotel and review embeddings)
        get boosted scores because they match from multiple perspectives.
        
        Args:
            embedding: Query embedding vector
            indexes: List of index names to search ["hotel", "visa", "review"]
            limit: Maximum number of results
            threshold: Minimum similarity score
            
        Returns:
            Merged list of results from all indexes, with boosted scores for multi-index hits
        """
        query_vector = np.array([embedding], dtype=np.float32)
        all_results = {}  # Key: node_id, Value: aggregated result
        
        # Search each requested index
        for index_name in indexes:
            if index_name == "hotel" and self.hotel_index is not None:
                index_results = self._search_index(
                    self.hotel_index,
                    self.hotel_mapping,
                    query_vector,
                    limit * 2,  # Get more to allow filtering
                    threshold,
                    "hotel"
                )
                for result in index_results:
                    node_id = result.get('hotel_id')
                    if node_id:
                        if node_id not in all_results:
                            all_results[node_id] = result
                        else:
                            # Boost score if hotel appears in multiple indexes
                            all_results[node_id]['similarity_score'] += result.get('similarity_score', 0) * 0.5
                            all_results[node_id]['search_indexes'] = all_results[node_id].get('search_indexes', []) + [index_name]
            
            elif index_name == "visa" and self.visa_index is not None:
                index_results = self._search_index(
                    self.visa_index,
                    self.visa_mapping,
                    query_vector,
                    limit * 2,
                    threshold,
                    "visa"
                )
                for result in index_results:
                    node_id = f"{result.get('from_country')}_to_{result.get('to_country')}"
                    if node_id not in all_results:
                        all_results[node_id] = result
            
            elif index_name == "review" and self.review_index is not None:
                index_results = self._search_index(
                    self.review_index,
                    self.review_mapping,
                    query_vector,
                    limit * 2,
                    threshold,
                    "review"
                )
                for result in index_results:
                    node_id = result.get('hotel_id')
                    if node_id:
                        if node_id not in all_results:
                            all_results[node_id] = result
                        else:
                            # Boost score if hotel review matches user query
                            all_results[node_id]['similarity_score'] += result.get('similarity_score', 0) * 0.5
                            all_results[node_id]['has_review_match'] = True
        
        # Sort by similarity score and return top results
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x.get('similarity_score', 0),
            reverse=True
        )
        
        return sorted_results[:limit]
    
    def _fetch_node_from_neo4j(self, node_id: str, node_type: str) -> Optional[Dict[str, Any]]:
        """
        Fetch full node details from Neo4j
        
        Args:
            node_id: Node ID (hotel_id, visa_id like "Egypt_to_France", or hotel_id for reviews)
            node_type: "hotel", "visa", or "review"
            
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
                # Convert node_id to string as hotel_id is stored as string in Neo4j
                params = {"hotel_id": str(node_id)}
            elif node_type == "review":
                # For reviews, node_id is actually the hotel_id from the review embedding mapping
                # Fetch hotel details (same as hotel node_type)
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
                params = {"hotel_id": str(node_id)}
            elif node_type == "visa":
                # Parse visa_id like "Egypt_to_France"
                parts = node_id.split("_to_")
                if len(parts) == 2:
                    from_country, to_country = parts[0], parts[1]
                    cypher = """
                    MATCH (from:Country {name: $from_country})-[v:NEEDS_VISA]->(to:Country {name: $to_country})
                    RETURN from.name AS from_country,
                           to.name AS to_country,
                           v.visa_type AS visa_type,
                           true AS visa_required
                    """
                    params = {"from_country": from_country, "to_country": to_country}
                else:
                    return None
            else:
                return None
            
            results = self.query_executor.execute(cypher, params)
            return results[0] if results else None
            
        except Exception as e:
            print(f"Error fetching {node_type} {node_id} from Neo4j: {e}")
            return None
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded indexes"""
        return {
            'hotel_index_loaded': self.hotel_index is not None,
            'hotel_vectors': self.hotel_index.ntotal if self.hotel_index else 0,
            'visa_index_loaded': self.visa_index is not None,
            'visa_vectors': self.visa_index.ntotal if self.visa_index else 0
        }


if __name__ == "__main__":
    # Test vector searcher
    from components.embedding_generator import EmbeddingGenerator
    
    print("=== Vector Searcher Test ===\n")
    
    searcher = VectorSearcher()
    print(f"Index stats: {searcher.get_index_stats()}\n")
    
    if searcher.hotel_index is not None:
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
            threshold=0.5
        )
        
        print(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. Hotel: {result.get('hotel_name')} ({result.get('city')})")
            print(f"   Similarity: {result.get('similarity_score', 0):.4f}")
            print(f"   Score: {result.get('avg_score')}")
            print()
    else:
        print("No hotel index loaded. Run create_embeddings.py first.")

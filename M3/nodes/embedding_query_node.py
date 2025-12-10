"""
Embedding Query Node - Generate embedding and search FAISS
"""

from state.graph_state import GraphState
from components.embedding_generator import EmbeddingGenerator
from components.vector_searcher import VectorSearcher
from utils.config_loader import ConfigLoader

# Initialize components once
generator = EmbeddingGenerator()
searcher = VectorSearcher()
config = ConfigLoader()


def embedding_query_node(state: GraphState) -> GraphState:
    """
    Generate query embedding and perform vector search
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with embedding results
    """
    query = state.get("user_query", "")
    
    # Generate embedding
    embedding = generator.embed(query)
    
    # Search FAISS indexes
    results = []
    if embedding:
        try:
            limit = config.get('retrieval.embedding.max_results', 10)
            threshold = config.get('retrieval.embedding.similarity_threshold', 0.7)
            
            print(f"\n🧠 [EMBEDDING RETRIEVAL]")
            print(f"Query: {query}")
            print(f"Embedding dimensions: {len(embedding)}")
            print(f"Searching hotels | Top-K: {limit} | Threshold: {threshold}")
            
            results = searcher.search(
                embedding=embedding,
                limit=limit,
                threshold=threshold
            )
            
            print(f"✓ Retrieved {len(results)} results from vector index")
            if results:
                print(f"Top result: {results[0].get('hotel_name', 'N/A')} (score: {results[0].get('similarity_score', 'N/A'):.3f})")
        except Exception as e:
            print(f"❌ Embedding search failed: {e}")
            results = []
    
    # Return only changed fields
    return {
        "query_embedding": embedding,
        "embedding_results": results
    }


if __name__ == "__main__":
    # Test embedding query node
    test_state: GraphState = {
        "user_query": "luxury hotels with great location"
    }
    
    result = embedding_query_node(test_state)
    print("Embedding Query Node Test:")
    print(f"Query: {test_state['user_query']}")
    print(f"Embedding dimension: {len(result.get('query_embedding', []))}")
    print(f"Results count: {len(result.get('embedding_results', []))}")
    if result.get('embedding_results'):
        print(f"Top result: {result['embedding_results'][0].get('hotel_name', 'N/A')}")

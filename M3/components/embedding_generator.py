"""
Embedding Generator for Graph-RAG Hotel Travel Assistant
Generates embeddings for text using embedding client
"""

from typing import List, Optional
from utils.embedding_client import EmbeddingClient


class EmbeddingGenerator:
    """
    Generate embeddings for text queries.
    Wrapper around EmbeddingClient for component layer.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding generator
        
        Args:
            model_name: Embedding model name (default from config)
        """
        self.embedding_client = EmbeddingClient(model_name=model_name)
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not text or not text.strip():
            return []
        
        return self.embedding_client.encode(text)
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_client.dimension
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self.embedding_client.model_name


if __name__ == "__main__":
    # Test embedding generator
    generator = EmbeddingGenerator()
    
    print("=== Embedding Generator Test ===\n")
    print(f"Model: {generator.get_model_name()}")
    print(f"Dimension: {generator.get_dimension()}\n")
    
    # Test embedding generation
    test_text = "Find hotels in Paris with good ratings"
    embedding = generator.embed(test_text)
    
    print(f"Text: {test_text}")
    print(f"Embedding shape: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

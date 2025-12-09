"""
Embedding client for Graph-RAG Hotel Travel Assistant
Manages sentence-transformer models for generating embeddings
"""

from typing import List, Optional, Union, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingClient:
    """
    Singleton embedding client using sentence-transformers.
    Supports multiple models with in-memory caching.
    """
    
    _instance: Optional['EmbeddingClient'] = None
    _model: Optional[SentenceTransformer] = None
    _model_name: str = "all-MiniLM-L6-v2"
    _dimension: int = 384
    _cache: dict = {}
    
    def __new__(cls, model_name: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding client
        
        Args:
            model_name: Sentence-transformer model name (if None, uses default from config)
                Options: 'all-MiniLM-L6-v2' (384 dims, fast)
                        'all-mpnet-base-v2' (768 dims, better quality)
        """
        if self._model is None:
            # Load default model from config if not specified
            if model_name is None:
                from .config_loader import ConfigLoader
                config = ConfigLoader()
                model_name = config.get('embedding.default_model', 'all-MiniLM-L6-v2')
            
            self._model_name = model_name
            self.load_model(model_name)
    
    def load_model(self, model_name: str) -> bool:
        """
        Load a sentence-transformer model
        
        Args:
            model_name: Model identifier from sentence-transformers
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            print(f"Loading embedding model: {model_name}...")
            self._model = SentenceTransformer(model_name)
            self._model_name = model_name
            
            # Get embedding dimension
            test_embedding = self._model.encode("test")
            self._dimension = len(test_embedding)
            
            print(f"✓ Embedding model loaded: {model_name} ({self._dimension} dimensions)")
            return True
            
        except Exception as e:
            print(f"✗ Failed to load embedding model {model_name}: {e}")
            self._model = None
            return False
    
    def encode(
        self,
        text: Union[str, List[str]],
        normalize: bool = True,
        show_progress: bool = False
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embedding(s) for text
        
        Args:
            text: Single text string or list of strings
            normalize: Normalize embeddings to unit length (for cosine similarity)
            show_progress: Show progress bar for batch encoding
            
        Returns:
            Single embedding vector or list of vectors
            
        Example:
            >>> client = EmbeddingClient()
            >>> embedding = client.encode("Hotels in Paris")
            >>> len(embedding)
            384
        """
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            # Check cache for single string
            if isinstance(text, str) and text in self._cache:
                return self._cache[text]
            
            # Generate embeddings
            embeddings = self._model.encode(
                text,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            
            # Convert to list format for JSON serialization
            if isinstance(text, str):
                result = embeddings.tolist()
                # Cache single embedding
                if len(self._cache) < 1000:  # Limit cache size
                    self._cache[text] = result
                return result
            else:
                return [emb.tolist() for emb in embeddings]
                
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for batch of texts efficiently
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            normalize: Normalize embeddings
            
        Returns:
            List of embedding vectors
        """
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            print(f"Error in batch encoding: {e}")
            raise
    
    def similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
    def get_dimension(self) -> int:
        """Get embedding dimension of current model"""
        return self._dimension
    
    def get_model_name(self) -> str:
        """Get current model name"""
        return self._model_name
    
    def clear_cache(self):
        """Clear embedding cache"""
        self._cache.clear()
        print("✓ Embedding cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached embeddings"""
        return len(self._cache)
    
    def get_config(self) -> dict:
        """Get current configuration"""
        return {
            'model_name': self._model_name,
            'dimension': self._dimension,
            'loaded': self._model is not None,
            'cache_size': len(self._cache)
        }
    
    @staticmethod
    def get_available_models() -> List[Dict[str, Any]]:
        """
        Get list of available embedding models from config
        
        Returns:
            List of model dicts with name, display_name, description, dimensions
        """
        from .config_loader import ConfigLoader
        config = ConfigLoader()
        return config.get('embedding.available_models', [
            {
                'name': 'all-MiniLM-L6-v2',
                'display_name': 'MiniLM L6 v2',
                'description': 'Fast, 384 dimensions',
                'dimensions': 384
            },
            {
                'name': 'all-mpnet-base-v2',
                'display_name': 'MPNet Base v2',
                'description': 'Better quality, 768 dimensions',
                'dimensions': 768
            }
        ])


# Convenience function for quick access
def get_embedding_client() -> EmbeddingClient:
    """Get EmbeddingClient singleton instance"""
    return EmbeddingClient()


if __name__ == "__main__":
    # Test embedding client
    client = EmbeddingClient()
    
    print("\n=== Embedding Client Test ===")
    print(f"Config: {client.get_config()}")
    
    if client._model:
        print("\n--- Test 1: Single text encoding ---")
        text = "Find me hotels in Paris"
        embedding = client.encode(text)
        print(f"Text: {text}")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        print("\n--- Test 2: Batch encoding ---")
        texts = [
            "Hotels in Paris",
            "Best hotels for families",
            "Luxury accommodations in London"
        ]
        embeddings = client.encode(texts)
        print(f"Encoded {len(embeddings)} texts")
        print(f"Dimensions: {[len(e) for e in embeddings]}")
        
        print("\n--- Test 3: Similarity calculation ---")
        text1 = "Hotels in Paris"
        text2 = "Accommodations in Paris"
        text3 = "Restaurants in Tokyo"
        
        emb1 = client.encode(text1)
        emb2 = client.encode(text2)
        emb3 = client.encode(text3)
        
        sim_12 = client.similarity(emb1, emb2)
        sim_13 = client.similarity(emb1, emb3)
        
        print(f"Similarity '{text1}' vs '{text2}': {sim_12:.4f}")
        print(f"Similarity '{text1}' vs '{text3}': {sim_13:.4f}")
        
        print(f"\n✓ Cache size: {client.get_cache_size()} embeddings")
    else:
        print("\n✗ Model not loaded")

"""
Quick test for MPNet embedding model files
"""
import faiss
import json
from sentence_transformers import SentenceTransformer

def test_mpnet_embeddings():
    print("=== Testing MPNet Embedding Files ===\n")
    
    # Load the model
    print("Loading all-mpnet-base-v2 model...")
    model = SentenceTransformer('all-mpnet-base-v2')
    print(f"✓ Model loaded. Dimension: {model.get_sentence_embedding_dimension()}\n")
    
    # Test hotel embeddings
    print("1. Testing hotel_embeddings_mpnet.faiss...")
    try:
        hotel_index = faiss.read_index("hotel_embeddings_mpnet.faiss")
        with open("hotel_id_mapping_mpnet.json", 'r') as f:
            hotel_mapping = json.load(f)
        print(f"   ✓ Hotels: {hotel_index.ntotal} vectors, {len(hotel_mapping)} mappings")
        print(f"   ✓ Dimension: {hotel_index.d}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test visa embeddings
    print("\n2. Testing visa_embeddings_mpnet.faiss...")
    try:
        visa_index = faiss.read_index("visa_embeddings_mpnet.faiss")
        with open("visa_id_mapping_mpnet.json", 'r') as f:
            visa_mapping = json.load(f)
        print(f"   ✓ Visas: {visa_index.ntotal} vectors, {len(visa_mapping)} mappings")
        print(f"   ✓ Dimension: {visa_index.d}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test review embeddings
    print("\n3. Testing review_embeddings_mpnet.faiss...")
    try:
        review_index = faiss.read_index("review_embeddings_mpnet.faiss")
        with open("review_id_mapping_mpnet.json", 'r') as f:
            review_mapping = json.load(f)
        print(f"   ✓ Reviews: {review_index.ntotal} vectors, {len(review_mapping)} mappings")
        print(f"   ✓ Dimension: {review_index.d}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test search functionality
    print("\n4. Testing search with MPNet model...")
    try:
        query = "luxury hotel in Cairo"
        query_embedding = model.encode([query])[0]
        
        distances, indices = hotel_index.search(query_embedding.reshape(1, -1), k=3)
        
        print(f"   Query: '{query}'")
        print(f"   Top 3 results:")
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
            # The mapping value is the feature string itself
            feature_string = hotel_mapping[str(idx)]
            # Extract hotel name from feature string (first part before " in ")
            hotel_name = feature_string.split(" in ")[0] if " in " in feature_string else feature_string[:50]
            print(f"   [{i}] {hotel_name} | Distance: {dist:.3f}")
        print("   ✓ Search working!")
    except Exception as e:
        print(f"   ✗ Search error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_mpnet_embeddings()
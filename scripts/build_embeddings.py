import json
import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.retrieval.vector_store import SupportVectorStore
from src.classification.main_classifier import EmbeddingIntentClassifier

def main():
    processed_path = Path("data/processed/apple_conversations.json")
    if not processed_path.exists():
        print(f"Error: {processed_path} not found. Please run scripts/preprocess.py first.")
        sys.exit(1)
        
    print(f"Loading processed conversations from {processed_path}...")
    with open(processed_path, "r", encoding="utf-8") as f:
        conversations = json.load(f)
        
    print(f"Loaded {len(conversations)} AppleSupport conversations.")
    
    # Initialize Intent Classifier for indexing metadata
    classifier = EmbeddingIntentClassifier()
    classifier.initialize("data/processed/intents.json")
    
    # Initialize Vector Store
    vector_store = SupportVectorStore(persist_dir="chroma_db", collection_name="apple_support_conversations")
    
    print("Indexing conversations into ChromaDB...")
    vector_store.index_conversations(conversations, intent_classifier=classifier)
    
    # Test retrieval
    test_query = "My battery drains within 2 hours after updating to iOS 11"
    print(f"\n--- TESTING RETRIEVAL FOR QUERY: '{test_query}' ---")
    results = vector_store.search(test_query, top_k=3, brand_filter="AppleSupport")
    for idx, res in enumerate(results, 1):
        print(f"\nRank {idx}: [Similarity: {res['similarity_score']:.4f}] (Conv ID: {res['conversation_id']}, Intent: {res['intent']})")
        print(f"  Customer: {res['customer_message']}")
        print(f"  Brand Reply: {res['brand_reply']}")

if __name__ == "__main__":
    main()

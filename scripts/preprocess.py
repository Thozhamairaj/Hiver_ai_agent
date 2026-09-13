import json
import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.preprocessing.reconstruct import (
    load_raw_tweets,
    reconstruct_conversations,
    filter_conversations_by_brand
)

def main():
    raw_path = Path("data/raw/twcs_sample.csv")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading raw tweets from {raw_path}...")
    tweets = load_raw_tweets(str(raw_path))
    print(f"Loaded {len(tweets)} tweet records.")
    
    print("Reconstructing conversation threads...")
    all_conversations = reconstruct_conversations(tweets)
    print(f"Reconstructed {len(all_conversations)} unique conversation threads.")
    
    # Save all conversations
    with open(output_dir / "all_conversations.json", "w", encoding="utf-8") as f:
        json.dump(all_conversations, f, indent=2)
        
    # Filter for AppleSupport
    target_brand = "AppleSupport"
    apple_conversations = filter_conversations_by_brand(all_conversations, target_brand)
    print(f"Filtered {len(apple_conversations)} conversation threads for brand '{target_brand}'.")
    
    with open(output_dir / "apple_conversations.json", "w", encoding="utf-8") as f:
        json.dump(apple_conversations, f, indent=2)
        
    print("\n--- SAMPLE RECONSTRUCTED APPLE CONVERSATION ---")
    if apple_conversations:
        sample = apple_conversations[0]
        print(f"Conversation ID: {sample['conversation_id']}")
        print(f"Customer Message: {sample['initial_customer_message']}")
        print(f"Brand Reply: {sample['brand_reply']}")
        print(f"Turn Count: {sample['message_count']}")
    
    print(f"\nPreprocessing successfully completed. Output written to {output_dir / 'apple_conversations.json'}")

if __name__ == "__main__":
    main()

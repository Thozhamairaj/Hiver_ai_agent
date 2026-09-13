import csv
import re
from typing import List, Dict, Any, Optional

def clean_tweet_text(text: str) -> str:
    """
    Clean raw tweet text while preserving customer semantics.
    - Normalizes extra whitespace.
    - Decodes common HTML entities (&amp;, &gt;, &lt;).
    """
    if not text:
        return ""
    text = text.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_raw_tweets(csv_path: str) -> List[Dict[str, Any]]:
    """
    Reads tweets from Kaggle TWCS CSV file.
    """
    tweets = []
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweets.append({
                "tweet_id": str(row["tweet_id"]).strip(),
                "author_id": str(row["author_id"]).strip(),
                "inbound": str(row["inbound"]).strip().lower() == "true",
                "created_at": str(row.get("created_at", "")).strip(),
                "text": clean_tweet_text(str(row.get("text", ""))),
                "response_tweet_id": str(row.get("response_tweet_id", "")).strip(),
                "in_response_to_tweet_id": str(row.get("in_response_to_tweet_id", "")).strip()
            })
    return tweets

def reconstruct_conversations(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reconstructs conversation threads from flat tweet records.
    Each conversation is indexed by its root tweet_id.
    """
    tweets_by_id = {t["tweet_id"]: t for t in tweets}
    
    # Trace parent pointer to find root tweet
    def get_root_id(tid: str, visited: Optional[set] = None) -> str:
        if visited is None:
            visited = set()
        if tid in visited:
            return tid
        visited.add(tid)
        
        parent_id = tweets_by_id[tid]["in_response_to_tweet_id"]
        if parent_id and parent_id in tweets_by_id:
            return get_root_id(parent_id, visited)
        return tid

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for tid in tweets_by_id:
        root_id = get_root_id(tid)
        if root_id not in groups:
            groups[root_id] = []
        groups[root_id].append(tweets_by_id[tid])
        
    conversations = []
    for root_id, thread in groups.items():
        # Sort thread messages by tweet_id / creation order
        sorted_thread = sorted(thread, key=lambda x: x["tweet_id"])
        
        customer_msgs = [t for t in sorted_thread if t["inbound"]]
        brand_msgs = [t for t in sorted_thread if not t["inbound"]]
        
        if not customer_msgs:
            continue
            
        initial_customer_msg = customer_msgs[0]
        brand_names = list({t["author_id"] for t in brand_msgs})
        primary_brand = brand_names[0] if brand_names else "Unknown"
        
        first_brand_reply = brand_msgs[0]["text"] if brand_msgs else ""
        
        dialog = []
        for t in sorted_thread:
            role = "customer" if t["inbound"] else "brand"
            dialog.append({
                "role": role,
                "author_id": t["author_id"],
                "text": t["text"],
                "tweet_id": t["tweet_id"]
            })
            
        conversations.append({
            "conversation_id": root_id,
            "brand": primary_brand,
            "all_brands": brand_names,
            "customer_user_id": initial_customer_msg["author_id"],
            "initial_customer_message": initial_customer_msg["text"],
            "all_customer_messages": " ".join([c["text"] for c in customer_msgs]),
            "brand_reply": first_brand_reply,
            "full_dialog": dialog,
            "message_count": len(sorted_thread),
            "created_at": initial_customer_msg["created_at"]
        })
        
    return conversations

def filter_conversations_by_brand(conversations: List[Dict[str, Any]], target_brand: str) -> List[Dict[str, Any]]:
    """
    Filter conversations to only include threads where the target brand participated.
    """
    return [c for c in conversations if target_brand.lower() in [b.lower() for b in c.get("all_brands", [])] or c.get("brand", "").lower() == target_brand.lower()]

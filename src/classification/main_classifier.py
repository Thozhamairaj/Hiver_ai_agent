import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

class EmbeddingIntentClassifier:
    """
    Main Intent Classifier using Sentence Transformers embeddings and cosine similarity matching.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.intent_embeddings = {}
        self.intents_data = []

    def load_intents(self, intents_json_path: str):
        with open(intents_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.intents_data = data["intents"]

    def initialize(self, intents_json_path: str = "data/processed/intents.json"):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            
        self.load_intents(intents_json_path)
        
        # Build prototype embeddings for each intent
        for intent_obj in self.intents_data:
            name = intent_obj["name"]
            desc = intent_obj["description"]
            examples = intent_obj.get("example_messages", [])
            
            # Combine description + example messages for robust prototype embedding
            text_corpus = [desc] + examples
            embeddings = self.model.encode(text_corpus, convert_to_tensor=False)
            mean_embedding = np.mean(embeddings, axis=0)
            # Normalize vector
            norm = np.linalg.norm(mean_embedding)
            if norm > 0:
                mean_embedding = mean_embedding / norm
            self.intent_embeddings[name] = mean_embedding

    def predict(self, text: str) -> Dict[str, Any]:
        if self.model is None or not self.intent_embeddings:
            self.initialize()
            
        text_embedding = self.model.encode([text], convert_to_tensor=False)[0]
        norm = np.linalg.norm(text_embedding)
        if norm > 0:
            text_embedding = text_embedding / norm
            
        best_intent = "other"
        best_score = -1.0
        
        scores = {}
        for intent_name, proto_emb in self.intent_embeddings.items():
            sim = float(np.dot(text_embedding, proto_emb))
            scores[intent_name] = sim
            if sim > best_score:
                best_score = sim
                best_intent = intent_name
                
        # Scale score to [0, 1] range for confidence
        confidence = max(0.0, min(1.0, float(best_score)))
        
        return {
            "intent": best_intent,
            "confidence": round(confidence, 4),
            "all_scores": {k: round(v, 4) for k, v in scores.items()}
        }

from collections import Counter
from typing import List, Dict, Any

class MajorityClassifier:
    """
    Baseline 1: Majority-Class Classifier.
    Always predicts the most frequent class in the training dataset.
    """
    def __init__(self):
        self.majority_intent = "battery_drain"
        self.majority_ratio = 0.175

    def fit(self, examples: List[Dict[str, Any]]):
        if not examples:
            return
        labels = [e["expected_intent"] for e in examples if "expected_intent" in e]
        if labels:
            counts = Counter(labels)
            self.majority_intent, top_count = counts.most_common(1)[0]
            self.majority_ratio = top_count / len(labels)

    def predict(self, text: str) -> Dict[str, Any]:
        return {
            "intent": self.majority_intent,
            "confidence": round(self.majority_ratio, 4)
        }

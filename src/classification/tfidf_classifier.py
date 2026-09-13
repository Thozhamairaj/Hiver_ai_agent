import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class TfidfLogisticClassifier:
    """
    Baseline 2: TF-IDF + Logistic Regression Classifier.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            sublinear_tf=True
        )
        self.model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        self.is_fitted = False
        self.classes_ = []

    def fit(self, texts: List[str], labels: List[str]):
        if not texts or not labels:
            raise ValueError("Training data cannot be empty.")
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.classes_ = list(self.model.classes_)
        self.is_fitted = True

    def predict(self, text: str) -> Dict[str, Any]:
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict.")
            
        X_test = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X_test)[0]
        max_idx = np.argmax(probs)
        predicted_intent = self.classes_[max_idx]
        confidence = float(probs[max_idx])
        
        return {
            "intent": predicted_intent,
            "confidence": round(confidence, 4)
        }

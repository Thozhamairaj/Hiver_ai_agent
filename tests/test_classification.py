import pytest
from src.classification.majority_classifier import MajorityClassifier
from src.classification.tfidf_classifier import TfidfLogisticClassifier
from src.classification.main_classifier import EmbeddingIntentClassifier

def test_majority_classifier():
    examples = [
        {"expected_intent": "battery_drain"},
        {"expected_intent": "battery_drain"},
        {"expected_intent": "system_performance_lag"}
    ]
    clf = MajorityClassifier()
    clf.fit(examples)
    res = clf.predict("Any message here")
    assert res["intent"] == "battery_drain"
    assert res["confidence"] > 0

def test_tfidf_classifier():
    texts = [
        "battery draining fast after update",
        "phone is super laggy and freezing",
        "verification code not arriving"
    ]
    labels = ["battery_drain", "system_performance_lag", "verification_code_issue"]
    
    clf = TfidfLogisticClassifier()
    clf.fit(texts, labels)
    res = clf.predict("my battery is dead quickly")
    assert "intent" in res
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0

def test_main_embedding_classifier():
    clf = EmbeddingIntentClassifier()
    clf.initialize("data/processed/intents.json")
    
    res = clf.predict("My battery dies in two hours")
    assert res["intent"] == "battery_drain"
    assert res["confidence"] > 0.4

import pytest
from src.escalation.escalation_engine import EscalationEngine

def test_escalation_high_risk_intent():
    engine = EscalationEngine()
    res = engine.evaluate(
        customer_message="I need a new iStore code",
        predicted_intent="verification_code_issue",
        intent_confidence=0.9,
        retrieved_evidence=[]
    )
    assert res["decision"] == "ESCALATE"
    assert "High-Risk Intent" in res["reason"] or "Account security" in res["reason"]

def test_escalation_sensitive_keyword():
    engine = EscalationEngine()
    res = engine.evaluate(
        customer_message="My phone is overheating and my account is locked out",
        predicted_intent="battery_drain",
        intent_confidence=0.85,
        retrieved_evidence=[{"similarity_score": 0.8}]
    )
    assert res["decision"] == "ESCALATE"
    assert "sensitive risk term" in res["reason"].lower() or "overheating" in res["reason"].lower()

def test_escalation_auto_handle():
    engine = EscalationEngine()
    res = engine.evaluate(
        customer_message="My battery drains fast after iOS 11 update",
        predicted_intent="battery_drain",
        intent_confidence=0.85,
        retrieved_evidence=[{"similarity_score": 0.75, "customer_message": "test", "brand_reply": "test"}]
    )
    assert res["decision"] == "AUTO_HANDLE"

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_api_support_endpoint():
    response = client.post(
        "/api/support",
        json={"message": "My battery drains quickly after iOS 11 update"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "confidence" in data
    assert "decision" in data
    assert "escalation_reason" in data
    assert "generated_reply" in data
    assert "retrieved_evidence" in data

def test_api_evaluation_endpoint():
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "classification_metrics" in data
    assert "retrieval_metrics" in data
    assert "top_5_failure_modes" in data

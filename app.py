import json
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.classification.main_classifier import EmbeddingIntentClassifier
from src.retrieval.vector_store import SupportVectorStore
from src.generation.response_generator import GeminiResponseGenerator
from src.escalation.escalation_engine import EscalationEngine

app = FastAPI(title="Hiver AI Customer Support Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances initialized on demand
_main_classifier = None
_vector_store = None
_escalation_engine = None
_generator = None

def get_classifier():
    global _main_classifier
    if _main_classifier is None:
        clf = EmbeddingIntentClassifier()
        clf.initialize("data/processed/intents.json")
        _main_classifier = clf
    return _main_classifier

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = SupportVectorStore(persist_dir="chroma_db", collection_name="apple_support_conversations")
    return _vector_store

def get_escalation_engine():
    global _escalation_engine
    if _escalation_engine is None:
        _escalation_engine = EscalationEngine()
    return _escalation_engine

def get_generator():
    global _generator
    if _generator is None:
        _generator = GeminiResponseGenerator()
    return _generator

class CustomerQueryRequest(BaseModel):
    message: str

@app.post("/api/support")
def handle_support_query(req: CustomerQueryRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Customer message cannot be empty.")

    msg = req.message.strip()
    
    classifier = get_classifier()
    vstore = get_vector_store()
    esc_engine = get_escalation_engine()
    gen = get_generator()

    # 1. Intent Classification
    intent_res = classifier.predict(msg)
    intent = intent_res["intent"]
    confidence = intent_res["confidence"]
    
    # 2. RAG Retrieval
    retrieved_evidence = vstore.search(msg, top_k=5, brand_filter="AppleSupport")
    
    # 3. Escalation Policy Decision
    esc_res = esc_engine.evaluate(msg, intent, confidence, retrieved_evidence)
    decision = esc_res["decision"]
    escalation_reason = esc_res["reason"]
    
    # 4. Response Generation
    gen_res = gen.generate_response(msg, intent, retrieved_evidence, confidence)
    
    return {
        "customer_message": msg,
        "intent": intent,
        "confidence": confidence,
        "decision": decision,
        "escalation_reason": escalation_reason,
        "generated_reply": gen_res["reply"],
        "retrieved_evidence": retrieved_evidence,
        "all_intent_scores": intent_res.get("all_scores", {})
    }

@app.get("/api/evaluation")
def get_evaluation_dashboard_data():
    eval_file = Path("data/processed/evaluation_results.json")
    if not eval_file.exists():
        raise HTTPException(status_code=404, detail="Evaluation results file not found. Run scripts/run_evaluation.py first.")
    
    with open(eval_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# Mount static frontend files
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

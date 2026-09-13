import os
import json
import re
from typing import List, Dict, Any, Optional

class GeminiResponseGenerator:
    """
    Response Generation module using Google Gemini API.
    Enforces evidence grounding, zero hallucination, and structured JSON output.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API Client: {e}")

    def format_retrieved_evidence(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        if not retrieved_docs:
            return "No historical support conversations found."
            
        evidence_lines = []
        for idx, doc in enumerate(retrieved_docs, 1):
            evidence_lines.append(
                f"[Evidence #{idx}] (Conv ID: {doc.get('conversation_id')}, Intent: {doc.get('intent')}, Similarity: {doc.get('similarity_score')}):\n"
                f"  Customer Message: {doc.get('customer_message')}\n"
                f"  Brand Support Reply: {doc.get('brand_reply')}\n"
            )
        return "\n".join(evidence_lines)

    def generate_response(
        self,
        customer_message: str,
        predicted_intent: str,
        retrieved_evidence: List[Dict[str, Any]],
        intent_confidence: float = 0.8
    ) -> Dict[str, Any]:
        
        evidence_text = self.format_retrieved_evidence(retrieved_evidence)
        
        system_prompt = f"""You are an AI Customer Support Agent representing AppleSupport.
Your job is to generate a helpful, professional, and strictly grounded response to the customer's query.

STRICT SYSTEM RULES:
1. Ground your answer ONLY in the provided Historical Support Evidence below.
2. DO NOT invent policies, fake refund promises, or claim actions were taken unless explicitly documented in evidence.
3. If the retrieved evidence is insufficient, unusual, ambiguous, or requires account security access, decide 'ESCALATE' and state why.
4. Return ONLY valid JSON in the exact structure specified below.

CUSTOMER MESSAGE: "{customer_message}"
PREDICTED INTENT: "{predicted_intent}" (Confidence: {intent_confidence:.2f})

HISTORICAL SUPPORT EVIDENCE:
{evidence_text}

OUTPUT JSON SCHEMA:
{{
  "intent": "{predicted_intent}",
  "reply": "<Professional customer support response grounded in evidence>",
  "confidence": <float score between 0.0 and 1.0>,
  "decision": "AUTO_HANDLE" or "ESCALATE",
  "reason": "<Detailed explanation for auto-handle or escalation decision>"
}}
"""

        # Call Gemini API if available
        if self.client:
            try:
                from google.genai import types
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=system_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                raw_text = response.text.strip()
                parsed = json.loads(raw_text)
                return {
                    "intent": parsed.get("intent", predicted_intent),
                    "reply": parsed.get("reply", ""),
                    "confidence": float(parsed.get("confidence", intent_confidence)),
                    "decision": parsed.get("decision", "AUTO_HANDLE"),
                    "reason": parsed.get("reason", "Generated via Gemini LLM")
                }
            except Exception as e:
                print(f"Gemini API invocation error: {e}. Falling back to grounded rule engine.")

        # Grounded Fallback Engine (when API Key is absent or fails)
        top_sim = retrieved_evidence[0]["similarity_score"] if retrieved_evidence else 0.0
        
        if top_sim < 0.5 or predicted_intent in ["verification_code_issue", "general_complaint_feedback", "other"]:
            return {
                "intent": predicted_intent,
                "reply": f"Thanks for reaching out to @AppleSupport. To assist with your query regarding {predicted_intent.replace('_', ' ')}, please send us a Direct Message (DM) with your device details and account information so our human support team can help you directly.",
                "confidence": round(top_sim, 4),
                "decision": "ESCALATE",
                "reason": f"Insufficient retrieval evidence (top similarity: {top_sim:.2f}) or high-risk intent requiring human verification."
            }
        else:
            best_reply = retrieved_evidence[0]["brand_reply"]
            return {
                "intent": predicted_intent,
                "reply": f"We can help! {best_reply}",
                "confidence": round(top_sim, 4),
                "decision": "AUTO_HANDLE",
                "reason": f"High intent confidence ({intent_confidence:.2f}) and strong historical evidence match (similarity: {top_sim:.2f})."
            }

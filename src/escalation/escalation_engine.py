import re
from typing import List, Dict, Any

class EscalationEngine:
    """
    Multi-Factor Escalation Decision Engine for Customer Support.
    Decides between AUTO_HANDLE and ESCALATE based on:
    - Intent Confidence
    - Retrieval Similarity
    - Number of useful retrieved examples
    - Intent risk category (e.g. Account Security, General Venting, Out-of-Scope)
    - Sensitive risk keywords
    """
    def __init__(
        self,
        min_intent_confidence: float = 0.65,
        min_retrieval_similarity: float = 0.45,
        min_useful_examples: int = 1
    ):
        self.min_intent_confidence = min_intent_confidence
        self.min_retrieval_similarity = min_retrieval_similarity
        self.min_useful_examples = min_useful_examples

        # High-risk intents that should always be escalated to human agents
        self.high_risk_intents = {
            "verification_code_issue": "Account security and 2FA authentication issues require human verification.",
            "general_complaint_feedback": "General customer frustration/venting requires human empathy and personalized support.",
            "other": "Unseen or out-of-scope inquiry lacking standard automated support resolution."
        }

        # High-risk sensitive keywords
        self.high_risk_keywords = [
            "locked out", "bank", "credit card", "security code", "passcode",
            "overheating", "fire", "smoke", "liquid damage", "warranty",
            "legal", "sue", "stolen", "hack"
        ]

    def evaluate(
        self,
        customer_message: str,
        predicted_intent: str,
        intent_confidence: float,
        retrieved_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        risk_factors = []
        msg_lower = customer_message.lower()

        # 1. High-Risk Intent Check
        if predicted_intent in self.high_risk_intents:
            reason = self.high_risk_intents[predicted_intent]
            risk_factors.append(f"High-Risk Intent: {predicted_intent}")
            return {
                "decision": "ESCALATE",
                "reason": reason,
                "risk_factors": risk_factors,
                "confidence": round(intent_confidence, 4)
            }

        # 2. Sensitive Keyword Check
        for kw in self.high_risk_keywords:
            if kw in msg_lower:
                risk_factors.append(f"Sensitive Risk Keyword: '{kw}'")
                return {
                    "decision": "ESCALATE",
                    "reason": f"Customer message contains sensitive risk term '{kw}' requiring human oversight.",
                    "risk_factors": risk_factors,
                    "confidence": round(intent_confidence, 4)
                }

        # 3. Intent Confidence Check
        if intent_confidence < self.min_intent_confidence:
            risk_factors.append(f"Low Intent Confidence ({intent_confidence:.2f} < {self.min_intent_confidence})")

        # 4. Retrieval Similarity & Evidence Count Check
        top_similarity = retrieved_evidence[0]["similarity_score"] if retrieved_evidence else 0.0
        useful_examples = [
            doc for doc in retrieved_evidence
            if doc.get("similarity_score", 0.0) >= self.min_retrieval_similarity
        ]

        if top_similarity < self.min_retrieval_similarity:
            risk_factors.append(f"Low Retrieval Similarity ({top_similarity:.2f} < {self.min_retrieval_similarity})")

        if len(useful_examples) < self.min_useful_examples:
            risk_factors.append(f"Insufficient Historical Evidence ({len(useful_examples)} < {self.min_useful_examples})")

        # 5. Final Decision Synthesis
        if not risk_factors:
            return {
                "decision": "AUTO_HANDLE",
                "reason": f"High intent confidence ({intent_confidence:.2f} >= {self.min_intent_confidence}) and strong historical evidence match ({top_similarity:.2f} similarity across {len(useful_examples)} examples).",
                "risk_factors": [],
                "confidence": round((intent_confidence + top_similarity) / 2.0, 4)
            }
        else:
            return {
                "decision": "ESCALATE",
                "reason": f"Escalated due to: {', '.join(risk_factors)}.",
                "risk_factors": risk_factors,
                "confidence": round(intent_confidence, 4)
            }

# Technical Decision Log - Hiver AI Support Agent

This document records 12 key technical decisions, alternative approaches evaluated, selection rationales, and architectural trade-offs made during the development of the Hiver AI Customer Support Agent.

---

### Decision 1: Brand Selection — AppleSupport
- **Decision**: Selected `AppleSupport` as the primary brand for dataset reconstruction and RAG evidence index.
- **Alternatives Considered**: `SpotifyCares`, `Tesco`, `VirginTrains`, or aggregate multi-brand indexing.
- **Reason for Choice**: Analysis of the Kaggle Twitter Customer Support dataset showed `AppleSupport` had the highest interaction volume, rich multi-turn dialogs, and a wide spectrum of customer intent categories (battery drain, iOS lag, app crashes, verification codes, rollback requests).
- **Trade-off**: Higher domain specificity for Apple iOS ecosystem, but allows much deeper retrieval relevance and grounded prompt engineering compared to a generic multi-brand chatbot.

---

### Decision 2: Conversation Reconstruction Logic via Parent Pointer Traversal
- **Decision**: Reconstructed multi-turn conversations by recursively traversing `in_response_to_tweet_id` and grouping tweets under root customer query IDs (`conversation_id`).
- **Alternatives Considered**: Treating tweets as isolated flat text records, or grouping by customer `author_id` alone.
- **Reason for Choice**: Flat tweets lose dialog context and agent response pairs. Grouping by root tweet ID creates cohesive, chronological support threads where initial customer symptoms map directly to brand resolution replies.
- **Trade-off**: Requires recursive tree parsing overhead, but yields structured dialog records essential for RAG evidence grounding.

---

### Decision 3: Empirical Intent Definition (8 Classes)
- **Decision**: Defined 8 data-driven intent categories (`battery_drain`, `system_performance_lag`, `app_crash_bug`, `verification_code_issue`, `playback_audio_issue`, `update_rollback_request`, `general_complaint_feedback`, `other`).
- **Alternatives Considered**: Generic e-commerce categories (e.g. Payment, Shipping, Refund) or fine-grained 30+ sub-intents.
- **Reason for Choice**: Derived directly from qualitative data inspection of `AppleSupport` customer messages in TWCS dataset.
- **Trade-off**: 8 classes balance high intra-class similarity with distinct boundary definitions for baseline and embedding classification.

---

### Decision 4: Baseline Models — Majority Class & TF-IDF + Logistic Regression
- **Decision**: Implemented Majority Class Classifier (Baseline 1) and TF-IDF + Logistic Regression (Baseline 2).
- **Alternatives Considered**: Naive Bayes, Random Forest, or zero baselines.
- **Reason for Choice**: Standard ML benchmarking best practices require a zero-variance lower bound (Majority class = 17.5% accuracy) and a linear n-gram statistical text classification baseline (TF-IDF + LogReg = 71.5% accuracy).
- **Trade-off**: TF-IDF requires vocabulary fitting and struggles with out-of-vocabulary semantic paraphrases, making it a clear baseline to compare against dense embedding models.

---

### Decision 5: Main Intent Classifier — Sentence Transformers (`all-MiniLM-L6-v2`)
- **Decision**: Built the main classifier using dense semantic embeddings from `all-MiniLM-L6-v2` with normalized cosine similarity prototype matching.
- **Alternatives Considered**: Fine-tuned BERT model, OpenAI embeddings, or heavy LLM zero-shot classification per request.
- **Reason for Choice**: `all-MiniLM-L6-v2` is lightweight (90MB), fast (sub-10ms inference on CPU), and achieves 92.0% accuracy / 0.9013 F1-score on the golden evaluation set.
- **Trade-off**: Small model footprint limits deep nuanced syntactic parsing compared to 7B parameter LLMs, but runs fully local and fast.

---

### Decision 6: Local Vector Store — ChromaDB
- **Decision**: Selected ChromaDB as the local persistent vector database (`chroma_db/`).
- **Alternatives Considered**: FAISS, Pinecone, Qdrant, or in-memory cosine array search.
- **Reason for Choice**: ChromaDB provides simple local persistence, native metadata filtering (`where={"brand": "AppleSupport"}`), zero cloud setup overhead, and easy integration with Python.
- **Trade-off**: Slightly higher disk persistence overhead than pure memory arrays, but guarantees vector index survival across application restarts.

---

### Decision 7: RAG Retrieval Top-K Selection (K = 5)
- **Decision**: Selected `K = 5` retrieved historical evidence examples for response generation.
- **Alternatives Considered**: `K = 3` or `K = 10`.
- **Reason for Choice**: Empirical evaluation on 200 golden set queries demonstrated:
  - `K = 3`: Hit Rate = 81.0%
  - `K = 5`: Hit Rate = 88.5%
  - `K = 10`: Hit Rate = 92.5%
  `K = 5` provides optimal hit rate (+7.5% over K=3) while avoiding context clutter in Gemini LLM prompts.
- **Trade-off**: Marginally higher prompt token count than K=3, but delivers significantly better evidence recall.

---

### Decision 8: Response Generator Architecture — Gemini 2.5 Flash API with Fallback
- **Decision**: Integrated `google-genai` SDK with `gemini-2.5-flash` model, backed by an empirical grounded rule engine when API keys are absent.
- **Alternatives Considered**: Unconstrained text generation, local LLaMA 7B, or non-LLM template filling.
- **Reason for Choice**: Gemini 2.5 Flash provides sub-second structured JSON response generation, excellent instruction following, and strong evidence grounding capabilities.
- **Trade-off**: Requires external API key (`GEMINI_API_KEY`), but fallback engine guarantees 100% application operation offline.

---

### Decision 9: Multi-Factor Escalation Engine (Independent of LLM Confidence)
- **Decision**: Built a rule-based `EscalationEngine` combining intent confidence, top retrieval similarity, evidence count, high-risk intent flags, and sensitive risk terms.
- **Alternatives Considered**: Asking Gemini LLM to decide escalation purely in prompt output.
- **Reason for Choice**: LLM self-reported confidence scores are notoriously overconfident and uncalibrated. A separate policy engine enforces strict deterministic safety boundaries for 2FA/codes, overheating, legal threats, and out-of-scope queries.
- **Trade-off**: Requires manual policy threshold tuning (`min_intent_confidence = 0.65`, `min_retrieval_similarity = 0.45`), but prevents critical safety failures.

---

### Decision 10: Human-Labelled Golden Evaluation Set (N = 200)
- **Decision**: Constructed a 200-example golden evaluation set (`data/golden_set/golden_eval_set.json`) covering all 8 intents, 3 difficulty tiers (Easy: 37%, Medium: 50%, Hard: 13%), and expected escalation decisions.
- **Alternatives Considered**: Evaluating on small 10-20 record samples or synthetic automated data.
- **Reason for Choice**: 200 examples provide statistically meaningful accuracy/F1 measurements across 8 classes and reflect realistic Twitter support customer variations.
- **Trade-off**: Requires rigorous annotation setup, but guarantees objective baseline benchmarking.

---

### Decision 11: LLM-as-a-Judge Evaluation Framework & Human Agreement Benchmarking
- **Decision**: Implemented a 5-dimension rubric (Correctness, Relevance, Groundedness, Helpfulness, Tone) scored 1-5, and benchmarked LLM judge ratings against human rater scores.
- **Alternatives Considered**: Using ROUGE/BLEU string overlap metrics alone.
- **Reason for Choice**: BLEU/ROUGE fail to measure support helpfulness, groundedness, or professional tone. LLM judge scoring correlated strongly with human ratings (Pearson r = 0.4132, MAD = 0.1487).
- **Trade-off**: LLM judge exhibits slight leniency bias (mean score 4.79 vs human 4.77), which is explicitly quantified and reported.

---

### Decision 12: Application Architecture — FastAPI Backend + Vanilla Web UI
- **Decision**: Built a lightweight FastAPI REST server with a clean vanilla HTML/CSS/JavaScript single-page interface.
- **Alternatives Considered**: React/Next.js heavy single page application or CLI interface.
- **Reason for Choice**: Eliminates heavy node_modules build tooling overhead, ensures instant local startup, and cleanly separates core AI pipeline logic from frontend presentation.
- **Trade-off**: Vanilla JS requires manual DOM manipulation, but achieves maximum lightweight simplicity and reproducibility.

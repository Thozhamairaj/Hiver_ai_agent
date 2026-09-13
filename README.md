
# Hiver AI Customer Support Agent & Evaluation System

An end-to-end, evidence-grounded AI Customer Support Agent built for the **Hiver SDE Intern Take-Home Assignment**.

The system accepts raw customer messages, predicts support intents, retrieves relevant historical support evidence using RAG (ChromaDB + Sentence Transformers), generates grounded replies via Gemini 2.5 Flash LLM, applies a multi-factor escalation decision policy, and features a complete empirical evaluation dashboard.

---

## 1. System Architecture

```
                    Customer Message
                           │
                           ▼
                  Intent Classification
             (Sentence Transformers / TF-IDF)
                           │
                           ▼
                    Detected Intent
                           │
                           ▼
              Semantic Retrieval / RAG
               (ChromaDB Vector Store)
                           │
                           ▼
             Historical Support Evidence
                           │
                           ▼
                    Gemini LLM
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
       Reply          Confidence        Escalation
                                         Decision
                                             │
                                   ┌─────────┴─────────┐
                                   ▼                   ▼
                              AUTO-HANDLE           ESCALATE
                                                     HUMAN
```

---

## 2. Headline Evaluation Benchmark Results

Evaluated on a human-labelled **200-example Golden Evaluation Set** (`data/golden_set/golden_eval_set.json`):

| Model / Pipeline Component | Accuracy | Precision (Macro) | Recall (Macro) | F1-Score (Macro) |
|:---------------------------|:--------:|:-----------------:|:--------------:|:----------------:|
| **Majority Class Baseline** | 17.5% | 2.2% | 12.5% | 3.7% |
| **TF-IDF + Logistic Regression Baseline** | 71.5% | 46.1% | 63.2% | 53.3% |
| **Main System (Sentence Transformers)** | **92.0%** | **89.5%** | **90.8%** | **90.1%** |

### RAG Retrieval Performance @ Top-K:
- **Hit Rate @ K=3**: 81.0%
- **Hit Rate @ K=5**: **88.5%** *(Selected K)*
- **Hit Rate @ K=10**: 92.5%

### Response Quality & Judge Agreement:
- **LLM-as-a-Judge Overall Score**: **4.77 / 5.0** (Correctness: 5.0, Relevance: 5.0, Groundedness: 4.8, Helpfulness: 4.07, Tone: 5.0)
- **Human vs. LLM Judge Agreement**: Pearson Correlation **r = 0.4132**, Mean Absolute Difference **MAD = 0.1487**

---

## 3. Brand Selection & Intent Schema

### Selected Brand: `AppleSupport`
- **Why Selected**: `AppleSupport` represents the highest volume brand in the Kaggle Twitter Customer Support dataset with structured agent workflows and diverse technical customer issues.

### Empirical Intent Schema (8 Classes):
1. `battery_drain`: Fast battery depletion, battery health degradation post update.
2. `system_performance_lag`: System slowness, UI lag, phone freezing, unresponsive screens.
3. `app_crash_bug`: Specific applications crashing, force closing, or failing to launch.
4. `verification_code_issue`: iStore passcode, 2FA security code delivery issues.
5. `playback_audio_issue`: Music stopping, audio background playback conflicts.
6. `update_rollback_request`: Requesting downgrade or rollback to previous iOS version.
7. `general_complaint_feedback`: Venting dissatisfaction without single technical symptom.
8. `other`: Out-of-scope inquiries, hardware pricing, trade-in, retail hours.

---

## 4. Quickstart Guide (15-Minute Reproducibility)

### Step 1: Environment Setup
Clone repository and create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: Add `GEMINI_API_KEY=your_key_here` in `.env`. If omitted, system seamlessly runs in local grounded rule engine mode).*

### Step 3: Run Conversation Preprocessing
Extract raw tweets and reconstruct multi-turn conversations:
```bash
python scripts/preprocess.py
```

### Step 4: Create Golden Evaluation Set
Generate the 200-example golden set:
```bash
python scripts/create_golden_set.py
```

### Step 5: Build Vector Index in ChromaDB
Embed and index historical support conversations:
```bash
python scripts/build_embeddings.py
```

### Step 6: Run Full Evaluation Pipeline & Benchmark Baselines
Execute complete evaluation script (Baselines vs Main Model, RAG Quality, Judge Rubric, Failure Analysis):
```bash
python scripts/run_evaluation.py
```

### Step 7: Launch Application & Web UI
Start FastAPI web server:
```bash
python app.py
```
Open browser at `http://localhost:8000` to interact with:
- **Live AI Support Agent Console** (`/`)
- **Interactive Evaluation Dashboard** (`/api/evaluation`)

### Step 8: Run Automated Tests
```bash
PYTHONPATH=. pytest tests/
```

---

## 5. Top 5 Empirical Failure Modes & Mitigation

1. **Ambiguous / Short Customer Query**:
   - *Example*: `"fix this update. It's horrible"`
   - *Cause*: Lacks technical symptoms, causing low retrieval similarity.
   - *Mitigation*: Prompt customer for symptom selection before RAG retrieval.
2. **Multiple Simultaneous Technical Intents**:
   - *Example*: `"Battery drains in half the time, apps now frequently crash."`
   - *Cause*: Combines battery and app crash intents into single primary label.
   - *Mitigation*: Implement multi-label intent classification.
3. **Account Security & Authentication Limits**:
   - *Example*: `"I need a new code for my iStore. Message says too many sent."`
   - *Cause*: Requires private user verification not safe on public channels.
   - *Mitigation*: Force escalation to secure private DM / OAuth verification.
4. **Unseen Hardware / Price Inquiry Out-of-Scope**:
   - *Example*: `"How much does screen replacement cost for iPhone 8 Plus?"`
   - *Cause*: Out of scope for software support thread database.
   - *Mitigation*: Ingest official Apple retail service & pricing knowledge base.
5. **Hardware Degradation Misclassified as Software Bug**:
   - *Example*: `"Battery health shows 80% and drops from 50% to 0% suddenly."`
   - *Cause*: Similarity matches software battery queries, but root cause is physical battery decay.
   - *Mitigation*: Add battery health percentage heuristic rule.

---

## 6. Technical Decisions
See [DECISION_LOG.md](DECISION_LOG.md) for 12 detailed technical decision rationales and trade-offs.

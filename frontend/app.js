document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
});

function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(sec => sec.classList.remove('active'));

  if (tabName === 'agent') {
    document.getElementById('tab-agent-btn').classList.add('active');
    document.getElementById('agent-section').classList.add('active');
  } else {
    document.getElementById('tab-dashboard-btn').classList.add('active');
    document.getElementById('dashboard-section').classList.add('active');
    loadDashboardData();
  }
}

function fillPreset(type) {
  const input = document.getElementById('customer-message');
  if (type === 'battery') {
    input.value = "My battery drains from 100% to 20% in two hours after updating to iOS 11.";
  } else if (type === 'lag') {
    input.value = "Everything feels super laggy and my screen freezes when scrolling through settings.";
  } else if (type === 'code') {
    input.value = "@AppleSupport I need a new code for my iStore. I haven't recd any but message says too many sent.";
  } else if (type === 'rollback') {
    input.value = "Can you please tell me how to downgrade my iPhone back to iOS 10.3.3?";
  }
}

async function handleQuerySubmit(event) {
  event.preventDefault();
  const msg = document.getElementById('customer-message').value.trim();
  if (!msg) return;

  const submitBtn = document.getElementById('submit-btn');
  submitBtn.disabled = true;
  submitBtn.querySelector('span').innerText = 'Processing Query...';

  try {
    const res = await fetch('/api/support', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }

    const data = await res.json();
    renderAgentResult(data);
  } catch (err) {
    alert(`Error handling query: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector('span').innerText = 'Submit to Agent';
  }
}

function renderAgentResult(data) {
  document.getElementById('result-placeholder').classList.add('hidden');
  document.getElementById('result-content').classList.remove('hidden');

  document.getElementById('res-intent').innerText = data.intent;
  document.getElementById('res-confidence').innerText = `${(data.confidence * 100).toFixed(1)}%`;

  const decBadge = document.getElementById('res-decision');
  decBadge.innerText = data.decision;
  decBadge.className = `badge ${data.decision.toLowerCase().replace('_', '-')}`;

  document.getElementById('res-reason').innerText = data.escalation_reason;
  document.getElementById('res-reply').innerText = data.generated_reply;

  const evContainer = document.getElementById('res-evidence');
  evContainer.innerHTML = '';

  if (!data.retrieved_evidence || data.retrieved_evidence.length === 0) {
    evContainer.innerHTML = '<p class="subtitle">No historical evidence matches found.</p>';
  } else {
    data.retrieved_evidence.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'evidence-card';
      card.innerHTML = `
        <div class="ev-header">
          <span>#${idx + 1} Conv ID: ${item.conversation_id} (${item.intent})</span>
          <span>Similarity: ${(item.similarity_score * 100).toFixed(1)}%</span>
        </div>
        <div><strong>Customer:</strong> ${item.customer_message}</div>
        <div style="margin-top: 0.25rem; color: #94a3b8;"><strong>Brand Reply:</strong> ${item.brand_reply}</div>
      `;
      evContainer.appendChild(card);
    });
  }
}

async function loadDashboardData() {
  try {
    const res = await fetch('/api/evaluation');
    if (!res.ok) return;

    const data = await res.json();
    const summary = data.summary;

    // Stat cards
    document.getElementById('dash-maj-acc').innerText = `${(summary.baseline_majority_accuracy * 100).toFixed(1)}%`;
    document.getElementById('dash-tfidf-acc').innerText = `${(summary.baseline_tfidf_accuracy * 100).toFixed(1)}%`;
    document.getElementById('dash-main-acc').innerText = `${(summary.classification_accuracy * 100).toFixed(1)}%`;
    document.getElementById('dash-hitrate').innerText = `${(summary.retrieval_hit_rate_k5 * 100).toFixed(1)}%`;
    document.getElementById('dash-judge').innerText = `${summary.llm_judge_quality_score} / 5`;

    // Baseline table
    const baselineTbody = document.querySelector('#baseline-table tbody');
    baselineTbody.innerHTML = '';
    
    const clMetrics = data.classification_metrics;
    const rows = [
      { name: 'Majority Class Baseline', metrics: clMetrics.majority_class },
      { name: 'TF-IDF + Logistic Regression Baseline', metrics: clMetrics.tfidf_logreg },
      { name: 'Main Embedding System (Sentence Transformers)', metrics: clMetrics.main_classifier }
    ];

    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${r.name}</strong></td>
        <td>${(r.metrics.accuracy * 100).toFixed(1)}%</td>
        <td>${(r.metrics.precision * 100).toFixed(1)}%</td>
        <td>${(r.metrics.recall * 100).toFixed(1)}%</td>
        <td><strong>${(r.metrics.f1 * 100).toFixed(1)}%</strong></td>
      `;
      baselineTbody.appendChild(tr);
    });

    // Retrieval table
    const retTbody = document.querySelector('#retrieval-table tbody');
    retTbody.innerHTML = '';
    const retMetrics = data.retrieval_metrics;

    Object.keys(retMetrics).forEach(k => {
      const item = retMetrics[k];
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${k}</strong></td>
        <td>${(item.hit_rate * 100).toFixed(1)}%</td>
        <td>${item.avg_similarity.toFixed(4)}</td>
      `;
      retTbody.appendChild(tr);
    });

    // Human vs Judge
    document.getElementById('dash-corr').innerText = data.human_vs_judge_metrics.pearson_correlation.toFixed(4);
    document.getElementById('dash-mad').innerText = data.human_vs_judge_metrics.mean_absolute_difference.toFixed(4);

    // Failure Modes
    const failContainer = document.getElementById('failure-modes-container');
    failContainer.innerHTML = '';

    data.top_5_failure_modes.forEach((fm, idx) => {
      const div = document.createElement('div');
      div.className = 'failure-card';
      div.innerHTML = `
        <div class="failure-title">Failure Mode #${idx + 1}: ${fm.mode}</div>
        <div class="failure-body">
          <p><strong>Example Message:</strong> "${fm.example}"</p>
          <p><strong>System Predicted:</strong> Intent: <em>${fm.predicted.intent}</em> | Decision: <em>${fm.predicted.decision}</em></p>
          <p><strong>Root Cause:</strong> ${fm.why_failed_or_challenged}</p>
          <p><strong>Proposed Improvement:</strong> ${fm.improvement}</p>
        </div>
      `;
      failContainer.appendChild(div);
    });

  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

const state = {
  payload: null,
  surface: "roadmap",
};

const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function pill(text) {
  return `<span class="pill ${text.toLowerCase().replaceAll(" ", "-")}">${text}</span>`;
}

function metric(label, value, hint) {
  return `
    <article class="metric">
      <span>${label}</span>
      <strong>${value}</strong>
      <em>${hint}</em>
    </article>
  `;
}

function renderSummary() {
  const { summary } = state.payload;
  const top = summary.top_workflow;
  document.querySelector("#metricGrid").innerHTML = [
    metric("Product bets", summary.workflow_count, "roadmap candidates"),
    metric("PRD inputs", summary.requirement_count, "evidence-backed requirements"),
    metric("Data contracts", summary.data_contract_count, "platform readiness checks"),
    metric("Launch blockers", summary.platform_blockers, "data or model gaps"),
  ].join("");

  document.querySelector("#heroDecision").innerHTML = `
    <span>Recommended first bet</span>
    <strong>${top.workflow}</strong>
    <em>${top.next_decision}</em>
  `;
}

function renderRoadmapDetail(workflowId) {
  const workflow = state.payload.roadmapQueue.find((item) => item.workflow_id === workflowId);
  const events = state.payload.stakeholderEvents
    .filter((item) => item.workflow_id === workflowId)
    .slice(0, 3);

  document.querySelector("#roadmapDetail").innerHTML = `
    <div class="detail-line">
      <span>Problem</span>
      <strong>${workflow.problem}</strong>
    </div>
    <div class="detail-line">
      <span>Hypothesis</span>
      <strong>${workflow.hypothesis}</strong>
    </div>
    <div class="decision-grid">
      <div><span>Priority</span><strong>${workflow.priority_score}</strong></div>
      <div><span>Requests</span><strong>${workflow.request_count}</strong></div>
      <div><span>Acceptance</span><strong>${Math.round(workflow.avg_match_acceptance * 100)}%</strong></div>
      <div><span>Readiness</span><strong>${workflow.readiness_score}</strong></div>
    </div>
    <div class="mini-feed">
      ${events.map((event) => `<p><b>${event.event_type}</b> ${event.note}</p>`).join("")}
    </div>
  `;
}

function renderRoadmap() {
  const rows = state.payload.roadmapQueue;
  document.querySelector("#roadmapRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td>
          <button type="button" class="link-button" data-workflow="${row.workflow_id}">${row.workflow}</button>
          <small>${row.product_area}, ${row.persona}</small>
        </td>
        <td>${pill(row.launch_status)}</td>
        <td>${row.priority_score}</td>
        <td>${row.request_count}</td>
        <td>${currency.format(row.estimated_impact)}</td>
        <td>${row.owner_team}</td>
      </tr>
    `)
    .join("");
  renderRoadmapDetail(rows[0].workflow_id);
}

function renderPrdDetail(requirementId) {
  const req = state.payload.prdCards.find((item) => item.requirement_id === requirementId);
  document.querySelector("#prdDetail").innerHTML = `
    <div class="detail-line">
      <span>PRD problem</span>
      <strong>${req.problem}</strong>
    </div>
    <div class="detail-line">
      <span>User story</span>
      <strong>${req.user_story}.</strong>
    </div>
    <div class="detail-line">
      <span>Acceptance criteria</span>
      <strong>${req.acceptance_criteria}</strong>
    </div>
    <div class="detail-line">
      <span>Validation plan</span>
      <strong>${req.validation_plan}</strong>
    </div>
  `;
}

function renderPrd() {
  const rows = state.payload.prdCards.slice(0, 12);
  document.querySelector("#prdRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td>
          <button type="button" class="link-button" data-requirement="${row.requirement_id}">${row.theme}</button>
          <small>${row.workflow}</small>
        </td>
        <td>${row.persona}</td>
        <td>${pill(row.severity)}</td>
        <td>${row.evidence_source}<small>${row.request_count} requests</small></td>
        <td>${row.instrumentation}</td>
        <td>${row.prd_status}</td>
      </tr>
    `)
    .join("");
  renderPrdDetail(rows[0].requirement_id);
}

function renderExperiment() {
  const experiments = state.payload.experimentReadout.slice(0, 8);
  const gates = state.payload.readinessRegister.slice(0, 8);

  document.querySelector("#experimentRows").innerHTML = experiments
    .map((row) => `
      <tr>
        <td>${row.workflow}<small>${row.product_area}</small></td>
        <td>${row.primary_metric}</td>
        <td>${row.sample_plan}</td>
        <td>${row.minimum_detectable_lift}</td>
        <td>${row.decision_rule}</td>
      </tr>
    `)
    .join("");

  document.querySelector("#gateCards").innerHTML = gates
    .map((row) => `
      <article class="gate-card">
        <span>${row.launch_status}</span>
        <strong>${row.workflow}</strong>
        <dl>
          <div><dt>Readiness</dt><dd>${row.readiness_score}</dd></div>
          <div><dt>Weakest gate</dt><dd>${row.weakest_gate}</dd></div>
          <div><dt>Owner</dt><dd>${row.owner_team}</dd></div>
        </dl>
      </article>
    `)
    .join("");
}

function renderPlatform() {
  const rows = state.payload.platformReadiness;
  const benchmarks = state.payload.publicBenchmarks;

  document.querySelector("#platformRows").innerHTML = rows
    .map((row) => `
      <tr>
        <td>
          ${row.workflow}
          <small>${row.contract_name}</small>
        </td>
        <td>${row.source_domain}<small>${row.required_fields}</small></td>
        <td>${row.freshness_sla_hours}h<small>${Math.round(row.missingness_rate * 100)}% missingness</small></td>
        <td>${Math.round(row.decision_confidence * 100)}%</td>
        <td>${row.model_action}</td>
        <td>${pill(row.launch_blocker)}</td>
      </tr>
    `)
    .join("");

  document.querySelector("#benchmarkCards").innerHTML = benchmarks
    .map((row) => `
      <article class="benchmark-card">
        <span>${row.source}</span>
        <strong>${row.metric}</strong>
        <em>${row.benchmark_value}</em>
        <p>${row.use_in_artifact}</p>
      </article>
    `)
    .join("");
}

function setSurface(surface) {
  state.surface = surface;
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.classList.toggle("active", button.dataset.surface === surface);
  });
  document.querySelectorAll(".surface").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${surface}Surface`);
  });
}

function bindEvents() {
  document.querySelector(".tabs").addEventListener("click", (event) => {
    const button = event.target.closest("[data-surface]");
    if (button) setSurface(button.dataset.surface);
  });

  document.body.addEventListener("click", (event) => {
    const workflow = event.target.closest("[data-workflow]");
    if (workflow) renderRoadmapDetail(workflow.dataset.workflow);
    const requirement = event.target.closest("[data-requirement]");
    if (requirement) renderPrdDetail(requirement.dataset.requirement);
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  renderSummary();
  renderRoadmap();
  renderPrd();
  renderExperiment();
  renderPlatform();
  bindEvents();

  const requestedSurface = new URLSearchParams(window.location.search).get("surface");
  if (["roadmap", "prd", "experiment", "platform"].includes(requestedSurface)) {
    setSurface(requestedSurface);
  }
}

init();

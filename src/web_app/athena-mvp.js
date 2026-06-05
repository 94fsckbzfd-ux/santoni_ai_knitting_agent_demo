const athenaForm = document.querySelector("#athenaMvpForm");
const athenaStatus = document.querySelector("#athenaStatus");
const athenaGate = document.querySelector("#athenaGate");
const athenaKpis = document.querySelector("#athenaKpis");
const athenaStages = document.querySelector("#athenaStages");
const engineeringBrief = document.querySelector("#engineeringBrief");
const manufacturabilityCheck = document.querySelector("#manufacturabilityCheck");
const productionReadiness = document.querySelector("#productionReadiness");
const toolInterfaces = document.querySelector("#toolInterfaces");
const evidenceLog = document.querySelector("#evidenceLog");
const loadAthenaExample = document.querySelector("#loadAthenaExample");
const exportAthenaEvidence = document.querySelector("#exportAthenaEvidence");

let latestWorkflowResult = null;

const examplePayload = {
  source_type: "style3d",
  customer_or_project: "Decathlon running top sample",
  product_category: "seamless running top",
  target_user: "women performance runners",
  use_case: "summer running and high-sweat training",
  functional_requirements: "breathability, quick dry, light compression, underarm ventilation, small logo pattern",
  material_preferences: "PA/elastane quick-dry blend, optional recycled yarn",
  constraints: "use approved seamless template, avoid unvalidated production-file changes, target low sample rework, cost controlled",
  source_assets: "Style3D render, CLO screenshot, technical package note",
  sampling_feedback: "Round 1 mock feedback: ventilation looks good, support zone feels slightly stiff, logo area needs elasticity review.",
  defect_signals: "support zone stiffness, logo elasticity variation",
};

async function initAthenaPage() {
  try {
    const [statusResponse, templateResponse] = await Promise.all([
      fetch(`/api/status?ts=${Date.now()}`),
      fetch(`/api/athena-mvp/template?ts=${Date.now()}`),
    ]);
    const status = await statusResponse.json();
    const template = await templateResponse.json();
    athenaStatus.textContent = `${status.version} · ${template.template_id}`;
  } catch {
    athenaStatus.textContent = "Server unavailable";
  }
}

function formPayload() {
  return {
    source_type: fieldValue("sourceType"),
    customer_or_project: fieldValue("customerOrProject"),
    product_category: fieldValue("productCategory"),
    target_user: fieldValue("targetUser"),
    use_case: fieldValue("useCase"),
    functional_requirements: fieldValue("functionalRequirements"),
    material_preferences: fieldValue("materialPreferences"),
    constraints: fieldValue("constraints"),
    source_assets: fieldValue("sourceAssets"),
    sampling_feedback: fieldValue("samplingFeedback"),
    defect_signals: fieldValue("defectSignals"),
  };
}

function fieldValue(id) {
  return document.querySelector(`#${id}`)?.value.trim() || "";
}

async function runAthenaWorkflow(payload) {
  athenaGate.textContent = "Running";
  const response = await fetch("/api/athena-mvp/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Design Intake API failed");
  latestWorkflowResult = await response.json();
  exportAthenaEvidence.disabled = false;
  renderAthenaResult(latestWorkflowResult);
}

function renderAthenaResult(result) {
  const objects = result.data_objects;
  athenaGate.textContent = objects.production_readiness.gate.replaceAll("_", " ");
  renderKpis(result.kpi_log || []);
  renderStages(result.stages || []);
  renderObject(engineeringBrief, objects.engineering_brief);
  renderObject(manufacturabilityCheck, objects.manufacturability_check);
  renderObject(productionReadiness, {
    sampling_feedback: objects.sampling_feedback,
    revision_suggestion: objects.revision_suggestion,
    production_readiness: objects.production_readiness,
  });
  renderListObjects(toolInterfaces, result.tool_interfaces || []);
  renderEvidence(result.evidence_log || []);
}

function renderKpis(items) {
  athenaKpis.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "athena-kpi";
    card.innerHTML = `
      <span>${escapeHtml(item.kpi)}</span>
      <strong>${escapeHtml(item.demo_target)}</strong>
      <p>${escapeHtml(item.baseline)} · ${escapeHtml(item.evidence_ref)}</p>
    `;
    athenaKpis.append(card);
  });
}

function renderStages(items) {
  athenaStages.innerHTML = "";
  items.forEach((stage, index) => {
    const card = document.createElement("article");
    card.className = "athena-stage";
    card.innerHTML = `
      <span>${index + 1}</span>
      <strong>${escapeHtml(stage.name)}</strong>
      <p>${escapeHtml(stage.owner_role)} · ${escapeHtml(stage.status)}</p>
      <small>${escapeHtml(stage.output_object)}</small>
    `;
    athenaStages.append(card);
  });
}

function renderObject(target, data) {
  target.innerHTML = "";
  const list = document.createElement("dl");
  Object.entries(data || {}).forEach(([key, value]) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = formatKey(key);
    dd.textContent = formatValue(value);
    row.append(dt, dd);
    list.append(row);
  });
  target.append(list);
}

function renderListObjects(target, items) {
  target.innerHTML = "";
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "mini-object";
    article.innerHTML = `
      <strong>${escapeHtml(item.tool)}</strong>
      <p>${escapeHtml(item.status)} · write: ${escapeHtml(item.write_permission)}</p>
      <small>${escapeHtml(item.input)} -> ${escapeHtml(item.output)}</small>
    `;
    target.append(article);
  });
}

function renderEvidence(items) {
  evidenceLog.innerHTML = "";
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "evidence-item";
    article.innerHTML = `
      <strong>${escapeHtml(item.evidence_id)} · ${escapeHtml(item.source)}</strong>
      <p>${escapeHtml(item.claim)}</p>
      <small>${escapeHtml(item.object_type)} · ${escapeHtml(item.status)}</small>
    `;
    evidenceLog.append(article);
  });
}

function formatKey(key) {
  return key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join("; ");
  }
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${formatKey(key)}: ${formatValue(item)}`)
      .join("; ");
  }
  return String(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setExample() {
  document.querySelector("#sourceType").value = examplePayload.source_type;
  document.querySelector("#customerOrProject").value = examplePayload.customer_or_project;
  document.querySelector("#productCategory").value = examplePayload.product_category;
  document.querySelector("#targetUser").value = examplePayload.target_user;
  document.querySelector("#useCase").value = examplePayload.use_case;
  document.querySelector("#functionalRequirements").value = examplePayload.functional_requirements;
  document.querySelector("#materialPreferences").value = examplePayload.material_preferences;
  document.querySelector("#constraints").value = examplePayload.constraints;
  document.querySelector("#sourceAssets").value = examplePayload.source_assets;
  document.querySelector("#samplingFeedback").value = examplePayload.sampling_feedback;
  document.querySelector("#defectSignals").value = examplePayload.defect_signals;
}

function exportEvidence() {
  if (!latestWorkflowResult) return;
  const payload = {
    exported_at: new Date().toISOString(),
    version: "v0.25.3",
    template_id: latestWorkflowResult.workflow_template.template_id,
    workflow_instance: latestWorkflowResult.workflow_instance,
    evidence_log: latestWorkflowResult.evidence_log,
    kpi_log: latestWorkflowResult.kpi_log,
    data_objects: latestWorkflowResult.data_objects,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const timestamp = new Date().toISOString().replaceAll(":", "-").slice(0, 19);
  link.href = url;
  link.download = `design-intake-structuring-evidence-${timestamp}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

athenaForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await runAthenaWorkflow(formPayload());
  } catch {
    athenaGate.textContent = "API unavailable";
  }
});

loadAthenaExample.addEventListener("click", () => {
  setExample();
});

exportAthenaEvidence.addEventListener("click", exportEvidence);

initAthenaPage();
runAthenaWorkflow(formPayload()).catch(() => {
  athenaGate.textContent = "API unavailable";
});

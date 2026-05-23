const caseCount = document.querySelector("#caseCount");
const implementedCount = document.querySelector("#implementedCount");
const needsReviewCount = document.querySelector("#needsReviewCount");
const draftCount = document.querySelector("#draftCount");
const approvedCount = document.querySelector("#approvedCount");
const needsChangesCount = document.querySelector("#needsChangesCount");
const internalOnlyCount = document.querySelector("#internalOnlyCount");
const onlineSolvableCount = document.querySelector("#onlineSolvableCount");
const dispatchLikelyCount = document.querySelector("#dispatchLikelyCount");
const severityCounts = document.querySelector("#severityCounts");
const casePlanList = document.querySelector("#casePlanList");
const caseSearch = document.querySelector("#caseSearch");
const statusFilter = document.querySelector("#statusFilter");
const categoryFilter = document.querySelector("#categoryFilter");
const solvableFilter = document.querySelector("#solvableFilter");
const caseList = document.querySelector("#caseList");
const caseEmpty = document.querySelector("#caseEmpty");

const editableListFields = [
  "machine_models",
  "symptom_keywords",
  "alarm_codes",
  "online_resolution_steps",
  "safety_warnings",
  "dispatch_triggers",
  "recommended_parts",
];

let allCases = [];

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function list(values) {
  const clean = (values || []).filter(Boolean);
  if (!clean.length) return "<span class=\"muted-text\">Not set</span>";
  return `<ul>${clean.map((value) => `<li>${escapeHtml(String(value))}</li>`).join("")}</ul>`;
}

function tags(values) {
  const clean = (values || []).filter(Boolean);
  if (!clean.length) return "<span class=\"muted-text\">Not set</span>";
  return clean.map((value) => `<span class=\"tag\">${escapeHtml(String(value))}</span>`).join("");
}

function textareaValue(values) {
  if (Array.isArray(values)) return values.join("\n");
  return String(values || "");
}

function renderPlans(plans) {
  casePlanList.innerHTML = "";
  (plans || []).forEach((plan) => {
    const li = document.createElement("li");
    li.textContent = `[${plan.status}] ${plan.name}: ${plan.description}`;
    casePlanList.append(li);
  });
}

function fillFilter(select, values) {
  const firstOption = select.querySelector("option");
  select.innerHTML = "";
  select.append(firstOption);
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.append(option);
  });
}

function reviewControls(caseItem) {
  const statuses = [
    ["approved", "Approve"],
    ["needs_changes", "Needs Changes"],
    ["internal_only", "Internal Only"],
    ["draft_needs_review", "Reset Draft"],
  ];
  return `
    <div class="case-review">
      <select class="review-status" aria-label="Review status for ${escapeHtml(caseItem.case_id)}">
        ${statuses.map(([value, label]) => `
          <option value="${value}" ${caseItem.review_status === value ? "selected" : ""}>${label}</option>
        `).join("")}
      </select>
      <input class="review-note" type="text" value="${escapeHtml(caseItem.review_note || "")}" placeholder="Review note">
      <button class="secondary-button review-save" type="button" data-case-id="${escapeHtml(caseItem.case_id)}">Save Console Changes</button>
    </div>
  `;
}

function initializeFilters(cases) {
  const statuses = [...new Set(cases.map((item) => item.review_status).filter(Boolean))].sort();
  const categories = [...new Set(cases.map((item) => item.issue_category).filter(Boolean))].sort();
  fillFilter(statusFilter, statuses);
  fillFilter(categoryFilter, categories);
}

function caseMatches(caseItem) {
  const query = caseSearch.value.trim().toLowerCase();
  const selectedStatus = statusFilter.value;
  const selectedCategory = categoryFilter.value;
  const selectedSolvable = solvableFilter.value;

  if (selectedStatus && caseItem.review_status !== selectedStatus) return false;
  if (selectedCategory && caseItem.issue_category !== selectedCategory) return false;
  if (selectedSolvable === "online" && !caseItem.online_solvable) return false;
  if (selectedSolvable === "dispatch" && caseItem.online_solvable) return false;
  if (!query) return true;

  const text = [
    caseItem.case_id,
    caseItem.title,
    caseItem.source,
    caseItem.review_status,
    caseItem.issue_category,
    caseItem.severity,
    caseItem.source_row_count,
    ...(caseItem.machine_models || []),
    ...(caseItem.symptom_keywords || []),
    ...(caseItem.alarm_codes || []),
    ...(caseItem.recommended_parts || []),
    ...(caseItem.online_resolution_steps || []),
    ...(caseItem.dispatch_triggers || []),
  ].join(" ").toLowerCase();
  return text.includes(query);
}

function renderDiff(caseItem) {
  const changed = caseItem.changed_fields || [];
  if (!changed.length) {
    return "<p class=\"muted-text\">No reviewer edits yet. The effective case matches the original import/mock content.</p>";
  }
  return `
    <div class="diff-list">
      ${changed.map((field) => {
        const original = caseItem.original_fields?.[field];
        const effective = caseItem.editable_fields?.[field];
        return `
          <div class="diff-row">
            <strong>${escapeHtml(field)}</strong>
            <div>
              <span>Original</span>
              <pre>${escapeHtml(JSON.stringify(original, null, 2))}</pre>
            </div>
            <div>
              <span>Effective</span>
              <pre>${escapeHtml(JSON.stringify(effective, null, 2))}</pre>
            </div>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderEditor(caseItem) {
  return `
    <details class="case-editor">
      <summary>Edit case knowledge, diff, and handoff payload</summary>
      <div class="editor-grid">
        <label>
          Title
          <input class="case-field" data-field="title" value="${escapeHtml(caseItem.title || "")}">
        </label>
        <label>
          Issue Category
          <input class="case-field" data-field="issue_category" value="${escapeHtml(caseItem.issue_category || "")}">
        </label>
        <label>
          Severity
          <select class="case-field" data-field="severity">
            ${["P1", "P2", "P3", ""].map((value) => `
              <option value="${value}" ${caseItem.severity === value ? "selected" : ""}>${value || "Unset"}</option>
            `).join("")}
          </select>
        </label>
        <label class="editor-check">
          <input class="case-field" data-field="online_solvable" type="checkbox" ${caseItem.online_solvable ? "checked" : ""}>
          Online solvable
        </label>
        <label>
          Machine Models
          <textarea class="case-field" data-field="machine_models">${escapeHtml(textareaValue(caseItem.machine_models))}</textarea>
        </label>
        <label>
          Symptom Keywords
          <textarea class="case-field" data-field="symptom_keywords">${escapeHtml(textareaValue(caseItem.symptom_keywords))}</textarea>
        </label>
        <label>
          Alarm Codes
          <textarea class="case-field" data-field="alarm_codes">${escapeHtml(textareaValue(caseItem.alarm_codes))}</textarea>
        </label>
        <label>
          Recommended Parts
          <textarea class="case-field" data-field="recommended_parts">${escapeHtml(textareaValue(caseItem.recommended_parts))}</textarea>
        </label>
        <label class="wide">
          Online Resolution Steps
          <textarea class="case-field tall" data-field="online_resolution_steps">${escapeHtml(textareaValue(caseItem.online_resolution_steps))}</textarea>
        </label>
        <label class="wide">
          Safety Warnings
          <textarea class="case-field tall" data-field="safety_warnings">${escapeHtml(textareaValue(caseItem.safety_warnings))}</textarea>
        </label>
        <label class="wide">
          Dispatch Triggers
          <textarea class="case-field tall" data-field="dispatch_triggers">${escapeHtml(textareaValue(caseItem.dispatch_triggers))}</textarea>
        </label>
        <label>
          Estimated Resolution Time
          <input class="case-field" data-field="estimated_resolution_time" value="${escapeHtml(caseItem.estimated_resolution_time || "")}">
        </label>
        <label>
          Confidence Notes
          <textarea class="case-field" data-field="confidence_notes">${escapeHtml(caseItem.confidence_notes || "")}</textarea>
        </label>
      </div>
      <div class="case-columns">
        <div class="case-section">
          <h3>Diff View</h3>
          ${renderDiff(caseItem)}
        </div>
        <div class="case-section">
          <h3>CRM / Ticket Handoff Payload Preview</h3>
          <pre class="payload-preview">${escapeHtml(JSON.stringify(caseItem.handoff_payload_preview || {}, null, 2))}</pre>
        </div>
      </div>
    </details>
  `;
}

function renderCase(caseItem) {
  const card = document.createElement("article");
  card.className = "case-card";
  card.dataset.caseId = caseItem.case_id;
  card.innerHTML = `
    <div class="case-card-header">
      <div>
        <p class="eyebrow">${escapeHtml(caseItem.case_id)}</p>
        <h2>${escapeHtml(caseItem.title)}</h2>
      </div>
      <span class="case-pill">${escapeHtml(caseItem.review_status)}</span>
    </div>
    <div class="case-meta">
      <span>${escapeHtml(caseItem.source)}</span>
      <span>${escapeHtml(caseItem.issue_category || "uncategorized")}</span>
      <span>${escapeHtml(caseItem.severity || "severity unset")}</span>
      ${caseItem.source_row_count ? `<span>${escapeHtml(caseItem.source_row_count)} Excel rows</span>` : ""}
      <span>${caseItem.online_solvable ? "online solvable" : "dispatch likely"}</span>
      <span>${caseItem.customer_visible ? "customer visible" : "internal review"}</span>
      ${(caseItem.changed_fields || []).length ? `<span>${caseItem.changed_fields.length} edited fields</span>` : ""}
    </div>
    ${reviewControls(caseItem)}
    ${renderEditor(caseItem)}
    <div class="case-section">
      <h3>Machine Models</h3>
      <div class="tag-list">${tags(caseItem.machine_models)}</div>
    </div>
    ${caseItem.source_serials?.length ? `
      <div class="case-section">
        <h3>Source Serials / WO</h3>
        <div class="tag-list">${tags([...(caseItem.source_serials || []).slice(0, 8), ...(caseItem.source_wo_numbers || []).slice(0, 8)])}</div>
      </div>
    ` : ""}
    <div class="case-section">
      <h3>Symptoms / Alarms</h3>
      <div class="tag-list">${tags([...(caseItem.symptom_keywords || []), ...(caseItem.alarm_codes || [])])}</div>
    </div>
    <div class="case-columns">
      <div class="case-section">
        <h3>Online Steps</h3>
        ${list(caseItem.online_resolution_steps)}
      </div>
      <div class="case-section">
        <h3>Dispatch Triggers</h3>
        ${list(caseItem.dispatch_triggers)}
      </div>
    </div>
    <div class="case-columns">
      <div class="case-section">
        <h3>Safety Warnings</h3>
        ${list(caseItem.safety_warnings)}
      </div>
      <div class="case-section">
        <h3>Parts / Time</h3>
        ${list([...(caseItem.recommended_parts || []), caseItem.estimated_resolution_time])}
      </div>
    </div>
    <p class="case-note">${escapeHtml(caseItem.confidence_notes || "No confidence note yet.")}</p>
    ${caseItem.reviewed_at ? `<p class="case-note">Reviewed at: ${escapeHtml(caseItem.reviewed_at)}</p>` : ""}
  `;
  caseList.append(card);
}

function renderCases() {
  const filtered = allCases.filter(caseMatches);
  caseList.innerHTML = "";
  filtered.forEach(renderCase);
  caseEmpty.hidden = filtered.length > 0;
}

function updateSummary(data) {
  const counts = data.severity_counts || {};
  caseCount.textContent = data.case_count || 0;
  implementedCount.textContent = data.implemented_count || 0;
  needsReviewCount.textContent = data.needs_review_count || 0;
  draftCount.textContent = data.draft_count || 0;
  approvedCount.textContent = data.approved_count || 0;
  needsChangesCount.textContent = data.needs_changes_count || 0;
  internalOnlyCount.textContent = data.internal_only_count || 0;
  onlineSolvableCount.textContent = data.online_solvable_count || 0;
  dispatchLikelyCount.textContent = data.dispatch_likely_count || 0;
  severityCounts.textContent = `${counts.P1 || 0} / ${counts.P2 || 0} / ${counts.P3 || 0}`;
}

async function loadServiceCases() {
  const response = await fetch(`/api/service-cases?ts=${Date.now()}`);
  const data = await response.json();
  allCases = data.cases || [];

  updateSummary(data);
  renderPlans(data.planned_features || []);
  initializeFilters(allCases);
  renderCases();
}

function collectCaseUpdates(card) {
  const updates = {};
  card.querySelectorAll(".case-field").forEach((field) => {
    const key = field.dataset.field;
    if (!key) return;
    if (field.type === "checkbox") {
      updates[key] = field.checked;
    } else if (editableListFields.includes(key)) {
      updates[key] = field.value.split(/\n|,|，|;|；/).map((item) => item.trim()).filter(Boolean);
    } else {
      updates[key] = field.value.trim();
    }
  });
  return updates;
}

[caseSearch, statusFilter, categoryFilter, solvableFilter].forEach((element) => {
  element.addEventListener("input", renderCases);
  element.addEventListener("change", renderCases);
});

loadServiceCases().catch(() => {
  caseList.innerHTML = "<article class=\"case-card\">Service Manager Console unavailable. Please restart the demo server.</article>";
});

caseList.addEventListener("click", async (event) => {
  const button = event.target.closest(".review-save");
  if (!button) return;

  const card = button.closest(".case-card");
  const payload = {
    case_id: button.dataset.caseId,
    review_status: card.querySelector(".review-status").value,
    review_note: card.querySelector(".review-note").value,
    case_updates: collectCaseUpdates(card),
  };
  button.disabled = true;
  button.textContent = "Saving";
  try {
    const response = await fetch("/api/service-cases/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Review save failed");
    }
    const data = await response.json();
    allCases = data.cases || [];
    updateSummary(data);
    renderCases();
  } catch (error) {
    button.textContent = "Save Failed";
    button.title = error.message;
    return;
  } finally {
    button.disabled = false;
  }
});

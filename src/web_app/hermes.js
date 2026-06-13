const hermesStatus = document.querySelector("#hermesStatus");
const hermesSummary = document.querySelector("#hermesSummary");
const hermesLoop = document.querySelector("#hermesLoop");
const hermesContract = document.querySelector("#hermesContract");
const hermesMemory = document.querySelector("#hermesMemory");
const hermesPlaybook = document.querySelector("#hermesPlaybook");
const hermesSuggestForm = document.querySelector("#hermesSuggestForm");
const hermesFocus = document.querySelector("#hermesFocus");
const hermesSuggestions = document.querySelector("#hermesSuggestions");
const hermesTools = document.querySelector("#hermesTools");
const hermesKpis = document.querySelector("#hermesKpis");
const hermesEvidence = document.querySelector("#hermesEvidence");

let lastHermesStatus = null;
let lastHermesOverview = null;
let lastHermesSuggestionResult = null;

const HERMES_STATUS_LABELS = {
  mock_contract: ["Mock Contract", "本地 Mock 契约"],
  read_only_planned: ["Read-only Planned", "只读接口规划"],
  available_local_api: ["Available Local API", "本地 API 可用"],
  planned_after_schema_confirmation: ["Planned After Schema", "Schema 确认后规划"],
  not_configured: ["Not Configured", "尚未配置"],
  proposal_only_no_auto_code_change: ["Proposal Only", "仅建议"],
  candidate_only_until_schema_confirmed: ["Candidate Only", "Schema 确认前仅候选"],
  read_only_no_aps_iot_write: ["Read-only", "只读"],
  blocked_in_demo: ["Blocked In Demo", "Demo 中禁止"],
  none: ["None", "无"],
  ok: ["OK", "正常"],
};

const HERMES_LABELS = {
  memory_event_count: ["Memory Events", "记忆事件"],
  evidence_coverage: ["Evidence Coverage", "证据覆盖"],
  development_suggestion_count: ["Dev Suggestions", "开发建议"],
  open_decision_count: ["Open Decisions", "待决事项"],
  adapter_contract_coverage: ["Adapter Interfaces", "接口契约"],
  human_review_required_count: ["Human Review", "人工审核"],
  playbook_candidate_count: ["Playbook Candidates", "Playbook 候选"],
  playbook_ready_for_review_count: ["Ready Playbooks", "可审核 Playbook"],
  playbook_approved_count: ["Approved Playbooks", "已批准 Playbook"],
  credential_storage_findings: ["Credential Findings", "凭据存储问题"],
  evidence_log_count: ["Evidence Items", "证据条目"],
  capture_memory_event: ["Capture memory event", "捕获记忆事件"],
  normalize_evidence: ["Normalize evidence", "标准化证据"],
  score_gap_or_opportunity: ["Score gap or opportunity", "评估差距或机会"],
  propose_development_suggestion: ["Propose development suggestion", "提出开发建议"],
  human_review: ["Human review", "人工审核"],
  planned_adapter_or_workflow_update: ["Plan adapter or workflow update", "规划接口或工作流更新"],
  regression_test: ["Regression test", "回归测试"],
  true: ["true", "是"],
  false: ["false", "否"],
};

function getHermesLanguage() {
  return window.SantoniI18n?.getLanguage?.() || (document.documentElement.lang.startsWith("zh") ? "zh" : "en");
}

function hermesIsZh() {
  return getHermesLanguage() === "zh";
}

function hermesPair(pair) {
  return hermesIsZh() ? pair[1] : pair[0];
}

function hermesLabel(key, fallback = key) {
  return HERMES_LABELS[key] ? hermesPair(HERMES_LABELS[key]) : HERMES_STATUS_LABELS[key] ? hermesPair(HERMES_STATUS_LABELS[key]) : fallback;
}

async function loadHermes() {
  hermesStatus.textContent = hermesIsZh() ? "加载中" : "Loading";
  const [statusResponse, overviewResponse] = await Promise.all([
    fetch(`/api/status?ts=${Date.now()}`),
    fetch(`/api/hermes/overview?ts=${Date.now()}`),
  ]);
  lastHermesStatus = await statusResponse.json();
  lastHermesOverview = await overviewResponse.json();
  renderHermes(lastHermesOverview);
  await refreshHermesSuggestions();
}

function renderHermes(result) {
  renderHermesStatus(result);
  renderHermesSummary(result);
  renderHermesLoop(result.workflow_template?.primary_loop || []);
  renderHermesContract(result.adapter_contract || {});
  renderHermesMemory(result.memory_events || []);
  renderHermesPlaybook(result.organization_memory_playbook || {});
  renderHermesSuggestions(lastHermesSuggestionResult?.suggestions || result.development_suggestions || []);
  renderHermesTools(result.tool_registry_candidates || []);
  renderHermesKpis(result.kpi_log || []);
  renderHermesEvidence(result.evidence_log || []);
}

function renderHermesStatus(result) {
  const version = lastHermesStatus?.version || result.workflow_instance?.version || "";
  const status = result.workflow_instance?.status || "mock_contract";
  hermesStatus.textContent = `${version} · ${hermesLabel(status)}`;
}

function renderHermesSummary(result) {
  const overview = result.hermes_overview || {};
  const kpiMap = new Map((result.kpi_log || []).map((item) => [item.kpi, item.value]));
  const tiles = [
    [["Real Hermes", "真实 Hermes"], hermesLabel(String(Boolean(result.workflow_instance?.real_hermes_connected)))],
    [["Writeback", "写回能力"], result.workflow_instance?.write_actions_blocked ? (hermesIsZh() ? "禁止" : "Blocked") : (hermesIsZh() ? "允许" : "Enabled")],
    [["Memory Events", "记忆事件"], kpiMap.get("memory_event_count") ?? 0],
    [["Playbook Candidates", "Playbook 候选"], kpiMap.get("playbook_candidate_count") ?? 0],
    [["Dev Suggestions", "开发建议"], kpiMap.get("development_suggestion_count") ?? 0],
    [["Open Decisions", "待决事项"], overview.open_decision_count ?? 0],
    [["Tool Candidates", "工具候选"], result.tool_registry_candidates?.length ?? 0],
    [["Evidence Items", "证据条目"], kpiMap.get("evidence_log_count") ?? 0],
    [["Adapter Status", "接口状态"], hermesLabel(overview.adapter_status || "mock_contract")],
  ];

  hermesSummary.innerHTML = "";
  tiles.forEach(([label, value]) => {
    const tile = document.createElement("article");
    tile.className = "production-tile";
    tile.innerHTML = `<span>${escapeHermes(hermesPair(label))}</span><strong>${escapeHermes(value)}</strong>`;
    hermesSummary.append(tile);
  });
}

function renderHermesLoop(steps) {
  hermesLoop.innerHTML = "";
  steps.forEach((step, index) => {
    const item = document.createElement("article");
    item.className = "workflow-step ok";
    item.innerHTML = `
      <span>${index + 1}</span>
      <strong>${escapeHermes(hermesLabel(step, step.replaceAll("_", " ")))}</strong>
      <p>${escapeHermes(hermesIsZh() ? "证据驱动，不自动改代码或写生产系统。" : "Evidence-driven; no automatic code or production writeback.")}</p>
    `;
    hermesLoop.append(item);
  });
}

function renderHermesContract(contract) {
  const interfaces = contract.interfaces || [];
  hermesContract.innerHTML = `
    <div class="mini-object">
      <small>${escapeHermes(contract.contract_id || "")}</small>
      <strong>${escapeHermes(hermesLabel(contract.adapter_status || "mock_contract"))}</strong>
      <p>${escapeHermes(contract.scope || "")}</p>
      <p>${escapeHermes(contract.credential_policy || "")}</p>
    </div>
  `;
  interfaces.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeHermes(item.direction)} · ${escapeHermes(item.evidence_ref)}</small>
      <strong>${escapeHermes(item.name)}</strong>
      <p>${escapeHermes(item.source_object)} → ${escapeHermes(item.target_object)}</p>
      <p>${escapeHermes(hermesLabel(item.status))} · ${escapeHermes(hermesLabel(item.write_policy, item.write_policy))}</p>
    `;
    hermesContract.append(card);
  });
}

function renderHermesMemory(events) {
  hermesMemory.innerHTML = "";
  events.forEach((event) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeHermes(event.event_id)} · ${escapeHermes(event.type)} · ${escapeHermes(event.evidence_ref)}</small>
      <strong>${escapeHermes(event.object_scope.join(" / "))}</strong>
      <p>${escapeHermes(event.summary)}</p>
      <p>${escapeHermes(hermesIsZh() ? "范围" : "Scope")}: ${escapeHermes(event.scope)} · ${escapeHermes(hermesIsZh() ? "租户" : "Tenant")}: ${escapeHermes(event.tenant_id || "null")} · ${escapeHermes(hermesIsZh() ? "工厂" : "Factory")}: ${escapeHermes(event.factory_id || "null")} · ${escapeHermes(hermesIsZh() ? "来源" : "Source")}: ${escapeHermes(event.source)}</p>
      <p>${escapeHermes(hermesIsZh() ? "留存" : "Retention")}: ${escapeHermes(event.retention_policy)} · ${escapeHermes(hermesIsZh() ? "敏感级别" : "Sensitivity")}: ${escapeHermes(event.sensitivity_level)} · ${escapeHermes(hermesIsZh() ? "晋升状态" : "Promotion")}: ${escapeHermes(event.promotion_status)}</p>
      <p>${escapeHermes(hermesIsZh() ? "写入策略" : "Write policy")}: ${escapeHermes(event.write_policy)}</p>
    `;
    hermesMemory.append(card);
  });
}

function renderHermesPlaybook(playbook) {
  const candidates = playbook.playbook_candidates || [];
  const kpis = playbook.playbook_kpis || {};
  if (!candidates.length) {
    hermesPlaybook.innerHTML = `<p class="muted-text">${escapeHermes(hermesIsZh() ? "暂无 Playbook 候选。" : "No playbook candidates yet.")}</p>`;
    return;
  }

  hermesPlaybook.innerHTML = `
    <div class="mini-object">
      <small>${escapeHermes(playbook.schema_id || "")} · ${escapeHermes(playbook.version || "")}</small>
      <strong>${escapeHermes(hermesIsZh() ? "组织记忆候选不会自动写入 Hermes" : "Organization-memory candidates do not write to live Hermes automatically")}</strong>
      <p>${escapeHermes(hermesIsZh() ? "候选必须先完成跟进闭环、具备可接受证据、通过人工审核，才可晋升为 playbook 或 regression case。" : "Candidates need closed follow-up, accepted evidence, and human review before promotion to a playbook or regression case.")}</p>
      <p>${escapeHermes(hermesIsZh() ? "候选" : "Candidates")}: ${escapeHermes(kpis.candidate_count ?? 0)} · ${escapeHermes(hermesIsZh() ? "可审核" : "Ready")}: ${escapeHermes(kpis.ready_for_review_count ?? 0)} · ${escapeHermes(hermesIsZh() ? "已批准" : "Approved")}: ${escapeHermes(kpis.approved_count ?? 0)}</p>
    </div>
  `;

  candidates.forEach((item) => {
    const card = document.createElement("article");
    card.className = `playbook-card ${escapeHermes(item.readiness || "candidate")}`;
    card.innerHTML = `
      <small>${escapeHermes(item.candidate_id)} · ${escapeHermes(item.management_theme || "")} · ${escapeHermes(item.promotion_status || "candidate")}</small>
      <strong>${escapeHermes(item.trigger_signal || item.recommended_action_pattern || "")}</strong>
      <dl>
        <div><dt>${escapeHermes(hermesIsZh() ? "状态" : "Status")}</dt><dd>${escapeHermes(item.current_follow_up_status || "")}</dd></div>
        <div><dt>${escapeHermes(hermesIsZh() ? "证据" : "Evidence")}</dt><dd>${escapeHermes(item.evidence_status || "")}</dd></div>
        <div><dt>${escapeHermes(hermesIsZh() ? "晋升门" : "Readiness")}</dt><dd>${escapeHermes(item.readiness || "")}</dd></div>
        <div><dt>${escapeHermes(hermesIsZh() ? "负责人" : "Owner")}</dt><dd>${escapeHermes(item.owner_role || "")}</dd></div>
      </dl>
      <p>${escapeHermes(hermesIsZh() ? "建议模式" : "Action pattern")}: ${escapeHermes(item.recommended_action_pattern || "")}</p>
      <p>${escapeHermes(hermesIsZh() ? "证据引用" : "Evidence refs")}: ${escapeHermes((item.evidence_refs || []).join(", "))}</p>
      <div class="playbook-actions">
        <button type="button" data-playbook-status="reviewed" data-candidate-id="${escapeHermes(item.candidate_id)}">${escapeHermes(hermesIsZh() ? "标记已审" : "Mark Reviewed")}</button>
        <button type="button" data-playbook-status="needs_changes" data-candidate-id="${escapeHermes(item.candidate_id)}">${escapeHermes(hermesIsZh() ? "需修改" : "Needs Changes")}</button>
        <button type="button" data-playbook-status="approved" data-candidate-id="${escapeHermes(item.candidate_id)}" ${item.ready_for_playbook_review ? "" : "disabled"}>${escapeHermes(hermesIsZh() ? "批准晋升" : "Approve")}</button>
      </div>
    `;
    hermesPlaybook.append(card);
  });
}

async function refreshHermesSuggestions() {
  const response = await fetch("/api/hermes/suggest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ focus: hermesFocus.value }),
  });
  lastHermesSuggestionResult = await response.json();
  renderHermesSuggestions(lastHermesSuggestionResult.suggestions || []);
}

function renderHermesSuggestions(suggestions) {
  hermesSuggestions.innerHTML = "";
  suggestions.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object hermes-suggestion";
    card.innerHTML = `
      <small>${escapeHermes(item.suggestion_id)} · ${escapeHermes(item.priority)} · ${escapeHermes(item.scope)}</small>
      <strong>${escapeHermes(item.title)}</strong>
      <p>${escapeHermes(item.reason)}</p>
      <p>${escapeHermes(hermesIsZh() ? "预期影响" : "Expected impact")}: ${escapeHermes(item.expected_impact)}</p>
      <ul>${(item.next_actions || []).map((action) => `<li>${escapeHermes(action)}</li>`).join("")}</ul>
      <p>${escapeHermes(hermesIsZh() ? "证据" : "Evidence")}: ${escapeHermes((item.evidence_refs || []).join(", "))}</p>
    `;
    hermesSuggestions.append(card);
  });
}

function renderHermesTools(tools) {
  hermesTools.innerHTML = "";
  tools.forEach((tool) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeHermes(hermesLabel(tool.status, tool.status))}</small>
      <strong>${escapeHermes(tool.tool_id)}</strong>
      <p>${escapeHermes(tool.endpoint)}</p>
      <p>${escapeHermes(hermesIsZh() ? "写权限" : "Write permission")}: ${escapeHermes(hermesLabel(tool.write_permission, tool.write_permission))}</p>
    `;
    hermesTools.append(card);
  });
}

function renderHermesKpis(kpis) {
  hermesKpis.innerHTML = "";
  kpis.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeHermes(hermesLabel(item.status, item.status))}</small>
      <strong>${escapeHermes(hermesLabel(item.kpi, item.kpi))}</strong>
      <p>${escapeHermes(hermesIsZh() ? "当前值" : "Value")}: ${escapeHermes(item.value)} · ${escapeHermes(hermesIsZh() ? "目标" : "Target")}: ${escapeHermes(item.target)}</p>
    `;
    hermesKpis.append(card);
  });
}

function renderHermesEvidence(evidence) {
  hermesEvidence.innerHTML = "";
  evidence.forEach((item) => {
    const card = document.createElement("article");
    card.className = "mini-object";
    card.innerHTML = `
      <small>${escapeHermes(item.evidence_id)} · ${escapeHermes(item.status)}</small>
      <strong>${escapeHermes(item.source)}</strong>
      <p>${escapeHermes(item.summary)}</p>
    `;
    hermesEvidence.append(card);
  });
}

function escapeHermes(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

hermesSuggestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await refreshHermesSuggestions();
});

hermesPlaybook.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-playbook-status]");
  if (!button) return;
  button.disabled = true;
  try {
    const response = await fetch("/api/hermes/playbook/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        candidate_id: button.dataset.candidateId,
        review_status: button.dataset.playbookStatus,
        review_note: "Hermes Console metadata-only playbook review.",
      }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Failed to save playbook review");
    if (lastHermesOverview) {
      lastHermesOverview.organization_memory_playbook = result.organization_memory_playbook;
    }
    renderHermesPlaybook(result.organization_memory_playbook || {});
  } catch (error) {
    hermesStatus.textContent = error.message;
    button.disabled = false;
  }
});

window.addEventListener("santoni:language-change", () => {
  if (lastHermesOverview) renderHermes(lastHermesOverview);
});

loadHermes().catch((error) => {
  hermesStatus.textContent = hermesIsZh() ? "Hermes 不可用" : "Hermes unavailable";
  hermesSummary.innerHTML = `<article class="production-tile"><span>Error</span><strong>${escapeHermes(error.message)}</strong></article>`;
});

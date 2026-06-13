(function () {
if (!window.fetch && window.XMLHttpRequest) {
  window.fetch = (url, options = {}) => new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(options.method || "GET", url, true);
    Object.entries(options.headers || {}).forEach(([key, value]) => xhr.setRequestHeader(key, value));
    xhr.onload = () => {
      resolve({
        ok: xhr.status >= 200 && xhr.status < 300,
        status: xhr.status,
        text: () => Promise.resolve(xhr.responseText),
        json: () => Promise.resolve(JSON.parse(xhr.responseText || "{}")),
      });
    };
    xhr.onerror = () => reject(new Error("Network request failed"));
    xhr.send(options.body || null);
  });
}
document.documentElement.dataset.userFetch = typeof window.fetch;
document.documentElement.dataset.userXhr = typeof window.XMLHttpRequest;
const userMessagesEl = document.querySelector("#userMessages");
const userFormEl = document.querySelector("#userChatForm");
const userInputEl = document.querySelector("#userMessageInput");
const userImageInputEl = document.querySelector("#userImageInput");
const userAttachmentPreviewEl = document.querySelector("#userAttachmentPreview");
const userResetButton = document.querySelector("#userResetButton");
const userStatusEl = document.querySelector("#userStatus");
const credentialDialogEl = document.querySelector("#credentialDialog");
const credentialFormEl = document.querySelector("#credentialForm");
const credentialUsernameEl = document.querySelector("#credentialUsername");
const credentialPasswordEl = document.querySelector("#credentialPassword");
const credentialMockButton = document.querySelector("#credentialMockButton");
const identityButtons = document.querySelectorAll("[data-identity-role]");
const identityHelpEl = document.querySelector("#identityHelp");
const gmWorkspaceEl = document.querySelector("#gmWorkspace");
const gmRefreshButton = document.querySelector("#gmRefreshButton");
const gmKpiDashboardEl = document.querySelector("#gmKpiDashboard");
const gmBriefSummaryEl = document.querySelector("#gmBriefSummary");
const gmStoryEntryEl = document.querySelector("#gmStoryEntry");
const gmStoryCardsEl = document.querySelector("#gmStoryCards");
const gmRiskCardsEl = document.querySelector("#gmRiskCards");
const gmEvidenceReviewPanelEl = document.querySelector("#gmEvidenceReviewPanel");
const gmEvidenceReviewCardsEl = document.querySelector("#gmEvidenceReviewCards");
const gmServiceRiskPanelEl = document.querySelector("#gmServiceRiskPanel");
const gmServiceRiskCardsEl = document.querySelector("#gmServiceRiskCards");
const gmFollowUpPanelEl = document.querySelector("#gmFollowUpPanel");
const gmFollowUpSummaryEl = document.querySelector("#gmFollowUpSummary");
const gmFollowUpListEl = document.querySelector("#gmFollowUpList");
const gmDailyBriefPanelEl = document.querySelector("#gmDailyBriefPanel");
const gmDailyBriefContentEl = document.querySelector("#gmDailyBriefContent");
const gmDailyBriefGenerateButton = document.querySelector("#gmDailyBriefGenerateButton");
const gmDailyBriefCopyButton = document.querySelector("#gmDailyBriefCopyButton");

let userSessionId = createSessionId();
let currentRole = null;
let userConversationLanguage = "zh";
let pendingAttachment = null;
let platformCredentials = null;
let credentialResolver = null;
let activationToolContext = false;
let gmDashboardLoaded = false;
let gmDashboardResult = null;
let gmDecisionLoop = null;
let gmDailyBriefText = "";
const gmActiveFollowUpActionIds = new Set();

const identityLabels = {
  production_manager: "总经理",
  customer_equipment_engineer: "服务工程师",
  designer: "设计开发",
};

const identityPlaceholders = {
  production_manager: "例如：总经理今天先看哪三件事？或者问：为什么这个订单有交付风险？",
  customer_equipment_engineer: "例如：SM8 机器错花，序列号 9009452，布面问题固定在同一路。",
  designer: "例如：我要开发一款无缝运动上衣，需要透气、快干，请先帮我澄清设计需求。",
};

const labels = {
  product_category: "产品类型",
  target_user: "目标用户",
  use_case: "使用场景",
  style_keywords: "风格方向",
  functional_requirements: "功能需求",
  material_preferences: "材料偏好",
  constraints: "限制条件",
  machine_model: "机型",
  serial_number: "序列号",
  symptoms: "故障现象",
  alarm_info: "报警信息",
  production_status: "生产影响",
  urgency: "紧急程度",
  factory_location: "工厂位置",
  customer_contact: "联系人",
  online_steps_attempted: "已尝试步骤",
  suggested_steps: "建议步骤",
  safety_warnings: "安全提醒",
  dispatch_triggers: "派工触发条件",
  recommended_parts: "建议备件",
  matched_case_title: "匹配案例",
  activation_password: "锁机激活密码",
  executive_answer: "管理层回答",
  template: "回答结构",
  conclusion: "结论",
  reason_evidence: "原因 / 证据",
  risk: "风险",
  recommendation: "建议",
  data_gap: "数据缺口",
  data_gaps: "数据缺口",
  management_summary: "管理摘要",
  metric: "分析指标",
  metric_snapshot: "指标快照",
  reason_and_evidence: "原因 / 证据",
  recommended_action: "建议动作",
  next_drilldowns: "继续下钻",
  data_boundary: "数据边界",
  evidence_refs: "证据编号",
  verification_process: "Athena 查证过程",
  checked_objects: "Athena 查了什么",
  findings: "发现了什么",
  evidence_level: "证据支持程度",
  cannot_conclude: "还不能判断",
  suggested_confirmation_owner: "建议确认人",
  read_only_boundary: "只读边界",
  confidence: "置信度",
  status: "状态",
};
function createSessionId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return `user-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function selectIdentity(role) {
  const previousRole = currentRole;
  currentRole = role;
  identityButtons.forEach((button) => {
    const active = button.dataset.identityRole === role;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  if (identityHelpEl) {
    identityHelpEl.textContent = `当前身份：${identityLabels[role] || role}。现在可以开始对话。`;
  }
  userStatusEl.textContent = identityLabels[role] || role;
  userInputEl.placeholder = identityPlaceholders[role] || "请输入你的需求。";
  toggleGeneralManagerWorkspace(role === "production_manager");
  if (previousRole !== role) {
    addBubble("agent", `已选择身份：${identityLabels[role] || role}。现在可以开始提问。`);
  }
  if (role === "production_manager") {
    loadGeneralManagerDashboard({ force: false }).catch(() => {
      renderGeneralManagerError("Production 看板暂时无法加载，请确认本地 demo server 正在运行。");
    });
  }
}

function clearIdentity() {
  currentRole = null;
  identityButtons.forEach((button) => {
    button.classList.remove("active");
    button.setAttribute("aria-pressed", "false");
  });
  if (identityHelpEl) {
    identityHelpEl.textContent = "请先选择身份。Athena 会根据身份进入对应工作流，并为未来权限控制保留依据。";
  }
  userStatusEl.textContent = "请选择身份";
  userInputEl.placeholder = "请先选择身份，再输入你的问题。";
  toggleGeneralManagerWorkspace(false);
}

function ensureIdentitySelected() {
  if (currentRole) return true;
  addBubble("agent", "请先选择身份：总经理、服务工程师或设计开发。选择后我才能进入对应工作流。");
  identityButtons[0]?.focus();
  return false;
}
function toggleGeneralManagerWorkspace(visible) {
  if (!gmWorkspaceEl) return;
  gmWorkspaceEl.hidden = !visible;
}

async function loadGeneralManagerDashboard({ force = false } = {}) {
  if (!gmWorkspaceEl || (gmDashboardLoaded && !force)) return;
  gmDashboardLoaded = true;
  gmBriefSummaryEl.innerHTML = "<p>正在读取 Production 数据和风险卡片...</p>";
  gmRiskCardsEl.innerHTML = "";
  const response = await fetch(`/api/production/overview?ts=${Date.now()}`);
  const result = await response.json();
  renderGeneralManagerDashboard(result);
}

function renderGeneralManagerDashboard(result) {
  gmDashboardResult = result;
  gmDecisionLoop = result.decision_loop || null;
  const brief = result.management_priority_brief || {};
  const priorities = brief.top_priorities || [];
  const summaryLines = brief.daily_brief?.summary_zh || brief.daily_brief?.summary || [];
  const kpis = result.actual_data_snapshot?.kpis || {};
  renderGeneralManagerKpiDashboard(result);
  renderGeneralManagerDailyBrief(result.daily_brief_narrative || {});
  gmBriefSummaryEl.innerHTML = `
    <div class="gm-user-summary-lines">
      <strong>${escapeHtml("浠婃棩绠＄悊鎽樿")}</strong>
      ${summaryLines.slice(0, 4).map((line) => `<p>${escapeHtml(localizeProductionPhrase(line))}</p>`).join("")}
    </div>
  `;
  gmRiskCardsEl.innerHTML = priorities.slice(0, 3).map((item) => renderGeneralManagerRiskCard(item)).join("");
  if (gmStoryEntryEl) gmStoryEntryEl.hidden = true;
  if (gmStoryCardsEl) gmStoryCardsEl.innerHTML = "";
  renderGeneralManagerEvidenceReview(result.evidence_review_queue || {});
  renderGeneralManagerServiceRisks(result.first_screen_service_risk || {});
  renderGeneralManagerFollowUps();
}

function renderGeneralManagerKpiDashboard(result) {
  if (!gmKpiDashboardEl) return;
  const kpis = result.actual_data_snapshot?.kpis || {};
  const brief = result.management_priority_brief || {};
  const priorities = brief.top_priorities || [];
  const serviceRisk = result.first_screen_service_risk || {};
  const serviceCount = serviceRisk.service_candidate_count ?? serviceRisk.service_risk_cards?.length ?? 0;
  const material = result.material_risk || {};
  const cards = [
    {
      label: "交付风险",
      value: kpis.near_due_order_count ?? result.production_overview?.delayed_order_count ?? 0,
      unit: "单需关注",
      tone: "high",
      note: "先看临近交付和未完成计划。",
    },
    {
      label: "排单状态",
      value: `${escapeHtml(kpis.scheduled_weaving_part_order_count ?? "-")} / ${escapeHtml(kpis.unscheduled_weaving_part_order_count ?? "-")}`,
      unit: "已排 / 未排",
      tone: (kpis.unscheduled_weaving_part_order_count || 0) > 0 ? "attention" : "ok",
      note: "APS 织造排产覆盖情况。",
    },
    {
      label: "计划完成",
      value: formatPercentLike(kpis.plan_completion_rate),
      unit: "完成率",
      tone: Number(kpis.plan_completion_rate || 0) < 0.85 ? "attention" : "ok",
      note: "基于 APS/ERP 导出快照。",
    },
    {
      label: "设备风险",
      value: kpis.machine_style_spec_mismatch_candidate_count ?? 0,
      unit: "规格候选",
      tone: (kpis.machine_style_spec_mismatch_candidate_count || 0) > 0 ? "attention" : "ok",
      note: "机台/款式筒径针距匹配。",
    },
    {
      label: "Service",
      value: serviceCount,
      unit: "待确认",
      tone: serviceCount > 0 ? "attention" : "ok",
      note: "只生成确认候选，不自动派工。",
    },
    {
      label: "数据可信度",
      value: `${escapeHtml(brief.data_source_policy?.actual_export_priority_count ?? 0)} / ${escapeHtml(priorities.length || 3)}`,
      unit: "真实证据",
      tone: "info",
      note: material.adapter_status === "mock_contract" ? "物料/质量/人工仍有数据缺口。" : "真实导出优先。",
    },
  ];
  gmKpiDashboardEl.innerHTML = `
    <div class="gm-user-dashboard-head">
      <div>
        <span>General Manager Dashboard</span>
        <h3>日常关键指标</h3>
      </div>
      <small>Dashboard 用来监控态势，Athena 下钻用来解释原因和证据。</small>
    </div>
    <div class="gm-user-kpi-grid">
      ${cards.map((card) => `
        <article class="gm-user-kpi-card ${escapeHtml(card.tone)}">
          <span>${escapeHtml(card.label)}</span>
          <strong>${card.value}</strong>
          <small>${escapeHtml(card.unit)}</small>
          <p>${escapeHtml(card.note)}</p>
        </article>
      `).join("")}
    </div>
  `;
}
function renderGeneralManagerDailyBrief(brief) {
  if (!gmDailyBriefPanelEl || !gmDailyBriefContentEl) return;
  const text = brief.narrative_zh || brief.narrative || "";
  if (!text) {
    gmDailyBriefPanelEl.hidden = true;
    gmDailyBriefContentEl.innerHTML = "";
    gmDailyBriefText = "";
    return;
  }
  gmDailyBriefPanelEl.hidden = false;
  gmDailyBriefText = text;
  const topThree = brief.top_three_priorities || [];
  const reviewItems = brief.do_not_conclude_yet || [];
  const owners = brief.confirmation_owners || [];
  gmDailyBriefContentEl.innerHTML = `
    <p class="gm-user-brief-main">${escapeHtml(text.split("\n")[0] || "今日早会摘要已生成。")}</p>
    <div class="gm-user-brief-columns">
      <article>
        <span>今天先盯哪三件事</span>
        <ol>${topThree.slice(0, 3).map((item) => `<li>${escapeHtml(item.title || "-")}<small>${escapeHtml(item.owner || "待指定")}</small></li>`).join("")}</ol>
      </article>
      <article>
        <span>哪些数据先别下结论</span>
        <ul>${reviewItems.slice(0, 3).map((item) => `<li>${escapeHtml(item.object || "-")}<small>${escapeHtml(item.owner || "计划 / APS Owner")}</small></li>`).join("")}</ul>
      </article>
      <article>
        <span>负责人确认点</span>
        <ul>${owners.slice(0, 4).map((item) => `<li>${escapeHtml(item.owner || "-")}<small>${escapeHtml(item.source || "")}</small></li>`).join("")}</ul>
      </article>
    </div>
    <details class="gm-user-analysis-details">
      <summary>查看完整早会摘要和证据边界</summary>
      <pre>${escapeHtml(text)}</pre>
      <ul>${(brief.evidence_boundary || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul>
    </details>
  `;
}
function renderGeneralManagerStoryEntry(pack) {
  if (!gmStoryEntryEl || !gmStoryCardsEl) return;
  const stories = (pack.stories || []).filter(Boolean).slice(0, 3);
  if (!stories.length) {
    gmStoryEntryEl.hidden = true;
    gmStoryCardsEl.innerHTML = "";
    return;
  }
  gmStoryEntryEl.hidden = false;
  gmStoryCardsEl.innerHTML = stories.map((story) => {
    const title = story.title_zh || story.title || "生产风险故事";
    const question = story.chatbi_question || story.manager_question || "";
    const badge = story.demo_badge_zh || story.demo_badge || story.evidence_mode || "";
    const boundary = story.evidence_mode === "actual_export"
      ? "真实 APS/ERP 导出"
      : story.evidence_mode === "hybrid"
        ? "真实订单上下文 + mock 补充"
        : "本地 mock / 待补数据";
    return `
      <article class="gm-user-story-card">
        <span>${escapeHtml(boundary)}</span>
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(badge)}</p>
        <button type="button" data-gm-story-question="${escapeHtml(question)}">让 Athena 下钻</button>
      </article>
    `;
  }).join("");
}
function renderGeneralManagerRiskCard(item) {
  const title = item.title_zh || item.title || item.risk_title || "生产风险";
  const conclusion = item.conclusion_zh || item.conclusion || "";
  const action = item.recommended_action_zh || item.recommended_action || "";
  const objects = summarizeAffectedObjects(item.affected_objects || {});
  const skills = (item.skills_used || []).slice(0, 3).map((skill) => skill.name_zh || skill.skill_id);
  const refs = (item.evidence_refs || []).slice(0, 3);
  const allRefs = item.evidence_refs || [];
  const fieldSources = item.field_sources || [];
  const dataGaps = item.data_gaps || [];
  const evidenceLevel = item.evidence_level || item.current_evidence_level || item.data_source_mode || "";
  const question = item.drilldown_question || `为什么 ${title}？请按证据链下钻。`;
  const actionId = item.action_candidate?.action_id || "";
  const rankText = item.rank ? `今天先盯第 ${item.rank} 件事` : "今天优先关注";
  return `
    <article class="gm-user-risk-card">
      <div class="gm-user-risk-top">
        <span>${escapeHtml(rankText)}</span>
        <strong>${escapeHtml(item.risk_level_label || item.priority || "P1")}</strong>
      </div>
      <p class="gm-user-risk-theme">${escapeHtml(item.risk_theme_label || item.management_theme || "生产风险")}</p>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(localizeProductionPhrase(conclusion))}</p>
      <dl>
        <div><dt>影响对象</dt><dd>${escapeHtml(objects || "-")}</dd></div>
        <div><dt>建议确认人</dt><dd>${escapeHtml(item.owner_role || "-")}</dd></div>
        <div><dt>建议动作</dt><dd>${escapeHtml(localizeProductionPhrase(action || "-"))}</dd></div>
        <div><dt>Athena 已检查</dt><dd>${skills.map((skill) => `<span class="gm-user-chip">${escapeHtml(skill)}</span>`).join("") || "-"}</dd></div>
        <div><dt>证据</dt><dd>${refs.map((ref) => `<span class="gm-user-chip evidence">${escapeHtml(ref)}</span>`).join("") || "-"}</dd></div>
      </dl>
      <details class="gm-user-evidence-details">
        <summary>证据详情 / 数据缺口</summary>
        <dl>
          <div><dt>证据等级</dt><dd>${escapeHtml(evidenceLevel || "待确认")}</dd></div>
          <div><dt>字段来源</dt><dd>${renderInlineChips(fieldSources)}</dd></div>
          <div><dt>完整证据链</dt><dd>${renderInlineChips(allRefs)}</dd></div>
          <div><dt>数据缺口</dt><dd>${renderInlineList(dataGaps.map(humanizeDataGap))}</dd></div>
        </dl>
      </details>
      <div class="gm-user-card-actions">
        <button type="button" data-gm-drilldown="${escapeHtml(question)}">让 Athena 下钻</button>
        <button type="button" data-gm-follow-up="${escapeHtml(actionId)}">生成跟进项</button>
      </div>
    </article>
  `;
}
function renderGeneralManagerServiceRisks(serviceRisk) {
  if (!gmServiceRiskPanelEl || !gmServiceRiskCardsEl) return;
  const cards = serviceRisk.service_risk_cards || [];
  if (!cards.length) {
    gmServiceRiskPanelEl.hidden = true;
    gmServiceRiskCardsEl.innerHTML = "";
    return;
  }
  gmServiceRiskPanelEl.hidden = false;
  gmServiceRiskCardsEl.innerHTML = cards.map((card) => renderGeneralManagerServiceRiskCard(card)).join("");
}

function renderGeneralManagerEvidenceReview(queue) {
  if (!gmEvidenceReviewPanelEl || !gmEvidenceReviewCardsEl) return;
  const cards = (queue.review_queue || []).slice(0, 4);
  if (!cards.length) {
    gmEvidenceReviewPanelEl.hidden = true;
    gmEvidenceReviewCardsEl.innerHTML = "";
    return;
  }
  gmEvidenceReviewPanelEl.hidden = false;
  gmEvidenceReviewCardsEl.innerHTML = cards.map((card) => renderGeneralManagerEvidenceReviewCard(card)).join("");
}

function renderGeneralManagerEvidenceReviewCard(card) {
  const drivers = (card.reconciliation_drivers || []).slice(0, 2);
  const driverText = drivers.map((driver) => driver.explanation_zh || driver.explanation_en || driver.driver).join("; ");
  const objectId = card.object_id || card.produce_order_code || "ORDER";
  const question = card.drilldown_question || `为什么订单 ${objectId} 是数据复核候选，而不是 hard delivery risk？`;
  const flags = card.sanity_flags || [];
  const actionId = `ACT-EVID-REVIEW-${safeActionSuffix(objectId)}`;
  const confirmationTask = card.suggested_confirmation_action || "请计划负责人确认订单状态、未排量和报工口径，再判断是否属于交付风险。";
  return `
    <article class="gm-user-evidence-review-card">
      <div class="gm-user-risk-top">
        <span>确认任务</span>
        <strong>数据需复核</strong>
      </div>
      <h3>请确认订单 ${escapeHtml(objectId)} 的数据口径</h3>
      <p>${escapeHtml(confirmationTask)}</p>
      <dl>
        <div><dt>建议确认人</dt><dd>${escapeHtml(card.suggested_confirmation_owner || "Planning Manager / APS Owner")}</dd></div>
        <div><dt>不能下结论</dt><dd>${escapeHtml(card.cannot_conclude_reason || "当前证据有矛盾，不能直接定义为 hard delivery risk。")}</dd></div>
      </dl>
      <details class="gm-user-evidence-details">
        <summary>字段来源 / sanity flag / 指标详情</summary>
        <dl>
          <div><dt>计划完成率</dt><dd>${escapeHtml(formatPercentLike(card.plan_completion_rate))}</dd></div>
          <div><dt>交期差</dt><dd>${escapeHtml(card.days_to_due ?? "-")} 天</dd></div>
          <div><dt>未排量</dt><dd>${escapeHtml(card.unscheduled_quantity ?? 0)}</dd></div>
          <div><dt>报工差异</dt><dd>${escapeHtml(card.quantity_report_gap ?? 0)}</dd></div>
          <div><dt>复核触发项</dt><dd>${escapeHtml(driverText || "-")}</dd></div>
          <div><dt>sanity flag</dt><dd>${renderInlineChips(flags)}</dd></div>
          <div><dt>字段来源</dt><dd>${renderInlineChips(card.field_sources || [card.field_source])}</dd></div>
          <div><dt>建议动作</dt><dd>${escapeHtml(card.suggested_confirmation_action || "-")}</dd></div>
        </dl>
      </details>
      <div class="gm-user-card-actions">
        <button type="button" data-gm-evidence-review-drilldown="${escapeHtml(question)}">让 Athena 下钻</button>
        <button type="button" data-gm-evidence-review-follow-up="${escapeHtml(actionId)}">生成复核待办</button>
      </div>
    </article>
  `;
}

function safeActionSuffix(value) {
  return String(value || "UNKNOWN").replace(/[^a-zA-Z0-9]+/g, "-").replace(/^-+|-+$/g, "").toUpperCase() || "UNKNOWN";
}
function renderGeneralManagerServiceRiskCard(card) {
  const question = card.drilldown_question || `请下钻 ${card.machine_id || "机台"} 的 Service 风险。`;
  const actionId = card.linked_action_id || "";
  return `
    <article class="gm-user-service-card">
      <div class="gm-user-risk-top">
        <span>${escapeHtml(card.risk_theme_label || "Service")}</span>
        <strong>${escapeHtml(card.risk_level_label || card.priority || "关注")}</strong>
      </div>
      <h3>${escapeHtml(card.title_zh || card.title || "Service 风险候选")}</h3>
      <p>${escapeHtml(card.why_it_matters_zh || card.why_it_matters || "")}</p>
      <dl>
        <div><dt>影响对象</dt><dd>${escapeHtml(summarizeAffectedObjects(card.affected_objects || {}) || "-")}</dd></div>
        <div><dt>建议确认人</dt><dd>${escapeHtml(card.suggested_owner || "-")}</dd></div>
        <div><dt>建议动作</dt><dd>${escapeHtml(card.recommended_action_zh || card.recommended_action || "-")}</dd></div>
        <div><dt>证据</dt><dd>${renderInlineChips(card.evidence_refs || [])}</dd></div>
      </dl>
      <details class="gm-user-evidence-details">
        <summary>Service 边界 / 数据缺口</summary>
        <dl>
          <div><dt>字段来源</dt><dd>${renderInlineChips(card.field_sources || [])}</dd></div>
          <div><dt>数据缺口</dt><dd>${renderInlineList((card.data_gaps || []).map(humanizeDataGap))}</dd></div>
          <div><dt>禁止动作</dt><dd>${renderInlineChips(card.blocked_actions || [])}</dd></div>
        </dl>
      </details>
      <div class="gm-user-card-actions">
        <button type="button" data-gm-service-drilldown="${escapeHtml(question)}">让 Athena 下钻</button>
        <button type="button" data-gm-service-follow-up="${escapeHtml(actionId)}">生成 Service 跟进项</button>
      </div>
    </article>
  `;
}
function renderInlineChips(values) {
  const clean = (values || []).filter(Boolean).slice(0, 8);
  if (!clean.length) return "-";
  return clean.map((value) => `<span class="gm-user-chip evidence">${escapeHtml(value)}</span>`).join("");
}

function renderInlineList(values) {
  const clean = (values || []).filter(Boolean).slice(0, 6);
  if (!clean.length) return "-";
  return `<ul>${clean.map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul>`;
}

function humanizeDataGap(value) {
  const text = String(value || "");
  const replacements = {
    "Need real IOT alarm duration and recovery timestamp before confirming service root cause.": "需要真实 IOT 报警持续时间和恢复时间，才能确认 Service 根因。",
    "Need maintenance owner confirmation before creating a real service ticket.": "需要机修 / Service 负责人确认后，才能创建真实工单。",
    "Need ERP/APS order impact confirmation before changing production priority.": "需要 ERP / APS 订单影响确认后，才能调整生产优先级。",
    "Live ERP/APS/IOT database integration.": "尚未接入实时 ERP / APS / IOT 数据库。",
    "Automatic schedule change, machine control, .co/.cx upload, or service dispatch.": "不支持自动改排程、控制机台、上传 .co/.cx 或自动派工。",
    "Customer-verified general-manager VOC coverage.": "总经理 VOC 仍需客户验证。",
    "Full downstream garment quality and warehouse flow based on real records.": "后道质量、仓储和出货流程还没有完整真实数据。",
  };
  return replacements[text] || text;
}

function summarizeAffectedObjects(affected) {
  const objectLabels = {
    orders: "订单",
    machines: "机台",
    materials: "物料",
    styles: "款式",
    teams: "班组",
    weaving_part_order_ids: "织造部件单",
    planned_task_ids: "计划任务",
  };
  return Object.entries(objectLabels)
    .map(([key, label]) => {
      const values = Array.isArray(affected[key]) ? affected[key].filter(Boolean).slice(0, 3) : [];
      return values.length ? `${label}: ${values.join(", ")}` : "";
    })
    .filter(Boolean)
    .join(" / ");
}
function renderGeneralManagerFollowUps() {
  if (!gmFollowUpPanelEl || !gmFollowUpListEl || !gmFollowUpSummaryEl) return;
  const loop = gmDecisionLoop || {};
  const followUps = (loop.follow_up_items || []).filter((item) => gmActiveFollowUpActionIds.has(item.action_id));
  const actions = new Map((loop.action_items || []).map((item) => [item.action_id, item]));
  if (!followUps.length) {
    gmFollowUpPanelEl.hidden = true;
    gmFollowUpSummaryEl.innerHTML = "";
    gmFollowUpListEl.innerHTML = "";
    return;
  }

  const counts = followUps.reduce((acc, item) => {
    const key = item.status || "pending_confirmation";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  gmFollowUpPanelEl.hidden = false;
  gmFollowUpSummaryEl.innerHTML = [
    ["待确认", counts.pending_confirmation || 0],
    ["需要数据", counts.needs_more_data || counts.waiting_evidence || 0],
    ["已确认", counts.confirmed || 0],
    ["已解决", counts.resolved || counts.closed || 0],
  ]
    .map(([label, value]) => `<article><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></article>`)
    .join("");
  gmFollowUpListEl.innerHTML = followUps.map((item) => renderGeneralManagerFollowUpItem(item, actions.get(item.action_id) || {})).join("");
}

function renderGeneralManagerFollowUpItem(item, action) {
  const status = item.status || "pending_confirmation";
  const question = item.drilldown_question || action.drilldown_question || `请继续下钻 ${item.linked_risk_card_id || item.action_id}`;
  const evidence = (item.evidence_refs || []).slice(0, 4);
  const expectedEvidence = (item.expected_evidence || []).slice(0, 3);
  const sourceLabel = followUpSourceLabel(item.source_card_type || action.source_card_type || "hard_risk");
  return `
    <article class="gm-user-followup-card ${escapeHtml(status.replaceAll("_", "-"))}">
      <div class="gm-user-followup-card-head">
        <span>${escapeHtml(sourceLabel)} / ${escapeHtml(statusLabel(status))} / ${escapeHtml(item.follow_up_id || item.action_id)}</span>
        <strong>${escapeHtml(action.recommended_action_zh || action.recommended_action || item.action_id)}</strong>
      </div>
      <dl>
        <div><dt>关联对象</dt><dd>${escapeHtml(item.related_object || action.related_object || item.linked_risk_card_id || "-")}</dd></div>
        <div><dt>负责人</dt><dd>${escapeHtml(item.owner_role || "-")}</dd></div>
        <div><dt>需要确认</dt><dd>${escapeHtml(item.confirmation_need || action.confirmation_need || "-")}</dd></div>
        <div><dt>Athena 建议原因</dt><dd>${escapeHtml(item.athena_recommendation_reason || action.athena_recommendation_reason || "-")}</dd></div>
        <div><dt>关联风险</dt><dd>${escapeHtml(item.linked_risk_card_id || item.source_priority_id || "-")}</dd></div>
        <div><dt>复查时间</dt><dd>${escapeHtml(item.review_time || "-")}</dd></div>
        <div><dt>证据状态</dt><dd>${escapeHtml(item.evidence_status || "-")}</dd></div>
        <div><dt>证据</dt><dd>${evidence.map((ref) => `<span class="gm-user-chip evidence">${escapeHtml(ref)}</span>`).join("") || "-"}</dd></div>
        <div><dt>还需要</dt><dd>${expectedEvidence.map((ref) => `<span class="gm-user-chip">${escapeHtml(ref)}</span>`).join("") || "-"}</dd></div>
      </dl>
      <div class="gm-user-followup-actions">
        <button type="button" data-gm-follow-up-status="needs_more_data" data-action-id="${escapeHtml(item.action_id)}">需要数据</button>
        <button type="button" data-gm-follow-up-status="confirmed" data-action-id="${escapeHtml(item.action_id)}">确认</button>
        <button type="button" data-gm-follow-up-status="resolved" data-action-id="${escapeHtml(item.action_id)}">已解决</button>
        <button type="button" data-gm-follow-up-status="dismissed" data-action-id="${escapeHtml(item.action_id)}">跳过</button>
        <button type="button" data-gm-follow-up-ask="${escapeHtml(question)}">继续追问</button>
      </div>
    </article>
  `;
}

function followUpSourceLabel(source) {
  const sourceLabels = {
    hard_risk: "风险待办",
    evidence_review: "复核待办",
    service_risk: "Service 待办",
  };
  return sourceLabels[source] || source || "本地待办";
}

function statusLabel(status) {
  const statusLabels = {
    pending_confirmation: "待确认",
    needs_more_data: "需要数据",
    resolved: "已解决",
    dismissed: "已跳过",
    assigned: "已分配",
    waiting_evidence: "等待证据",
    confirmed: "已确认",
    closed: "已关闭",
    unable_to_process: "无法处理",
  };
  return statusLabels[status] || status;
}
async function createGeneralManagerFollowUp(actionId) {
  const cleanActionId = String(actionId || "").trim();
  if (!cleanActionId) {
    addBubble("agent", "这张风险卡还没有可生成的本地跟进项。");
    return;
  }
  const updatedLoop = await saveGeneralManagerFollowUpStatus(cleanActionId, "pending_confirmation", "User page generated local follow-up candidate.");
  gmDecisionLoop = updatedLoop;
  gmActiveFollowUpActionIds.add(cleanActionId);
  renderGeneralManagerFollowUps();
  addBubble("agent", "已生成本地跟进项。Athena 只记录本地 metadata，不写 APS / ERP / IOT。");
}

async function updateGeneralManagerFollowUpStatus(actionId, status) {
  const updatedLoop = await saveGeneralManagerFollowUpStatus(actionId, status, `User page changed local follow-up status to ${status}.`);
  gmDecisionLoop = updatedLoop;
  gmActiveFollowUpActionIds.add(actionId);
  renderGeneralManagerFollowUps();
  addBubble("agent", `已更新本地待办状态：${statusLabel(status)}。`);
}

async function saveGeneralManagerFollowUpStatus(actionId, status, note) {
  const response = await fetch("/api/production/follow-up/review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action_id: actionId,
      review_status: status,
      review_note: note,
      reviewed_by: "user_page_general_manager",
    }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Failed to save follow-up");
  return result.decision_loop || {};
}

async function askGeneralManagerWorkspace(question, { echoUser = true } = {}) {
  const cleanQuestion = String(question || "").trim();
  if (!cleanQuestion) return;
  if (echoUser) addBubble("user", cleanQuestion);
  const loading = document.createElement("article");
  loading.className = "user-bubble agent loading";
  loading.innerHTML = "<p>正在让 Athena 按生产证据链下钻...</p>";
  userMessagesEl.append(loading);
  userMessagesEl.scrollTop = userMessagesEl.scrollHeight;
  const response = await fetch("/api/production/chatbi", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: cleanQuestion }),
  });
  const result = await response.json();
  loading.remove();
  addBubble("agent", result.answer_summary || result.executive_answer?.conclusion || "分析完成", normalizeProductionChatbiResponse(result));
}

function renderGeneralManagerError(message) {
  if (!gmBriefSummaryEl || !gmRiskCardsEl) return;
  if (gmKpiDashboardEl) gmKpiDashboardEl.innerHTML = "";
  gmBriefSummaryEl.innerHTML = `<p>${escapeHtml(message)}</p>`;
  gmRiskCardsEl.innerHTML = "";
  if (gmEvidenceReviewPanelEl) gmEvidenceReviewPanelEl.hidden = true;
  if (gmEvidenceReviewCardsEl) gmEvidenceReviewCardsEl.innerHTML = "";
  if (gmServiceRiskPanelEl) gmServiceRiskPanelEl.hidden = true;
  if (gmServiceRiskCardsEl) gmServiceRiskCardsEl.innerHTML = "";
}

function localizeProductionPhrase(value) {
  return String(value || "")
    .replace("Actual APS/ERP export:", "真实 APS/ERP 导出：")
    .replace("Delivery:", "交付：")
    .replace("Data boundary:", "数据边界：");
}
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function addBubble(type, text, response) {
  const bubble = document.createElement("article");
  bubble.className = `user-bubble ${type}`;
  const body = document.createElement("p");
  body.textContent = text;
  bubble.append(body);
  if (response) bubble.append(renderUserResponse(response));
  userMessagesEl.append(bubble);
  userMessagesEl.scrollTop = userMessagesEl.scrollHeight;
}

function renderUserResponse(response) {
  const fragment = document.createDocumentFragment();
  const cards = document.createElement("div");
  cards.className = "user-result-list";

  if (response.workflow?.startsWith("designer")) {
    appendCard(cards, "我已理解的信息", response.payload?.known_info || response.payload?.understanding || {});
    appendCard(cards, "还需要确认", { missing_info: response.payload?.missing_info || [] });
    appendCard(cards, "下一步", { follow_up_questions: response.follow_up_questions || [] });
  } else if (response.workflow?.startsWith("service")) {
    const assist = response.payload?.online_assist || {};
    appendCard(cards, "在线协助", {
      matched_case_title: assist.matched_case_title,
      suggested_steps: assist.suggested_steps,
      safety_warnings: assist.safety_warnings,
    });
    appendCard(cards, "服务信息", response.payload?.known_info || response.payload?.understanding || {});
    appendCard(cards, "还需要补充", {
      missing_info: response.payload?.missing_info || [],
      dispatch_triggers: assist.dispatch_triggers,
      recommended_parts: assist.recommended_parts,
    });
  } else if (response.workflow?.startsWith("production_athena")) {
    appendProductionAthenaAnswer(cards, response.payload || {});
  } else if (response.follow_up_questions?.length) {
    appendCard(cards, "需要确认", { follow_up_questions: response.follow_up_questions });
  }

  if (cards.childElementCount) fragment.append(cards);
  return fragment;
}
function normalizeProductionChatbiResponse(result) {
  const executive = result.executive_answer || {};
  const rootCauses = result.root_causes || [];
  const evidenceRefs = [
    ...(result.evidence_refs || []),
    ...rootCauses.flatMap((cause) => cause.evidence_refs || []),
  ];
  return {
    workflow: "production_athena",
    summary: result.answer_summary || executive.conclusion,
    payload: {
      executive_answer: executive,
      management_summary: result.answer_summary || executive.conclusion,
      metric: result.analysis?.metric || result.metric || "production_root_cause",
      confidence: result.confidence || result.analysis?.confidence || "",
      reason_and_evidence: rootCauses.map((cause) => ({
        category: cause.category_label || cause.category,
        cause: cause.cause,
        evidence_refs: cause.evidence_refs || [],
      })),
      evidence_refs: [...new Set(evidenceRefs)].slice(0, 12),
      verification_process: normalizeManagerVerificationProcess(result.verification_process || {}),
      recommended_action: executive.recommendation ? [executive.recommendation] : [],
      next_drilldowns: result.next_drilldowns || [],
      data_gaps: result.data_gaps || (executive.data_gap ? [executive.data_gap] : []),
      data_boundary: result.data_boundary || result.permission_boundary || "Read-only Production evidence analysis; no APS/ERP/IOT write-back.",
      skill_execution_trace: (result.skill_execution_trace || []).slice(0, 5).map((step) => ({
        skill: step.skill_name_zh || step.skill_id,
        checked: step.what_athena_checked_zh || step.what_athena_checked,
        evidence_refs: step.evidence_refs || [],
        data_gap: step.limitation_or_data_gap,
      })),
    },
  };
}

function normalizeManagerVerificationProcess(process) {
  const checkedObjects = (process.checked_objects || []).slice(0, 6).map((item) => {
    const label = item.manager_label_zh || item.manager_label || item.object || "生产对象";
    const reason = item.why_checked || "用于确认当前风险判断。";
    return `${label}：${reason}`;
  });
  const findings = (process.findings || []).slice(0, 4).map((item) => {
    const refs = (item.evidence_refs || []).filter(Boolean).slice(0, 4).join(", ");
    return refs ? `${item.finding}（证据：${refs}）` : item.finding;
  }).filter(Boolean);
  return {
    checked_objects: checkedObjects,
    findings,
    evidence_level: process.evidence_level_label_zh || process.evidence_level || "待确认",
    cannot_conclude: (process.cannot_conclude || []).slice(0, 4),
    suggested_confirmation_owner: process.suggested_confirmation_owner || "生产主管 / 机修负责人",
    read_only_boundary: "Athena 只做查证和建议，不写 APS / ERP / IOT，不自动派工，不控制机台。",
  };
}

function appendProductionAthenaAnswer(parent, payload) {
  const executive = payload.executive_answer || {};
  const verification = payload.verification_process || {};
  const evidence = (payload.reason_and_evidence || []).slice(0, 3);
  const evidenceRefs = (payload.evidence_refs || []).slice(0, 6);
  const actions = (payload.recommended_action || []).slice(0, 2);
  const dataGaps = (payload.data_gaps || []).slice(0, 5);
  const checkedObjects = (verification.checked_objects || []).slice(0, 4);
  const findings = (verification.findings || []).slice(0, 3);
  const conclusionText = executive.conclusion || payload.management_summary || "Athena 已完成查证";
  const evidenceText = verification.evidence_level || payload.confidence || evidenceRefs.slice(0, 3).join(" / ") || "当前证据不足，需要继续确认";
  const ownerText = verification.suggested_confirmation_owner || "生产主管 / 机修负责人";
  const nextActionText = executive.recommendation || actions[0] || "建议负责人基于证据做下一步确认。";
  const card = document.createElement("section");
  card.className = "user-result-card gm-user-analysis gm-user-analysis-compact";
  card.innerHTML = `
    <div class="gm-user-analysis-hero">
      <span>${escapeHtml("Santoni Athena")}</span>
      <h3>${escapeHtml(conclusionText)}</h3>
      <p>${escapeHtml(nextActionText)}</p>
    </div>
    <div class="gm-user-analysis-grid compact">
      <article>
        <span>${escapeHtml("结论")}</span>
        <p>${escapeHtml(conclusionText)}</p>
      </article>
      <article>
        <span>${escapeHtml("证据支持到什么程度")}</span>
        <p>${escapeHtml(evidenceText)}</p>
      </article>
      <article>
        <span>${escapeHtml("建议确认人")}</span>
        <p>${escapeHtml(ownerText)}</p>
      </article>
      <article>
        <span>${escapeHtml("下一步动作")}</span>
        <p>${escapeHtml(nextActionText)}</p>
      </article>
    </div>
    <details class="gm-user-analysis-details">
      <summary>${escapeHtml("查看完整证据与边界")}</summary>
      <dl>
        <div><dt>${escapeHtml("Athena 查了什么")}</dt><dd>${escapeHtml(checkedObjects.join("；") || "-")}</dd></div>
        <div><dt>${escapeHtml("发现什么")}</dt><dd>${escapeHtml(findings.join("；") || evidence[0]?.cause || "-")}</dd></div>
        <div><dt>${escapeHtml("证据等级")}</dt><dd>${escapeHtml(verification.evidence_level || payload.confidence || "-")}</dd></div>
        <div><dt>${escapeHtml("完整查证对象")}</dt><dd>${escapeHtml(checkedObjects.join("；") || "-")}</dd></div>
        <div><dt>${escapeHtml("原因与证据")}</dt><dd>${escapeHtml(evidence.map((item) => `${item.category || ""}: ${item.cause || ""}`).filter(Boolean).join("；") || evidenceRefs.join(" / ") || "-")}</dd></div>
        <div><dt>${escapeHtml("不能判断")}</dt><dd>${escapeHtml((verification.cannot_conclude || []).slice(0, 4).join("；") || dataGaps.join("；") || "-")}</dd></div>
        <div><dt>${escapeHtml("只读边界")}</dt><dd>${escapeHtml(verification.read_only_boundary || payload.data_boundary || "-")}</dd></div>
      </dl>
    </details>
  `;
  parent.append(card);
}
function appendCard(parent, title, data) {
  const rows = compactRows(data);
  if (!rows.length) return;
  const card = document.createElement("section");
  card.className = "user-result-card";
  const heading = document.createElement("h3");
  heading.textContent = title;
  card.append(heading);
  const list = document.createElement("dl");
  rows.forEach(([key, value]) => {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    const detail = document.createElement("dd");
    term.textContent = labels[key] || key.replaceAll("_", " ");
    detail.textContent = formatValue(value);
    item.append(term, detail);
    list.append(item);
  });
  card.append(list);
  parent.append(card);
}

function compactRows(data) {
  return Object.entries(data || {}).filter(([key, value]) => {
    if (["parser_status", "reasoning_status", "language", "case_database_status", "skill"].includes(key)) return false;
    if (value === null || value === undefined || value === "") return false;
    if (Array.isArray(value) && !value.length) return false;
    if (typeof value === "object" && !Array.isArray(value) && !Object.keys(value).length) return false;
    return true;
  }).slice(0, 6);
}

function formatValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (item && typeof item === "object") return formatObjectValue(item);
      return String(item);
    }).join("；");
  }
  if (value && typeof value === "object") {
    return formatObjectValue(value);
  }
  return String(value);
}

function formatObjectValue(value) {
  return Object.entries(value)
    .filter(([, item]) => item !== null && item !== undefined && item !== "")
    .map(([key, item]) => {
      const formatted = Array.isArray(item)
        ? item.map((entry) => (entry && typeof entry === "object" ? formatObjectValue(entry) : String(entry))).join("、")
        : item && typeof item === "object"
          ? formatObjectValue(item)
          : item;
      return `${labels[key] || key}: ${formatted}`;
    })
    .join("；");
}
async function submitMessage(message) {
  if (currentRole === "production_manager" && !pendingAttachment) {
    await askGeneralManagerWorkspace(message, { echoUser: true });
    return;
  }
  const attachments = pendingAttachment ? [pendingAttachment] : [];
  const attachmentLabel = pendingAttachment ? `\n[图片：${pendingAttachment.name}]` : "";
  const platformTool = await platformToolForMessage(message);
  addBubble("user", `${message || "请看我上传的图片"}${attachmentLabel}`);

  const loading = document.createElement("article");
  loading.className = "user-bubble agent loading";
  loading.innerHTML = "<p>正在分析，请稍等...</p>";
  userMessagesEl.append(loading);
  userMessagesEl.scrollTop = userMessagesEl.scrollHeight;

  const result = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      role: currentRole,
      message,
      attachments,
      session_id: userSessionId,
      platform_tool: platformTool,
    }),
  });
  const response = await result.json();
  loading.remove();
  if (response.workflow?.startsWith("designer")) currentRole = "designer";
  if (response.workflow?.startsWith("service")) currentRole = "customer_equipment_engineer";
  if (response.workflow?.startsWith("production_athena")) currentRole = "production_manager";
  userConversationLanguage = response.language || userConversationLanguage;
  addBubble("agent", response.summary || "已完成。", response);
  clearAttachment();
}
async function platformToolForMessage(message) {
  if (!shouldUseActivationTool(message)) {
    return { mode: "mock" };
  }
  activationToolContext = true;
  if (!platformCredentials) {
    platformCredentials = await requestPlatformCredentials();
  }
  if (!platformCredentials) {
    return { mode: "mock" };
  }
  return {
    mode: "real_attempt",
    credentials: platformCredentials,
  };
}

function shouldUseActivationTool(message) {
  if (isActivationCredentialIntent(message)) return true;
  const text = String(message || "").toLowerCase();
  return activationToolContext && /top2|serial|搴忓垪鍙穦鏈哄瀷|鍨嬪彿|machine\s*code|鏈哄櫒鐮亅activation|婵€娲粅password|瀵嗙爜|unlock|瑙ｉ攣|lock|閿亅\d{6,}/i.test(text);
}

function isActivationCredentialIntent(message) {
  const text = String(message || "").toLowerCase();
  const hasTop2Activation = /top2/i.test(text) && /activation|password|code|machine\s*code|lock|locked|unlock|婵€娲粅瀵嗙爜|鏈哄櫒鐮亅閿佸畾|瑙ｉ攣|閿佹満/.test(text);
  const hasDirectActivationTask = /activation\s*(password|code)|machine\s*code|unlock\s*(the\s*)?machine|machine\s*(is\s*)?locked|locked\s*machine|generate\s*(an?\s*)?(activation\s*)?password|婵€娲诲瘑鐮亅婵€娲荤爜|鏈哄櫒鐮亅瑙ｉ攣鏈哄櫒|鏈哄櫒.*閿亅閿佹満|鐢熸垚瀵嗙爜|鑾峰彇瀵嗙爜/.test(text);
  return hasTop2Activation || hasDirectActivationTask;
}

function requestPlatformCredentials() {
  return new Promise((resolve) => {
    credentialResolver = resolve;
    credentialUsernameEl.value = "";
    credentialPasswordEl.value = "";
    credentialDialogEl.showModal();
    credentialUsernameEl.focus();
  });
}

credentialFormEl.addEventListener("submit", (event) => {
  event.preventDefault();
  const username = credentialUsernameEl.value.trim();
  const password = credentialPasswordEl.value;
  if (!username || !password) return;
  credentialDialogEl.close();
  credentialResolver?.({ username, password });
  credentialResolver = null;
});

credentialMockButton.addEventListener("click", () => {
  credentialDialogEl.close();
  credentialResolver?.(null);
  credentialResolver = null;
});

credentialDialogEl.addEventListener("cancel", (event) => {
  event.preventDefault();
  credentialDialogEl.close();
  credentialResolver?.(null);
  credentialResolver = null;
});

userFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = userInputEl.value.trim();
  if (!message && !pendingAttachment) return;
  if (!ensureIdentitySelected()) return;
  userInputEl.value = "";
  try {
    await submitMessage(message);
  } catch {
    addBubble("agent", "服务暂时没有连接，请确认本地 demo server 正在运行。");
  }
});

document.querySelectorAll(".quick-actions button").forEach((button) => {
  button.addEventListener("click", () => {
    if (!ensureIdentitySelected()) return;
    const promptRole = button.dataset.promptRole || "";
    if (promptRole && promptRole !== currentRole) {
      addBubble("agent", `这个快捷问题属于${identityLabels[promptRole] || promptRole}身份。请先切换身份，或直接输入当前身份的问题。`);
      return;
    }
    userInputEl.value = button.dataset.prompt || "";
    userInputEl.focus();
  });
});

identityButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectIdentity(button.dataset.identityRole || "");
    userInputEl.focus();
  });
});

gmRefreshButton?.addEventListener("click", () => {
  loadGeneralManagerDashboard({ force: true }).catch(() => {
    renderGeneralManagerError("Production 看板暂时无法刷新，请确认本地 demo server 正在运行。");
  });
});

gmDailyBriefGenerateButton?.addEventListener("click", async () => {
  try {
    const response = await fetch(`/api/production/daily-brief?ts=${Date.now()}`);
    const result = await response.json();
    renderGeneralManagerDailyBrief(result.daily_brief_narrative || {});
    addBubble("agent", "今日早会摘要已重新生成。");
  } catch (error) {
    addBubble("agent", `早会摘要生成失败：${error.message}`);
  }
});

gmDailyBriefCopyButton?.addEventListener("click", async () => {
  if (!gmDailyBriefText) return;
  try {
    await navigator.clipboard.writeText(gmDailyBriefText);
    addBubble("agent", "今日早会摘要已复制。");
  } catch {
    addBubble("agent", gmDailyBriefText);
  }
});

gmStoryCardsEl?.addEventListener("click", (event) => {
  const storyButton = event.target.closest("button[data-gm-story-question]");
  if (!storyButton) return;
  askGeneralManagerWorkspace(storyButton.dataset.gmStoryQuestion || "").catch(() => {
    addBubble("agent", "Athena 暂时无法下钻演示故事，请确认本地 demo server 正在运行。");
  });
});

gmRiskCardsEl?.addEventListener("click", (event) => {
  const drilldownButton = event.target.closest("button[data-gm-drilldown]");
  if (drilldownButton) {
    askGeneralManagerWorkspace(drilldownButton.dataset.gmDrilldown || "").catch(() => {
      addBubble("agent", "Athena 暂时无法下钻，请确认本地 demo server 正在运行。");
    });
    return;
  }
  const followUpButton = event.target.closest("button[data-gm-follow-up]");
  if (!followUpButton) return;
  followUpButton.disabled = true;
  createGeneralManagerFollowUp(followUpButton.dataset.gmFollowUp || "")
    .catch((error) => {
      addBubble("agent", `本地跟进项生成失败：${error.message}`);
    })
    .finally(() => {
      followUpButton.disabled = false;
    });
});

gmEvidenceReviewPanelEl?.addEventListener("click", (event) => {
  const drilldownButton = event.target.closest("button[data-gm-evidence-review-drilldown]");
  if (drilldownButton) {
    askGeneralManagerWorkspace(drilldownButton.dataset.gmEvidenceReviewDrilldown || "").catch(() => {
      addBubble("agent", "Athena 暂时无法下钻数据复核候选，请确认本地 demo server 正在运行。");
    });
    return;
  }
  const followUpButton = event.target.closest("button[data-gm-evidence-review-follow-up]");
  if (!followUpButton) return;
  followUpButton.disabled = true;
  createGeneralManagerFollowUp(followUpButton.dataset.gmEvidenceReviewFollowUp || "")
    .catch((error) => {
      addBubble("agent", `复核待办生成失败：${error.message}`);
    })
    .finally(() => {
      followUpButton.disabled = false;
    });
});

gmServiceRiskPanelEl?.addEventListener("click", (event) => {
  const drilldownButton = event.target.closest("button[data-gm-service-drilldown]");
  if (drilldownButton) {
    askGeneralManagerWorkspace(drilldownButton.dataset.gmServiceDrilldown || "").catch(() => {
      addBubble("agent", "Athena 暂时无法下钻 Service 风险，请确认本地 demo server 正在运行。");
    });
    return;
  }
  const followUpButton = event.target.closest("button[data-gm-service-follow-up]");
  if (!followUpButton) return;
  followUpButton.disabled = true;
  createGeneralManagerFollowUp(followUpButton.dataset.gmServiceFollowUp || "")
    .catch((error) => {
      addBubble("agent", `Service 本地跟进项生成失败：${error.message}`);
    })
    .finally(() => {
      followUpButton.disabled = false;
    });
});

gmFollowUpPanelEl?.addEventListener("click", (event) => {
  const askButton = event.target.closest("button[data-gm-follow-up-ask]");
  if (askButton) {
    askGeneralManagerWorkspace(askButton.dataset.gmFollowUpAsk || "").catch(() => {
      addBubble("agent", "Athena 暂时无法继续追问，请确认本地 demo server 正在运行。");
    });
    return;
  }
  const statusButton = event.target.closest("button[data-gm-follow-up-status]");
  if (!statusButton) return;
  statusButton.disabled = true;
  updateGeneralManagerFollowUpStatus(statusButton.dataset.actionId || "", statusButton.dataset.gmFollowUpStatus || "")
    .catch((error) => {
      addBubble("agent", `本地待办状态更新失败：${error.message}`);
    })
    .finally(() => {
      statusButton.disabled = false;
    });
});

userResetButton.addEventListener("click", async () => {
  try {
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: userSessionId }),
    });
  } catch {
    // Local reset still works if the backend call fails.
  }
  userSessionId = createSessionId();
  clearIdentity();
  platformCredentials = null;
  activationToolContext = false;
  gmDashboardLoaded = false;
  gmDashboardResult = null;
  gmDecisionLoop = null;
  gmActiveFollowUpActionIds.clear();
  renderGeneralManagerFollowUps();
  renderGeneralManagerServiceRisks({});
  userMessagesEl.innerHTML = "";
  clearAttachment();
  addBubble("agent", "已开始新的对话。请先选择身份：总经理、服务工程师或设计开发。");
});
userImageInputEl.addEventListener("change", async () => {
  const file = userImageInputEl.files?.[0];
  if (!file) {
    clearAttachment();
    return;
  }
  pendingAttachment = {
    name: file.name,
    type: file.type,
    size: file.size,
    data_url: await readFileAsDataURL(file),
  };
  userAttachmentPreviewEl.hidden = false;
  userAttachmentPreviewEl.textContent = `${file.name} / ${Math.round(file.size / 1024)} KB`;
});

function clearAttachment() {
  pendingAttachment = null;
  userImageInputEl.value = "";
  userAttachmentPreviewEl.hidden = true;
  userAttachmentPreviewEl.textContent = "";
}

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

async function loadStatus() {
  try {
    const response = await fetch(`/api/status?ts=${Date.now()}`);
    const status = await response.json();
    userStatusEl.textContent = currentRole ? (identityLabels[currentRole] || currentRole) : "请选择身份";
  } catch {
    userStatusEl.textContent = "Offline";
  }
}

loadStatus();
clearIdentity();
addBubble("agent", "你好。请先选择身份：总经理、服务工程师或设计开发。选择后我会进入对应工作流。");
window.SantoniUserAppReady = true;
})();















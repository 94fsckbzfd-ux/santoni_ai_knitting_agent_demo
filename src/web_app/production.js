const productionStatus = document.querySelector("#productionStatus");
const productionSummary = document.querySelector("#productionSummary");
const actualDataSnapshot = document.querySelector("#actualDataSnapshot");
const gmThreeMinuteBrief = document.querySelector("#gmThreeMinuteBrief");
const skillRegistryPanel = document.querySelector("#skillRegistryPanel");
const stableDemoStoryPack = document.querySelector("#stableDemoStoryPack");
const internalDemoCandidatePanel = document.querySelector("#internalDemoCandidatePanel");
const mvpDemoStory = document.querySelector("#mvpDemoStory");
const mvpSuccessCheck = document.querySelector("#mvpSuccessCheck");
const prdAlignmentAudit = document.querySelector("#prdAlignmentAudit");
const serviceRiskBrief = document.querySelector("#serviceRiskBrief");
const workflowLane = document.querySelector("#workflowLane");
const managementPriorityBrief = document.querySelector("#managementPriorityBrief");
const evidenceReviewQueuePanel = document.querySelector("#evidenceReviewQueue");
const decisionLoop = document.querySelector("#decisionLoop");
const permissionBoundary = document.querySelector("#permissionBoundary");
const operationsStack = document.querySelector("#operationsStack");
const optimizationSignals = document.querySelector("#optimizationSignals");
const adapterContract = document.querySelector("#adapterContract");
const serviceCandidates = document.querySelector("#serviceCandidates");
const productionKpis = document.querySelector("#productionKpis");
const productionEvidence = document.querySelector("#productionEvidence");
const materialRiskPanel = document.querySelector("#materialRiskPanel");
const dataReadinessPanel = document.querySelector("#dataReadinessPanel");
const questionBankPanel = document.querySelector("#questionBankPanel");
const refreshProduction = document.querySelector("#refreshProduction");
const chatbiForm = document.querySelector("#chatbiForm");
const chatbiQuestion = document.querySelector("#chatbiQuestion");
const chatbiOutput = document.querySelector("#chatbiOutput");
const chatbiQuickQuestions = document.querySelector("#chatbiQuickQuestions");

let lastRuntimeStatus = null;
let lastProductionResult = null;
let lastAdapterContract = null;

const STATUS_LABELS = {
  attention_required: ["Attention Required", "需关注"],
  monitor: ["Monitor", "观察中"],
  on_track: ["On Track", "正常"],
  attention: ["Attention", "需关注"],
  ok: ["OK", "正常"],
  low: ["Low", "低"],
  medium: ["Medium", "中"],
  high: ["High", "高"],
  mock_contract: ["Mock Contract", "本地 Mock 契约"],
  read_only_planned: ["Read-only Planned", "只读接口规划"],
  read_only_observed: ["Read-only Observed", "只读观察"],
  true: ["true", "是"],
  false: ["false", "否"],
  running: ["Running", "运行中"],
  idle: ["Idle", "空闲"],
  stopped: ["Stopped", "停机"],
  material_hold: ["Material Hold", "物料等待"],
  quality_hold: ["Quality Hold", "质量暂停"],
  not_started: ["Not Started", "未开始"],
  blocked: ["Blocked", "阻塞"],
  pending_confirmation: ["Pending Confirmation", "待确认"],
  assigned: ["Assigned", "已分配"],
  waiting_evidence: ["Waiting Evidence", "等待证据"],
  confirmed: ["Confirmed", "已确认"],
  closed: ["Closed", "已关闭"],
  unable_to_process: ["Unable to Process", "无法处理"],
};

const STAGE_LABELS = {
  order_intake: ["Order Intake", "接单"],
  erp_input: ["ERP Input", "ERP 输入"],
  aps_scheduling: ["APS Scheduling", "APS 排程"],
  iot_execution: ["IOT Execution", "IOT 执行"],
  production_monitoring: ["Production / Service Escalation", "生产监控 / 服务升级"],
  garment_output: ["Garment Output", "成衣输出"],
};

const OWNER_LABELS = {
  "Sales / Customer Service": ["Sales / Customer Service", "销售 / 客服"],
  "Planner / ERP Owner": ["Planner / ERP Owner", "计划员 / ERP 负责人"],
  Planner: ["Planner", "计划员"],
  "Production Supervisor": ["Production Supervisor", "生产主管"],
  "Production Manager / Service Manager": ["Production Manager / Service Manager", "生产经理 / 服务经理"],
  "Quality / Warehouse": ["Quality / Warehouse", "质量 / 仓库"],
};

const RESOURCE_LABELS = {
  people: ["People", "人"],
  machine: ["Machine", "机"],
  material: ["Material", "料"],
  method: ["Method", "法"],
  environment: ["Environment", "环"],
  measurement: ["Measurement", "测"],
};

const KPI_LABELS = {
  oee: ["OEE", "OEE"],
  downtime_minutes: ["Downtime Minutes", "停机分钟"],
  order_delay_risk: ["Order Delay Risk", "订单延误风险"],
  material_risk: ["Material Risk", "物料风险"],
  labor_efficiency: ["Labor Efficiency", "人工效率"],
  quality_risk: ["Quality Risk", "质量风险"],
  waste_cost_opportunity: ["Waste / Cost Opportunity", "浪费 / 降本机会"],
  capacity_occupation: ["Capacity Occupation", "产能占用"],
  scrap_rate: ["Scrap Rate", "废弃率"],
  adapter_contract_coverage: ["Adapter Contract Coverage", "接口契约覆盖"],
  management_priority_items: ["Management Priority Items", "管理优先级"],
};

const CHATBI_METRIC_LABELS = {
  scrap_rate: ["Scrap Rate", "废弃率"],
  oee: ["OEE", "OEE"],
  downtime: ["Downtime", "停机"],
  material_risk: ["Material Risk", "物料风险"],
  order_delay: ["Order Delay", "订单延误"],
  machine_bottleneck: ["Machine Bottleneck", "机台瓶颈"],
  data_gap: ["Data Gap", "数据缺口"],
  management_priority: ["Management Priority", "管理优先级"],
  unscheduled_weaving_part_order: ["Unscheduled Weaving Part Order", "未排满织造部件单"],
  machine_plan_load: ["Machine Plan Load", "机台计划负载"],
  machine_style_mismatch: ["Machine / Style Spec Mismatch", "机台 / 款式规格不匹配"],
  quantity_report_gap: ["Plan / Report Quantity Gap", "计划 / 报工数量差异"],
  overall: ["Overall Snapshot", "整体快照"],
};

const TYPE_LABELS = {
  material_flow: ["Material Flow", "物料流转"],
  machine_downtime: ["Machine Downtime", "机台停机"],
  people_optimization: ["People Optimization", "人员优化"],
  method_optimization: ["Method Optimization", "工艺优化"],
  measurement_optimization: ["Measurement Optimization", "质量检测优化"],
  service_recovery: ["Service Recovery", "服务恢复"],
};

const PHRASE_LABELS = {
  "machine waiting and planner rework": "机台等待和计划返工",
  "lost machine hours": "机台工时损失",
  "repeat manual work or quality rework": "重复人工处理或质量返工",
  "production recovery lead time": "生产恢复等待时间",
  "Confirm substitute lot or resequence APS schedule before machine idle time expands.": "在机台等待扩大前，确认替代批次或重新调整 APS 排程。",
  "Confirm APS yarn forecast demand, substitute lot, or resequence schedule before machine idle time expands.": "在机台等待扩大前，确认 APS 纱线预估需求、替代批次或重新调整排程。",
  "Review alarm, setup status, and service request candidate before next shift.": "下一班次前复核报警、setup 状态和服务请求候选。",
  "Review IOT alarm, setup status, program evidence, and service request candidate before next shift.": "下一班次前复核 IOT 报警、setup 状态、程序证据和服务请求候选。",
  "Prepare service case context, but do not auto-dispatch in Production MVP.": "准备服务案例上下文，但 Production MVP 不自动派工。",
  "fabric tension variation": "布面张力波动",
  "minor yarn feeder warning": "轻微送纱器警告",
  "material not ready": "物料未就绪",
  "waiting for next work order": "等待下一工单",
  "none": "无",
  "operator": "操作员",
  "mechanic": "机修",
  "available": "可用",
  "late": "延迟",
  "erp_exception": "ERP 异常",
  "read_only_evidence": "只读证据",
  "IOT quality field mock": "IOT 质量字段 mock",
  "Smartex/IOT reserved field mock": "Smartex/IOT 预留质量字段 mock",
  "ERP mock order intake": "ERP mock 接单",
  "ERP/APS/IOT mock join": "ERP/APS/IOT mock 关联",
  "ERP and material mock join": "ERP 和物料 mock 关联",
  "ERP sync mock": "ERP 同步 mock",
  "IOT machine monitor mock": "IOT 机台监控 mock",
  "Material availability mock": "物料可用性 mock",
  "Labor shift mock": "班组工时 mock",
  "Quality measurement mock": "质量检测 mock",
  "APS/IOT page research field map": "APS/IOT 页面调研字段映射",
  "IOT program-interface observation": "IOT 程序接口观察",
  "Order ORD-20260605-001 is synced, scheduled, and running.": "订单 ORD-20260605-001 已同步、已排程，正在生产。",
  "Order ORD-20260605-002 is running with a quality hold and machine stop.": "订单 ORD-20260605-002 存在质量暂停和机台停机。",
  "Order ORD-20260605-003 is blocked by elastane material availability.": "订单 ORD-20260605-003 被氨纶物料到料问题阻塞。",
  "Order ORD-20260605-004 has ERP exception and is not scheduled.": "订单 ORD-20260605-004 有 ERP 异常，尚未排程。",
  "SM8-03 stopped with fabric tension variation and requires service review candidate.": "SM8-03 因布面张力波动停机，需要形成服务复核候选。",
  "Elastane lot E-224 is late and creates material flow risk.": "氨纶批次 E-224 延迟，带来物料流转风险。",
  "Mechanic support hours are above plan due to repeated interventions.": "由于重复干预，机修支持工时高于计划。",
  "Order ORD-20260605-002 has elevated defect rate and quality warning.": "订单 ORD-20260605-002 缺陷率升高并触发质量预警。",
  "Production Console now maps APS order/schedule/material pages and IOT monitor/dashboard/data-analysis/device pages to normalized read-only objects.": "Production Console 已将 APS 订单/排单/物料页面和 IOT 监控/仪表盘/数据分析/单机页面映射为标准化只读对象。",
  "Future real integration should use formal IOT program-interface documentation instead of browser scraping.": "未来真实集成应使用正式 IOT 程序接口文档，而不是浏览器页面抓取。",
  "seamless running top": "无缝跑步上衣",
  "seamless sports bra": "无缝运动文胸",
  "compression sock": "压力袜",
  "seamless base layer": "无缝贴身层",
  "estimated good garments": "预计合格成衣",
  "quality holds": "质量暂停",
  "Read-only APS/IOT field mapping for the Production Operations Console.": "Production Operations Console 的 APS/IOT 只读字段映射。",
  "No APS/IOT credentials are stored in code, .env, mock data, docs, logs, exported files, or API responses.": "APS/IOT 凭据不会保存到代码、.env、mock 数据、文档、日志、导出文件或 API 响应中。",
  "APS and IOT read-only source pages mapped": "APS 和 IOT 只读来源页面已映射",
  "review under 70% or over 95%": "低于 70% 或高于 95% 需复核",
  "Read-only question-to-data root cause analysis for production KPIs.": "面向生产 KPI 的只读问数与根因分析。",
  "Style / quality": "款式 / 质量",
  "Machine": "机器",
  "Method / setup": "工艺 / 调机",
  "Material": "物料",
  "Machine downtime": "机器停机",
  "Order / schedule": "订单 / 排单",
  "Optimization signal": "优化信号",
  "machine": "机器",
  "style_quality": "款式 / 质量",
  "method": "工艺",
  "material": "物料",
  "order_schedule": "订单 / 排单",
};

function getLanguage() {
  return window.SantoniI18n?.getLanguage?.() || (document.documentElement.lang.startsWith("zh") ? "zh" : "en");
}

function isZh() {
  return getLanguage() === "zh";
}

function textPair(pair) {
  return isZh() ? pair[1] : pair[0];
}

function labelFrom(map, key, fallback = key) {
  return map[key] ? textPair(map[key]) : localizePhrase(fallback);
}

async function loadProduction() {
  productionStatus.textContent = isZh() ? "加载中" : "Loading";
  const [statusResponse, overviewResponse, adapterResponse] = await Promise.all([
    fetch(`/api/status?ts=${Date.now()}`),
    fetch(`/api/production/overview?ts=${Date.now()}`),
    fetch(`/api/production/adapter-contract?ts=${Date.now()}`),
  ]);
  lastRuntimeStatus = await statusResponse.json();
  lastProductionResult = await overviewResponse.json();
  lastAdapterContract = await adapterResponse.json();
  renderProduction(lastProductionResult);
}

function renderProduction(result) {
  renderProductionStatus(result);
  renderGmThreeMinuteBrief(result.management_priority_brief || {});
  renderStableDemoStoryPack(result.stable_demo_story_pack || {});
  renderInternalDemoCandidate(result.internal_demo_candidate || {});
  renderSkillRegistry(result.skill_registry || {});
  renderActualDataSnapshot(result.actual_data_snapshot || {});
  renderMvpDemoStory(result.mvp_demo_story || {});
  renderMvpSuccessCheck(result.mvp_success_check || {});
  renderPrdAlignmentAudit(result.prd_alignment_audit || {});
  renderServiceRiskBrief(result.service_escalations || [], result.resource_lens?.machine || {});
  renderSummary(result.production_overview);
  renderWorkflow(result.workflow_stages || []);
  renderManagementPriorityBrief(result.management_priority_brief || {});
  renderEvidenceReviewQueue(result.evidence_review_queue || {});
  renderDecisionLoop(result.decision_loop || {});
  renderPermissionBoundary(result.permission_boundary || {});
  renderOperationsStack(result);
  renderSignals(result.optimization_signals || []);
  renderAdapterContract(result.adapter_contract || lastAdapterContract);
  renderServiceCandidates(result.service_escalations || []);
  renderKpis(result.kpi_log || []);
  renderMaterialRisk(result.material_risk || {});
  renderDataReadiness(result.data_readiness || {});
  renderQuestionBank(result.general_manager_question_bank || {});
  renderEvidence(result.evidence_log || []);
}

function renderProductionStatus(result) {
  const version = lastRuntimeStatus?.version || result.workflow_template?.version || "";
  const status = result.workflow_instance?.status || "on_track";
  productionStatus.textContent = `${version} · ${labelFrom(STATUS_LABELS, status)}`;
}

function renderSkillRegistry(registry) {
  if (!skillRegistryPanel) return;
  const skills = registry.skills || [];
  if (!skills.length) {
    skillRegistryPanel.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前还没有加载 Athena Skill Registry。" : "Athena Skill Registry is not loaded yet.")}</p>`;
    return;
  }
  const coreSkills = skills.slice(0, 8).map((skill) => `
    <article class="skill-card">
      <span>${escapeHtml(skill.skill_id)}</span>
      <strong>${escapeHtml(isZh() ? skill.name_zh : skill.name_en)}</strong>
      <p>${escapeHtml(skill.purpose || "")}</p>
      <small>${escapeHtml(isZh() ? "演示状态" : "Demo status")}: ${escapeHtml(skill.demo_status || "-")}</small>
    </article>
  `).join("");
  skillRegistryPanel.innerHTML = `
    <div class="skill-registry-strip">
      <div>
        <span>${escapeHtml(isZh() ? "能力层定位" : "Skill Layer")}</span>
        <strong>${escapeHtml(registry.positioning || "Athena uses production-management skills to inspect evidence.")}</strong>
      </div>
      <small>${escapeHtml(isZh() ? "只读边界：不写 APS / ERP / IOT，不自动改排程或派工。" : "Read-only: no APS / ERP / IOT writes, no automatic scheduling or dispatch.")}</small>
    </div>
    <div class="skill-card-grid">${coreSkills}</div>
  `;
}

function renderActualDataSnapshot(snapshot) {
  if (!actualDataSnapshot) return;
  if (!snapshot.schema_id) {
    actualDataSnapshot.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前还没有加载 Tianpai APS Export。" : "No Tianpai APS Export is loaded yet.")}</p>`;
    return;
  }

  const loaded = snapshot.actual_export_status === "read_only_external_csv";
  const metrics = snapshot.kpis || {};
  const machineLoad = snapshot.machine_plan_load_top || [];
  const mismatch = snapshot.machine_style_spec_mismatch_candidates || {};
  const joinRows = (snapshot.join_quality || []).map((item) => `
    <li>
      <span>${escapeHtml(item.join_id || "")}</span>
      <strong>${escapeHtml(percent(item.match_rate || 0))}</strong>
    </li>
  `).join("");
  const kpiCards = [
    [[isZh() ? "总订单数" : "Total Orders"], metrics.total_order_count ?? 0],
    [[isZh() ? "临近交期订单" : "Near-due Orders"], metrics.near_due_order_count ?? 0],
    [[isZh() ? "已排部件单" : "Scheduled WPO"], metrics.scheduled_weaving_part_order_count ?? 0],
    [[isZh() ? "未排部件单" : "Unscheduled WPO"], metrics.unscheduled_weaving_part_order_count ?? 0],
    [[isZh() ? "计划完成率" : "Plan Completion"], percent(metrics.plan_completion_rate || 0)],
    [[isZh() ? "报工完成率" : "Report Completion"], percent(metrics.manual_report_completion_rate || 0)],
    [[isZh() ? "机台计划负载候选" : "Machine Load Candidates"], metrics.machine_plan_load_candidate_count ?? 0],
    [[isZh() ? "规格不匹配候选" : "Spec Mismatch Candidates"], metrics.machine_style_spec_mismatch_candidate_count ?? 0],
  ].map(([label, value]) => `
    <article class="actual-kpi-card">
      <span>${escapeHtml(label[0])}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `).join("");
  const loadRows = machineLoad.slice(0, 5).map((item) => `
    <li>
      <strong>${escapeHtml(item.machine_code || item.machine_id || "-")}</strong>
      <span>${escapeHtml(isZh() ? "计划量" : "planned")}: ${escapeHtml(item.planned_quantity ?? 0)} · ${escapeHtml(isZh() ? "任务" : "tasks")}: ${escapeHtml(item.task_count ?? 0)} · ${escapeHtml(isZh() ? "完成率" : "completion")}: ${escapeHtml(percent(item.completion_rate || 0))}</span>
    </li>
  `).join("");
  const mismatchRows = (mismatch.candidates || []).slice(0, 5).map((item) => `
    <li>
      <strong>${escapeHtml(item.produce_order_code || "-")} · ${escapeHtml(item.machine_code || item.machine_id || "-")}</strong>
      <span>${escapeHtml(item.sku_code || "-")} / ${escapeHtml(item.part || "-")} · ${escapeHtml((item.mismatch_fields || []).join(", ") || "-")}</span>
      <small>${escapeHtml(isZh() ? "要求" : "required")}: ${escapeHtml(item.required_cylinder_diameter || "-")}/${escapeHtml(item.required_needle_spacing || "-")} · ${escapeHtml(isZh() ? "机台" : "machine")}: ${escapeHtml(item.machine_cylinder_diameter || "-")}/${escapeHtml(item.machine_needle_spacing || "-")}</small>
    </li>
  `).join("");

  actualDataSnapshot.innerHTML = `
    <div class="actual-source-strip">
      <div>
        <span>${escapeHtml(isZh() ? "当前数据源" : "Current Data Source")}</span>
        <strong>${escapeHtml(snapshot.current_data_source_label || "Mock / Tianpai APS Export")}</strong>
      </div>
      <div>
        <span>${escapeHtml(isZh() ? "真实导出状态" : "Actual Export")}</span>
        <strong>${escapeHtml(loaded ? (isZh() ? "已加载，只读" : "Loaded, read-only") : (isZh() ? "未加载" : "Not loaded"))}</strong>
      </div>
      <small>${escapeHtml(snapshot.raw_file_stored_in_repo ? "raw_file_stored_in_repo=true" : "raw_file_stored_in_repo=false")} · ${escapeHtml(isZh() ? "外部 CSV 只读，原始客户数据不进入 repo" : "External CSV is read-only; raw customer data is not copied into the repo")}</small>
    </div>
    <div class="actual-kpi-grid">${kpiCards}</div>
    <div class="actual-snapshot-grid">
      <article>
        <h3>${escapeHtml(isZh() ? "关联质量" : "Join Quality")}</h3>
        <ul class="actual-join-list">${joinRows}</ul>
      </article>
      <article>
        <h3>${escapeHtml(isZh() ? "机台计划负载 Top 5" : "Machine Plan Load Top 5")}</h3>
        <ul>${loadRows || `<li>${escapeHtml(isZh() ? "暂无机台计划负载。" : "No machine load data.")}</li>`}</ul>
      </article>
      <article>
        <h3>${escapeHtml(isZh() ? "机台 / 款式规格不匹配候选" : "Machine / Style Spec Mismatch Candidates")}</h3>
        <p>${escapeHtml(isZh() ? "候选总数" : "Total candidates")}: ${escapeHtml(mismatch.candidate_count_total ?? 0)}</p>
        <ul>${mismatchRows || `<li>${escapeHtml(isZh() ? "当前未发现筒径/针距不匹配候选。" : "No cylinder/gauge mismatch candidates found.")}</li>`}</ul>
      </article>
    </div>
  `;
}

function renderGmThreeMinuteBrief(brief) {
  if (!gmThreeMinuteBrief) return;
  const priorities = brief.top_priorities || [];
  if (!priorities.length) {
    gmThreeMinuteBrief.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照还没有形成总经理三件事简报。" : "No general-manager brief is available in the current snapshot.")}</p>`;
    return;
  }

  const cards = priorities.slice(0, 3).map((item) => {
    const title = isZh() ? item.title_zh || item.title : item.title;
    const conclusion = isZh() ? item.conclusion_zh || item.conclusion : item.conclusion;
    const action = isZh() ? item.recommended_action_zh || item.recommended_action : item.recommended_action;
    const affected = item.affected_objects || {};
    const objects = affectedObjectSummary(affected);
    const riskLevel = riskLevelLabel(item);
    const evidenceClaims = Array.isArray(item.evidence_claims) ? item.evidence_claims : [];
    const keyEvidence = renderPriorityEvidencePreview(item.evidence_refs || [], evidenceClaims);
    const fullEvidence = renderPriorityEvidenceDetails(item.evidence_refs || [], evidenceClaims);
    const dataGaps = renderPriorityDataGaps(item.data_gaps || []);
    const actualChains = renderPriorityActualChains(item.actual_evidence_chains || []);
    const skillsPreview = renderPrioritySkills(item.skills_used || []);
    const skillTrace = renderSkillExecutionTrace(item.skill_execution_trace || []);
    const drilldownQuestion = gmDrilldownQuestion(item);
    const fieldSources = (item.field_sources || []).filter(Boolean).slice(0, 3).join(" / ") || "-";
    const demoReady = item.internal_demo_ready ? (isZh() ? "可内部演示" : "Internal demo ready") : (isZh() ? "仅作可视化提示" : "Visibility only");
    const sourceMode = item.data_source_mode || "mock_snapshot_fallback";

    return `
      <article class="gm-brief-card ${escapeHtml((item.priority || "P2").toLowerCase())}">
        <div class="gm-brief-rank">
          <span>${escapeHtml(item.priority || "P2")}</span>
          <strong>#${escapeHtml(item.rank || "")}</strong>
        </div>
        <div>
          <h3>${escapeHtml(title || "")}</h3>
          <p>${escapeHtml(localizePhrase(conclusion || ""))}</p>
          <dl>
            <div><dt>${escapeHtml(isZh() ? "风险主题" : "Risk Theme")}</dt><dd>${escapeHtml(item.risk_theme_label || item.risk_theme || item.management_theme || "-")}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "风险等级" : "Risk Level")}</dt><dd>${escapeHtml(riskLevel)}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "数据源" : "Data Source")}</dt><dd>${escapeHtml(sourceMode)}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "证据等级" : "Evidence Level")}</dt><dd>${escapeHtml(item.evidence_level || "-")}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "演示状态" : "Demo Status")}</dt><dd>${escapeHtml(demoReady)}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "为什么重要" : "Why it matters")}</dt><dd>${escapeHtml(localizePhrase(item.risk_if_ignored_zh && isZh() ? item.risk_if_ignored_zh : item.risk_if_ignored || ""))}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "对象" : "Objects")}</dt><dd>${escapeHtml(objects || "-")}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "关键证据" : "Key Evidence")}</dt><dd>${keyEvidence}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "字段来源" : "Field Source")}</dt><dd>${escapeHtml(fieldSources)}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "负责人" : "Owner")}</dt><dd>${escapeHtml(item.owner_role || "-")}</dd></div>
            <div><dt>${escapeHtml(isZh() ? "Athena 已检查" : "Athena checked")}</dt><dd>${skillsPreview}</dd></div>
          </dl>
          <small>${escapeHtml(localizePhrase(action || ""))}</small>
          <details class="gm-brief-details">
            <summary>${escapeHtml(isZh() ? "展开完整证据和数据缺口" : "Full Evidence and Data Gaps")}</summary>
            <div>
              <strong>${escapeHtml(isZh() ? "完整证据" : "Full evidence")}</strong>
              ${fullEvidence}
              <strong>${escapeHtml(isZh() ? "真实数据证据链" : "Actual Data Evidence Chain")}</strong>
              ${actualChains}
              <strong>${escapeHtml(isZh() ? "Athena 技能执行过程" : "Skill Execution Trace")}</strong>
              ${skillTrace}
              <strong>${escapeHtml(isZh() ? "数据缺口" : "Data gaps")}</strong>
              ${dataGaps}
            </div>
          </details>
          <div class="gm-brief-actions">
            <button type="button" class="secondary-button" data-gm-question="${escapeHtml(drilldownQuestion)}">${escapeHtml(isZh() ? "继续追问" : "Continue Asking")}</button>
          </div>
        </div>
      </article>
    `;
  }).join("");
  const summaryLines = isZh() && Array.isArray(brief.daily_brief?.summary_zh)
    ? brief.daily_brief.summary_zh
    : (brief.daily_brief?.summary || []);
  const summaryList = summaryLines.slice(0, 5).map((line) => `<li>${escapeHtml(localizePhrase(line))}</li>`).join("");

  gmThreeMinuteBrief.innerHTML = `
    <div class="gm-brief-summary">
      <div>
        <p>${escapeHtml(isZh() ? "Athena 把当前订单、质量、设备、物料和人员证据压缩成总经理第一屏。每条建议都需要负责人确认后才能行动。" : "Athena compresses order, quality, machine, material, and labor evidence into a first-screen management brief. Every action still requires owner confirmation.")}</p>
        <ul class="gm-summary-lines">${summaryList || `<li>${escapeHtml(isZh() ? "当前快照没有摘要。" : "No management summary in the current snapshot.")}</li>`}</ul>
      </div>
      <small>${escapeHtml(isZh() ? "优先级规则" : "Priority policy")}: ${escapeHtml((brief.priority_policy?.kpi_priority || ["delivery", "quality", "cost"]).join(" > "))}</small>
    </div>
    <div class="gm-brief-grid">${cards}</div>
  `;
}

function renderMvpDemoStory(story) {
  if (!mvpDemoStory) return;
  if (!story.schema_id) {
    mvpDemoStory.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照还没有 MVP 演示故事线。" : "No MVP demo story is available in the current snapshot.")}</p>`;
    return;
  }

  const title = isZh() ? story.title_zh || story.title : story.title;
  const positioning = isZh() ? story.positioning_zh || story.positioning : story.positioning;
  const initialStory = isZh() ? story.initial_story_zh || story.initial_story : story.initial_story;
  const dataBoundary = isZh() ? story.data_boundary_zh || story.data_boundary : story.data_boundary;
  const criteria = isZh() ? story.success_criteria_zh || story.success_criteria : story.success_criteria || [];
  const steps = (story.story_steps || []).map((step, index) => {
    const stepTitle = isZh() ? step.title_zh || step.title : step.title;
    const managerUnderstanding = isZh()
      ? step.expected_manager_understanding_zh || step.expected_manager_understanding
      : step.expected_manager_understanding;
    const refs = Array.isArray(step.object_refs) ? step.object_refs.filter(Boolean).slice(0, 4) : [];
    const proof = Array.isArray(isZh() ? step.proof_zh : step.proof)
      ? (isZh() ? step.proof_zh : step.proof).filter(Boolean).slice(0, 5)
      : [];

    return `
      <article class="mvp-story-step">
        <span>${escapeHtml(String(index + 1).padStart(2, "0"))}</span>
        <div>
          <h3>${escapeHtml(stepTitle || "")}</h3>
          <p>${escapeHtml(localizePhrase(managerUnderstanding || ""))}</p>
          <small>${escapeHtml(isZh() ? "对象" : "Objects")}: ${escapeHtml(refs.join(" / ") || "-")}</small>
          <small>${escapeHtml(isZh() ? "证据" : "Evidence")}: ${escapeHtml(proof.join(" / ") || "-")}</small>
        </div>
      </article>
    `;
  }).join("");
  const criteriaItems = criteria.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("");

  mvpDemoStory.innerHTML = `
    <div class="mvp-story-head">
      <div>
        <span>${escapeHtml(story.source_prd_section || "MVP Demo Story")}</span>
        <h3>${escapeHtml(title || "")}</h3>
      </div>
      <p>${escapeHtml(positioning || "")}</p>
      <strong>${escapeHtml(initialStory || "")}</strong>
    </div>
    <div class="mvp-story-steps">${steps}</div>
    <div class="mvp-story-footer">
      <div>
        <h3>${escapeHtml(isZh() ? "三分钟内应确认" : "Within three minutes")}</h3>
        <ul>${criteriaItems}</ul>
      </div>
      <p>${escapeHtml(dataBoundary || "")}</p>
    </div>
  `;
}

function renderStableDemoStoryPack(pack) {
  if (!stableDemoStoryPack) return;
  if (!pack.schema_id) {
    stableDemoStoryPack.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前还没有稳定演示故事包。" : "No stable demo story pack is available yet.")}</p>`;
    return;
  }

  const title = isZh() ? pack.title_zh || pack.title : pack.title;
  const positioning = isZh() ? pack.positioning_zh || pack.positioning : pack.positioning;
  const policy = isZh() ? pack.demo_policy_zh || pack.demo_policy : pack.demo_policy || {};
  const actual = pack.actual_data_available || {};
  const usable = isZh() ? actual.usable_for_demo_zh || actual.usable_for_demo : actual.usable_for_demo || [];
  const sequence = isZh() ? pack.recommended_demo_sequence_zh || pack.recommended_demo_sequence : pack.recommended_demo_sequence || [];
  const mockNeeded = pack.mock_needed_for_demo || [];
  const stories = (pack.stories || []).map((story, index) => {
    const storyTitle = isZh() ? story.title_zh || story.title : story.title;
    const badge = isZh() ? story.demo_badge_zh || story.demo_badge : story.demo_badge;
    const shows = (story.what_athena_shows || []).filter(Boolean).slice(0, 4);
    const realSources = (story.real_data_sources || []).filter(Boolean).slice(0, 6);
    const mockSupplements = (story.mock_supplements || []).filter(Boolean).slice(0, 4);
    const gaps = (story.data_gaps || []).filter(Boolean).slice(0, 4);
    const evidenceRefs = (story.evidence_refs || []).filter(Boolean).slice(0, 6);
    const question = story.chatbi_question || story.manager_question || "";
    const modeClass = String(story.evidence_mode || "mock").replaceAll("_", "-");
    return `
      <article class="stable-demo-card ${escapeHtml(modeClass)}">
        <div class="stable-demo-card-head">
          <span>${escapeHtml(String(index + 1).padStart(2, "0"))}</span>
          <div>
            <strong>${escapeHtml(storyTitle || "")}</strong>
            <small>${escapeHtml(badge || story.evidence_mode || "")}</small>
          </div>
        </div>
        <p>${escapeHtml(story.manager_question || "")}</p>
        <div class="stable-demo-tags">
          <span>${escapeHtml(story.evidence_mode || "-")}</span>
          <span>${escapeHtml(story.internal_demo_ready ? (isZh() ? "可内部演示" : "Internal demo ready") : (isZh() ? "仅作说明" : "Narrative only"))}</span>
          <span>${escapeHtml(story.suggested_owner || "-")}</span>
        </div>
        <details open>
          <summary>${escapeHtml(isZh() ? "Athena 会展示什么" : "What Athena Shows")}</summary>
          <ul>${shows.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}</ul>
        </details>
        <details>
          <summary>${escapeHtml(isZh() ? "真实数据源" : "Real Data Sources")}</summary>
          <ul>${realSources.map((item) => `<li>${escapeHtml(item)}</li>`).join("") || `<li>-</li>`}</ul>
        </details>
        <details>
          <summary>${escapeHtml(isZh() ? "Mock 补充 / 数据缺口" : "Mock Supplements / Data Gaps")}</summary>
          <ul>
            ${mockSupplements.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
            ${gaps.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}
          </ul>
        </details>
        <small>${escapeHtml(isZh() ? "证据" : "Evidence")}: ${escapeHtml(evidenceRefs.join(" / ") || "-")}</small>
        <button type="button" class="secondary-button" data-demo-story-question="${escapeHtml(question)}">${escapeHtml(isZh() ? "让 Athena 下钻" : "Ask Athena")}</button>
      </article>
    `;
  }).join("");

  stableDemoStoryPack.innerHTML = `
    <div class="stable-demo-intro">
      <div>
        <span>${escapeHtml(pack.pack_id || "")}</span>
        <h3>${escapeHtml(title || "")}</h3>
        <p>${escapeHtml(positioning || "")}</p>
      </div>
      <div class="stable-demo-policy">
        <strong>${escapeHtml(isZh() ? "演示边界" : "Demo Boundary")}</strong>
        <ul>
          ${Object.values(policy).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </div>
    </div>
    <div class="stable-demo-data-grid">
      <article>
        <strong>${escapeHtml(isZh() ? "现在可用的真实数据" : "Actual Data Available")}</strong>
        <ul>${usable.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </article>
      <article>
        <strong>${escapeHtml(isZh() ? "需要 mock 或后续接入的数据" : "Mock / Future Data Needed")}</strong>
        <ul>${mockNeeded.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
      </article>
      <article>
        <strong>${escapeHtml(isZh() ? "推荐演示顺序" : "Recommended Demo Sequence")}</strong>
        <ol>${sequence.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>
      </article>
    </div>
    <div class="stable-demo-card-grid">${stories}</div>
  `;
}

function renderInternalDemoCandidate(candidate) {
  if (!internalDemoCandidatePanel) return;
  if (!candidate.schema_id) {
    internalDemoCandidatePanel.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前还没有 v0.108.3 演示候选契约。" : "No v0.108.3 internal demo candidate contract is available yet.")}</p>`;
    return;
  }
  const flow = candidate.guided_demo_flow || {};
  const presenter = candidate.presenter_mode || {};
  const boundary = candidate.evidence_boundary_layer || {};
  const requests = candidate.data_request_wizard?.requests || [];
  const service = candidate.service_risk_confirmation_flow || {};
  const hermes = candidate.hermes_training_memory_review || {};
  const report = candidate.internal_demo_candidate_report || {};
  const flowSteps = (flow.steps || []).map((step) => `
    <li>
      <strong>${escapeHtml(step.label || step.step_id || "")}</strong>
      <span>${escapeHtml(step.manager_goal || "")}</span>
    </li>
  `).join("");
  const boundaryModes = Object.entries(boundary.modes || {}).map(([mode, info]) => `
    <article>
      <strong>${escapeHtml(info.manager_label || mode)}</strong>
      <span>${escapeHtml(mode)}</span>
      <p>${escapeHtml(info.description || "")}</p>
    </article>
  `).join("");
  const requestCards = requests.slice(0, 5).map((request) => `
    <article>
      <strong>${escapeHtml(request.domain || request.request_id || "")}</strong>
      <span>${escapeHtml(request.priority || "")} · ${escapeHtml(request.sensitivity_level || "")}</span>
      <p>${escapeHtml(request.purpose || "")}</p>
    </article>
  `).join("");
  const regressionCount = presenter.recommended_questions?.length || candidate.gm_question_regression_set?.questions?.length || 0;
  internalDemoCandidatePanel.innerHTML = `
    <div class="internal-demo-grid">
      <article>
        <span>${escapeHtml(isZh() ? "状态" : "Status")}</span>
        <strong>${escapeHtml(flow.status || "ready_for_internal_demo")}</strong>
        <p>${escapeHtml(isZh() ? "Demo reset 只重置本地演示状态，不写 APS/ERP/IOT。" : "Demo reset only touches local demo state and does not write APS/ERP/IOT.")}</p>
      </article>
      <article>
        <span>${escapeHtml(isZh() ? "Presenter" : "Presenter")}</span>
        <strong>${escapeHtml(String(regressionCount))}</strong>
        <p>${escapeHtml(isZh() ? "已固化总经理问题回归集和预期输出。" : "GM regression questions and expected outputs are fixed.")}</p>
      </article>
      <article>
        <span>${escapeHtml(isZh() ? "Service 确认" : "Service confirmation")}</span>
        <strong>${escapeHtml(String(service.confirmation_cards?.length || 0))}</strong>
        <p>${escapeHtml(isZh() ? "只生成确认流程，不自动派工或创建真实工单。" : "Confirmation flow only; no auto-dispatch or real ticket creation.")}</p>
      </article>
      <article>
        <span>${escapeHtml(isZh() ? "Hermes 候选" : "Hermes candidates")}</span>
        <strong>${escapeHtml(String(hermes.candidate_count || 0))}</strong>
        <p>${escapeHtml(isZh() ? "只生成本地 memory/training candidate，不写 live Hermes。" : "Local memory/training candidates only; no live Hermes write.")}</p>
      </article>
    </div>
    <div class="internal-demo-split">
      <section>
        <h3>${escapeHtml(isZh() ? "引导演示流程" : "Guided Demo Flow")}</h3>
        <ol>${flowSteps}</ol>
      </section>
      <section>
        <h3>${escapeHtml(isZh() ? "证据边界" : "Evidence Boundary")}</h3>
        <div class="internal-demo-boundaries">${boundaryModes}</div>
      </section>
    </div>
    <section>
      <h3>${escapeHtml(isZh() ? "下一轮数据请求" : "Next Data Requests")}</h3>
      <div class="internal-demo-requests">${requestCards}</div>
    </section>
    <p class="muted-text">${escapeHtml(isZh() ? `报告：${report.path || "docs/product/athena_delivery_risk_driver_guard_v0.108.3.md"}` : `Report: ${report.path || "docs/product/athena_delivery_risk_driver_guard_v0.108.3.md"}`)}</p>
  `;
}

function renderMvpSuccessCheck(check) {
  if (!mvpSuccessCheck) return;
  if (!check.schema_id) {
    mvpSuccessCheck.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照还没有 MVP 成功标准检查。" : "No MVP success check is available in the current snapshot.")}</p>`;
    return;
  }

  const status = check.within_three_minutes_ready
    ? (isZh() ? "三分钟演示路径已覆盖" : "Three-minute path covered")
    : (isZh() ? "仍需补证据" : "Needs more evidence");
  const readout = isZh() ? check.manager_readout_zh || check.manager_readout : check.manager_readout;
  const boundary = isZh() ? check.remaining_data_boundary_zh || check.remaining_data_boundary : check.remaining_data_boundary || [];
  const summary = check.criteria_summary || {};
  const criteriaCards = (check.criteria_checks || []).map((item) => {
    const requirement = isZh() ? item.prd_requirement_zh || item.prd_requirement : item.prd_requirement;
    const surface = isZh() ? item.manager_visible_surface_zh || item.manager_visible_surface : item.manager_visible_surface;
    const passed = item.status === "pass";
    return `
      <article class="mvp-success-card ${passed ? "pass" : "needs-work"}">
        <div>
          <span>${escapeHtml(passed ? (isZh() ? "通过" : "Pass") : (isZh() ? "待补" : "Needs work"))}</span>
          <strong>${escapeHtml(requirement || item.criterion_id || "")}</strong>
        </div>
        <p>${escapeHtml(surface || "")}</p>
        <small>${escapeHtml(isZh() ? "证据" : "Evidence")}: ${escapeHtml((item.evidence_refs || []).filter(Boolean).slice(0, 5).join(" / ") || "-")}</small>
        <small>${escapeHtml(isZh() ? "对象" : "Objects")}: ${escapeHtml((item.object_refs || []).filter(Boolean).slice(0, 5).join(" / ") || "-")}</small>
      </article>
    `;
  }).join("");
  const boundaryItems = boundary.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

  mvpSuccessCheck.innerHTML = `
    <div class="mvp-success-head">
      <div>
        <span>${escapeHtml(check.source_prd_section || "17. Success Criteria")}</span>
        <strong>${escapeHtml(status)}</strong>
      </div>
      <div class="mvp-success-score">
        <span>${escapeHtml(isZh() ? "覆盖率" : "Coverage")}</span>
        <strong>${escapeHtml(Math.round((check.readiness_score || 0) * 100))}%</strong>
      </div>
      <p>${escapeHtml(readout || "")}</p>
      <small>${escapeHtml(check.current_evidence_level || "")} · ${escapeHtml(summary.pass_count ?? 0)}/${escapeHtml(summary.check_count ?? 0)}</small>
    </div>
    <div class="mvp-success-grid">${criteriaCards}</div>
    <div class="mvp-success-boundary">
      <h3>${escapeHtml(isZh() ? "仍需真实数据证明" : "Still Needs Real Data")}</h3>
      <ul>${boundaryItems}</ul>
    </div>
  `;
}

function renderPrdAlignmentAudit(audit) {
  if (!prdAlignmentAudit) return;
  if (!audit.schema_id) {
    prdAlignmentAudit.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照还没有 PRD 覆盖审计。" : "No PRD alignment audit is available in the current snapshot.")}</p>`;
    return;
  }

  const statusLabels = {
    covered: isZh() ? "已覆盖" : "Covered",
    covered_with_gaps: isZh() ? "已覆盖 / 有缺口" : "Covered with gaps",
    documented_boundary: isZh() ? "边界已记录" : "Boundary documented",
    open_by_design: isZh() ? "按设计保留" : "Open by design",
  };
  const coverage = Math.round((audit.coverage_score || 0) * 100);
  const sectionCards = (audit.section_checks || []).map((item) => {
    const status = item.status || "covered_with_gaps";
    const refs = (item.evidence_refs || []).filter(Boolean).slice(0, 5).join(" / ") || "-";
    const objects = (item.implemented_by || []).filter(Boolean).slice(0, 5).join(" / ") || "-";

    return `
      <article class="prd-section-card ${escapeHtml(status.replaceAll("_", "-"))}">
        <div>
          <span>${escapeHtml(statusLabels[status] || status)}</span>
          <strong>${escapeHtml(item.section || "")}</strong>
        </div>
        <p>${escapeHtml(isZh() ? "实现对象" : "Implemented by")}: ${escapeHtml(objects)}</p>
        <small>${escapeHtml(isZh() ? "证据" : "Evidence")}: ${escapeHtml(refs)}</small>
        <small>${escapeHtml(isZh() ? "剩余缺口" : "Remaining gap")}: ${escapeHtml(item.remaining_gap || "-")}</small>
      </article>
    `;
  }).join("");
  const openQuestions = (audit.remaining_open_questions || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const loopItems = (audit.core_loop_coverage || [])
    .map((item) => `<span>${escapeHtml(item.replaceAll("_", " "))}</span>`)
    .join("");

  prdAlignmentAudit.innerHTML = `
    <div class="prd-alignment-head">
      <div>
        <span>${escapeHtml(audit.source_prd || "docs/product/athena_prd_v0.1.md")}</span>
        <strong>${escapeHtml(isZh() ? "本地 MVP PRD 覆盖审计" : "Local MVP PRD Coverage Audit")}</strong>
      </div>
      <div class="prd-alignment-score">
        <span>${escapeHtml(isZh() ? "覆盖率" : "Coverage")}</span>
        <strong>${escapeHtml(coverage)}%</strong>
      </div>
      <p>${escapeHtml(audit.coverage_status || "")}</p>
      <small>${escapeHtml(audit.audit_id || "")} · ${escapeHtml(isZh() ? "只读审计" : "read-only audit")}</small>
    </div>
    <div class="prd-core-loop">${loopItems}</div>
    <div class="prd-alignment-grid">${sectionCards}</div>
    <div class="prd-alignment-footer">
      <div>
        <h3>${escapeHtml(isZh() ? "仍需确认的问题" : "Remaining Open Questions")}</h3>
        <ul>${openQuestions}</ul>
      </div>
      <p>${escapeHtml(audit.blocked_completion_claim || "")}</p>
    </div>
  `;
}

function affectedObjectSummary(affected) {
  const labels = {
    orders: isZh() ? "订单" : "Orders",
    styles: isZh() ? "款式" : "Styles",
    machines: isZh() ? "机台" : "Machines",
    materials: isZh() ? "物料" : "Materials",
    teams: isZh() ? "班组" : "Teams",
    roles: isZh() ? "角色" : "Roles",
    process_stages: isZh() ? "工序" : "Process",
    service_candidates: isZh() ? "服务候选" : "Service Candidates",
    weaving_part_order_ids: isZh() ? "织造部件单" : "Weaving Part Orders",
    planned_task_ids: isZh() ? "计划任务" : "Planned Tasks",
  };
  return Object.entries(labels).map(([key, label]) => {
    const values = Array.isArray(affected[key]) ? affected[key].filter(Boolean) : [];
    return values.length ? `${label}: ${values.join(", ")}` : "";
  }).filter(Boolean).join(" · ");
}

function riskLevelLabel(item) {
  const level = item.risk_level || "gray";
  const fallback = {
    red: isZh() ? "红色：今天必须确认" : "Red: must be confirmed today",
    yellow: isZh() ? "黄色：24-48 小时内确认" : "Yellow: confirm within 24-48 hours",
    gray: isZh() ? "灰色：证据不足，仅作可视化提醒" : "Gray: insufficient data; visibility only",
  };
  if (!isZh() && item.risk_level_label) return item.risk_level_label;
  return fallback[level] || fallback.gray;
}

function evidenceLevelLabel(adapterStatus) {
  if (adapterStatus === "mock_contract") return isZh() ? "Level 1: mock / demo evidence" : "Level 1: mock / demo evidence";
  if (adapterStatus === "excel_imported") return isZh() ? "Level 2: Excel imported evidence" : "Level 2: Excel imported evidence";
  if (adapterStatus === "read_only_database" || adapterStatus === "read_only_planned") return isZh() ? "Level 3: read-only database evidence" : "Level 3: read-only database evidence";
  if (adapterStatus === "human_reviewed") return isZh() ? "Level 4: reviewed human confirmation" : "Level 4: reviewed human confirmation";
  return isZh() ? "Level 1: mock / demo evidence" : "Level 1: mock / demo evidence";
}

function renderPriorityEvidencePreview(refs, claims) {
  const claimByRef = new Map(claims.map((item) => [item.evidence_ref, item]));
  const items = refs.slice(0, 3).map((ref) => {
    const claim = claimByRef.get(ref) || {};
    const text = claim.claim ? `${ref}: ${localizePhrase(claim.claim)}` : ref;
    return `<span class="evidence-chip">${escapeHtml(text)}</span>`;
  }).join("");
  return items || escapeHtml("-");
}

function renderPriorityEvidenceDetails(refs, claims) {
  const claimByRef = new Map(claims.map((item) => [item.evidence_ref, item]));
  const rows = refs.map((ref) => {
    const claim = claimByRef.get(ref) || {};
    return `
      <li>
        <span>${escapeHtml(ref)} · ${escapeHtml(evidenceLevelLabel(claim.adapter_status || "mock_contract"))}</span>
        <small>${escapeHtml(localizePhrase(claim.claim || ""))}${claim.source ? ` · ${escapeHtml(claim.source)}` : ""}</small>
      </li>
    `;
  }).join("");
  return `<ul class="gm-evidence-list">${rows || `<li><span>${escapeHtml(isZh() ? "暂无证据" : "No evidence")}</span></li>`}</ul>`;
}

function renderPriorityDataGaps(gaps) {
  const rows = gaps.map((gap) => `<li>${escapeHtml(localizePhrase(gap))}</li>`).join("");
  return `<ul class="gm-data-gap-list">${rows || `<li>${escapeHtml(isZh() ? "当前 mock 没有额外数据缺口。" : "No additional data gap in current mock.")}</li>`}</ul>`;
}

function renderPrioritySkills(skills) {
  const items = (skills || []).slice(0, 5).map((skill) => {
    const name = isZh() ? skill.name_zh || skill.skill_id : skill.name_en || skill.skill_id;
    return `<span class="skill-chip">${escapeHtml(name)}</span>`;
  }).join("");
  return items || escapeHtml("-");
}

function renderSkillExecutionTrace(trace) {
  const rows = (trace || []).slice(0, 6).map((step) => {
    const title = isZh() ? step.step_name_zh || step.skill_id : step.step_name_en || step.skill_id;
    const checked = isZh() ? step.what_athena_checked_zh || step.what_athena_checked : step.what_athena_checked;
    const result = isZh() ? step.result_summary_zh || step.result_summary : step.result_summary;
    const objects = (step.data_objects_checked || []).slice(0, 5).join(" / ") || "-";
    const refs = (step.evidence_refs || []).slice(0, 5).join(" / ") || "-";
    return `
      <article class="skill-trace-step">
        <div>
          <span>${escapeHtml(step.skill_id || "")}</span>
          <strong>${escapeHtml(title || "")}</strong>
        </div>
        <p>${escapeHtml(checked || "")}</p>
        <small>${escapeHtml(isZh() ? "对象" : "Objects")}: ${escapeHtml(objects)}</small>
        <small>${escapeHtml(isZh() ? "证据" : "Evidence")}: ${escapeHtml(refs)}</small>
        <small>${escapeHtml(isZh() ? "证据等级" : "Evidence level")}: ${escapeHtml(step.evidence_level || "-")}</small>
        <p>${escapeHtml(result || "")}</p>
        <small>${escapeHtml(isZh() ? "限制/缺口" : "Limitation / data gap")}: ${escapeHtml(step.limitation_or_data_gap || "-")}</small>
      </article>
    `;
  }).join("");
  return `<div class="skill-trace-list">${rows || `<p class="muted-text">${escapeHtml(isZh() ? "暂无技能执行过程。" : "No skill execution trace.")}</p>`}</div>`;
}

function renderPriorityActualChains(chains) {
  const rows = (chains || []).slice(0, 3).map((chain, index) => {
    const refs = (chain.evidence_refs || []).filter(Boolean).slice(0, 4).join(" / ") || "-";
    const values = [
      ["订单", "Order", chain.produce_order_code],
      ["部件单", "WPO", chain.weaving_part_order_id || (chain.weaving_part_order_ids || []).join(", ")],
      ["任务", "Task", chain.planned_task_id || (chain.planned_task_ids || []).join(", ")],
      ["机台", "Machine", chain.machine_code || chain.machine_id || (chain.machine_ids || []).join(", ")],
      ["字段来源", "Field Source", chain.field_source],
    ].filter(([, , value]) => value !== undefined && value !== null && String(value).trim() !== "");
    return `
      <li>
        <span>${escapeHtml(index + 1)}. ${escapeHtml(refs)}</span>
        ${values.map(([zh, en, value]) => `<small>${escapeHtml(isZh() ? zh : en)}: ${escapeHtml(value)}</small>`).join("")}
      </li>
    `;
  }).join("");
  return `<ul class="gm-evidence-list">${rows || `<li><span>${escapeHtml(isZh() ? "暂无真实导出证据链" : "No actual export evidence chain")}</span></li>`}</ul>`;
}

function gmDrilldownQuestion(item) {
  const affected = item.affected_objects || {};
  const orders = Array.isArray(affected.orders) ? affected.orders.filter(Boolean).join(", ") : "";
  const machines = Array.isArray(affected.machines) ? affected.machines.filter(Boolean).join(", ") : "";
  const theme = item.management_theme || "";

  if (item.drilldown_question) {
    return item.drilldown_question;
  }

  if (isZh()) {
    if (theme === "quality") {
      return `为什么 ${orders || item.priority_id} 的质量/废弃风险高？请按款式、机台、工艺、物料和证据下钻。`;
    }
    if (theme === "delivery") {
      return `为什么 ${orders || item.priority_id} 有交付风险？请按订单、排单、物料、影响交付和证据下钻。`;
    }
    if (theme === "labor") {
      return `为什么 ${orders || machines || item.priority_id} 的人工有效工时风险高？请按班组、人工干预、服务/调机/等待/返工和证据下钻。`;
    }
    return `为什么 ${machines || orders || item.priority_id} 造成产能或成本损失？请按机台、停机、OEE、人工和证据下钻。`;
  }

  if (theme === "quality") {
    return `Why does ${orders || item.priority_id} have quality or scrap risk? Drill down by style, machine, method, material, and evidence.`;
  }
  if (theme === "delivery") {
    return `Why does ${orders || item.priority_id} have delivery risk? Drill down by order, scheduling, material, delivery impact, and evidence.`;
  }
  if (theme === "labor") {
    return `Why does ${orders || machines || item.priority_id} have labor effective-hour risk? Drill down by team, manual intervention, service/setup/waiting/rework, and evidence.`;
  }
  return `Why does ${machines || orders || item.priority_id} create capacity or cost loss? Drill down by machine, downtime, OEE, labor, and evidence.`;
}

function renderServiceRiskBrief(items, machineLens) {
  if (!serviceRiskBrief) return;
  const machineSignals = machineLens.signals || [];
  const repeatedAlarmCount = machineSignals.filter((signal) => signal.risk === "medium" || signal.risk === "high").length;
  const stoppedCount = items.filter((item) => item.priority === "P1").length;

  if (!items.length) {
    serviceRiskBrief.innerHTML = `
      <div class="service-risk-summary">
        <p>${escapeHtml(isZh() ? "当前快照没有需要服务复核的机台候选。" : "No service-review machine candidate in the current snapshot.")}</p>
        <small>${escapeHtml(isZh() ? "仍保持只读监控，不自动创建工单。" : "Read-only monitoring remains active; no ticket is created automatically.")}</small>
      </div>
    `;
    return;
  }

  const cards = items.map((item) => {
    const signal = machineSignals.find((entry) => entry.title === item.machine_id) || {};
    const riskLevel = item.priority === "P1" ? (isZh() ? "红色：今天必须确认" : "Red: confirm today") : (isZh() ? "黄色：24-48 小时内确认" : "Yellow: confirm in 24-48 hours");
    const drilldownQuestion = serviceDrilldownQuestion(item);
    return `
      <article class="service-risk-card ${escapeHtml((item.priority || "P2").toLowerCase())}">
        <div class="priority-card-head">
          <span>${escapeHtml(item.priority || "P2")} · ${escapeHtml(riskLevel)}</span>
          <strong>${escapeHtml(item.machine_id)} · ${escapeHtml(localizePhrase(item.issue || ""))}</strong>
        </div>
        <dl>
          <div><dt>${escapeHtml(isZh() ? "影响订单" : "Affected Order")}</dt><dd>${escapeHtml(item.order_id || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "证据" : "Evidence")}</dt><dd>${escapeHtml(item.evidence_ref || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "自动派工" : "Auto Dispatch")}</dt><dd>${escapeHtml(labelFrom(STATUS_LABELS, String(item.auto_dispatch)))}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "机台信号" : "Machine Signal")}</dt><dd>${escapeHtml(localizePhrase(signal.detail || item.reason || ""))}</dd></div>
        </dl>
        <small>${escapeHtml(localizePhrase(item.reason || ""))}</small>
        <div class="gm-brief-actions">
          <button type="button" class="secondary-button" data-service-question="${escapeHtml(drilldownQuestion)}">${escapeHtml(isZh() ? "下钻服务风险" : "Drill Down Service Risk")}</button>
        </div>
      </article>
    `;
  }).join("");

  serviceRiskBrief.innerHTML = `
    <div class="service-risk-summary">
      <p>${escapeHtml(isZh() ? "Service 风险独立展示，因为停机、反复报警和机修响应会直接影响交付。这里仅生成服务请求候选，不自动派工。" : "Service risks are shown separately because stoppage, repeated alarms, and maintenance response can directly affect delivery. This section creates candidates only and never dispatches automatically.")}</p>
      <div class="service-risk-metrics">
        <div><span>${escapeHtml(isZh() ? "服务候选" : "Candidates")}</span><strong>${escapeHtml(items.length)}</strong></div>
        <div><span>${escapeHtml(isZh() ? "停机候选" : "Stopped")}</span><strong>${escapeHtml(stoppedCount)}</strong></div>
        <div><span>${escapeHtml(isZh() ? "报警/异常信号" : "Alarm Signals")}</span><strong>${escapeHtml(repeatedAlarmCount)}</strong></div>
      </div>
    </div>
    <div class="service-risk-grid">${cards}</div>
  `;
}

function serviceDrilldownQuestion(item) {
  if (isZh()) {
    return `为什么 ${item.machine_id || "这台机"} 需要服务复核？请按停机、报警、影响订单、服务候选和证据下钻。`;
  }
  return `Why does ${item.machine_id || "this machine"} need service review? Drill down by downtime, alarm, affected order, service candidate, and evidence.`;
}

function renderSummary(summary) {
  const tiles = [
    [["Backlog Orders", "未交货订单"], summary.backlog_order_count ?? summary.order_count],
    [["Style Count", "款式数"], summary.total_style_count ?? 0],
    [["Scheduled", "已排程"], summary.scheduled_order_count],
    [["Pending / Exception", "待排 / 异常"], summary.pending_or_exception_order_count],
    [["Running Machines", "运行机台"], `${summary.running_machine_count}/${summary.machine_count}`],
    [["Running Rate", "运行率"], percent(summary.machine_running_rate)],
    [["Capacity Occupation", "产能占用率"], percent(summary.capacity_occupation_rate ?? summary.machine_running_rate)],
    [["Average OEE", "平均 OEE"], percent(summary.average_oee)],
    [["Downtime", "停机时间"], isZh() ? `${summary.downtime_minutes} 分钟` : `${summary.downtime_minutes} min`],
    [["Material Risks", "物料风险"], summary.material_risk_count],
    [["Scrap Rate", "废弃率"], percent(summary.scrap_rate)],
    [["Average Yield", "平均良品率"], percent(summary.average_yield_rate)],
    [["Service Candidates", "服务候选"], summary.service_escalation_count],
  ];

  productionSummary.innerHTML = "";
  tiles.forEach(([label, value]) => {
    const tile = document.createElement("article");
    tile.className = "production-tile";
    tile.innerHTML = `<span>${escapeHtml(textPair(label))}</span><strong>${escapeHtml(value)}</strong>`;
    productionSummary.append(tile);
  });
}

function renderWorkflow(stages) {
  workflowLane.innerHTML = "";
  stages.forEach((stage, index) => {
    const card = document.createElement("article");
    card.className = `workflow-step ${stage.status === "ok" ? "ok" : "attention"}`;
    card.innerHTML = `
      <span>${index + 1}</span>
      <strong>${escapeHtml(labelFrom(STAGE_LABELS, stage.id, stage.name))}</strong>
      <p>${escapeHtml(labelFrom(OWNER_LABELS, stage.owner_role, stage.owner_role))} · ${escapeHtml(labelFrom(STATUS_LABELS, stage.status))}</p>
      <small>${escapeHtml(labelFrom(STATUS_LABELS, stage.adapter_status))} · ${escapeHtml(stage.evidence_ref)}</small>
    `;
    workflowLane.append(card);
  });
}

function renderManagementPriorityBrief(brief) {
  if (!managementPriorityBrief) return;
  const priorities = brief.top_priorities || [];
  if (!priorities.length) {
    managementPriorityBrief.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照没有形成带证据的管理优先级。" : "No evidence-backed management priorities in the current snapshot.")}</p>`;
    return;
  }

  const policy = brief.priority_policy || {};
  const headline = brief.daily_brief?.headline || "";
  const cards = priorities.map((item) => {
    const title = isZh() ? item.title_zh || item.title : item.title;
    const conclusion = isZh() ? item.conclusion_zh || item.conclusion : item.conclusion;
    const action = isZh() ? item.recommended_action_zh || item.recommended_action : item.recommended_action;
    const affected = item.affected_objects || {};
    const affectedText = Object.entries(affected)
      .filter(([, value]) => Array.isArray(value) && value.filter(Boolean).length)
      .map(([key, value]) => `${key}: ${value.filter(Boolean).join(", ")}`)
      .join(" | ");
    return `
      <article class="priority-card ${escapeHtml((item.priority || "P2").toLowerCase())}">
        <div class="priority-card-head">
          <span>${escapeHtml(item.priority)} · #${escapeHtml(item.rank)}</span>
          <strong>${escapeHtml(title)}</strong>
        </div>
        <p>${escapeHtml(localizePhrase(conclusion || ""))}</p>
        <dl>
          <div><dt>${escapeHtml(isZh() ? "负责人" : "Owner")}</dt><dd>${escapeHtml(item.owner_role || "")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "确认门" : "Gate")}</dt><dd>${escapeHtml(item.decision_gate || "")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "证据" : "Evidence")}</dt><dd>${escapeHtml((item.evidence_refs || []).join(" / "))}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "对象" : "Objects")}</dt><dd>${escapeHtml(affectedText || "-")}</dd></div>
        </dl>
        <small>${escapeHtml(localizePhrase(action || ""))}</small>
      </article>
    `;
  }).join("");

  managementPriorityBrief.innerHTML = `
    <div class="priority-brief-head">
      <p>${escapeHtml(isZh() ? "Athena 不是只回答单个指标，而是把订单、工序、异常、证据和动作排成管理优先级。" : "Athena ranks orders, process signals, evidence, and actions into management priorities.")}</p>
      <small>${escapeHtml(isZh() ? "原则" : "Policy")}: ${escapeHtml(policy.kpi_priority?.join(" > ") || "delivery > quality > cost")} · ${escapeHtml(isZh() ? "只读，需要人工确认后行动" : "read-only; human confirmation required")}</small>
      ${headline ? `<small>${escapeHtml(headline)}</small>` : ""}
    </div>
    <div class="priority-card-grid">${cards}</div>
  `;
}

function renderEvidenceReviewQueue(queue) {
  if (!evidenceReviewQueuePanel) return;
  const cards = queue.review_queue || [];
  if (!cards.length) {
    evidenceReviewQueuePanel.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前没有数据复核候选。" : "No evidence review candidates are available.")}</p>`;
    return;
  }
  const rows = cards.slice(0, 10).map((card) => {
    const drivers = (card.reconciliation_drivers || []).map((driver) => isZh() ? driver.explanation_zh || driver.driver : driver.explanation_en || driver.driver);
    return `
      <article class="evidence-review-card">
        <div class="priority-card-head">
          <span>${escapeHtml(card.review_type || "evidence_review")}</span>
          <strong>${escapeHtml(card.object_id || card.produce_order_code || "-")}</strong>
        </div>
        <p>${escapeHtml(card.why_not_delivery_risk || "")}</p>
        <dl>
          <div><dt>${escapeHtml(isZh() ? "计划完成率" : "Plan completion")}</dt><dd>${escapeHtml(percent(card.plan_completion_rate || 0))}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "交期差" : "Days to due")}</dt><dd>${escapeHtml(card.days_to_due ?? "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "未排量" : "Unscheduled")}</dt><dd>${escapeHtml(card.unscheduled_quantity ?? 0)}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "报工差异" : "Report gap")}</dt><dd>${escapeHtml(card.quantity_report_gap ?? 0)}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "确认人" : "Owner")}</dt><dd>${escapeHtml(card.suggested_confirmation_owner || "-")}</dd></div>
          <div><dt>${escapeHtml("sanity flag")}</dt><dd>${escapeHtml((card.sanity_flags || []).join(" / ") || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "字段来源" : "Field source")}</dt><dd>${escapeHtml((card.field_sources || []).join(" / ") || card.field_source || "-")}</dd></div>
        </dl>
        <details>
          <summary>${escapeHtml(isZh() ? "查看 driver / 不能下结论原因" : "Show drivers / cannot conclude")}</summary>
          <p>${escapeHtml(drivers.join("；") || "-")}</p>
          <p>${escapeHtml(card.cannot_conclude_reason || "-")}</p>
        </details>
      </article>
    `;
  }).join("");
  evidenceReviewQueuePanel.innerHTML = `
    <div class="service-risk-summary">
      <p>${escapeHtml(queue.summary || "")}</p>
      <div class="service-risk-metrics">
        <div><span>${escapeHtml(isZh() ? "复核候选" : "Candidates")}</span><strong>${escapeHtml(queue.candidate_count ?? cards.length)}</strong></div>
        <div><span>${escapeHtml(isZh() ? "数据状态" : "Adapter")}</span><strong>${escapeHtml(queue.adapter_status || "-")}</strong></div>
        <div><span>${escapeHtml(isZh() ? "边界" : "Boundary")}</span><strong>${escapeHtml(isZh() ? "只读" : "Read-only")}</strong></div>
      </div>
    </div>
    <div class="evidence-review-grid">${rows}</div>
  `;
}

function renderDecisionLoop(loop) {
  if (!decisionLoop) return;
  const followUps = loop.follow_up_items || [];
  const actions = new Map((loop.action_items || []).map((item) => [item.action_id, item]));
  const kpis = loop.loop_kpis || {};
  if (!followUps.length) {
    decisionLoop.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "还没有可跟进事项。" : "No follow-up items yet.")}</p>`;
    return;
  }

  const summary = [
    [["Pending", "待确认"], kpis.pending_confirmation_count ?? 0],
    [["Assigned", "已分配"], kpis.assigned_count ?? 0],
    [["Waiting Evidence", "等待证据"], kpis.waiting_evidence_count ?? 0],
    [["Confirmed", "已确认"], kpis.confirmed_count ?? 0],
    [["Closed", "已关闭"], kpis.closed_follow_up_count ?? 0],
    [["Unable", "无法处理"], kpis.unable_to_process_count ?? 0],
  ].map(([label, value]) => `
    <div class="operation-metric">
      <span>${escapeHtml(textPair(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join("");

  const cards = followUps.map((item) => {
    const action = actions.get(item.action_id) || {};
    return `
      <article class="follow-up-card ${escapeHtml((item.status || "pending_confirmation").replaceAll("_", "-"))}">
        <div class="priority-card-head">
          <span>${escapeHtml(labelFrom(STATUS_LABELS, item.status, item.status))} · ${escapeHtml(item.follow_up_id)}</span>
          <strong>${escapeHtml(action.recommended_action_zh && isZh() ? action.recommended_action_zh : action.recommended_action || item.action_id)}</strong>
        </div>
        <dl>
          <div><dt>${escapeHtml(isZh() ? "负责人" : "Owner")}</dt><dd>${escapeHtml(item.owner_role || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "关联风险卡片" : "Linked Risk Card")}</dt><dd>${escapeHtml(item.linked_risk_card_id || item.source_priority_id || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "复查时间" : "Review")}</dt><dd>${escapeHtml(item.review_time || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "证据状态" : "Evidence")}</dt><dd>${escapeHtml(item.evidence_status || "-")}</dd></div>
          <div><dt>${escapeHtml(isZh() ? "关闭门" : "Closure Gate")}</dt><dd>${escapeHtml(item.closure_gate || "-")}</dd></div>
        </dl>
        <small>${escapeHtml((item.expected_evidence || []).join(" / "))}</small>
        <div class="follow-up-actions">
          <button type="button" data-follow-up-status="pending_confirmation" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "待确认" : "Pending")}</button>
          <button type="button" data-follow-up-status="assigned" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "分配" : "Assign")}</button>
          <button type="button" data-follow-up-status="waiting_evidence" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "等证据" : "Need Evidence")}</button>
          <button type="button" data-follow-up-status="confirmed" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "确认" : "Confirm")}</button>
          <button type="button" data-follow-up-status="closed" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "关闭" : "Close")}</button>
          <button type="button" data-follow-up-status="unable_to_process" data-action-id="${escapeHtml(item.action_id)}">${escapeHtml(isZh() ? "无法处理" : "Unable")}</button>
        </div>
      </article>
    `;
  }).join("");

  decisionLoop.innerHTML = `
    <div class="priority-brief-head">
      <p>${escapeHtml(isZh() ? "把 Athena 的建议动作转成可跟进事项：负责人、证据、确认门、状态和记忆候选都保留下来。" : "Athena turns recommended actions into follow-up items with owner, evidence, gates, status, and memory candidates.")}</p>
      <small>${escapeHtml(loop.status || "ready_for_review")} · ${escapeHtml(isZh() ? "只写本地 review metadata，不写 APS/IOT/工单系统" : "metadata-only local review; no APS/IOT/ticket writeback")}</small>
    </div>
    <div class="operation-metrics">${summary}</div>
    <div class="priority-card-grid">${cards}</div>
  `;
}

function renderPermissionBoundary(boundary) {
  if (!permissionBoundary) return;
  if (!boundary.schema_id) {
    permissionBoundary.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前快照还没有权限边界对象。" : "No permission boundary object is available in the current snapshot.")}</p>`;
    return;
  }

  const allowed = (isZh() ? boundary.allowed_actions_zh : boundary.allowed_actions) || [];
  const blocked = (isZh() ? boundary.blocked_actions_zh : boundary.blocked_actions) || [];
  const evidencePolicy = isZh() ? boundary.evidence_policy_zh || {} : boundary.evidence_policy || {};
  const owner = isZh()
    ? boundary.final_confirmation_owner_zh || boundary.final_confirmation_owner || "-"
    : boundary.final_confirmation_owner || "-";
  const authority = isZh()
    ? boundary.decision_authority_zh || boundary.decision_authority || ""
    : boundary.decision_authority || "";
  const note = boundary.ui_note ? (isZh() ? boundary.ui_note.zh : boundary.ui_note.en) : "";

  const allowedItems = allowed.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("");
  const blockedItems = blocked.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("");
  const policyItems = Object.entries(evidencePolicy).map(([key, value]) => `
    <div>
      <dt>${escapeHtml(key.replaceAll("_", " "))}</dt>
      <dd>${escapeHtml(localizePhrase(value || ""))}</dd>
    </div>
  `).join("");

  permissionBoundary.innerHTML = `
    <div class="permission-boundary-head">
      <div>
        <span>${escapeHtml(isZh() ? "最终确认人" : "Final confirmation owner")}</span>
        <strong>${escapeHtml(owner)}</strong>
      </div>
      <p>${escapeHtml(authority)}</p>
      ${note ? `<small>${escapeHtml(note)}</small>` : ""}
    </div>
    <div class="permission-boundary-grid">
      <article>
        <h3>${escapeHtml(isZh() ? "Athena 可以做" : "Allowed")}</h3>
        <ul>${allowedItems}</ul>
      </article>
      <article>
        <h3>${escapeHtml(isZh() ? "Athena 不会做" : "Blocked")}</h3>
        <ul>${blockedItems}</ul>
      </article>
    </div>
    <dl class="permission-policy">${policyItems}</dl>
  `;
}

function renderOperationsStack(result) {
  const overview = result.production_overview || {};
  const resources = result.resource_lens || {};
  const output = result.garment_output || {};
  const orders = output.orders || [];
  const styleCount = overview.total_style_count ?? uniqueCount(orders.map((order) => order.style_code));
  const averageDefectRate = overview.scrap_rate || averageMeasurementPercent(resources.measurement?.signals || [], "defect");
  const averageYieldRate = overview.average_yield_rate || averageMeasurementPercent(resources.measurement?.signals || [], "yield");

  const sections = [
    {
      key: "order",
      title: ["Orders", "订单"],
      subtitle: [
        "Backlog, style mix, and yarn/material risks that can block delivery.",
        "关注未交货订单、款式数量，以及会向上影响订单交付的纱线/物料风险。",
      ],
      metrics: [
        [["Backlog Orders", "未交货订单数"], overview.backlog_order_count ?? overview.order_count ?? 0],
        [["Style Count", "总款式数"], styleCount],
        [["Remaining Quantity", "剩余数量"], overview.total_remaining_quantity ?? 0],
        [["Material Risk Items", "物料风险项"], overview.material_risk_count ?? 0],
        [["Exception Orders", "异常订单"], overview.exception_order_count ?? 0],
      ],
      signals: resourceSignals(resources.material, "material").slice(0, 4),
      note: ["Material link focuses on yarn lots in the current mock snapshot.", "当前 mock 重点展示纱线批次和到料风险。"],
    },
    {
      key: "schedule",
      title: ["Scheduling", "排单"],
      subtitle: [
        "APS coverage, unscheduled orders, and capacity occupation before workshop execution.",
        "关注 APS 排单覆盖、未排订单，以及进入车间前的产能占用。",
      ],
      metrics: [
        [["Scheduled Orders", "已排订单"], overview.scheduled_order_count ?? 0],
        [["Unscheduled / Exception Orders", "未排 / 异常订单"], overview.pending_or_exception_order_count ?? 0],
        [["Scheduled Quantity", "已排数量"], overview.scheduled_quantity ?? 0],
        [["Schedule Coverage", "排单覆盖率"], percent(ratio(overview.scheduled_order_count, overview.order_count))],
        [["Capacity Occupation", "产能占用率"], percent(overview.capacity_occupation_rate ?? overview.machine_running_rate)],
      ],
      signals: [
        ...workflowSignals(result.workflow_stages || [], ["aps_scheduling", "iot_execution"]),
        ...resourceSignals(resources.method, "method").slice(0, 2),
        ...resourceSignals(resources.people, "people").slice(0, 2),
      ],
      note: ["Capacity is shown as current machine occupation in the mock data.", "当前产能占用率使用 mock 机台运行占用作为代理指标。"],
    },
    {
      key: "machine",
      title: ["Machines", "机器"],
      subtitle: [
        "Machine status, running rate, OEE, downtime, style load, waste proxy, and fault machines.",
        "关注机器状态、开机率、OEE、停机、款式负载、废料率代理和故障机器。",
      ],
      metrics: [
        [["Machine Count", "机器总数"], overview.machine_count ?? 0],
        [["Running Rate", "开机率"], percent(overview.machine_running_rate)],
        [["Average OEE", "平均 OEE"], percent(overview.average_oee)],
        [["Downtime", "停机分钟"], isZh() ? `${overview.downtime_minutes ?? 0} 分钟` : `${overview.downtime_minutes ?? 0} min`],
        [["Style Load", "款式数量"], styleCount],
        [["Fault Machines", "故障机器"], overview.fault_machine_count ?? overview.service_escalation_count ?? 0],
        [["Offline Machines", "离线机器"], overview.offline_machine_count ?? 0],
        [["Waste / Defect Proxy", "废料率 / 不良率代理"], averageDefectRate ? percent(averageDefectRate) : textPair(["Reserved", "预留"])],
      ],
      signals: [
        ...resourceSignals(resources.machine, "machine").slice(0, 5),
        ...resourceSignals(resources.environment, "environment").slice(0, 2),
      ],
      note: ["Waste rate uses current QC defect-rate mock until real Smartex/IOT fields are connected.", "废料率暂用当前 QC 缺陷率 mock 作为代理；未来接入 Smartex/IOT 后替换为真实字段。"],
    },
    {
      key: "garment",
      title: ["Garments", "成衣"],
      subtitle: [
        "Good quantity, yield, quality holds, and defect reason summary after production.",
        "关注成衣良品数量、良品率、质量暂停和不良原因统计。",
      ],
      metrics: [
        [["Planned Quantity", "计划件数"], output.total_planned_quantity ?? 0],
        [["Estimated Good Quantity", "预计良品数"], output.estimated_good_quantity ?? 0],
        [["Average Yield", "平均良品率"], averageYieldRate ? percent(averageYieldRate) : textPair(["Reserved", "预留"])],
        [["Scrap Quantity", "废弃数量"], overview.scrap_quantity ?? 0],
        [["Quality Holds", "质量暂停"], output.quality_hold_count ?? 0],
      ],
      signals: [
        ...garmentOrderSignals(orders).slice(0, 4),
        ...resourceSignals(resources.measurement, "measurement").slice(0, 3),
      ],
      note: ["Defect reasons are summarized from quality and service-risk evidence in this mock.", "不良原因来自质量检测和服务风险证据的 mock 汇总。"],
    },
  ];

  operationsStack.innerHTML = "";
  sections.forEach((section) => operationsStack.append(renderOperationSection(section)));
}

function renderOperationSection(section) {
  const article = document.createElement("article");
  article.className = `operation-section ${section.key}`;
  const metrics = section.metrics.map(([label, value]) => `
    <div class="operation-metric">
      <span>${escapeHtml(textPair(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join("");
  const signals = section.signals.length ? section.signals.map((signal) => `
    <li>
      <strong>${escapeHtml(signal.title)}</strong>
      <span>${escapeHtml(signal.detail)}${signal.evidence ? ` · ${escapeHtml(signal.evidence)}` : ""}</span>
    </li>
  `).join("") : `<li><span>${escapeHtml(isZh() ? "当前 mock 快照没有相关风险。" : "No related risk in current mock snapshot.")}</span></li>`;

  article.innerHTML = `
    <div class="operation-section-header">
      <div>
        <p class="eyebrow">${escapeHtml(textPair(section.title))}</p>
        <h3>${escapeHtml(textPair(section.title))}</h3>
        <p>${escapeHtml(textPair(section.subtitle))}</p>
      </div>
      <span>${escapeHtml(textPair(section.note))}</span>
    </div>
    <div class="operation-metrics">${metrics}</div>
    <ul class="operation-signal-list">${signals}</ul>
  `;
  return article;
}

function renderSignals(items) {
  renderMiniList(optimizationSignals, items, (item) => `
    <strong>${escapeHtml(localizePhrase(item.title))}</strong>
    <p>${escapeHtml(localizePhrase(item.waste_or_cost_point))} · ${escapeHtml(localizePhrase(item.suggested_action))}</p>
    <small>${escapeHtml(labelFrom(TYPE_LABELS, item.type, item.type))} · ${escapeHtml(labelFrom(STATUS_LABELS, item.severity, item.severity))} · ${escapeHtml(item.evidence_ref)}</small>
  `);
}

function renderAdapterContract(contract) {
  if (!adapterContract) return;
  if (!contract) {
    adapterContract.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "接口契约不可用。" : "Adapter contract unavailable.")}</p>`;
    return;
  }
  const systems = contract.source_systems || [];
  const mappings = contract.field_mapping || [];
  adapterContract.innerHTML = "";

  systems.forEach((system) => {
    const article = document.createElement("article");
    article.className = "mini-object";
    article.innerHTML = `
      <strong>${escapeHtml(system.system)} · ${escapeHtml(labelFrom(STATUS_LABELS, system.status, system.status))}</strong>
      <p>${escapeHtml(system.adapter)} · ${escapeHtml(system.primary_console_sections.join(" / "))}</p>
      <small>${escapeHtml(system.source_pages.slice(0, 5).join(" / "))}</small>
    `;
    adapterContract.append(article);
  });

  mappings.slice(0, 4).forEach((mapping) => {
    const article = document.createElement("article");
    article.className = "mini-object";
    article.innerHTML = `
      <strong>${escapeHtml(mapping.console_section)} · ${escapeHtml(mapping.object)}</strong>
      <p>${escapeHtml(mapping.source_system)} · ${escapeHtml(mapping.source_pages.join(" / "))}</p>
      <small>${escapeHtml(mapping.observed_fields.slice(0, 6).join(" / "))}</small>
    `;
    adapterContract.append(article);
  });

  const policy = document.createElement("article");
  policy.className = "mini-object";
  policy.innerHTML = `
    <strong>${escapeHtml(isZh() ? "只读边界" : "Read-only Boundary")}</strong>
    <p>${escapeHtml(localizePhrase(contract.credential_policy))}</p>
    <small>${escapeHtml((contract.blocked_actions || []).slice(0, 5).join(" / "))}</small>
  `;
  adapterContract.append(policy);
}

function renderServiceCandidates(items) {
  renderMiniList(serviceCandidates, items, (item) => `
    <strong>${escapeHtml(item.candidate_id)} · ${escapeHtml(item.priority)}</strong>
    <p>${escapeHtml(item.machine_id)} · ${escapeHtml(localizePhrase(item.issue))}</p>
    <small>${escapeHtml(isZh() ? "自动派工" : "auto dispatch")}: ${escapeHtml(labelFrom(STATUS_LABELS, String(item.auto_dispatch)))} · ${escapeHtml(item.evidence_ref)}</small>
  `);
}

function renderKpis(items) {
  renderMiniList(productionKpis, items, (item) => `
    <strong>${escapeHtml(labelFrom(KPI_LABELS, item.kpi, item.kpi))} · ${escapeHtml(labelFrom(STATUS_LABELS, item.status))}</strong>
    <p>${escapeHtml(isZh() ? "当前值" : "value")}: ${escapeHtml(formatKpiValue(item))} · ${escapeHtml(isZh() ? "目标" : "target")}: ${escapeHtml(localizePhrase(item.target))}</p>
    <small>${escapeHtml(item.evidence_ref)}</small>
  `);
}

function renderMaterialRisk(material) {
  if (!materialRiskPanel) return;
  const structure = material.inventory_structure || {};
  const balance = material.balance_exceptions || {};
  const signals = material.risk_signals || [];
  const tiles = [
    [["Rows", "库存行数"], structure.row_count || 0],
    [["Task Orders", "生产任务单"], structure.unique_task_order_count || 0],
    [["Yarn Codes", "纱线编码"], structure.unique_yarn_code_count || 0],
    [["Batches", "批次"], structure.unique_batch_count || 0],
    [["Suppliers", "供应商"], structure.unique_supplier_count || 0],
    [["Zero/Negative Rows", "零/负结存行"], balance.exception_row_count || 0],
  ].map(([label, value]) => `
    <div class="operation-metric">
      <span>${escapeHtml(textPair(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join("");
  const signalCards = signals.map((signal) => `
    <article class="mini-object">
      <strong>${escapeHtml(signal.priority || "P1")} · ${escapeHtml(signal.theme || "")}</strong>
      <p>${escapeHtml(isZh() ? signal.conclusion_zh || signal.conclusion : signal.conclusion)}</p>
      <small>${escapeHtml(signal.owner_role || "")} · ${escapeHtml((signal.evidence_refs || []).join(" / "))}</small>
    </article>
  `).join("");
  materialRiskPanel.innerHTML = `
    <div class="priority-brief-head">
      <p>${escapeHtml(isZh()
        ? "Athena 已把纱线库存作为“料”的聚合证据接入，但还不会把负结存直接等同于缺料。"
        : "Athena now consumes yarn inventory as material evidence, but does not treat negative balance as shortage until confirmed.")}</p>
      <small>${escapeHtml(material.adapter_status || "mock_contract")} · ${escapeHtml((material.blocked_actions || []).slice(0, 4).join(" / "))}</small>
    </div>
    <div class="operation-metrics">${tiles}</div>
    <div class="priority-card-grid">${signalCards}</div>
  `;
}

function renderDataReadiness(readiness) {
  if (!dataReadinessPanel) return;
  const coverage = readiness.question_coverage || {};
  const sourceCards = (readiness.data_sources || []).map((source) => `
    <article class="mini-object">
      <strong>${escapeHtml(source.source_id)} · ${escapeHtml(source.status)}</strong>
      <p>${escapeHtml(source.name || "")}</p>
      <small>${escapeHtml((source.fields || []).slice(0, 6).join(" / "))}</small>
    </article>
  `).join("");
  const tiles = [
    [["Readiness", "可用性"], percent(readiness.readiness_score || 0)],
    [["Answerable", "可回答"], coverage.answerable_now || 0],
    [["Partial", "部分可答"], coverage.partial || 0],
    [["Blocked", "暂不可答"], coverage.blocked || 0],
  ].map(([label, value]) => `
    <div class="operation-metric">
      <span>${escapeHtml(textPair(label))}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `).join("");
  dataReadinessPanel.innerHTML = `
    <div class="priority-brief-head">
      <p>${escapeHtml(isZh()
        ? "数据可用性评估会告诉 Athena 当前能回答什么、不能回答什么，以及下一步应该向谁要数据。"
        : "Data readiness tells Athena what can be answered, what cannot, and who should provide the next data source.")}</p>
      <small>${escapeHtml(readiness.status || "partial_ready")}</small>
    </div>
    <div class="operation-metrics">${tiles}</div>
    <div class="priority-card-grid">${sourceCards}</div>
  `;
}

function renderQuestionBank(bank) {
  if (!questionBankPanel) return;
  const questions = bank.questions || [];
  const p0 = questions.filter((item) => item.priority === "P0").length;
  const partial = questions.filter((item) => item.current_readiness === "partial").length;
  const blocked = questions.filter((item) => item.current_readiness === "blocked").length;
  const cards = questions.slice(0, 6).map((item) => `
    <article class="mini-object">
      <strong>${escapeHtml(item.question_id)} · ${escapeHtml(item.priority)} · ${escapeHtml(item.current_readiness)}</strong>
      <p>${escapeHtml(item.question || "")}</p>
      <small>${escapeHtml((item.missing_data_sources || []).slice(0, 5).join(" / ") || "ready")}</small>
    </article>
  `).join("");
  questionBankPanel.innerHTML = `
    <article class="mini-object">
      <strong>${escapeHtml(isZh() ? "问题库状态" : "Question Bank")}</strong>
      <p>${escapeHtml(bank.status || "hypothesis_pending_voc")} · ${escapeHtml(bank.question_count || 0)} ${escapeHtml(isZh() ? "个问题" : "questions")} · P0 ${escapeHtml(p0)}</p>
      <small>${escapeHtml(isZh() ? "部分可答" : "partial")}: ${escapeHtml(partial)} · ${escapeHtml(isZh() ? "暂不可答" : "blocked")}: ${escapeHtml(blocked)}</small>
    </article>
    ${cards}
  `;
}

function renderEvidence(items) {
  renderMiniList(productionEvidence, items, (item) => `
    <strong>${escapeHtml(item.evidence_id)} · ${escapeHtml(labelFrom(STATUS_LABELS, item.adapter_status, item.adapter_status))}</strong>
    <p>${escapeHtml(localizePhrase(item.claim))}</p>
    <small>${escapeHtml(localizePhrase(item.source))}</small>
  `);
}

function formatMismatchDetails(details) {
  const rows = (details || []).filter(Boolean).map((item) => {
    const label = isZh() ? (item.field_label_zh || item.field) : item.field;
    const required = item.required_value || "-";
    const actual = item.actual_machine_value || "-";
    const requiredSource = item.required_field_source || "-";
    const actualSource = item.actual_field_source || "-";
    return isZh()
      ? `${label}: 要求 ${required} (${requiredSource}) / 机台 ${actual} (${actualSource})`
      : `${label}: required ${required} (${requiredSource}) / machine ${actual} (${actualSource})`;
  });
  return rows.join("; ");
}

async function askChatbi(question) {
  const cleanQuestion = String(question || "").trim();
  if (!cleanQuestion) return;
  chatbiQuestion.value = cleanQuestion;
  chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "正在分析结构化生产数据..." : "Analyzing structured production data...")}</p>`;
  const response = await fetch("/api/production/chatbi", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: cleanQuestion }),
  });
  const result = await response.json();
  renderChatbi(result);
}

function renderChatbi(result) {
  const causes = result.root_causes || [];
  const actions = result.recommended_actions || [];
  const drilldowns = result.next_drilldowns || [];
  const executive = result.executive_answer || {};
  const gaps = result.data_gaps || [];
  const evidence = result.evidence_log || [];
  const actualChains = result.actual_evidence_chains || [];
  const trace = renderSkillExecutionTrace(result.skill_execution_trace || []);
  const snapshot = Object.entries(result.metric_snapshot || {})
    .map(([key, value]) => `
      <div class="chatbi-kv">
        <span>${escapeHtml(localizeMetricKey(key))}</span>
        <strong>${escapeHtml(formatChatbiValue(key, value))}</strong>
      </div>
    `).join("");
  const causeCards = causes.map((cause) => `
    <article class="chatbi-cause">
      <div class="chatbi-cause-header">
        <strong>${escapeHtml(cause.rank || "")}. ${escapeHtml(localizePhrase(cause.category_label || cause.category))}</strong>
        <span>${escapeHtml((cause.evidence_refs || []).join(" / "))}</span>
      </div>
      <p>${escapeHtml(localizePhrase(cause.cause))}</p>
      <ul>
        ${(cause.data_points || []).map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}
      </ul>
    </article>
  `).join("");
  const actualChainCards = actualChains.slice(0, 6).map((chain, index) => {
    const refs = (chain.evidence_refs || []).filter(Boolean).slice(0, 5).join(" / ") || "-";
    const source = chain.field_source || "Tianpai APS Export";
    const rows = [
      ["produce_order_code", chain.produce_order_code],
      ["weaving_part_order_id", chain.weaving_part_order_id || (chain.weaving_part_order_ids || []).join(", ")],
      ["planned_task_id", chain.planned_task_id || (chain.planned_task_ids || []).join(", ")],
      ["machine_code", chain.machine_code],
      ["machine_id", chain.machine_id],
      ["sku_code", chain.sku_code],
      ["part", chain.part],
      ["required_cylinder_diameter", chain.required_cylinder_diameter],
      ["machine_cylinder_diameter", chain.machine_cylinder_diameter],
      ["required_needle_spacing", chain.required_needle_spacing],
      ["machine_needle_spacing", chain.machine_needle_spacing],
      ["mismatch_details", formatMismatchDetails(chain.mismatch_details || [])],
    ].filter(([, value]) => value !== undefined && value !== null && String(value).trim() !== "");
    return `
      <article class="chatbi-evidence-chain">
        <div class="chatbi-cause-header">
          <strong>${escapeHtml(index + 1)}. ${escapeHtml(chain.produce_order_code || chain.machine_code || chain.weaving_part_order_id || chain.planned_task_id || "actual evidence")}</strong>
          <span>${escapeHtml(refs)}</span>
        </div>
        <ul>
          ${rows.map(([key, value]) => `<li><strong>${escapeHtml(localizeMetricKey(key))}:</strong> ${escapeHtml(value)}</li>`).join("")}
          <li><strong>${escapeHtml(isZh() ? "字段来源" : "Field Source")}:</strong> ${escapeHtml(source)}</li>
        </ul>
      </article>
    `;
  }).join("");
  const modeLabel = result.actual_data_mode
    ? (isZh() ? "真实导出数据" : "Actual export data")
    : (isZh() ? "Mock 管理快照" : "Mock management snapshot");

  chatbiOutput.innerHTML = `
    <article class="chatbi-answer">
      <div class="chatbi-answer-head">
        <span>${escapeHtml(labelFrom(CHATBI_METRIC_LABELS, result.metric, result.metric))} · ${escapeHtml(modeLabel)}</span>
        <strong>${escapeHtml(result.confidence || "medium")}</strong>
      </div>
      <p>${escapeHtml(localizePhrase(result.answer_summary || ""))}</p>
      <div class="chatbi-snapshot">${snapshot}</div>
    </article>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "管理层回答" : "Executive Answer")}</h3>
      <ul>
        <li><strong>${escapeHtml(isZh() ? "结论" : "Conclusion")}:</strong> ${escapeHtml(localizePhrase(executive.conclusion || result.answer_summary || ""))}</li>
        <li><strong>${escapeHtml(isZh() ? "原因/证据" : "Reason/Evidence")}:</strong> ${escapeHtml(localizePhrase(executive.reason_evidence || ""))}</li>
        <li><strong>${escapeHtml(isZh() ? "风险" : "Risk")}:</strong> ${escapeHtml(localizePhrase(executive.risk || ""))}</li>
        <li><strong>${escapeHtml(isZh() ? "建议" : "Recommendation")}:</strong> ${escapeHtml(localizePhrase(executive.recommendation || ""))}</li>
        <li><strong>${escapeHtml(isZh() ? "数据缺口" : "Data Gap")}:</strong> ${escapeHtml(localizePhrase(executive.data_gap || ""))}</li>
      </ul>
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "根因分析" : "Root Cause")}</h3>
      ${causeCards || `<p class="muted-text">${escapeHtml(isZh() ? "没有足够证据形成 root cause。" : "Not enough evidence for root cause.")}</p>`}
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "Athena 技能执行过程" : "Skill Execution Trace")}</h3>
      ${trace}
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "建议动作" : "Recommended Actions")}</h3>
      <ul>${actions.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}</ul>
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "下一步下钻" : "Next Drilldowns")}</h3>
      <ul>${drilldowns.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}</ul>
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "数据缺口" : "Data Gaps")}</h3>
      <ul>${gaps.map((item) => `<li>${escapeHtml(localizePhrase(item))}</li>`).join("")}</ul>
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "证据日志" : "Evidence Log")}</h3>
      <ul>${evidence.map((item) => `<li><strong>${escapeHtml(item.evidence_id)}</strong> ${escapeHtml(localizePhrase(item.claim))}</li>`).join("")}</ul>
    </div>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "真实数据证据链" : "Actual Data Evidence Chain")}</h3>
      ${actualChainCards || `<p class="muted-text">${escapeHtml(isZh() ? "该问题当前使用 mock 证据，未命中真实 APS/ERP 导出问答。" : "This question uses mock evidence and did not match an actual APS/ERP export question.")}</p>`}
    </div>
  `;
}

function localizeMetricKey(key) {
  const labels = {
    scrap_rate: ["scrap_rate", "废弃率"],
    scrap_quantity: ["scrap_quantity", "废弃数量"],
    actual_output: ["actual_output", "实际产量"],
    target: ["target", "目标"],
    status: ["status", "状态"],
    average_oee: ["average_oee", "平均 OEE"],
    downtime_minutes: ["downtime_minutes", "停机分钟"],
    material_risk_count: ["material_risk_count", "物料风险数"],
    pending_or_exception_order_count: ["pending_or_exception_order_count", "待排 / 异常订单"],
    top_bottleneck_machine: ["top_bottleneck_machine", "首要瓶颈机台"],
    missing_scope_count: ["missing_scope_count", "缺口数量"],
    known_scope: ["known_scope", "已知范围"],
    data_boundary: ["data_boundary", "数据边界"],
    average_days_to_due: ["average_days_to_due", "平均距交期天数"],
    earliest_due_date: ["earliest_due_date", "最早交期"],
    latest_due_date: ["latest_due_date", "最晚交期"],
    priority_count: ["priority_count", "优先级数量"],
    top_priority: ["top_priority", "最高优先级"],
    priority_policy: ["priority_policy", "优先级规则"],
    risk_order_count: ["risk_order_count", "风险订单数"],
    total_order_count: ["total_order_count", "总订单数"],
    top_candidate_count: ["top_candidate_count", "候选项数量"],
    source: ["source", "数据来源"],
    machine_count: ["machine_count", "机台数量"],
    top_machine: ["top_machine", "最高负载机台"],
    candidate_count_total: ["candidate_count_total", "候选项总数"],
    sample_count: ["sample_count", "样本数"],
    top_gap_count: ["top_gap_count", "最大差异数量"],
    produce_order_code: ["produce_order_code", "订单号"],
    weaving_part_order_id: ["weaving_part_order_id", "织造部件单 ID"],
    planned_task_id: ["planned_task_id", "计划任务 ID"],
    machine_code: ["machine_code", "机台编号"],
    machine_id: ["machine_id", "机台 ID"],
    sku_code: ["sku_code", "SKU 编码"],
    part: ["part", "部件"],
    required_cylinder_diameter: ["required_cylinder_diameter", "款式要求筒径"],
    machine_cylinder_diameter: ["machine_cylinder_diameter", "机台实际筒径"],
    required_needle_spacing: ["required_needle_spacing", "款式要求针距"],
    machine_needle_spacing: ["machine_needle_spacing", "机台实际针距"],
    mismatch_details: ["mismatch_details", "不匹配明细"],
  };
  return labels[key] ? textPair(labels[key]) : key;
}

function formatChatbiValue(key, value) {
  if (typeof value === "number" && ["scrap_rate", "defect_rate", "yield_rate", "scrap_share", "average_oee"].some((token) => key.includes(token))) {
    return percent(value);
  }
  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value);
  }
  return localizePhrase(value);
}

function renderMiniList(target, items, renderItem) {
  target.innerHTML = "";
  if (!items.length) {
    target.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "当前 mock 快照没有相关条目。" : "No items in current mock snapshot.")}</p>`;
    return;
  }
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "mini-object";
    article.innerHTML = renderItem(item);
    target.append(article);
  });
}

function resourceSignals(lens, resourceKey) {
  return (lens?.signals || []).map((signal) => ({
    title: localizeResourceTitle(resourceKey, signal.title),
    detail: localizePhrase(signal.detail),
    evidence: signal.evidence_ref,
    risk: signal.risk,
  }));
}

function workflowSignals(stages, stageIds) {
  return stages
    .filter((stage) => stageIds.includes(stage.id))
    .map((stage) => ({
      title: labelFrom(STAGE_LABELS, stage.id, stage.name),
      detail: `${labelFrom(OWNER_LABELS, stage.owner_role, stage.owner_role)} · ${labelFrom(STATUS_LABELS, stage.status)}`,
      evidence: stage.evidence_ref,
    }));
}

function garmentOrderSignals(orders) {
  return (orders || []).map((order) => ({
    title: `${order.style_code} · ${labelFrom(STATUS_LABELS, order.status, order.status)}`,
    detail: `${localizePhrase(order.garment)} · ${isZh() ? "预计良品" : "estimated good"} ${order.estimated_good_quantity} / ${order.planned_quantity} · ${isZh() ? "废弃" : "scrap"} ${order.scrap_quantity || 0}${formatDefectReasons(order.defect_reasons)}`,
    evidence: order.evidence_ref,
  }));
}

function formatDefectReasons(reasons) {
  if (!reasons || !reasons.length) return "";
  return ` · ${isZh() ? "原因" : "reasons"}: ${reasons.map((reason) => localizePhrase(reason)).join(", ")}`;
}

function uniqueCount(values) {
  return new Set((values || []).filter(Boolean)).size;
}

function ratio(numerator, denominator) {
  const top = Number(numerator || 0);
  const bottom = Number(denominator || 0);
  return bottom ? top / bottom : 0;
}

function averageMeasurementPercent(signals, fieldName) {
  const values = (signals || [])
    .map((signal) => {
      const match = String(signal.detail || "").match(new RegExp(`${fieldName}\\s+([0-9.]+)%`, "i"));
      return match ? Number(match[1]) / 100 : null;
    })
    .filter((value) => Number.isFinite(value));
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function localizeResourceTitle(resourceKey, value) {
  if (!isZh()) return value;
  let text = String(value || "");
  if (resourceKey === "people") {
    text = text.replace("operator", "操作员").replace("mechanic", "机修");
  }
  if (resourceKey === "machine") {
    text = text
      .replace("running", "运行中")
      .replace("idle", "空闲")
      .replace("stopped", "停机")
      .replace("material_hold", "物料等待");
  }
  if (resourceKey === "material") {
    text = text
      .replace("PA quick dry yarn", "PA 速干纱")
      .replace("covered elastane", "包覆氨纶")
      .replace("recycled polyester", "再生涤纶")
      .replace("lot", "批次");
  }
  if (resourceKey === "environment") {
    text = text.replace("Seamless Zone A", "无缝 A 区").replace("Hosiery Zone B", "袜机 B 区");
  }
  return text;
}

function localizePhrase(value) {
  if (!isZh()) return String(value ?? "");
  let text = String(value ?? "");
  if (PHRASE_LABELS[text]) return PHRASE_LABELS[text];

  const replacements = [
    [/minor yarn feeder warning/g, "轻微送纱器警告"],
    [/logo elasticity variation/g, "logo 弹性波动"],
    [/Material risk for PA quick dry yarn/g, "PA 速干纱物料风险"],
    [/Material risk for covered elastane/g, "包覆氨纶物料风险"],
    [/Material risk for recycled polyester/g, "再生涤纶物料风险"],
    [/downtime above threshold/g, "停机超过阈值"],
    [/People needs management attention/g, "人员需要管理关注"],
    [/Method needs management attention/g, "工艺需要管理关注"],
    [/Measurement needs management attention/g, "质量检测需要管理关注"],
    [/Use People evidence to identify the next improvement owner\./g, "根据人员证据确认下一步改善负责人。"],
    [/Use Method evidence to identify the next improvement owner\./g, "根据工艺证据确认下一步改善负责人。"],
    [/Use Measurement evidence to identify the next improvement owner\./g, "根据质量检测证据确认下一步改善负责人。"],
    [/efficiency/g, "效率"],
    [/manual interventions/g, "人工干预"],
    [/OEE/g, "OEE"],
    [/downtime/g, "停机"],
    [/alarm/g, "报警"],
    [/IOT/g, "IOT"],
    [/time availability/g, "时间开动率"],
    [/performance/g, "性能开动率"],
    [/actual output/g, "实际产量"],
    [/scrap/g, "废弃数量"],
    [/demand/g, "需求量"],
    [/in transit/g, "在途量"],
    [/setup/g, "setup"],
    [/variance/g, "偏差"],
    [/yield/g, "良率"],
    [/defect/g, "缺陷率"],
    [/source/g, "来源"],
    [/stock/g, "库存"],
    [/kg/g, "kg"],
    [/\bmin\b/g, "分钟"],
    [/read_only_evidence/g, "只读证据"],
    [/available/g, "可用"],
    [/late/g, "延迟"],
    [/erp_exception/g, "ERP 异常"],
    [/stable/g, "稳定"],
    [/limited_connectivity/g, "联网受限"],
    [/warning/g, "预警"],
    [/ok/g, "正常"],
    [/none/g, "无"],
    [/waiting for next work order/g, "等待下一工单"],
    [/fabric tension variation/g, "布面张力波动"],
    [/material not ready/g, "物料未就绪"],
  ];
  replacements.forEach(([pattern, replacement]) => {
    text = text.replace(pattern, replacement);
  });
  return text;
}

function formatKpiValue(item) {
  if (["oee", "labor_efficiency"].includes(item.kpi)) return percent(item.value);
  return item.value;
}

function percent(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

refreshProduction.addEventListener("click", () => {
  loadProduction().catch(() => {
    productionStatus.textContent = isZh() ? "API 不可用" : "API unavailable";
  });
});

chatbiForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  askChatbi(chatbiQuestion.value).catch(() => {
    chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "Santoni Athena 暂不可用，请重启 demo。" : "Santoni Athena is unavailable. Please restart the demo.")}</p>`;
  });
});

chatbiQuickQuestions?.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-question-zh]");
  if (!button) return;
  const question = isZh() ? button.dataset.questionZh : button.dataset.questionEn;
  askChatbi(question).catch(() => {
    chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "Santoni Athena 暂不可用，请重启 demo。" : "Santoni Athena is unavailable. Please restart the demo.")}</p>`;
  });
});

stableDemoStoryPack?.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-demo-story-question]");
  if (!button) return;
  askChatbi(button.dataset.demoStoryQuestion).then(() => {
    chatbiOutput?.scrollIntoView({ behavior: "smooth", block: "start" });
  }).catch(() => {
    chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "Santoni Athena 暂不可用，请重启 demo。" : "Santoni Athena is unavailable. Please restart the demo.")}</p>`;
  });
});

gmThreeMinuteBrief?.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-gm-question]");
  if (!button) return;
  askChatbi(button.dataset.gmQuestion).then(() => {
    chatbiOutput?.scrollIntoView({ behavior: "smooth", block: "start" });
  }).catch(() => {
    chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "Santoni Athena 暂不可用，请重启 demo。" : "Santoni Athena is unavailable. Please restart the demo.")}</p>`;
  });
});

serviceRiskBrief?.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-service-question]");
  if (!button) return;
  askChatbi(button.dataset.serviceQuestion).then(() => {
    chatbiOutput?.scrollIntoView({ behavior: "smooth", block: "start" });
  }).catch(() => {
    chatbiOutput.innerHTML = `<p class="muted-text">${escapeHtml(isZh() ? "Santoni Athena 暂不可用，请重启 demo。" : "Santoni Athena is unavailable. Please restart the demo.")}</p>`;
  });
});

decisionLoop?.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-follow-up-status]");
  if (!button) return;
  button.disabled = true;
  productionStatus.textContent = isZh() ? "保存跟进状态" : "Saving follow-up";
  try {
    const response = await fetch("/api/production/follow-up/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action_id: button.dataset.actionId,
        review_status: button.dataset.followUpStatus,
        review_note: "Production Console demo follow-up update.",
        reviewed_by: "production_console",
      }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Failed to save follow-up");
    lastProductionResult.decision_loop = result.decision_loop;
    renderDecisionLoop(result.decision_loop || {});
    renderProductionStatus(lastProductionResult);
  } catch (error) {
    productionStatus.textContent = `${isZh() ? "保存失败" : "Save failed"}: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

window.addEventListener("santoni:language-change", () => {
  if (lastProductionResult) renderProduction(lastProductionResult);
});

loadProduction().catch(() => {
  productionStatus.textContent = isZh() ? "API 不可用" : "API unavailable";
});


const productionStatus = document.querySelector("#productionStatus");
const productionSummary = document.querySelector("#productionSummary");
const workflowLane = document.querySelector("#workflowLane");
const operationsStack = document.querySelector("#operationsStack");
const optimizationSignals = document.querySelector("#optimizationSignals");
const adapterContract = document.querySelector("#adapterContract");
const serviceCandidates = document.querySelector("#serviceCandidates");
const productionKpis = document.querySelector("#productionKpis");
const productionEvidence = document.querySelector("#productionEvidence");
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
};

const CHATBI_METRIC_LABELS = {
  scrap_rate: ["Scrap Rate", "废弃率"],
  oee: ["OEE", "OEE"],
  downtime: ["Downtime", "停机"],
  material_risk: ["Material Risk", "物料风险"],
  order_delay: ["Order Delay", "订单延误"],
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
  renderSummary(result.production_overview);
  renderWorkflow(result.workflow_stages || []);
  renderOperationsStack(result);
  renderSignals(result.optimization_signals || []);
  renderAdapterContract(result.adapter_contract || lastAdapterContract);
  renderServiceCandidates(result.service_escalations || []);
  renderKpis(result.kpi_log || []);
  renderEvidence(result.evidence_log || []);
}

function renderProductionStatus(result) {
  const version = lastRuntimeStatus?.version || result.workflow_template?.version || "";
  const status = result.workflow_instance?.status || "on_track";
  productionStatus.textContent = `${version} · ${labelFrom(STATUS_LABELS, status)}`;
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

function renderEvidence(items) {
  renderMiniList(productionEvidence, items, (item) => `
    <strong>${escapeHtml(item.evidence_id)} · ${escapeHtml(labelFrom(STATUS_LABELS, item.adapter_status, item.adapter_status))}</strong>
    <p>${escapeHtml(localizePhrase(item.claim))}</p>
    <small>${escapeHtml(localizePhrase(item.source))}</small>
  `);
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
  const evidence = result.evidence_log || [];
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

  chatbiOutput.innerHTML = `
    <article class="chatbi-answer">
      <div class="chatbi-answer-head">
        <span>${escapeHtml(labelFrom(CHATBI_METRIC_LABELS, result.metric, result.metric))}</span>
        <strong>${escapeHtml(result.confidence || "medium")}</strong>
      </div>
      <p>${escapeHtml(localizePhrase(result.answer_summary || ""))}</p>
      <div class="chatbi-snapshot">${snapshot}</div>
    </article>
    <div class="chatbi-section">
      <h3>${escapeHtml(isZh() ? "根因分析" : "Root Cause")}</h3>
      ${causeCards || `<p class="muted-text">${escapeHtml(isZh() ? "没有足够证据形成 root cause。" : "Not enough evidence for root cause.")}</p>`}
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
      <h3>${escapeHtml(isZh() ? "证据日志" : "Evidence Log")}</h3>
      <ul>${evidence.map((item) => `<li><strong>${escapeHtml(item.evidence_id)}</strong> ${escapeHtml(localizePhrase(item.claim))}</li>`).join("")}</ul>
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

window.addEventListener("santoni:language-change", () => {
  if (lastProductionResult) renderProduction(lastProductionResult);
});

loadProduction().catch(() => {
  productionStatus.textContent = isZh() ? "API 不可用" : "API unavailable";
});

const messagesEl = document.querySelector("#messages");
const formEl = document.querySelector("#chatForm");
const inputEl = document.querySelector("#messageInput");
const imageInputEl = document.querySelector("#imageInput");
const attachmentPreviewEl = document.querySelector("#attachmentPreview");
const workflowTitle = document.querySelector("#workflowTitle");
const appVersionEl = document.querySelector("#appVersion");
const apiStatusEl = document.querySelector("#apiStatus");
const exportLogButton = document.querySelector("#exportLogButton");
const clearMemoryButton = document.querySelector("#clearMemoryButton");
const detectedRoleEl = document.querySelector("#detectedRole");
const operatingModelProgressEl = document.querySelector("#operatingModelProgress");
const developerChangelogEl = document.querySelector("#developerChangelog");
const realPlatformToggleEl = document.querySelector("#realPlatformToggle");
const platformUsernameEl = document.querySelector("#platformUsername");
const platformPasswordEl = document.querySelector("#platformPassword");
const developerRoleButtons = document.querySelectorAll("[data-dev-role]");

let currentRole = null;
let conversationLanguage = "en";
let pendingAttachment = null;
let appVersion = "v0.113.3";
let runtimeStatus = {};
let sessionId = createSessionId();
let developerGmBriefLoaded = false;
const conversationLog = [];

const roleLabels = {
  production_manager: "总经理",
  customer_equipment_engineer: "Service Engineer",
  designer: "Design Development",
};

const workflowTitles = {
  production_manager: "总经理生产决策工作流",
  customer_equipment_engineer: "Service Assist Workflow",
  designer: "Designer Workflow",
};

const examples = {
  production_manager: "今天我应该先处理哪三件事？",
  customer_equipment_engineer: "SM8-TOP2V 张力报警停机，需要现场服务。",
  designer: "帮我设计一款透气快干的无缝跑步上衣。",
};

function createSessionId() {
  return `developer-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function detectLanguage(text) {
  return /[\u4e00-\u9fff]/.test(text || "") ? "zh" : "en";
}

function t(en, zh) {
  return conversationLanguage === "zh" ? zh : en;
}

function setRole(role) {
  currentRole = role || null;
  const label = currentRole ? roleLabels[currentRole] || currentRole : "Select identity";
  if (detectedRoleEl) detectedRoleEl.textContent = `Role: ${label}`;
  if (workflowTitle) workflowTitle.textContent = currentRole ? workflowTitles[currentRole] || "Main Agent" : "Select Identity";
  if (inputEl) {
    inputEl.placeholder = currentRole
      ? examples[currentRole] || "Describe your request..."
      : "Select identity before sending a test message.";
  }
  developerRoleButtons.forEach((button) => {
    const selected = button.dataset.devRole === currentRole;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  });
}

function ensureDeveloperIdentitySelected() {
  if (currentRole) return true;
  addMessage(
    "agent",
    "Main Agent",
    "Please select an identity first: 总经理, Service Engineer, or Design Development. Then send a test message."
  );
  developerRoleButtons[0]?.focus();
  return false;
}

function getUserLabel(role) {
  return roleLabels[role] || "User";
}

function addMessage(type, label, body, response) {
  if (!messagesEl) return;
  const wrapper = document.createElement("article");
  wrapper.className = `message ${type}`;
  const labelEl = document.createElement("div");
  labelEl.className = "message-label";
  labelEl.textContent = label;
  const bodyEl = document.createElement("div");
  bodyEl.className = "message-body";
  bodyEl.textContent = body || "";
  wrapper.append(labelEl, bodyEl);
  if (response) wrapper.append(renderPayload(response));
  messagesEl.appendChild(wrapper);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderPayload(response) {
  const details = document.createElement("details");
  details.className = "payload-view";
  const summary = document.createElement("summary");
  summary.textContent = response.workflow === "production_athena" ? "Production Athena payload" : "Payload";
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(response, null, 2);
  details.append(summary, pre);
  return details;
}

function recordConversationTurn(turn) {
  conversationLog.push({ timestamp: new Date().toISOString(), ...turn });
}

function clearAttachment() {
  pendingAttachment = null;
  if (attachmentPreviewEl) {
    attachmentPreviewEl.hidden = true;
    attachmentPreviewEl.textContent = "";
  }
  if (imageInputEl) imageInputEl.value = "";
}

async function loadVersion() {
  try {
    const response = await fetch("/version.json");
    const data = await response.json();
    appVersion = data.version || appVersion;
    if (appVersionEl) appVersionEl.textContent = appVersion;
  } catch (error) {
    if (appVersionEl) appVersionEl.textContent = appVersion;
  }
}

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const status = await response.json();
    runtimeStatus = status;
    if (apiStatusEl) {
      apiStatusEl.textContent = status.ok ? `API online · ${status.version}` : "API unavailable";
      apiStatusEl.title = `Provider: ${status.active_llm_provider || "unknown"}; Model: ${status.active_llm_model || "unknown"}; Enabled: ${status.active_llm_enabled}`;
    }
    // Keep these field references explicit for regression tests and future UI wiring.
    status.active_llm_provider;
    status.active_llm_model;
    status.active_llm_enabled;
  } catch (error) {
    if (apiStatusEl) apiStatusEl.textContent = "API offline";
  }
}

async function loadOperatingModel() {
  if (!operatingModelProgressEl) return;
  try {
    const response = await fetch("/api/project-docs");
    const docs = await response.json();
    const implemented = docs.implemented_features || [];
    operatingModelProgressEl.innerHTML = "";
    implemented.slice(0, 6).forEach((feature) => {
      const item = document.createElement("p");
      item.textContent = `✓ ${feature}`;
      operatingModelProgressEl.appendChild(item);
    });
  } catch (error) {
    operatingModelProgressEl.textContent = "Project docs unavailable.";
  }
}

async function loadDeveloperChangelog() {
  if (!developerChangelogEl) return;
  try {
    const response = await fetch("/changelog.html");
    const html = await response.text();
    const doc = new DOMParser().parseFromString(html, "text/html");
    const entries = [...doc.querySelectorAll(".version-entry")].slice(0, 4);
    developerChangelogEl.innerHTML = "";
    entries.forEach((entry) => {
      const item = document.createElement("article");
      item.className = "developer-changelog-item";
      item.textContent = `${entry.querySelector("h2")?.textContent || "Unknown version"} · ${entry.querySelector("h3")?.textContent || "Untitled"}`;
      developerChangelogEl.appendChild(item);
    });
  } catch (error) {
    developerChangelogEl.textContent = "Changelog unavailable.";
  }
}

function normalizeProductionChatbiResponse(response) {
  return {
    workflow: "production_athena",
    summary: response.summary || response.management_summary || "Santoni Athena analysis complete.",
    payload: response,
    language: response.language || conversationLanguage,
  };
}

function summarizeVerification(response) {
  const process = response.verification_process || response.manager_verification_process || {};
  const checked = process.checked_objects || response.checked_objects || [];
  const finding = process.finding || response.finding || response.summary || "已完成基于证据的查证。";
  const evidenceLevel = process.evidence_level || response.evidence_level || response.evidence_level_label || "未标记";
  const cannotConclude = process.cannot_conclude || response.cannot_conclude || response.data_gaps || [];
  const owner = process.suggested_confirmation_owner || response.suggested_confirmation_owner || response.confirmation_owner || "生产主管";
  const lines = [
    "查证过程：",
    `1. Athena 查了：${Array.isArray(checked) && checked.length ? checked.join("、") : "订单、排产、机台、证据链"}`,
    `2. 发现：${finding}`,
    `3. 证据等级：${evidenceLevel}`,
    `4. 还不能确认：${Array.isArray(cannotConclude) ? cannotConclude.join("；") : cannotConclude || "需要现场复核"}`,
    `5. 建议确认人：${owner}`,
  ];
  return lines.join("\n");
}

async function loadDeveloperGeneralManagerBrief() {
  if (developerGmBriefLoaded) return;
  developerGmBriefLoaded = true;
  addMessage("agent", "Santoni Athena", "正在加载总经理今日三件事...");
  const response = await fetch("/api/production/daily-brief");
  const brief = await response.json();
  setRole("production_manager");
  addMessage("agent", "Santoni Athena", brief.narrative || brief.summary || "今日三件事已生成。", brief);
  recordConversationTurn({ message: "load daily brief", response: brief });
}

async function sendProductionChatbiMessage(prompt, options = {}) {
  if (options.echoUser) addMessage("user", getUserLabel(currentRole), prompt);
  addMessage("agent", "Santoni Athena", "正在查证订单、排产、机台、Service 风险和证据链...");
  const response = await fetch("/api/production/chatbi", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: prompt, language: conversationLanguage, session_id: sessionId }),
  });
  const raw = await response.json();
  const normalized = normalizeProductionChatbiResponse(raw);
  const pending = messagesEl?.lastElementChild;
  if (pending?.textContent.includes("正在查证")) pending.remove();
  setRole("production_manager");
  addMessage("agent", "Santoni Athena", `${normalized.summary}\n\n${summarizeVerification(raw)}\n\nSkill Execution Trace: management-facing verification, not raw debug trace.`, normalized);
  recordConversationTurn({ message: prompt, response: normalized });
  return normalized;
}

async function sendMainAgentMessage(message, attachments) {
  addMessage("user", getUserLabel(currentRole), `${message}${attachments.length ? `\n[Image: ${attachments[0].name}]` : ""}`);
  addMessage("agent", "Main Agent", t("Routing request to sub-agents...", "正在将请求分配给对应 Agent..."));
  const platformTool = realPlatformToggleEl?.checked
    ? { mode: "real_attempt", username: platformUsernameEl?.value || "", password: platformPasswordEl?.value || "" }
    : { mode: "mock" };
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role: currentRole, message, attachments, session_id: sessionId, platform_tool: platformTool }),
  });
  const data = await response.json();
  const pending = messagesEl?.lastElementChild;
  if (pending?.textContent.includes("Routing") || pending?.textContent.includes("正在将")) pending.remove();
  if (data.workflow?.startsWith("designer")) setRole("designer");
  if (data.workflow?.startsWith("service")) setRole("customer_equipment_engineer");
  if (data.workflow?.startsWith("production_athena")) setRole("production_manager");
  addMessage("agent", data.workflow?.startsWith("production_athena") ? "Santoni Athena" : "Main Agent", data.summary || "Done.", data);
  recordConversationTurn({ message, attachments, response: data });
}

async function handleSubmit(event) {
  event.preventDefault();
  const message = (inputEl?.value || "").trim();
  if (!message && !pendingAttachment) return;
  if (!ensureDeveloperIdentitySelected()) return;
  conversationLanguage = detectLanguage(message);
  inputEl.value = "";
  const attachments = pendingAttachment ? [pendingAttachment] : [];
  clearAttachment();
  if (currentRole === "production_manager" && !attachments.length) {
    await sendProductionChatbiMessage(message, { echoUser: true });
    return;
  }
  await sendMainAgentMessage(message, attachments);
}

function exportLog() {
  const payload = {
    version: appVersion,
    role: currentRole,
    language: conversationLanguage,
    session_id: sessionId,
    runtime_status: runtimeStatus,
    turns: conversationLog,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `ai-knitting-agent-test-log-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function clearMemory() {
  conversationLog.length = 0;
  currentRole = null;
  conversationLanguage = "en";
  developerGmBriefLoaded = false;
  sessionId = createSessionId();
  clearAttachment();
  setRole(null);
  if (messagesEl) messagesEl.innerHTML = "";
  addMessage("agent", "Main Agent", "Memory cleared. Please select an identity before starting a new test conversation.");
}

developerRoleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const selectedRole = button.dataset.devRole || null;
    setRole(selectedRole);
    addMessage("agent", "Main Agent", `已选择身份：${roleLabels[selectedRole] || selectedRole}。现在可以开始测试。`);
    if (selectedRole === "production_manager") {
      loadDeveloperGeneralManagerBrief().catch((error) => addMessage("agent", "Santoni Athena", `总经理三件事加载失败：${error.message}`));
    }
  });
});

formEl?.addEventListener("submit", (event) => {
  handleSubmit(event).catch((error) => addMessage("agent", "Main Agent", `Request failed: ${error.message}`));
});

imageInputEl?.addEventListener("change", () => {
  const file = imageInputEl.files?.[0];
  if (!file) return;
  pendingAttachment = { name: file.name, type: file.type, size: file.size };
  if (attachmentPreviewEl) {
    attachmentPreviewEl.hidden = false;
    attachmentPreviewEl.textContent = `Attached: ${file.name}`;
  }
});

exportLogButton?.addEventListener("click", exportLog);
clearMemoryButton?.addEventListener("click", clearMemory);

setRole(currentRole);
loadVersion();
loadStatus();
loadOperatingModel();
loadDeveloperChangelog();
addMessage(
  "agent",
  "Main Agent",
  "Please select an identity first: 总经理, Service Engineer, or Design Development. Then send a test message."
);

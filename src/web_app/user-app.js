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

let userSessionId = createSessionId();
let currentRole = "auto";
let currentLanguage = "zh";
let pendingAttachment = null;
let platformCredentials = null;
let credentialResolver = null;
let activationToolContext = false;

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
  urgency: "紧急度",
  factory_location: "工厂位置",
  customer_contact: "联系人",
  online_steps_attempted: "已尝试步骤",
  suggested_steps: "建议步骤",
  safety_warnings: "安全提醒",
  dispatch_triggers: "派工触发条件",
  recommended_parts: "建议备件",
  matched_case_title: "匹配案例",
  activation_password: "激活密码",
  status: "状态",
};

function createSessionId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID();
  return `user-${Date.now()}-${Math.random().toString(16).slice(2)}`;
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
  } else if (response.follow_up_questions?.length) {
    appendCard(cards, "需要确认", { follow_up_questions: response.follow_up_questions });
  }

  if (cards.childElementCount) fragment.append(cards);
  return fragment;
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
  if (Array.isArray(value)) return value.join("；");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .filter(([, item]) => item !== null && item !== undefined && item !== "")
      .map(([key, item]) => `${labels[key] || key}: ${Array.isArray(item) ? item.join("，") : item}`)
      .join("；");
  }
  return String(value);
}

async function submitMessage(message) {
  const attachments = pendingAttachment ? [pendingAttachment] : [];
  const attachmentLabel = pendingAttachment ? `\n[图片：${pendingAttachment.name}]` : "";
  const platformTool = await platformToolForMessage(message);
  addBubble("user", `${message || "请看我上传的图片"}${attachmentLabel}`);

  const loading = document.createElement("article");
  loading.className = "user-bubble agent loading";
  loading.innerHTML = "<p>正在分析，请稍候...</p>";
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
  currentLanguage = response.language || currentLanguage;
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
  return activationToolContext && /top2|serial|序列号|机型|型号|machine\s*code|机器码|activation|激活|password|密码|unlock|解锁|lock|锁|\d{6,}/i.test(text);
}

function isActivationCredentialIntent(message) {
  const text = String(message || "").toLowerCase();
  const hasTop2Activation = /top2/i.test(text) && /activation|password|code|machine\s*code|lock|locked|unlock|激活|密码|机器码|锁定|解锁|锁机/.test(text);
  const hasDirectActivationTask = /activation\s*(password|code)|machine\s*code|unlock\s*(the\s*)?machine|machine\s*(is\s*)?locked|locked\s*machine|generate\s*(an?\s*)?(activation\s*)?password|激活密码|激活码|机器码|解锁机器|机器.*锁|锁机|生成密码|获取密码/.test(text);
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
  userInputEl.value = "";
  try {
    await submitMessage(message);
  } catch {
    addBubble("agent", "服务暂时没有连接，请确认本地 demo server 正在运行。");
  }
});

document.querySelectorAll(".quick-actions button").forEach((button) => {
  button.addEventListener("click", () => {
    userInputEl.value = button.dataset.prompt || "";
    userInputEl.focus();
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
  currentRole = "auto";
  platformCredentials = null;
  activationToolContext = false;
  userMessagesEl.innerHTML = "";
  clearAttachment();
  addBubble("agent", "已开始新的对话。请告诉我您的需求。");
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
  userAttachmentPreviewEl.textContent = `${file.name} · ${Math.round(file.size / 1024)} KB`;
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
    userStatusEl.textContent = status.version || "Connected";
  } catch {
    userStatusEl.textContent = "Offline";
  }
}

loadStatus();
addBubble("agent", "您好。请直接描述您的设计需求或设备问题，我会帮您一步步确认信息。");

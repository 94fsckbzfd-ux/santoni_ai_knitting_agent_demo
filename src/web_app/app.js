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
const realPlatformToggleEl = document.querySelector("#realPlatformToggle");
const platformUsernameEl = document.querySelector("#platformUsername");
const platformPasswordEl = document.querySelector("#platformPassword");

let currentRole = "auto";
let currentLanguage = "en";
let pendingAttachment = null;
let appVersion = "v0.19.4";
let runtimeStatus = {};
let sessionId = createSessionId();
const conversationLog = [];

const examples = {
  designer: "I want to design a seamless running top for Decathlon women runners. It should be breathable, lightweight, quick dry, and have ventilation zones under the arms.",
  customer_equipment_engineer: "Our SM8-TOP2V machine has stopped with yarn tension alarm during production. We need onsite service today and may need spare parts.",
};

function setRole(role) {
  currentRole = role;
  const label = role === "customer_equipment_engineer" ? "Equipment Engineer" : role === "designer" ? "Designer" : "Auto";
  detectedRoleEl.textContent = `Role: ${label}`;
  workflowTitle.textContent = role === "designer" ? "Designer Workflow" : role === "customer_equipment_engineer" ? "Service Assist Workflow" : "Main Agent";
  inputEl.placeholder = examples[role] || "Tell me who you are and what you need. Example: I am a designer... / My machine stopped...";
}

function addMessage(type, label, body, response) {
  const wrapper = document.createElement("article");
  wrapper.className = `message ${type}`;

  const labelEl = document.createElement("div");
  labelEl.className = "message-label";
  labelEl.textContent = label;
  wrapper.append(labelEl);

  const bodyEl = document.createElement("p");
  bodyEl.className = "message-body";
  bodyEl.textContent = body;
  wrapper.append(bodyEl);

  if (response) {
    wrapper.append(renderResponse(response));
  }

  messagesEl.append(wrapper);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderResponse(response) {
  const fragment = document.createDocumentFragment();
  const grid = document.createElement("div");
  grid.className = "result-grid";
  currentLanguage = response.language || currentLanguage;

  if (response.workflow === "chat") {
    return fragment;
  }

  if (response.workflow === "designer_discovery") {
    grid.append(
      renderCard(t("Text Understanding", "文本理解"), response.payload.understanding),
      renderCard(t("Known Information", "已知信息"), response.payload.known_info),
      renderCard(t("Missing Information", "缺失信息"), { missing_info: response.payload.missing_info })
    );
  } else if (response.workflow === "service_assist") {
    grid.append(
      renderCard(t("Text Understanding", "文本理解"), response.payload.understanding),
      renderCard(t("Known Information", "已知信息"), response.payload.known_info),
      renderCard(t("Online Assist", "在线协助"), response.payload.online_assist),
      renderCard(t("Missing Information", "缺失信息"), { missing_info: response.payload.missing_info })
    );
  } else if (response.workflow === "designer") {
    const cards = [];
    if (response.payload.image_understanding) {
      cards.push(renderCard(t("Image Understanding", "图片理解"), response.payload.image_understanding));
    }
    if (response.payload.understanding) {
      cards.push(renderCard(t("Text Understanding", "文本理解"), response.payload.understanding));
    }
    cards.push(
      renderCard(t("Translation Agent", "需求转译 Agent"), response.payload.design_spec),
      renderCard(t("Digital Twin Agent", "数字孪生 Agent"), response.payload.digital_twin)
    );
    grid.append(...cards);
  } else if (response.workflow === "service") {
    const { image_understanding: imageUnderstanding, understanding, ...servicePayload } = response.payload;
    if (imageUnderstanding) {
      grid.append(renderCard(t("Image Understanding", "图片理解"), imageUnderstanding));
    }
    if (understanding) {
      grid.append(renderCard(t("Text Understanding", "文本理解"), understanding));
    }
    grid.append(renderCard(t("Service Dispatch Agent", "服务派工 Agent"), servicePayload));
  } else {
    grid.append(renderCard(t("Clarification", "澄清问题"), response.payload));
  }

  fragment.append(grid);

  if (response.follow_up_questions?.length) {
    const list = document.createElement("ul");
    list.className = "follow-ups";
    response.follow_up_questions.forEach((question) => {
      const item = document.createElement("li");
      item.textContent = question;
      list.append(item);
    });
    fragment.append(list);
  }

  return fragment;
}

function renderCard(title, data) {
  const card = document.createElement("section");
  card.className = "result-card";

  const heading = document.createElement("h3");
  heading.textContent = title;
  card.append(heading);

  const list = document.createElement("dl");
  Object.entries(data || {}).forEach(([key, value]) => {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = formatKey(key);
    description.textContent = formatValue(value);
    row.append(term, description);
    list.append(row);
  });

  card.append(list);
  return card;
}

function formatKey(key) {
  if (currentLanguage === "zh") {
    const zhLabels = {
      product_category: "产品品类",
      style_direction: "风格方向",
      yarn: "纱线建议",
      knit_structure: "组织结构",
      machine: "推荐机型",
      source_brief: "原始需求",
      sws_project_id: "SWS 项目编号",
      preview: "3D 预览",
      parameter_package: "参数包",
      gauge: "针距",
      structure: "结构",
      estimated_sample_time: "预计打样时间",
      estimated_unit_cost: "预计单件成本",
      estimated_yield: "预计良率",
      risks: "风险提示",
      ticket_id: "工单编号",
      issue_category: "问题类型",
      priority: "优先级",
      assigned_engineer: "派发工程师",
      recommended_parts: "建议备件",
      eta: "预计到场时间",
      status: "工单状态",
      dispatch_rationale: "派工理由",
      source_issue: "原始问题",
      image_count: "图片数量",
      primary_image: "主要图片",
      image_type: "图片类型",
      detected_signals: "识别线索",
      workflow_hint: "流程判断",
      confidence: "置信度",
      case_database_status: "案例库状态",
      matched_case_id: "匹配案例",
      tool_candidate: "候选工具",
      tool_status: "工具状态",
      tool_result: "工具结果",
      mode: "模式",
      login_url: "登录地址",
      discovered_fields: "识别字段",
      login_fields: "登录页字段",
      post_login_summary: "登录后页面摘要",
      page_title: "页面标题",
      safe_links: "安全链接",
      matched_terms: "匹配关键词",
      input_count: "输入框数量",
      safe_input_names: "字段名",
      activation_password: "激活密码",
      lease_password: "激活密码",
      lease_status: "租赁状态",
      lease_expiry_date: "租赁到期日期",
      reason: "原因",
      required_inputs: "所需输入",
      manual_escalation_triggers: "人工升级条件",
      suggested_steps: "建议步骤",
      image_reference: "图片参考",
      image_evidence: "图片证据",
      parser_status: "解析状态",
      reasoning_status: "推理状态",
      parser_error: "解析错误",
      target_user: "目标用户",
      use_case: "使用场景",
      style_keywords: "风格关键词",
      functional_requirements: "功能需求",
      material_preferences: "材料偏好",
      constraints: "限制条件",
      missing_info: "缺失信息",
      language: "语言",
      machine_model: "机器型号",
      serial_number: "序列号",
      machine_code: "机器码",
      symptoms: "故障现象",
      alarm_info: "报警信息",
      production_status: "生产状态",
      urgency: "紧急度",
      onsite_required: "是否需要现场服务",
      parts_clues: "备件线索",
      evidence_status: "证据状态",
      factory_location: "工厂位置",
      customer_contact: "客户联系人",
      online_steps_attempted: "已尝试在线排查",
      recommendation_reasoning: "推荐理由",
      next_actions: "下一步动作",
      customer_message: "客户回复",
      question: "问题",
    };
    if (zhLabels[key]) return zhLabels[key];
  }

  return key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatValue(value) {
  if (Array.isArray(value)) return value.join("; ");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${formatKey(key)}: ${item}`)
      .join("; ");
  }
  return String(value);
}

function detectLanguage(text) {
  return /[\u4e00-\u9fff]/.test(text || "") ? "zh" : "en";
}

function t(english, chinese) {
  return currentLanguage === "zh" ? chinese : english;
}

async function sendMessage(message) {
  currentLanguage = detectLanguage(message);
  const attachments = pendingAttachment ? [pendingAttachment] : [];
  const attachmentText = pendingAttachment ? `\n[Image: ${pendingAttachment.name}]` : "";
  addMessage("user", currentRole === "designer" ? "Designer" : currentRole === "customer_equipment_engineer" ? "Customer Equipment Engineer" : "User", `${message}${attachmentText}`);
  addMessage("agent", "Main Agent", t("Routing request to sub-agents...", "正在将请求分配给对应子 Agent..."));

  const pending = messagesEl.lastElementChild;

  const result = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role: currentRole, message, attachments, session_id: sessionId, platform_tool: getPlatformToolSettings() }),
  });

  const response = await result.json();
  pending.remove();
  if (response.workflow?.startsWith("designer")) setRole("designer");
  if (response.workflow?.startsWith("service")) setRole("customer_equipment_engineer");
  addMessage("agent", "Main Agent", response.summary || "Done.", response);
  recordConversationTurn({ message, attachments, response });
  clearAttachment();
}

function getPlatformToolSettings() {
  if (!realPlatformToggleEl?.checked) {
    return { mode: "mock" };
  }
  return {
    mode: "real_attempt",
    credentials: {
      username: platformUsernameEl.value,
      password: platformPasswordEl.value,
    },
  };
}

function recordConversationTurn({ message, attachments, response }) {
  conversationLog.push({
    timestamp: new Date().toISOString(),
    version: appVersion,
    role: currentRole,
    language: response?.language || currentLanguage,
    user_message: message,
    attachments: attachments.map((attachment) => ({
      name: attachment.name,
      type: attachment.type,
      size: attachment.size,
    })),
    agent_response: response,
  });
}

exportLogButton.addEventListener("click", () => {
  const exportPayload = {
    exported_at: new Date().toISOString(),
    app: "Santoni AI Knitting Agent Demo",
    version: appVersion,
    runtime_status: runtimeStatus,
    session_id: sessionId,
    current_role: currentRole,
    turn_count: conversationLog.length,
    turns: conversationLog,
  };

  const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const timestamp = new Date().toISOString().replaceAll(":", "-").slice(0, 19);
  link.href = url;
  link.download = `ai-knitting-agent-test-log-${timestamp}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});

clearMemoryButton.addEventListener("click", async () => {
  try {
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
  } catch {
    // The local UI can still reset even if the backend is not reachable.
  }
  resetLocalConversation();
});

imageInputEl.addEventListener("change", async () => {
  const file = imageInputEl.files?.[0];
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

  attachmentPreviewEl.hidden = false;
  attachmentPreviewEl.textContent = `${file.name} · ${Math.round(file.size / 1024)} KB`;
});

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message && !pendingAttachment) return;

  inputEl.value = "";
  try {
    await sendMessage(message);
  } catch (error) {
    addMessage(
      "agent",
      "Main Agent",
      t(
        "Backend is not reachable. Please keep the local demo server running with: python scripts/run_web_demo.py",
        "后端服务未连接。请保持本地服务运行：python scripts/run_web_demo.py"
      )
    );
  }
});

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function clearAttachment() {
  pendingAttachment = null;
  imageInputEl.value = "";
  attachmentPreviewEl.hidden = true;
  attachmentPreviewEl.textContent = "";
}

function createSessionId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function resetLocalConversation() {
  sessionId = createSessionId();
  conversationLog.length = 0;
  currentRole = "auto";
  currentLanguage = "en";
  clearAttachment();
  setRole("auto");
  messagesEl.innerHTML = "";
  addMessage(
    "agent",
    "Main Agent",
    "Memory cleared. Start a new test conversation."
  );
}

setRole(currentRole);
loadVersion();
loadStatus();
loadOperatingModel();
addMessage(
  "agent",
  "Main Agent",
  "Tell me who you are and what you need: a knitting design brief, reference image, or machine service issue. I will route the request to the correct sub-agents."
);

async function loadVersion() {
  try {
    const response = await fetch(`/version.json?ts=${Date.now()}`);
    const versionInfo = await response.json();
    appVersion = versionInfo.version;
    appVersionEl.textContent = versionInfo.version;
  } catch {
    appVersionEl.textContent = appVersion;
  }
}

async function loadStatus() {
  try {
    const response = await fetch(`/api/status?ts=${Date.now()}`);
    const status = await response.json();
    runtimeStatus = status;
    if (status.version) {
      if (appVersion && appVersion !== status.version) {
        addMessage(
          "agent",
          "System",
          `Frontend ${appVersion} is connected to backend ${status.version}. Please restart the demo server before testing.`
        );
      }
      appVersion = status.version;
      appVersionEl.textContent = status.version;
    }
    if (status.llm_provider === "deepseek") {
      apiStatusEl.textContent = status.deepseek_key_configured ? `DeepSeek · ${status.deepseek_model}` : "Fallback Mode";
    } else {
      apiStatusEl.textContent = status.openai_key_configured ? `OpenAI · ${status.openai_model}` : "Fallback Mode";
    }
  } catch {
    runtimeStatus = { status: "unknown" };
    apiStatusEl.textContent = "Status Unknown";
  }
}

async function loadOperatingModel() {
  try {
    const response = await fetch(`/api/operating-model?ts=${Date.now()}`);
    const model = await response.json();
    operatingModelProgressEl.innerHTML = "";
    model.capabilities.forEach((capability) => {
      const item = document.createElement("section");
      item.className = "model-item";
      item.innerHTML = `
        <div class="model-item-header">
          <strong>${capability.name}</strong>
          <span class="model-status">${capability.status} · ${capability.progress}%</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:${capability.progress}%"></div></div>
        <p>${capability.next_step}</p>
      `;
      operatingModelProgressEl.append(item);
    });
  } catch {
    operatingModelProgressEl.innerHTML = "<p>Operating model status unavailable.</p>";
  }
}

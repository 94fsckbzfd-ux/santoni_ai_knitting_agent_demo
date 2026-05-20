"""Main Agent orchestration skeleton."""

from dataclasses import dataclass, field

from agent_core.agents.image_understanding_agent import ImageUnderstandingAgent
from agent_core.language import choose, detect_language
from agent_core.workflows.designer_workflow import DesignerWorkflow
from agent_core.workflows.service_workflow import ServiceWorkflow


@dataclass(frozen=True)
class AgentRequest:
    user_role: str
    message: str
    channel: str = "web"
    session_id: str = "demo-session"
    language: str = "auto"
    attachments: list[dict] = field(default_factory=list)
    platform_tool: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResponse:
    workflow: str
    summary: str
    payload: dict
    follow_up_questions: list[str] = field(default_factory=list)
    language: str = "en"


class MainAgent:
    """Routes user requests to the right MVP workflow."""

    DESIGN_KEYWORDS = [
        "design",
        "style",
        "fabric",
        "yarn",
        "sample",
        "garment",
        "knit",
        "seamless",
        "打版",
        "设计",
        "面料",
        "纱线",
        "样衣",
        "服装",
        "针织",
        "无缝",
        "透气",
        "瑜伽",
        "跑步",
        "袜",
    ]
    SERVICE_KEYWORDS = [
        "alarm",
        "install",
        "installation",
        "ticket",
        "repair",
        "maintenance",
        "service",
        "stopped",
        "broken",
        "down",
        "故障",
        "坏",
        "安装",
        "调试",
        "报修",
        "报警",
        "停机",
        "维修",
        "保养",
        "派工",
        "备件",
        "错花",
        "选针",
        "漏油",
        "油箱",
        "死机",
        "白屏",
        "显示屏",
        "触摸",
        "坏针",
        "打针",
        "撞针",
        "马达",
        "驱动器",
        "电子眼",
        "输纱器",
        "租赁",
        "租赁密码",
        "激活密码",
        "生成激活密码",
        "激活机器码",
        "锁机激活",
        "锁机",
        "机器锁定",
        "锁屏",
        "锁定",
        "解锁",
        "解锁机器",
        "机器码",
        "top2mp",
        "lease",
        "rental password",
        "activation password",
        "lock screen",
        "machine is locked",
        "machine locked",
        "locked machine",
        "machine lock",
        "unlock machine",
        "unlock the machine",
    ]
    DESIGN_ROLE_KEYWORDS = ["设计师", "designer", "brand", "品牌", "产品经理", "开发一款", "我要设计"]
    SERVICE_ROLE_KEYWORDS = ["工程师", "technician", "service engineer", "设备", "机修", "工厂", "机台", "机器"]
    GREETING_KEYWORDS = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "你好",
        "您好",
        "嗨",
        "早上好",
        "下午好",
    ]

    def __init__(self) -> None:
        self.designer_workflow = DesignerWorkflow()
        self.service_workflow = ServiceWorkflow()
        self.image_understanding_agent = ImageUnderstandingAgent()
        self.sessions: dict[str, dict] = {}

    def reset_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def handle(self, request: AgentRequest) -> AgentResponse:
        message = request.message.lower()
        role = request.user_role.lower()
        has_attachments = bool(request.attachments)
        is_design_intent = self._has_design_intent(message)
        is_service_intent = self._has_service_intent(message)
        session = self.sessions.setdefault(request.session_id, {"workflow": None, "designer": {}, "service": {}, "language": None})
        detected_language = detect_language(request.message)
        if request.language == "auto":
            language = detected_language if detected_language == "zh" or not session.get("language") else session["language"]
        else:
            language = request.language
        session["language"] = language
        role = self._infer_role(role, message, has_attachments, session)

        if self._is_greeting_only(message):
            return self._chat_response(role, language)

        if role in {"designer", "brand_designer"} and self._is_designer_advice_question(message) and session.get("designer"):
            decision = self.designer_workflow.prepare(request.message, language, None, session.get("designer", {}))
            session["designer"] = decision.get("memory", session.get("designer", {}))
            return self._designer_advice_response(language, session["designer"])

        if role in {"designer", "brand_designer"} and (is_design_intent or has_attachments or session.get("workflow") == "designer"):
            image_context = self.image_understanding_agent.run(request.attachments, "designer", language)
            decision = self.designer_workflow.prepare(
                request.message,
                language,
                image_context,
                session.get("designer", {}),
                ready_to_generate=self._wants_design_output(message),
            )
            session["workflow"] = "designer"
            session["designer"] = decision.get("memory", session.get("designer", {}))
            if not decision["ready"]:
                return AgentResponse(
                    workflow="designer_discovery",
                    summary=choose(
                        language,
                        "Before creating a knitting proposal, I need to understand the design intent better.",
                        "在生成打版方案前，我需要先更完整地了解设计意图。",
                    ),
                    payload={
                        "understanding": decision["understanding"],
                        "known_info": decision["known_info"],
                        "missing_info": decision["missing_info"],
                        "image_understanding": image_context,
                    },
                    follow_up_questions=decision["questions"],
                    language=language,
                )

            result = self.designer_workflow.run_prepared(request.message, language, image_context, decision["understanding"])
            return AgentResponse(
                workflow="designer",
                summary=choose(
                    language,
                    "I converted the design brief into a simulated knitting proposal and SWS preview.",
                    "我已将设计需求转换为模拟针织打版方案和 SWS 预览结果。",
                ),
                payload=result,
                follow_up_questions=[
                    choose(language, "Do you want to optimize for lower cost, faster sampling, or premium hand feel?", "你希望优先优化成本、打样速度，还是高端手感？"),
                    choose(language, "Should this proposal target Decathlon's entry, mid, or performance line?", "这个方案面向迪卡侬入门、中端，还是专业运动系列？"),
                ],
                language=language,
            )

        if role in {"customer_equipment_engineer", "factory_engineer"} and (
            is_service_intent or has_attachments or session.get("workflow") == "service" or message.strip()
        ):
            image_context = self.image_understanding_agent.run(request.attachments, "service", language)
            decision = self.service_workflow.prepare(
                request.message,
                language,
                image_context,
                session.get("service", {}),
                ready_to_dispatch=self._wants_service_dispatch(message),
                platform_tool=request.platform_tool,
            )
            session["workflow"] = "service"
            session["service"] = decision.get("memory", session.get("service", {}))
            if not decision["ready"]:
                return AgentResponse(
                    workflow="service_assist",
                    summary=self._service_assist_summary(language, decision),
                    payload={
                        "understanding": decision["understanding"],
                        "known_info": decision["known_info"],
                        "missing_info": decision["missing_info"],
                        "online_assist": decision["online_assist"],
                        "image_understanding": image_context,
                    },
                    follow_up_questions=decision["questions"],
                    language=language,
                )

            result = self.service_workflow.run_prepared(request.message, language, image_context, decision["understanding"])
            return AgentResponse(
                workflow="service",
                summary=choose(
                    language,
                    "I created and dispatched a service ticket based on the reported issue.",
                    "我已根据报修信息创建并派发服务工单。",
                ),
                payload=result,
                follow_up_questions=[
                    choose(language, "Can you upload an alarm photo or short machine video for the engineer?", "可以上传报警照片或一段机器视频，方便工程师提前判断吗？"),
                    choose(language, "Is production fully stopped or running at reduced speed?", "目前是完全停机，还是降速继续生产？"),
                ],
                language=language,
            )

        return AgentResponse(
            workflow="clarify",
            summary=choose(language, "I need a little more detail before routing this request.", "我需要再了解一点信息，才能决定进入哪个工作流。"),
            payload={
                "question": choose(
                    language,
                    "Are you working on a knitting design, or do you need help with a machine/service issue?",
                    "你现在是想做针织产品设计，还是需要处理设备/服务问题？",
                )
            },
            follow_up_questions=[
                choose(language, "If design: tell me what product you want to create and what problem it should solve.", "如果是设计，请告诉我想做什么产品，以及它要解决什么问题。"),
                choose(language, "If service: tell me what machine or production issue happened.", "如果是服务，请告诉我是哪台机器或生产问题。"),
            ],
            language=language,
        )

    def _infer_role(self, selected_role: str, message: str, has_attachments: bool, session: dict) -> str:
        if self._has_service_intent(message) or any(word in message for word in self.SERVICE_ROLE_KEYWORDS):
            return "customer_equipment_engineer"
        if self._has_design_intent(message) or any(word in message for word in self.DESIGN_ROLE_KEYWORDS):
            return "designer"

        if session.get("workflow") == "designer":
            return "designer"
        if session.get("workflow") == "service":
            return "customer_equipment_engineer"

        if has_attachments and selected_role in {"designer", "brand_designer", "customer_equipment_engineer", "factory_engineer"}:
            return selected_role

        if selected_role in {"designer", "brand_designer", "customer_equipment_engineer", "factory_engineer"}:
            return selected_role

        return "unknown"

    def _has_design_intent(self, message: str) -> bool:
        return any(word in message for word in self.DESIGN_KEYWORDS)

    def _has_service_intent(self, message: str) -> bool:
        return any(word in message for word in self.SERVICE_KEYWORDS)

    def _is_greeting_only(self, message: str) -> bool:
        normalized = message.strip().lower().strip("!！.。?？,， ")
        return normalized in self.GREETING_KEYWORDS

    def _wants_design_output(self, message: str) -> bool:
        return any(
            word in message
            for word in [
                "generate proposal",
                "create proposal",
                "final proposal",
                "generate 3d",
                "3d preview",
                "3d image",
                "sws",
                "sampling plan",
                "生成方案",
                "输出方案",
                "打版方案",
                "最终方案",
                "开始打版",
                "生成3d",
                "生成 3d",
                "3d图",
                "3d 图",
                "3d预览",
                "3d 预览",
                "数字孪生",
                "效果图",
                "生成sws",
                "确认生成",
            ]
        )

    def _wants_service_dispatch(self, message: str) -> bool:
        return any(
            word in message
            for word in [
                "dispatch",
                "create ticket",
                "onsite",
                "send engineer",
                "派工",
                "创建工单",
                "生成工单",
                "安排工程师",
                "上门",
                "现场",
            ]
        )

    def _is_designer_advice_question(self, message: str) -> bool:
        return any(word in message for word in ["最快", "什么时候", "多久", "交期", "样衣", "供应商", "lead time", "sample"])

    def _chat_response(self, role: str, language: str) -> AgentResponse:
        if role in {"customer_equipment_engineer", "factory_engineer"}:
            summary = choose(
                language,
                "Hello, I can help you create and dispatch a Santoni service ticket. Please describe the machine model, alarm or symptom, and production impact.",
                "你好，我可以帮你创建设备服务工单并派发工程师。请告诉我机器型号、报警或故障现象，以及是否影响生产。",
            )
        else:
            summary = choose(
                language,
                "Hello, I can help turn a design idea or reference image into a Santoni knitting proposal. Tell me the product type, target user, use case, and key functions.",
                "你好，我可以把设计想法或参考图片转换成 Santoni 针织打版方案。请告诉我产品类型、目标用户、使用场景和关键功能。",
            )

        return AgentResponse(
            workflow="chat",
            summary=summary,
            payload={},
            follow_up_questions=[],
            language=language,
        )

    def _service_assist_summary(self, language: str, decision: dict) -> str:
        understanding = decision.get("understanding", {})
        online_assist = decision.get("online_assist", {})
        tool_result = online_assist.get("tool_result", {})
        if tool_result.get("tool") in {"activation_password_generator", "lease_password_generator"}:
            if tool_result.get("status") == "success":
                password = tool_result.get("activation_password") or tool_result.get("lease_password", "")
                if tool_result.get("mode") == "real_attempt":
                    return choose(
                        language,
                        f"I generated the lock-machine activation password from the real platform: {password}. Please enter it on the lock screen and confirm whether the machine is unlocked.",
                        f"我已从真实平台生成锁机激活密码：{password}。请在机器锁定界面输入，并反馈是否解锁成功。",
                    )
                return choose(
                    language,
                    f"I generated a mock lock-machine activation password: {password}. Please enter it on the lock screen and confirm whether the machine is unlocked.",
                    f"我已通过模拟工具生成锁机激活密码：{password}。请在机器锁定界面输入，并反馈是否解锁成功。",
                )
            if tool_result.get("status") == "manual_escalation_required":
                return choose(
                    language,
                    "The mock platform cannot generate an activation password automatically for this serial number. Santoni service staff must intervene manually.",
                    "模拟平台无法为这个序列号自动生成激活密码，需要 Santoni 服务人员人工介入。",
                )
            if tool_result.get("status") == "missing_input":
                return choose(
                    language,
                    "To generate a lock-machine activation password, I need the machine model, serial number, and lock-screen machine code first.",
                    "要生成锁机激活密码，我需要先确认机器型号、机器序列号和锁定界面机器码。",
                )
            if tool_result.get("status") == "missing_credentials":
                return choose(
                    language,
                    "Real platform mode is enabled. Please enter the platform username and password, or switch back to mock mode.",
                    "已启用真实平台模式。请先输入平台用户名和密码，或切回 mock 模式。",
                )
            if tool_result.get("status") == "real_platform_mapping_required":
                return choose(
                    language,
                    "I connected to the real login page and discovered the form. Password generation is still paused until we map the post-login steps.",
                    "我已连到真实登录页并识别到表单。生成密码步骤还需要配置登录后的页面操作映射，所以暂未提交生成。",
                )
            if tool_result.get("status") == "real_platform_login_discovered":
                return choose(
                    language,
                    "I submitted the real login form and discovered the post-login page structure. Activation password generation is still paused until we map the serial search and generation button steps.",
                    "我已提交真实登录表单，并识别到登录后的页面结构。生成激活密码还需要配置序列号查询和生成按钮的页面操作映射，所以暂未提交生成。",
                )
            if tool_result.get("status") == "real_platform_serial_filter_mapping_required":
                return choose(
                    language,
                    "I logged in to the real platform, but still need the serial-number filter postback mapping before generating the activation password.",
                    "我已登录真实平台，但还需要补齐序列号筛选的页面提交映射，才能继续生成激活密码。",
                )
            if tool_result.get("status") == "real_platform_login_not_completed":
                return choose(
                    language,
                    "I submitted the real platform login form, but the platform still returned the login page. Please confirm the username/password and whether the account can access Default2.aspx.",
                    "我已提交真实平台登录表单，但平台仍返回登录页。请确认用户名/密码是否正确，以及这个账号是否可以访问 Default2.aspx。",
                )
            if tool_result.get("status") == "real_platform_serial_not_found":
                return choose(
                    language,
                    "I logged in and searched the real platform, but did not find this serial number. Santoni service staff should verify the platform data manually.",
                    "我已登录并查询真实平台，但没有找到这个序列号，需要 Santoni 服务人员人工核对平台数据。",
                )
            if tool_result.get("status") == "real_platform_activation_dialog_mapping_required":
                return choose(
                    language,
                    "I logged in and found the serial number, but still need the toolbar mapping for the Generate Activation Password dialog.",
                    "我已登录并找到序列号，但还需要补齐“生成激活密码”弹窗的工具栏映射。",
                )
            if tool_result.get("status") == "real_platform_activation_submit_mapping_required":
                return choose(
                    language,
                    "I opened the activation-password dialog, but still need the activation-code input or submit-button mapping.",
                    "我已打开激活密码弹窗，但还需要补齐“激活码”输入框或弹窗生成按钮的映射。",
                )
            if tool_result.get("status") == "real_platform_activation_password_not_found":
                return choose(
                    language,
                    "I submitted the activation code, but could not read the generated activation password from the returned page.",
                    "我已提交激活码，但还没有从返回页面中读取到生成后的激活密码。",
                )
            if tool_result.get("status") == "real_platform_connection_failed":
                return choose(
                    language,
                    "I could not connect to the real platform from this environment. The mock tool remains available for workflow testing.",
                    "当前环境无法连接真实平台。可以继续使用 mock 工具测试流程。",
                )

        if online_assist.get("skill") == "service_case_online_assist_mock":
            if understanding.get("online_guidance_request") == "wrong_pattern_fixed_feed_check":
                return choose(
                    language,
                    "Yes, first confirm whether the wrong pattern is fixed on the same feed/position. If it is fixed, prioritize checking that feed's actuator cable, actuator position, and selector area; if it is random, check the pattern/program and yarn path stability first.",
                    "对，第一步就是确认错花是否固定在同一路/同一位置。如果固定，优先检查该路选针器线缆、选针器位置和选针区域；如果随机出现，先看花型/程序和纱路稳定性。",
                )
            observations = understanding.get("diagnostic_observations") or []
            if "wrong_pattern_fixed_same_feed" in observations:
                return choose(
                    language,
                    "Because the wrong pattern is fixed on the same feed/position, this is more likely actuator cable, actuator position, or selector-area related. Check that feed first and then run a low-speed test.",
                    "既然错花固定在同一路/同一位置，更像是该路选针器线缆、选针器位置或选针区域问题。请优先检查该路，然后低速测试是否复现。",
                )
            if "wrong_pattern_random" in observations:
                return choose(
                    language,
                    "Because the wrong pattern is random, first check whether the pattern/program is correct and whether yarn path or tension is unstable before focusing on a single actuator.",
                    "如果错花是随机出现，先不要只盯单个选针器，优先确认花型/程序是否正确，以及纱路或张力是否不稳定。",
                )
            if online_assist.get("matched_case_id"):
                return choose(
                    language,
                    f"I matched this to service case {online_assist.get('matched_case_id')}. Start with the online checks and tell me the result of the first check.",
                    f"我已匹配到服务案例 {online_assist.get('matched_case_id')}。先按在线排查步骤做第一项，然后把结果反馈给我。",
                )

        return choose(
            language,
            "I will first collect the key service information and try online assistance before dispatching a ticket.",
            "我会先收集关键服务信息，并优先尝试在线协助，再决定是否派工。",
        )

    def _designer_advice_response(self, language: str, memory: dict) -> AgentResponse:
        category = memory.get("product_category") or choose(language, "the product", "这个产品")
        use_case = memory.get("use_case") or choose(language, "the intended use case", "目标场景")
        summary = choose(
            language,
            f"For {category} in {use_case}, fastest sample timing depends on yarn availability and structure complexity. With mock assumptions, a simple first sample may take 7-10 working days; a more complete SWS-style sample may take 2-3 weeks.",
            f"针对{category}（场景：{use_case}），最快样衣时间主要取决于纱线是否现货、组织结构复杂度和是否需要完整 SWS 参数。按当前模拟假设，简单首样约 7-10 个工作日；较完整的 SWS 风格样衣约 2-3 周。",
        )
        return AgentResponse(
            workflow="designer_advice",
            summary=summary,
            payload={
                "known_info": memory,
                "advice_type": choose(language, "sample lead time", "样衣交期"),
            },
            follow_up_questions=[
                choose(language, "Do you need fastest visual sample or production-representative sample?", "你需要最快外观样，还是更接近量产的功能样？"),
                choose(language, "Is yarn already confirmed or should I assume available stock yarn?", "纱线已经确认了吗？还是先按现货纱线假设？"),
            ],
            language=language,
        )

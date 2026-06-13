"""Main Agent orchestration skeleton."""

from dataclasses import dataclass, field

from agent_core.agents.image_understanding_agent import ImageUnderstandingAgent
from agent_core.language import choose, detect_language
from agent_core.workflows.designer_workflow import DesignerWorkflow
from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow
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
    athena_runtime_event: dict = field(default_factory=dict)


class MainAgent:
    """Routes user requests to the right MVP workflow."""

    DESIGN_KEYWORDS = [
        "design", "style", "fabric", "yarn", "sample", "garment", "knit", "seamless",
        "proposal", "3d", "sws", "clo",
        "设计", "设计师", "设计开发", "产品开发", "打版", "打样", "样衣", "款式", "版型", "无缝",
        "透气", "快干", "速干", "面料", "纱线", "服装", "针织", "跑步", "运动上衣", "越野",
        "生成3d", "3d图", "打版方案",
    ]
    SERVICE_KEYWORDS = [
        "alarm", "install", "installation", "ticket", "repair", "maintenance", "service",
        "stopped", "broken", "down", "fault", "technician", "machine", "top2", "top2mp",
        "lease", "rental password", "activation password", "lock screen", "machine is locked",
        "machine locked", "locked machine", "machine lock", "unlock machine", "unlock the machine",
        "故障", "报警", "停机", "维修", "保养", "安装", "调试", "派工", "上门", "工程师",
        "服务", "售后", "机台", "机器", "设备", "错花", "选针", "漏油", "油箱", "死机",
        "白屏", "触摸", "坏针", "马达", "驱动器", "维修工单", "现场服务", "远程协助",
        "无法开机", "无法生产", "断纱", "张力报警", "锁机", "锁定", "锁屏", "解锁",
        "激活密码", "生成激活密码", "机器码", "序列号",
    ]
    DESIGN_ROLE_KEYWORDS = [
        "designer", "brand", "设计师", "设计开发", "产品开发", "产品经理", "品牌", "我要设计", "开发一款",
    ]
    SERVICE_ROLE_KEYWORDS = [
        "technician", "service engineer", "工程师", "售后", "服务工程师", "维修工程师", "机修", "设备", "工厂", "机台", "机器",
    ]
    PRODUCTION_MANAGER_KEYWORDS = [
        "general manager", "factory manager", "production manager", "operations manager",
        "delivery", "order", "schedule", "aps", "iot", "oee", "scrap", "waste", "yield",
        "downtime", "material", "capacity", "root cause", "backlog",
        "总经理", "厂长", "生产经理", "生产主管", "管理层", "订单", "交期", "货期", "交付",
        "排单", "排产", "延期", "逾期", "废弃", "废料", "废品", "废品率", "报废", "不良",
        "良品", "良率", "质量", "停机", "开动率", "稼动率", "物料", "纱线", "库存", "批次",
        "供应商", "产能", "瓶颈", "原因", "分析", "排行", "根因", "未交货", "未排", "已排",
        "补单", "成本", "人工效率", "有效工时", "异常", "历史对比", "同比", "环比", "趋势",
        "看板", "报表", "织造", "白坯", "预处理", "排缸", "染色", "裁剪", "缝制", "包装",
        "验针", "集装箱",
    ]
    PRODUCTION_ANALYTIC_CONTEXT_KEYWORDS = PRODUCTION_MANAGER_KEYWORDS + [
        "what should i watch", "three priorities", "what happened", "why",
        "今天先看", "今天先盯", "三件事", "为什么", "怎么回事",
    ]
    GREETING_KEYWORDS = [
        "hi", "hello", "hey", "good morning", "good afternoon", "你好", "您好", "嗨", "早上好", "下午好",
    ]
    def __init__(self) -> None:
        self.designer_workflow = DesignerWorkflow()
        self.service_workflow = ServiceWorkflow()
        self.production_workflow = ProductionOperationsWorkflow()
        self.image_understanding_agent = ImageUnderstandingAgent()
        self.sessions: dict[str, dict] = {}

    def reset_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def handle(self, request: AgentRequest) -> AgentResponse:
        response = self._handle(request)
        return self._with_runtime_event(request, response)

    def _handle(self, request: AgentRequest) -> AgentResponse:
        message = request.message.lower()
        role = request.user_role.lower()
        has_attachments = bool(request.attachments)
        is_design_intent = self._has_design_intent(message)
        is_service_intent = self._has_service_intent(message)
        session = self.sessions.setdefault(
            request.session_id,
            {"workflow": None, "designer": {}, "service": {}, "production": {}, "language": None},
        )
        detected_language = detect_language(request.message)
        if request.language == "auto":
            language = detected_language if detected_language == "zh" or not session.get("language") else session["language"]
        else:
            language = request.language
        session["language"] = language
        role = self._infer_role(role, message, has_attachments, session)

        if self._is_greeting_only(message):
            return self._chat_response(role, language)

        if self._should_route_production_manager(role, message):
            session["workflow"] = "production"
            analysis = self.production_workflow.chatbi({"question": request.message, "language": language})
            session["production"] = {
                "last_metric": analysis.get("metric", ""),
                "last_evidence_refs": sorted(
                    {
                        ref
                        for item in analysis.get("root_causes", [])
                        for ref in item.get("evidence_refs", [])
                    }
                ),
            }
            return self._production_manager_response(language, analysis)

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
        if self._should_route_production_manager(selected_role, message):
            return "production_manager"
        if self._has_service_intent(message) or any(word in message for word in self.SERVICE_ROLE_KEYWORDS):
            return "customer_equipment_engineer"
        if self._has_design_intent(message) or any(word in message for word in self.DESIGN_ROLE_KEYWORDS):
            return "designer"

        if session.get("workflow") == "designer":
            return "designer"
        if session.get("workflow") == "service":
            return "customer_equipment_engineer"
        if session.get("workflow") == "production":
            return "production_manager"

        if has_attachments and selected_role in {"designer", "brand_designer", "customer_equipment_engineer", "factory_engineer"}:
            return selected_role

        if selected_role in {"designer", "brand_designer", "customer_equipment_engineer", "factory_engineer", "production_manager"}:
            return selected_role

        return "unknown"

    def _has_design_intent(self, message: str) -> bool:
        return any(word in message for word in self.DESIGN_KEYWORDS)

    def _has_service_intent(self, message: str) -> bool:
        return any(word in message for word in self.SERVICE_KEYWORDS)

    def _has_production_manager_intent(self, message: str) -> bool:
        return any(word in message for word in self.PRODUCTION_MANAGER_KEYWORDS)

    def _should_route_production_manager(self, selected_role: str, message: str) -> bool:
        if selected_role == "production_manager":
            return True
        if not self._has_production_manager_intent(message):
            return False
        if not self._has_service_intent(message):
            return True
        production_owner_terms = [
            "general manager",
            "factory manager",
            "production manager",
            "operations manager",
            "总经理",
            "厂长",
            "生产经理",
            "生产主管",
            "管理层",
        ]
        production_analysis_terms = [
            "delivery",
            "order",
            "schedule",
            "root cause",
            "backlog",
            "交期",
            "货期",
            "交付",
            "订单",
            "排单",
            "排产",
            "废品率",
            "良率",
            "物料",
            "纱线",
            "产能",
            "瓶颈",
            "根因",
            "今天先看",
            "今天先盯",
            "三件事",
            "看板",
            "报表",
            "历史对比",
        ]
        return any(word in message for word in production_owner_terms + production_analysis_terms)

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

    def _production_manager_response(self, language: str, analysis: dict) -> AgentResponse:
        root_causes = analysis.get("root_causes", [])
        top_causes = root_causes[:3]
        recommendations = analysis.get("recommended_actions", [])[:3]
        evidence_refs = []
        for item in top_causes:
            evidence_refs.extend(item.get("evidence_refs", []))
        payload = {
            "executive_answer": analysis.get("executive_answer", {}),
            "management_summary": analysis.get("answer_summary", ""),
            "metric": analysis.get("metric", ""),
            "actual_data_mode": analysis.get("actual_data_mode", False),
            "metric_snapshot": analysis.get("metric_snapshot", {}),
            "management_priority_brief": analysis.get("management_priority_brief", {}),
            "decision_loop": analysis.get("decision_loop", {}),
            "reason_and_evidence": top_causes,
            "recommended_action": recommendations,
            "next_drilldowns": analysis.get("next_drilldowns", []),
            "data_gaps": analysis.get("data_gaps", []),
            "data_boundary": choose(
                language,
                "This is read-only Athena production analysis over the current mock/registered evidence. It does not connect to live APS/IOT databases, does not change schedules, and does not create service tickets.",
                "这是基于当前 mock / 已登记证据的只读 Athena 生产分析；暂未连接真实 APS/IOT 数据库，不会修改排单，也不会创建真实服务工单。",
            ),
            "evidence_refs": sorted(set(evidence_refs)),
            "confidence": analysis.get("confidence", "medium"),
        }
        return AgentResponse(
            workflow="production_athena",
            summary=analysis.get("answer_summary", ""),
            payload=payload,
            follow_up_questions=[
                choose(language, "Do you want me to drill down by order, style, machine, material lot, or shift?", "要继续按订单、款式、机台、物料批次或班次下钻吗？"),
                choose(language, "Should I explain which parts are evidence-backed and which parts need more data?", "需要我说明哪些结论有证据、哪些仍然缺数据吗？"),
            ],
            language=language,
        )

    def _with_runtime_event(self, request: AgentRequest, response: AgentResponse) -> AgentResponse:
        if response.athena_runtime_event:
            return response

        evidence_refs = self._collect_evidence_refs(response.payload)
        persona = self._runtime_persona(response.workflow, request.user_role)
        data_boundary = self._runtime_data_boundary(response.workflow, response.payload)
        blocked_actions = self._runtime_blocked_actions(response.workflow)
        event = {
            "schema": "athena.runtime_event.v1",
            "source": "demo",
            "scope": "session",
            "tenant_id": None,
            "factory_id": None,
            "retention_policy": "session_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "candidate",
            "session_id": request.session_id,
            "channel": request.channel,
            "workflow": response.workflow,
            "persona": persona,
            "selected_role": request.user_role,
            "intent": self._runtime_intent(response.workflow, response.payload),
            "language": response.language,
            "data_sufficiency": self._runtime_data_sufficiency(response),
            "data_boundary": data_boundary,
            "evidence_refs": evidence_refs,
            "memory_event_candidate": {
                "event_type": "conversation_turn",
                "scope": "session",
                "tenant_id": None,
                "factory_id": None,
                "source": "demo",
                "retention_policy": "session_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "candidate",
                "object_scope": ["main_agent", response.workflow],
                "summary": (
                    f"{persona} request routed to {response.workflow}; raw user text and generated sensitive "
                    "values are intentionally excluded from this candidate."
                ),
                "evidence_refs": evidence_refs,
                "contains_raw_user_message": False,
                "contains_credentials": False,
                "write_policy": "candidate_only_until_live_hermes_connector",
            },
            "blocked_actions": blocked_actions,
        }
        return AgentResponse(
            workflow=response.workflow,
            summary=response.summary,
            payload=response.payload,
            follow_up_questions=response.follow_up_questions,
            language=response.language,
            athena_runtime_event=event,
        )

    def _runtime_persona(self, workflow: str, selected_role: str) -> str:
        if workflow.startswith("production_athena"):
            return "production_manager"
        if workflow.startswith("service"):
            return "customer_equipment_engineer"
        if workflow.startswith("designer"):
            return "designer"
        if selected_role in {"production_manager", "customer_equipment_engineer", "factory_engineer", "designer"}:
            return selected_role
        return "unknown"

    @staticmethod
    def _runtime_intent(workflow: str, payload: dict) -> str:
        if workflow.startswith("production_athena"):
            metric = payload.get("metric") or "analysis"
            return f"production_{metric}"
        if workflow.startswith("service"):
            issue_type = (payload.get("known_info") or payload.get("understanding") or {}).get("issue_type")
            return f"service_{issue_type or 'intake'}"
        if workflow.startswith("designer"):
            category = (payload.get("known_info") or payload.get("understanding") or {}).get("product_category")
            return f"designer_{category or 'intake'}"
        return workflow

    @staticmethod
    def _runtime_data_sufficiency(response: AgentResponse) -> str:
        if response.workflow == "clarify":
            return "needs_routing_input"
        missing_info = response.payload.get("missing_info", [])
        if missing_info or response.follow_up_questions:
            return "needs_more_input"
        if response.workflow.startswith("production_athena") and response.payload.get("evidence_refs"):
            return "evidence_backed_mock_analysis"
        return "sufficient_for_current_mock"

    @staticmethod
    def _runtime_data_boundary(workflow: str, payload: dict) -> str:
        if payload.get("data_boundary"):
            return payload["data_boundary"]
        if workflow.startswith("production_athena"):
            return "Read-only production analysis over local mock/registered evidence; no live APS/IOT database connection or production writeback."
        if workflow.startswith("service"):
            return "Service flow uses local mock cases and controlled tools; no real CRM/ticket-system writeback and no credential persistence."
        if workflow.startswith("designer"):
            return "Designer flow uses local mock workflow objects; no real SWS/Arachne/Style3D writeback."
        return "Local demo runtime event candidate only; no live Hermes writeback."

    @staticmethod
    def _runtime_blocked_actions(workflow: str) -> list[str]:
        actions = {
            "store_credentials_or_tokens",
            "store_raw_user_message_in_memory_candidate",
            "write_live_hermes_memory_without_connector_review",
        }
        if workflow.startswith("production_athena"):
            actions.update(
                {
                    "write_to_aps_or_iot",
                    "change_production_schedule",
                    "upload_co_file",
                    "upload_cx_file",
                    "create_service_ticket_automatically",
                }
            )
        elif workflow.startswith("service"):
            actions.update(
                {
                    "write_real_crm_ticket",
                    "dispatch_without_required_information",
                    "persist_platform_credentials",
                }
            )
        elif workflow.startswith("designer"):
            actions.update(
                {
                    "write_to_sws_or_arachne",
                    "claim_physical_sample_validation",
                    "create_customer_commitment_without_review",
                }
            )
        return sorted(actions)

    @classmethod
    def _collect_evidence_refs(cls, value: object) -> list[str]:
        refs: set[str] = set()
        cls._collect_evidence_refs_into(value, refs)
        return sorted(refs)

    @classmethod
    def _collect_evidence_refs_into(cls, value: object, refs: set[str]) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"evidence_ref", "evidence_id"} and isinstance(item, str):
                    refs.add(item)
                elif key == "evidence_refs" and isinstance(item, list):
                    refs.update(ref for ref in item if isinstance(ref, str))
                cls._collect_evidence_refs_into(item, refs)
        elif isinstance(value, list):
            for item in value:
                cls._collect_evidence_refs_into(item, refs)

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


import json

from agent_core.main_agent import AgentRequest, MainAgent
from agent_core.operating_model import project_documentation
from agent_core.tools.lease_password_tool import ActivationPasswordTool
from agent_core.tools.service_case_importer import ServiceCaseExcelImporter
from agent_core.tools.service_case_knowledge import ServiceCaseKnowledgeBase
from agent_core.workflows.athena_mvp_workflow import AthenaMvpWorkflow
from agent_core.workflows.hermes_integration_workflow import HermesIntegrationWorkflow
from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow
from agent_core.workflows.tianpai_aps_erp_export_adapter import TianpaiApsErpExportAdapter
from agent_core.workflows.training_automation_workflow import TrainingAutomationWorkflow

from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def test_routes_designer_request():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="Design a seamless running top"))
    assert response.workflow == "designer_discovery"


def test_routes_service_request():
    response = MainAgent().handle(AgentRequest(user_role="customer_equipment_engineer", message="Machine alarm, need repair"))
    assert response.workflow == "service_assist"


def test_routes_chinese_designer_request_and_returns_chinese():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="帮我设计一款无缝跑步上衣，要透气快干"))
    assert response.workflow == "designer_discovery"
    assert response.language == "zh"


def test_greeting_does_not_trigger_designer_workflow():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="你好"))
    assert response.workflow == "chat"
    assert "设计" in response.summary


def test_vague_message_asks_for_clarification():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="帮我看看"))
    assert response.workflow == "clarify"


def test_role_priority_over_keywords():
    response = MainAgent().handle(AgentRequest(user_role="customer_equipment_engineer", message="SM8 stopped with yarn tension alarm"))
    assert response.workflow in {"service_assist", "service"}


def test_designer_request_with_image_context():
    response = MainAgent().handle(
        AgentRequest(
            user_role="designer",
            message="帮我按这张图做一款更透气的无缝跑步上衣",
            attachments=[{"name": "reference-top.png", "type": "image/png", "size": 1234}],
        )
    )
    assert response.workflow == "designer_discovery"
    assert "image_understanding" in response.payload
    assert "understanding" in response.payload


def test_service_request_with_image_context():
    response = MainAgent().handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            message="这张报警照片显示机器停机，需要派工",
            attachments=[{"name": "alarm-panel.jpg", "type": "image/jpeg", "size": 1234}],
        )
    )
    assert response.workflow in {"service_assist", "service"}
    assert "image_understanding" in response.payload
    assert "understanding" in response.payload


def test_designer_fallback_understanding_changes_category():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="Design performance socks with quick dry yarn"))
    assert response.payload["understanding"]["product_category"] == "performance sock"

    response = MainAgent().handle(AgentRequest(user_role="designer", message="请生成打版方案：无缝跑步上衣，夏季跑步，女性用户，透气快干"))
    assert response.payload["understanding"]["product_category"] == "seamless running top"


def test_designer_generates_only_when_requested():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="请生成打版方案：无缝跑步上衣，夏季跑步，女性用户，透气快干"))
    assert response.workflow == "designer"
    assert "reasoning_status" in response.payload["design_spec"]
    assert "reasoning_status" in response.payload["digital_twin"]


def test_designer_3d_request_triggers_generation_after_discovery():
    agent = MainAgent()
    session_id = "designer-3d"
    agent.handle(
        AgentRequest(
            user_role="auto",
            session_id=session_id,
            message="帮我设计一款无缝跑步上衣，要透气快干，男性，夏季跑步，入门款，60到90cm",
        )
    )
    response = agent.handle(AgentRequest(user_role="auto", session_id=session_id, message="帮我生成一个3D图"))
    assert response.workflow == "designer"
    assert response.payload["understanding"]["product_category"] != "未知"


def test_service_fallback_understanding_changes_issue_type():
    response = MainAgent().handle(AgentRequest(user_role="customer_equipment_engineer", message="新机器刚到工厂，需要安排安装和开机调试"))
    assert response.workflow in {"service_assist", "service"}


def test_auto_role_routes_designer_intent():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="我是设计师，我要设计一款冬季越野跑速干衣"))
    assert response.workflow == "designer_discovery"


def test_auto_role_routes_service_intent():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="我的机器坏了，能不能帮我排查一下？"))
    assert response.workflow == "service_assist"


def test_main_agent_routing_dictionary_keeps_normal_chinese_terms():
    text = Path("src/agent_core/main_agent.py").read_text(encoding="utf-8")

    for term in ["design", "service", "production", "总经理", "设计", "维修"]:
        assert term in text.lower()


def test_auto_role_routes_normal_chinese_production_site_terms():
    agent = MainAgent()
    questions = [
        "总经理想看今天哪些订单有交付风险",
        "废品率为什么升高，是款式、机台还是物料造成的？",
        "纱线库存和批次会不会影响织造交付？",
        "排缸和染色之后的不良是否导致补单？",
    ]

    for question in questions:
        response = agent.handle(AgentRequest(user_role="auto", message=question))
        assert response.workflow == "production_athena"


def test_auto_role_keeps_normal_chinese_machine_fault_in_service():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="SM8 机台张力报警停机，需要工程师上门维修"))

    assert response.workflow == "service_assist"


def test_auto_role_routes_general_manager_delivery_question_to_production_athena():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="我是总经理，我要知道最近订单的交期"))

    assert response.workflow == "production_athena"
    assert response.language == "zh"
    assert response.summary
    assert response.payload["management_summary"] == response.summary
    assert response.payload["management_priority_brief"]["top_priorities"]
    assert response.payload["reason_and_evidence"]
    assert response.payload["recommended_action"]
    assert "read-only" in response.payload["data_boundary"].lower() or "只读" in response.payload["data_boundary"]


def test_auto_role_routes_order_delivery_question_without_declared_role():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="最近订单交期怎么样？"))

    assert response.workflow == "production_athena"
    assert response.payload["metric"] == "order_delay"
    assert response.payload["evidence_refs"]


def test_production_manager_huoqi_question_uses_order_delay_metric():
    response = MainAgent().handle(
        AgentRequest(user_role="production_manager", message="\u5e2e\u6211\u770b\u4e00\u4e0b\u6700\u8fd1\u4e00\u5468\u7684\u5e73\u5747\u8d27\u671f")
    )

    assert response.workflow == "production_athena"
    assert response.payload["metric"] == "order_delay"
    assert response.payload["metric_snapshot"]
    assert response.payload["evidence_refs"]
    assert response.payload.get("actual_data_mode") is True or response.payload["metric_snapshot"].get("data_boundary")


def test_machine_repair_stoppage_still_routes_to_service():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="SM8 机器停机，需要维修"))

    assert response.workflow == "service_assist"

def test_chat_response_includes_athena_runtime_event_for_hermes_candidate():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            session_id="runtime-production",
            message="As general manager, why is scrap rate 4%? Please find the root cause.",
        )
    )
    event = response.athena_runtime_event
    serialized_event = json.dumps(event, ensure_ascii=False)

    assert response.workflow == "production_athena"
    assert event["schema"] == "athena.runtime_event.v1"
    assert event["workflow"] == response.workflow
    assert event["persona"] == "production_manager"
    assert event["scope"] == "session"
    assert event["session_id"] == "runtime-production"
    assert event["intent"] == "production_scrap_rate"
    assert event["evidence_refs"]
    assert event["memory_event_candidate"]["promotion_status"] == "candidate"
    assert event["memory_event_candidate"]["contains_raw_user_message"] is False
    assert event["memory_event_candidate"]["contains_credentials"] is False
    assert "write_to_aps_or_iot" in event["blocked_actions"]
    assert "store_raw_user_message_in_memory_candidate" in event["blocked_actions"]
    assert "As general manager" not in serialized_event


def test_runtime_event_excludes_generated_activation_password_values():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2MP locked machine, serial number 12345678, machine code ABCD-1234, need activation password",
        )
    )
    tool_result = response.payload["online_assist"]["tool_result"]
    event = response.athena_runtime_event
    serialized_event = json.dumps(event, ensure_ascii=False)

    assert response.workflow == "service_assist"
    assert tool_result["status"] == "success"
    assert tool_result["activation_password"] not in serialized_event
    assert event["persona"] == "customer_equipment_engineer"
    assert event["memory_event_candidate"]["contains_credentials"] is False
    assert "persist_platform_credentials" in event["blocked_actions"]


def test_service_requires_dispatch_confirmation_after_image_intake():
    agent = MainAgent()
    session_id = "service-image-confirm"
    agent.handle(
        AgentRequest(
            user_role="auto",
            session_id=session_id,
            message="我的机器坏了，帮我快速恢复生产。SM8-TOP2V，序列号12312312",
        )
    )
    response = agent.handle(
        AgentRequest(
            user_role="auto",
            session_id=session_id,
            message="这是报警照片",
            attachments=[{"name": "alarm-panel.jpg", "type": "image/jpeg", "size": 1234}],
        )
    )
    assert response.workflow == "service_assist"
    assert "factory_location" in response.payload["missing_info"]
    assert "customer_contact" in response.payload["missing_info"]
    assert "online_steps_attempted" in response.payload["missing_info"]


def test_service_dispatch_confirmation_after_required_fields():
    agent = MainAgent()
    session_id = "service-required-fields"
    agent.handle(
        AgentRequest(
            user_role="auto",
            session_id=session_id,
            message=(
                "我的机器停机，SM8-TOP2V，序列号12312312，张力报警。"
                "工厂：上海一号工厂，联系人 Joey 13800138000，已经重启并检查纱路。"
            ),
            attachments=[{"name": "alarm-panel.jpg", "type": "image/jpeg", "size": 1234}],
        )
    )
    response = agent.handle(AgentRequest(user_role="auto", session_id=session_id, message="现在需要派工"))
    assert response.workflow == "service"
    assert response.payload["understanding"]["factory_location"] == "上海一号工厂"
    assert response.payload["understanding"]["customer_contact"] == "13800138000"


def test_service_case_online_assist_matches_tension_alarm():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="SM8-TOP2V 序列号2312312，张力报警停机，已经重启一次还是报警",
        )
    )
    online_assist = response.payload["online_assist"]
    assert online_assist["skill"] == "service_case_online_assist_mock"
    assert online_assist["case_database_status"] == "mock_matched"
    assert online_assist["matched_case_id"] == "SVC-MOCK-0001"
    assert online_assist["online_solvable"] is True
    assert online_assist["suggested_steps"]
    assert online_assist["safety_warnings"]


def test_service_case_knowledge_reports_no_match_for_unknown_case():
    result = ServiceCaseKnowledgeBase().match(
        {
            "machine_model": "UNKNOWN-MODEL",
            "issue_type": "unusual request",
            "symptoms": ["unknown symptom"],
            "production_status": "running",
            "urgency": "P3",
        },
        "瀹㈡埛璇㈤棶鍩硅璧勬枡锛屼笉鏄満鍣ㄦ晠闅?",
        "zh",
    )
    assert result["case_database_status"] == "mock_no_match"


def test_service_case_review_library_marks_imported_cases_for_review():
    review = ServiceCaseKnowledgeBase().review_cases()
    assert review["case_count"] >= 10
    assert review["implemented_count"] >= 1
    assert review["approved_count"] >= 1
    assert review["needs_review_count"] >= 1
    assert review["online_solvable_count"] >= 1
    assert review["dispatch_likely_count"] >= 1
    assert "severity_counts" in review
    assert any(case["review_status"] == "needs_service_review" for case in review["cases"])
    assert all("handoff_payload_preview" in case for case in review["cases"])
    assert any(item["name"] == "Excel auto importer" for item in review["planned_features"])
    assert any(item["name"] == "Case edit and diff view" for item in review["planned_features"])


def test_project_docs_track_done_and_planned_features():
    docs = project_documentation()
    assert docs["version"] == "v0.113.1"
    assert any(item["name"] == "Service Case Library review page" for item in docs["implemented_features"])
    assert any(item["name"] == "Operation guide page" for item in docs["implemented_features"])
    assert any(item["name"] == "Excel auto importer" for item in docs["implemented_features"])
    assert any(item["name"] == "Case approval workflow" for item in docs["implemented_features"])
    assert any(item["name"] == "Customer-facing interaction page" for item in docs["implemented_features"])
    assert any(item["name"] == "Customer identity selection gate" for item in docs["implemented_features"])
    assert any(item["name"] == "Developer identity selection gate" for item in docs["implemented_features"])
    assert any(item["name"] == "User page script scope guard" for item in docs["implemented_features"])
    assert any(item["name"] == "Production delivery-time wording route" for item in docs["implemented_features"])
    assert any(item["name"] == "Production management answer template" for item in docs["implemented_features"])
    assert any(item["name"] == "Production high-frequency management questions" for item in docs["implemented_features"])
    assert any(item["name"] == "Production object model and Management Priority Engine v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Decision Loop / Follow-up Engine v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Production permission boundary and GM final confirmation" for item in docs["implemented_features"])
    assert any(item["name"] == "Production MVP demo story" for item in docs["implemented_features"])
    assert any(item["name"] == "Production MVP success check" for item in docs["implemented_features"])
    assert any(item["name"] == "Production PRD alignment audit" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai APS/ERP export adapter" for item in docs["implemented_features"])
    assert any(item["name"] == "Production mock plus actual snapshot console" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai actual-data management Q&A" for item in docs["implemented_features"])
    assert any(item["name"] == "Production GM first-screen actual priority workflow" for item in docs["implemented_features"])
    assert any(item["name"] == "Risk card drilldown and local follow-up contract" for item in docs["implemented_features"])
    assert any(item["name"] == "GM Demo Mode UI" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena Skill Registry" for item in docs["implemented_features"])
    assert any(item["name"] == "Skill Execution Trace" for item in docs["implemented_features"])
    assert any(item["name"] == "User-page General Manager agent workspace" for item in docs["implemented_features"])
    assert any(item["name"] == "General Manager follow-up loop demo" for item in docs["implemented_features"])
    assert any(item["name"] == "Developer General Manager flow parity" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena v0.90 development progress report" for item in docs["implemented_features"])
    assert any(item["name"] == "Activation credential prompt" for item in docs["implemented_features"])
    assert any(item["name"] == "Unlock intent credential trigger" for item in docs["implemented_features"])
    assert any(item["name"] == "Natural lock activation routing" for item in docs["implemented_features"])
    assert any(item["name"] == "Lock-machine activation wording" for item in docs["implemented_features"])
    assert any(item["name"] == "Full Santoni logo asset" for item in docs["implemented_features"])
    assert any(item["name"] == "Service Manager Console" for item in docs["implemented_features"])
    assert any(item["name"] == "Developer changelog preview" for item in docs["implemented_features"])
    assert any(item["name"] == "Design Intake Structuring Console" for item in docs["implemented_features"])
    assert any(item["name"] == "Production Operations Console" for item in docs["implemented_features"])
    assert any(item["name"] == "Bilingual page language switch" for item in docs["implemented_features"])
    assert any(item["name"] == "Production Console Chinese display" for item in docs["implemented_features"])
    assert any(item["name"] == "Production site flow layout" for item in docs["implemented_features"])
    assert any(item["name"] == "APS/IOT adapter field mapping" for item in docs["implemented_features"])
    assert any(item["name"] == ".co/.cx program-file terminology" for item in docs["implemented_features"])
    assert any(item["name"] == "Santoni Athena production insight" for item in docs["implemented_features"])
    assert any(item["name"] == "Main chat production-manager routing" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena runtime event envelope" for item in docs["implemented_features"])
    assert any(item["name"] == "Production order-id workflow spine" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai Material Risk v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai Data Readiness v1" for item in docs["implemented_features"])
    assert any(item["name"] == "General Manager Question Bank v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Active LLM runtime status" for item in docs["implemented_features"])
    assert any(item["name"] == "Chinese routing dictionary cleanup" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena structure PNG" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena PRD v0.1" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena PRD visible entry" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena PRD web route" for item in docs["implemented_features"])
    assert any(item["name"] == "Developer page API interaction fix" for item in docs["implemented_features"])
    assert any(item["name"] == "General Manager 3-minute production brief" for item in docs["implemented_features"])
    assert any(item["name"] == "First-screen Service Risk brief" for item in docs["implemented_features"])
    assert any(item["name"] == "Risk card drill-down actions" for item in docs["implemented_features"])
    assert any(item["name"] == "PRD first-screen risk-card alignment" for item in docs["implemented_features"])
    assert any(item["name"] == "PRD risk-card evidence detail layer" for item in docs["implemented_features"])
    assert any(item["name"] == "PRD follow-up status lifecycle" for item in docs["implemented_features"])
    assert any(item["name"] == "PRD first-screen management summary" for item in docs["implemented_features"])
    assert any(item["name"] == "Hermes Adapter Contract" for item in docs["implemented_features"])
    assert any(item["name"] == "Hermes memory event governance" for item in docs["implemented_features"])
    assert any(item["name"] == "Organization Memory / Playbook Engine v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai training data pack" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai APS workflow fragment" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai actual onsite workflow" for item in docs["implemented_features"])
    assert any(item["name"] == "Tianpai training governance" for item in docs["implemented_features"])
    assert any(item["name"] == "Athena Automatic Training Console" for item in docs["implemented_features"])
    assert any(item["name"] == "Training review and data intake" for item in docs["implemented_features"])
    assert any(item["name"] == "Training round summary and baseline promotion" for item in docs["implemented_features"])
    assert any(item["name"] == "Playbook Regression Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Automatic Regression Runner v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Regression Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Next Loop Handoff v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Next Loop Handoff Review v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Next Loop Closure Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Training Iteration Proposal v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Training Iteration Proposal Review v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Work Packet Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Patch Queue Contract v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Execution Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Execution Gate Review v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Worktree Preparation Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Worktree Launch Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Worktree Result Intake v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Worktree Result Review Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Candidate Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Approval Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Handoff Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Execution Readiness Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Execution Readiness Review v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Execution Result Intake v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Closure / Hermes Sync Audit v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Review Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Handoff Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Execution Readiness Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Execution Readiness Review v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Execution Result Intake v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Closure Audit v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Sync Closure Review Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Sync Handoff Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Sync Execution Readiness Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Sync Execution Result Intake v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Sync Closure Audit v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Completion Review Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Publication Handoff Queue v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Publication Readiness Gate v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Publication Result Intake v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Publication Closure Audit v1" for item in docs["implemented_features"])
    assert any(item["name"] == "Codex Promotion Final Release / Archive Review Gate v1" for item in docs["implemented_features"])
    assert "Athena's product-level value proposition is workflow-native onsite workforce, management decision-loop agent, and Hermes-governed self-evolution." in docs["confirmed"]
    assert any(item["name"] == "Real SWS/Arachne adapter" for item in docs["planned_features"])
    assert any(item["name"] == "Real APS/IOT production adapters" for item in docs["planned_features"])
    assert any(item["name"] == "Real ERP order and material adapter" for item in docs["planned_features"])
    assert any(item["name"] == "Real Hermes runtime connector" for item in docs["planned_features"])
    assert any(item["name"] == "Live Hermes automatic training runner" for item in docs["planned_features"])
    assert any(item["name"] == "Live Hermes playbook regression runner" for item in docs["planned_features"])
    assert any(item["name"] == "Production follow-up real workflow integration" for item in docs["planned_features"])
    assert any(item["name"] == "Real Hermes organization-memory connector" for item in docs["planned_features"])
    assert len(docs["athena_mvp_state_flow"]) == 6
    assert len(docs["production_operations_state_flow"]) == 6
    assert len(docs["hermes_integration_state_flow"]) == 6
    assert len(docs["training_automation_state_flow"]) == 37
    assert any("APS Planned Task delivery-time CSV" in item for item in docs["confirmed"])
    assert any("automatic regression baseline" in item for item in docs["confirmed"])
    assert any("explicit production-manager bridge" in item for item in docs["confirmed"])
    assert any("athena_runtime_event envelope" in item for item in docs["confirmed"])
    assert any("playbook candidates only" in item for item in docs["confirmed"])
    assert any("follow-up closure" in item and "regression-case preparation" in item for item in docs["confirmed"])
    assert any("playbook_regression_queue" in item for item in docs["confirmed"])
    assert any("Automatic Regression Runner v1" in item for item in docs["confirmed"])
    assert any("Regression Gate v1" in item for item in docs["confirmed"])
    assert any("Next Loop Handoff v1" in item for item in docs["confirmed"])
    assert any("Next Loop Handoff Review v1" in item for item in docs["confirmed"])
    assert any("Next Loop Closure Gate v1" in item for item in docs["confirmed"])
    assert any("Training Iteration Proposal v1" in item for item in docs["confirmed"])
    assert any("Training Iteration Proposal Review v1" in item for item in docs["confirmed"])
    assert any("Codex Work Packet Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Patch Queue Contract v1" in item for item in docs["confirmed"])
    assert any("Codex Execution Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Execution Gate Review v1" in item for item in docs["confirmed"])
    assert any("Codex Worktree Preparation Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Worktree Launch Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Worktree Result Intake v1" in item for item in docs["confirmed"])
    assert any("Codex Worktree Result Review Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Candidate Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Approval Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Handoff Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Execution Readiness Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Execution Readiness Review v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Execution Result Intake v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Closure / Hermes Sync Audit v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Review Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Handoff Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Execution Readiness Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Execution Readiness Review v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Execution Result Intake v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Closure Audit v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Sync Closure Review Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Sync Handoff Queue v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Sync Execution Readiness Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Sync Execution Result Intake v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Sync Closure Audit v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Completion Review Gate v1" in item for item in docs["confirmed"])
    assert any("Codex Promotion Final Release / Archive Review Gate v1" in item for item in docs["confirmed"])
    assert any("explicit identity selection" in item for item in docs["confirmed"])
    assert any("Developer/debug chat" in item and "explicit identity selection" in item for item in docs["confirmed"])
    assert any("shared global identifiers" in item for item in docs["confirmed"])
    assert any("Chinese 鐠愌勬埂 questions" in item for item in docs["confirmed"])
    assert any("fixed conclusion" in item for item in docs["confirmed"])
    assert any("High-frequency general-manager questions" in item for item in docs["confirmed"])
    assert any("runtime events are local session-scope candidates" in item for item in docs["uncertain"])


def test_tianpai_training_pack_structures_voc_and_iot_exports():
    pack_path = Path("docs/training/tianpai_training_pack_v0_1.json")
    summary_path = Path("docs/training/tianpai_training_summary_v0_1.md")

    assert pack_path.exists()
    assert summary_path.exists()

    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    summary = summary_path.read_text(encoding="utf-8")
    changelog = Path("src/web_app/changelog.html").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert pack["schema_version"] == "tianpai_training_pack.v0.1"
    assert pack["project_version_context"] == "v0.113.1"
    assert pack["tenant_id"] == "tianpai"
    assert pack["factory_id"] is None
    assert len(pack["source_files"]) == 10
    assert {"user_feedback", "IOT export", "APS export", "meeting", "material inventory"}.issubset({item["type"] for item in pack["source_files"]})
    assert any(item["source_id"] == "SRC-TPI-APS-WORKFLOW-001" for item in pack["source_files"])
    assert any(item["source_id"] == "SRC-TPI-APS-PLANNED-TASK-001" and item["stored_in_repo"] is False for item in pack["source_files"])
    assert any(item["source_id"] == "SRC-TPI-ONSITE-WORKFLOW-001" for item in pack["source_files"])
    assert any(item["source_id"] == "SRC-TPI-MATERIAL-INVENTORY-001" and item["stored_in_repo"] is False for item in pack["source_files"])

    finding_ids = {item["finding_id"] for item in pack["data_quality_findings"]}
    assert {
        "DQ-TPI-001",
        "DQ-TPI-002",
        "DQ-TPI-003",
        "DQ-TPI-004",
        "DQ-TPI-005",
        "DQ-TPI-006",
        "DQ-TPI-007",
        "DQ-TPI-008",
    }.issubset(finding_ids)
    assert pack["iot_aggregate_summary"]["production_output"]["order_id_missing_rate"] == 1.0
    assert pack["iot_aggregate_summary"]["production_output"]["machine_count"] >= 1
    assert pack["iot_aggregate_summary"]["scrap_statistics"]["converted_scrap_total"] > 0
    assert pack["iot_aggregate_summary"]["fault_analysis"]["fault_code_count"] >= 1

    task_ids = {item["task_id"] for item in pack["candidate_training_tasks"]}
    assert {
        "TPI-GM-DELIVERY-001",
        "TPI-IOT-DATA-GAP-001",
        "TPI-IOT-DOWNTIME-001",
        "TPI-IOT-SCRAP-001",
        "TPI-IOT-FAULT-001",
        "TPI-GM-COST-001",
        "TPI-APS-WORKFLOW-001",
        "TPI-WORKFLOW-BOUNDARY-001",
        "TPI-PROCESS-STAGES-001",
        "TPI-MATERIAL-RISK-001",
        "TPI-DATA-READINESS-001",
    }.issubset(task_ids)
    assert pack["aps_workflow_insights"][0]["workflow_stages"] == [
        "order_intake",
        "ERP_order_entry",
        "ERP_work_split",
        "APS_weaving_scheduling",
        "yarn_picking",
        "weaving_greige",
        "pre_treatment",
        "storage_before_dyeing",
        "dyeing_scheduling",
        "dyeing",
        "inspection_replenishment_if_failed",
        "cutting",
        "sewing",
        "packing_1",
        "needle_and_metal_detection",
        "packing_2",
        "finished_goods_storage",
        "container_loading",
    ]
    assert pack["aps_workflow_insights"][0]["system_boundaries"]["APS"] == "Only responsible for scheduling Tianpai's weaving portion."
    assert "not involved" in pack["aps_workflow_insights"][0]["system_boundaries"]["IOT"]
    governance = pack["training_governance"]
    assert governance["first_training_persona"]["role"] == "tianpai_general_manager"
    assert governance["answer_format"] == [
        "management_summary",
        "reason_and_evidence",
        "recommended_action",
    ]
    assert governance["kpi_priority"] == ["delivery", "quality", "cost"]
    assert governance["data_insufficiency_policy"]["allowed"] is True
    assert "standard_field_name (site_term)" in governance["terminology_policy"]["format"]
    assert "real data integration" in governance["automation_boundary"]["requires_human_confirmation"]
    assert governance["acceptance_standard"]["status"] == "iterative"

    required_memory_fields = {
        "scope",
        "tenant_id",
        "factory_id",
        "source",
        "retention_policy",
        "sensitivity_level",
        "promotion_status",
    }
    assert pack["hermes_memory_events"]
    assert all(required_memory_fields.issubset(event) for event in pack["hermes_memory_events"])
    assert all(event["scope"] == "tenant" for event in pack["hermes_memory_events"])
    assert all(event["tenant_id"] == "tianpai" for event in pack["hermes_memory_events"])
    assert all(event["promotion_status"] == "candidate" for event in pack["hermes_memory_events"])
    assert any(event["event_id"] == "MEM-TPI-004" and event["source"] == "meeting" for event in pack["hermes_memory_events"])
    assert any(event["event_id"] == "MEM-TPI-005" and event["source"] == "user feedback" for event in pack["hermes_memory_events"])

    assert "delivery date" in summary
    assert "order_id" in summary
    assert "APS Planned Task delivery-time attachment" in summary
    assert "produce_order_code" in summary
    assert "IOT currently does not participate" in summary
    assert "needle inspection and metal detection" in summary
    assert "Material Inventory Summary" in summary
    assert "TPI-MATERIAL-RISK-001" in summary
    assert "TPI-DATA-READINESS-001" in summary
    assert "delivery > quality > cost" in summary
    assert "standard_field_name (site_term)" in summary
    assert "Tianpai Training Governance" in changelog
    assert "Tianpai Actual Onsite Workflow" in changelog
    assert "Tianpai APS Workflow Fragment" in changelog
    assert "Tianpai Training Data Pack" in changelog
    assert "tianpai_training_pack_v0_1.json" in readme


def test_all_web_pages_include_bilingual_language_switch():
    web_root = Path("src/web_app")
    html_files = list(web_root.glob("*.html"))

    assert html_files
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        assert '/i18n.js?v=0.113.1' in content

    i18n_script = (web_root / "i18n.js").read_text(encoding="utf-8")
    assert "santoniDemoLanguage" in i18n_script
    assert "language-toggle" in i18n_script
    assert "Chinese / English" in (web_root / "README.md").read_text(encoding="utf-8")


def test_customer_home_renders_production_athena_cards():
    web_root = Path("src/web_app")
    page = (web_root / "index.html").read_text(encoding="utf-8")
    script = (web_root / "user-app.js").read_text(encoding="utf-8")
    readme = (web_root / "README.md").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert 'data-identity-role="production_manager"' in page
    assert 'data-identity-role="customer_equipment_engineer"' in page
    assert 'data-identity-role="designer"' in page
    assert 'data-prompt-role="production_manager"' in page
    assert "<h1>" in page and "</h1>" in page
    assert 'id="userChatForm"' in page
    assert 'id="userMessageInput"' in page
    assert 'id="gmWorkspace"' in page
    assert 'id="gmStoryEntry"' in page
    assert 'id="gmStoryCards"' in page
    assert 'id="gmRiskCards"' in page
    assert 'id="gmEvidenceReviewPanel"' in page
    assert 'id="gmEvidenceReviewCards"' in page
    assert 'id="gmServiceRiskPanel"' in page
    assert 'id="gmServiceRiskCards"' in page
    assert 'id="gmDemoReadinessPanel"' not in page
    assert 'id="gmDemoReadinessList"' not in page
    assert "Internal Demo Mode" not in page
    assert "Demo Readiness" not in page
    assert "Development Progress" not in page
    assert "raw JSON" not in page
    assert "payload" not in page.lower()
    assert 'id="gmFollowUpPanel"' in page
    assert 'id="gmFollowUpList"' in page
    assert 'id="gmFollowUpSummary"' in page
    assert 'id="gmQuestionForm"' not in page
    assert 'id="gmAgentOutput"' not in page
    assert "Santoni Athena" in page
    assert 'data-prompt-role="production_manager"' in page
    assert 'data-identity-role="production_manager"' in page
    assert "let currentRole = null" in script
    assert script.lstrip("\ufeff").startswith("(function () {")
    assert "let currentLanguage" not in script
    assert "let userConversationLanguage" in script
    assert "window.SantoniUserAppReady = true" in script
    assert "ensureIdentitySelected" in script
    assert "executive_answer" in script
    assert "renderGeneralManagerDashboard" in script
    assert "appendProductionAthenaAnswer" in script
    assert "production_manager" in script
    assert "dataset.promptRole" in script
    assert "production_athena" in script
    assert "gmEvidenceReviewPanel" in script
    assert "gmFollowUpPanel" in script
    assert "gmDailyBriefPanel" in script
    assert "formatObjectValue" in script
    assert 'currentRole = "production_manager"' in script
    assert "loadGeneralManagerDashboard" in script
    assert "renderGeneralManagerFollowUps" in script
    assert "renderGeneralManagerStoryEntry" in script
    assert "renderGeneralManagerEvidenceReview" in script
    assert "renderGeneralManagerServiceRisks" in script
    assert "renderGeneralManagerDemoReadiness" not in script
    assert "createGeneralManagerFollowUp" in script
    assert "updateGeneralManagerFollowUpStatus" in script
    assert "saveGeneralManagerFollowUpStatus" in script
    assert "normalizeProductionChatbiResponse" in script
    assert 'currentRole === "production_manager"' in script
    assert "await askGeneralManagerWorkspace(message" in script
    assert "/api/production/overview" in script
    assert "/api/production/chatbi" in script
    assert "/api/production/follow-up/review" in script
    assert "data-gm-drilldown" in script
    assert "data-gm-story-question" in script
    assert "data-gm-evidence-review-drilldown" in script
    assert "data-gm-follow-up" in script
    assert "data-gm-follow-up-status" in script
    assert "data-gm-follow-up-ask" in script
    assert "data-gm-service-drilldown" in script
    assert "data-gm-service-follow-up" in script
    assert "gm-user-evidence-details" in script
    assert "first_screen_service_risk" in script
    assert "internal_demo_readiness_mode" not in script
    assert "verification_process" in script
    assert "Athena 查证过程" in script
    assert "checked_objects" in script
    assert "findings" in script
    assert "cannot_conclude" in script
    assert "suggested_confirmation_owner" in script
    assert "read_only_boundary" in script
    assert "gmActiveFollowUpActionIds" in script
    assert "User page generated local follow-up candidate" in script
    assert "metadata" in script
    assert 'addBubble("user", cleanQuestion)' in script
    assert "raw payload" not in script.lower()
    assert "identity selection before effective chat" in readme
    assert "General Manager Follow-up Loop Demo" in readme
    assert "production-manager/order/delivery/KPI/root-cause" in readme
    assert "embedded Production workspace" in readme
    assert "same-page Santoni Athena root-cause drilldown panel" in readme
    assert "Delivery Risk Driver Guard v0.108.3" in readme
    assert "Evidence Review Queue v0.109.0" in readme
    assert "GM First Screen Hierarchy Polish v0.113.0" in readme
    assert "delivery status or quantity reconciliation candidates" in readme
    assert "Style_Component" in readme
    assert "athena_runtime_event" in readme
    assert "User-Page General Manager Agent Workspace" in changelog
    assert "Unified General Manager Conversation Flow" in changelog
    assert "General Manager Follow-up Loop Demo" in changelog
    assert "Customer Identity Selection Gate" in changelog
    assert "Athena Runtime Event Envelope" in changelog
    assert "Main Chat Production Manager Routing" in changelog
    assert "Evidence Review Queue" in changelog
    assert "GM First Screen Hierarchy Polish" in changelog


def test_developer_page_requires_explicit_identity_selection():
    web_root = Path("src/web_app")
    page = (web_root / "developer.html").read_text(encoding="utf-8")
    script = (web_root / "app.js").read_text(encoding="utf-8")
    readme = (web_root / "README.md").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert 'data-dev-role="production_manager"' in page
    assert 'data-dev-role="customer_equipment_engineer"' in page
    assert 'data-dev-role="designer"' in page
    assert 'data-dev-role="production_manager"' in page
    assert "Production Management</button>" not in page
    assert "Role: Select identity" in page
    assert "Role: Auto" not in page
    assert "let currentRole = null" in script
    assert "ensureDeveloperIdentitySelected" in script
    assert "developerRoleButtons" in script
    assert "production_manager" in script
    assert "Please select an identity first" in script
    assert "production_athena" in script
    assert "developerGmBriefLoaded" in script
    assert "loadDeveloperGeneralManagerBrief" in script
    assert "sendProductionChatbiMessage" in script
    assert "normalizeProductionChatbiResponse" in script
    assert 'currentRole === "production_manager"' in script
    assert 'fetch("/api/production/chatbi"' in script
    assert "Skill Execution Trace" in script
    assert 'href="/api/status"' in page
    assert 'href="/api/operating-model"' in page
    assert 'href="/api/project-docs"' in page
    assert "Please select an identity first" in script
    assert "已选择身份" in script
    assert "总经理" in script
    assert "总经理生产决策工作流" in script
    assert "developer/debug page require identity selection" in readme
    assert "Developer General Manager Flow Parity" in readme
    assert "User and Developer Identity Gate Feedback" in changelog
    assert "Developer Page API Interaction Fix" in changelog
    assert "Developer General Manager Flow Parity" in changelog


def test_status_endpoint_reports_active_llm_runtime_contract():
    server = Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    app = Path("src/web_app/app.js").read_text(encoding="utf-8")
    llm_client = Path("src/agent_core/llm_client.py").read_text(encoding="utf-8")

    assert '"active_llm_provider": llm_provider' in server
    assert '"active_llm_model": active_model' in server
    assert '"active_llm_enabled": active_enabled' in server
    assert 'os.environ[key] = value' in server
    assert "status.active_llm_provider" in app
    assert "status.active_llm_model" in app
    assert "status.active_llm_enabled" in app
    assert "os.environ[key.strip()] = value.strip()" in llm_client


def test_athena_structure_png_artifact_and_renderer_exist():
    png = Path("docs/athena_structure_v0.113.0.png")
    renderer = Path("scripts/render_athena_structure_png.py").read_text(encoding="utf-8")
    changelog = Path("src/web_app/changelog.html").read_text(encoding="utf-8")

    assert png.exists()
    assert png.stat().st_size > 10_000
    assert "Santoni Athena Current Structure" in renderer
    assert "athena_structure_v0.113.0.png" in renderer
    assert "Athena Structure PNG" in changelog


def test_athena_prd_v01_is_available_in_markdown_and_html():
    prd = Path("docs/product/athena_prd_v0.1.md").read_text(encoding="utf-8")
    athena_html = Path("docs/Athena.html").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    changelog = Path("src/web_app/changelog.html").read_text(encoding="utf-8")
    run_web_demo = Path("scripts/run_web_demo.py").read_text(encoding="utf-8")

    assert "Santoni Athena PRD v0.1" in prd
    assert "digital general manager" in prd
    assert "What are the three things I should handle first today?" in prd
    assert "Delivery risk" in prd
    assert "quality/replenishment" in prd
    assert "labor effective-hour" in prd
    assert "Athena must not" in prd
    assert "automatically modify scheduling" in prd.lower()
    assert 'id="prd-v01"' in athena_html
    assert 'id="prd-v01-detail"' in athena_html
    assert "docs/product/athena_prd_v0.1.md" in athena_html
    assert athena_html.index('id="prd-v01"') < athena_html.index('id="documents"')
    assert "Athena is a digital general manager for knitting factories." in athena_html
    assert "MVP Success Criteria" in athena_html
    assert "Within three minutes" in athena_html
    assert "athena_prd_v0.1.md" in readme
    assert "Athena PRD v0.1" in changelog
    assert "DOCS_ROOT" in run_web_demo
    assert "_send_docs_file" in run_web_demo
    assert "relative.startswith(\"docs/\")" in run_web_demo
    assert "mimetypes.guess_type" in run_web_demo


def test_production_page_defaults_to_chinese_customer_display():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")

    assert '<html lang="zh-CN">' in production_html
    assert "Athena GM Demo Mode" in production_html
    assert "今天我应该先盯哪三件事？" in production_html
    assert "What are the top three production priorities today?" in production_html
    assert '/production.js?v=0.113.1' in production_html
    assert 'id="skillRegistryPanel"' in production_html
    assert 'id="actualDataSnapshot"' in production_html
    assert 'id="stableDemoStoryPack"' in production_html
    assert 'id="mvpDemoStory"' in production_html
    assert 'id="mvpSuccessCheck"' in production_html
    assert 'id="prdAlignmentAudit"' in production_html
    assert 'id="permissionBoundary"' in production_html
    assert "MVP Demo Story" in production_html
    assert "MVP Success Check" in production_html
    assert "PRD Alignment Audit" in production_html
    assert "Mock / Tianpai APS Export" in production_html
    assert "Stable Demo Story Pack" in production_html
    assert "稳定演示故事包" in production_html
    assert "总经理最终确认" in production_html
    assert "attention_required" in production_script
    assert "Attention Required" in production_script or "attention_required" in production_script
    assert "renderMvpDemoStory" in production_script
    assert "renderStableDemoStoryPack" in production_script
    assert "renderMvpSuccessCheck" in production_script
    assert "renderPrdAlignmentAudit" in production_script
    assert "renderActualDataSnapshot" in production_script
    assert "renderSkillRegistry" in production_script
    assert "machine_style_spec_mismatch_candidate_count" in production_script
    assert "renderPermissionBoundary" in production_script
    assert "Final confirmation owner" in production_script
    assert "Production Console Chinese display" in (web_root / "changelog.html").read_text(encoding="utf-8")


def test_production_page_uses_site_flow_layout():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")

    assert "production site flow".lower() in (web_root / "changelog.html").read_text(encoding="utf-8").lower()
    assert "operationsStack" in production_html
    assert 'id="operationsStack"' in production_html
    assert "renderOperationsStack" in production_script
    assert "Backlog Orders" in production_script
    assert "Scheduling" in production_script
    assert "Fault Machines" in production_script
    assert "Average Yield" in production_script
    assert "Scrap" in production_script or "scrap" in production_script
    assert "APS / IOT Field Mapping" in production_html
    assert 'id="adapterContract"' in production_html
    assert "/api/production/adapter-contract" in production_script
    assert 'id="materialRiskPanel"' in production_html
    assert 'id="dataReadinessPanel"' in production_html
    assert 'id="questionBankPanel"' in production_html
    assert "renderMaterialRisk" in production_script
    assert "renderDataReadiness" in production_script
    assert "renderQuestionBank" in production_script
    assert "Tianpai Material Risk / Data Readiness" in (web_root / "changelog.html").read_text(encoding="utf-8")


def test_production_page_includes_santoni_athena_panel():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert "Santoni Athena" in production_html
    assert "order_id" in production_html
    assert 'id="chatbiForm"' in production_html
    assert "chatbiForm" in production_html
    assert "managementPriorityBrief" in production_html
    assert 'id="managementPriorityBrief"' in production_html
    assert 'id="gmThreeMinuteBrief"' in production_html
    assert "General Manager 3-Minute Brief" in production_html
    assert 'id="serviceRiskBrief"' in production_html
    assert "Service Risk" in production_html
    assert "Decision Loop" in production_html
    assert 'id="decisionLoop"' in production_html
    assert "/api/production/chatbi" in production_script
    assert "/api/production/priority-brief" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/demo-story-pack" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/internal-demo-candidate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/skills" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/follow-up" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/material-risk" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/data-readiness" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/question-bank" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/production/follow-up/review" in production_script
    assert "renderChatbi" in production_script
    assert "renderGmThreeMinuteBrief" in production_script
    assert "renderServiceRiskBrief" in production_script
    assert "gmDrilldownQuestion" in production_script
    assert "serviceDrilldownQuestion" in production_script
    assert "data-gm-question" in production_script
    assert "data-service-question" in production_script
    assert 'button[data-gm-question]' in production_script
    assert 'button[data-service-question]' in production_script
    assert "labor effective-hour risk" in production_script
    assert "人工有效工时风险" in production_script or "labor effective-hour risk" in production_script
    assert "gm-brief-details" in production_script
    assert "skill_execution_trace" in production_script
    assert "renderSkillExecutionTrace" in production_script
    assert "renderPrioritySkills" in production_script
    assert "evidence-chip" in production_script
    assert "Full Evidence and Data Gaps" in production_script
    assert "risk_level_label" in production_script
    assert "linked_risk_card_id" in production_script
    assert "pending_confirmation" in production_script
    assert "unable_to_process" in production_script
    assert "data-follow-up-status=\"confirmed\"" in production_script
    assert "data-follow-up-status=\"unable_to_process\"" in production_script
    assert "gm-summary-lines" in production_script
    assert "summary_zh" in production_script
    assert "Continue Asking" in production_script
    assert "Drill Down Service Risk" in production_script
    assert "Candidate Only" in production_html
    assert "never dispatches automatically" in production_script
    assert "renderManagementPriorityBrief" in production_script
    assert "renderDecisionLoop" in production_script
    assert "stable_demo_story_pack" in production_script
    assert "internal_demo_candidate" in production_script
    assert "renderInternalDemoCandidate" in production_script
    assert "data-demo-story-question" in production_script
    assert 'button[data-demo-story-question]' in production_script
    assert "management_priority_brief" in production_script
    assert "decision_loop" in production_script
    assert "executive_answer" in production_script
    assert "executive_answer" in production_script
    assert "General Manager 3-Minute Brief" in production_html
    assert "Athena Skill Layer" in production_html
    assert 'id="internalDemoCandidatePanel"' in production_html
    assert "Internal Demo Candidate" in production_html
    assert "Skill Registry" in production_html
    assert "GM Demo Mode UI" in changelog
    assert "Athena Skill Registry" in changelog
    assert "Skill Execution Trace" in changelog
    assert "First-Screen Service Risk Brief" in changelog
    assert "General Manager 3-Minute Brief" in changelog
    assert "Risk Card Drill-Down Actions" in changelog
    assert "PRD Risk-Card Evidence Details" in changelog
    assert "PRD Follow-Up Status Lifecycle" in changelog
    assert "PRD First-Screen Management Summary" in changelog
    assert "gm-brief-grid" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "gm-brief-actions" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "gm-brief-details" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "gm-summary-lines" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "evidence-chip" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "skill-chip" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "skill-trace-step" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "service-risk-grid" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "stable-demo-story-pack" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "stable-demo-card-grid" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "internal-demo-candidate" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "internal-demo-grid" in (web_root / "styles.css").read_text(encoding="utf-8")
    assert "Internal Demo Candidate Report" in changelog
    assert "Data Request Wizard" in changelog
    assert "Hermes Training / Memory Review" in changelog
    assert "Santoni Athena Production Insight Naming" in changelog
    assert "Production Management Priority Engine" in changelog
    assert "Production Decision Loop Follow-up Engine" in changelog


def test_hermes_integration_workflow_outputs_adapter_contract_without_live_credentials():
    result = HermesIntegrationWorkflow().overview()
    contract = result["adapter_contract"]
    serialized = json.dumps(result, ensure_ascii=False).lower()

    assert result["workflow_template"]["template_id"] == "athena.hermes_integration.v1"
    assert result["workflow_instance"]["version"] == "v0.113.1"
    assert result["workflow_instance"]["read_only"] is True
    assert result["workflow_instance"]["real_hermes_connected"] is False
    assert result["workflow_instance"]["write_actions_blocked"] is True
    assert result["organization_memory_playbook"]["schema_id"] == "athena.organization_memory_playbook.v1"
    assert result["organization_memory_playbook"]["version"] == "v0.113.1"
    assert result["organization_memory_playbook"]["source_decision_loop_id"].startswith("PROD-DECISION-LOOP")
    assert result["organization_memory_playbook"]["playbook_kpis"]["candidate_count"] == 8
    assert result["organization_memory_playbook"]["playbook_kpis"]["regression_case_candidate_count"] == 8
    assert all(item["evidence_refs"] for item in result["organization_memory_playbook"]["playbook_candidates"])
    assert all(item["memory_event_candidate"]["tenant_id"] == "tianpai" for item in result["organization_memory_playbook"]["playbook_candidates"])
    assert all(item["ready_for_playbook_review"] is False for item in result["organization_memory_playbook"]["playbook_candidates"])
    assert "write_live_hermes_memory" in result["organization_memory_playbook"]["blocked_actions"]
    assert contract["contract_id"] == "athena.hermes_agent_core_contract.v1"
    assert contract["adapter_status"] == "mock_contract"
    assert "store_hermes_token_in_repo" in result["workflow_instance"]["blocked_actions"]
    assert "write_to_aps_or_iot" in result["workflow_instance"]["blocked_actions"]
    assert {
        "scope",
        "tenant_id",
        "factory_id",
        "source",
        "retention_policy",
        "sensitivity_level",
        "promotion_status",
    }.issubset(result["workflow_template"]["memory_event_schema"]["required_fields"])
    assert "api key" in serialized
    assert "password" in serialized
    assert "1qaz" not in serialized
    assert len(result["memory_events"]) >= 4
    required_memory_fields = set(result["workflow_template"]["memory_event_schema"]["required_fields"])
    allowed_scopes = set(result["workflow_template"]["memory_event_schema"]["scope_values"])
    allowed_sources = set(result["workflow_template"]["memory_event_schema"]["source_values"])
    allowed_promotions = set(result["workflow_template"]["memory_event_schema"]["promotion_status_values"])
    assert all(required_memory_fields.issubset(event) for event in result["memory_events"])
    assert {event["scope"] for event in result["memory_events"]}.issubset(allowed_scopes)
    assert {event["source"] for event in result["memory_events"]}.issubset(allowed_sources)
    assert {event["promotion_status"] for event in result["memory_events"]}.issubset(allowed_promotions)
    assert all(event["tenant_id"] is None and event["factory_id"] is None for event in result["memory_events"])
    assert any(event["scope"] == "domain" for event in result["memory_events"])
    assert len(result["development_suggestions"]) >= 3
    assert all(item["evidence_refs"] for item in result["development_suggestions"])
    assert any(tool["tool_id"] == "tool.agent_core.production_overview" for tool in result["tool_registry_candidates"])
    assert any(item["kpi"] == "playbook_candidate_count" for item in result["kpi_log"])


def test_hermes_suggest_filters_focus_and_keeps_human_review_gate():
    result = HermesIntegrationWorkflow().suggest({"focus": "production"})

    assert result["agent"]["agent_id"] == "athena.hermes_development_suggestion_agent.v1"
    assert result["analysis_request"]["write_actions_blocked"] is True
    assert result["analysis_request"]["real_hermes_connected"] is False
    assert result["suggestions"]
    assert all("production" in item["scope"].lower() or "production" in item["reason"].lower() for item in result["suggestions"])
    assert all(item["human_review_required"] is True for item in result["suggestions"])
    assert "auto_modify_code_without_human_review" in result["blocked_actions"]


def test_hermes_playbook_review_promotes_only_closed_evidence_backed_candidates():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        production_review_path = temp_path / "production_follow_up_reviews.json"
        playbook_review_path = temp_path / "hermes_playbook_reviews.json"
        production_workflow = ProductionOperationsWorkflow(follow_up_store_path=production_review_path)
        initial = production_workflow.follow_up_loop()
        action_id = initial["decision_loop"]["action_items"][0]["action_id"]

        production_workflow.apply_follow_up_review(
            {
                "action_id": action_id,
                "review_status": "closed",
                "review_note": "Closed after production review.",
                "evidence_note": "Inspection row accepted and KPI recovered in next review.",
            }
        )

        workflow = HermesIntegrationWorkflow(
            playbook_review_path=playbook_review_path,
            production_workflow=production_workflow,
        )
        playbook = workflow.playbook()
        candidate = next(
            item
            for item in playbook["organization_memory_playbook"]["playbook_candidates"]
            if item["source_action_id"] == action_id
        )
        assert candidate["ready_for_playbook_review"] is True
        assert candidate["readiness"] == "ready_for_playbook_review"

        updated = workflow.apply_playbook_review(
            {
                "candidate_id": candidate["candidate_id"],
                "review_status": "approved",
                "review_note": "Approved as Tianpai tenant playbook pattern.",
            }
        )
        store = json.loads(playbook_review_path.read_text(encoding="utf-8"))
        promoted = next(
            item
            for item in updated["organization_memory_playbook"]["playbook_candidates"]
            if item["candidate_id"] == candidate["candidate_id"]
        )
        assert updated["organization_memory_playbook"]["review_state"]["review_count"] == 1
        assert updated["organization_memory_playbook"]["playbook_kpis"]["approved_count"] == 1
        assert promoted["promotion_status"] == "approved"
        assert promoted["memory_event_candidate"]["promotion_status"] == "approved"
        assert store["metadata_only"] is True
        assert store["reviews"][0]["contains_raw_file"] is False
        assert store["reviews"][0]["contains_credentials"] is False
        assert "write_live_hermes_memory" in updated["blocked_actions"]

        try:
            workflow.apply_playbook_review(
                {
                    "candidate_id": candidate["candidate_id"],
                    "review_status": "reviewed",
                    "review_note": "password should not be saved",
                }
            )
        except ValueError as exc:
            assert "credentials" in str(exc)
        else:
            raise AssertionError("credential-like playbook review note was not rejected")

    with TemporaryDirectory() as temp_dir:
        workflow = HermesIntegrationWorkflow(playbook_review_path=Path(temp_dir) / "blocked_playbook_reviews.json")
        candidate = workflow.playbook()["organization_memory_playbook"]["playbook_candidates"][0]
        assert candidate["ready_for_playbook_review"] is False
        try:
            workflow.apply_playbook_review(
                {
                    "candidate_id": candidate["candidate_id"],
                    "review_status": "approved",
                    "review_note": "Trying to approve too early.",
                }
            )
        except ValueError as exc:
            assert "cannot be approved" in str(exc)
        else:
            raise AssertionError("unclosed playbook candidate was approved")


def test_hermes_page_exposes_integration_console_and_language_switch():
    web_root = Path("src/web_app")
    page = (web_root / "hermes.html").read_text(encoding="utf-8")
    script = (web_root / "hermes.js").read_text(encoding="utf-8")
    docs = (web_root / "docs.html").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert "Hermes Integration Console" in page
    assert "Mock contract only" in page
    assert "Organization Memory / Playbook Engine" in page
    assert 'id="hermesPlaybook"' in page
    assert '/i18n.js?v=0.113.1' in page
    assert '/hermes.js?v=0.113.1' in page
    assert "/api/hermes/overview" in script
    assert "/api/hermes/suggest" in script
    assert "/api/hermes/playbook/review" in script
    assert "renderHermesPlaybook" in script
    assert "ready_for_playbook_review" in script
    assert "retention_policy" in script
    assert "promotion_status" in script
    assert "/api/hermes/playbook" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "Open Hermes Integration Console" in docs
    assert "Hermes Memory Event Governance" in changelog
    assert "Hermes Organization Memory Playbook Engine" in changelog


def test_training_automation_workflow_runs_auto_evaluation_and_json_payload():
    with TemporaryDirectory() as temp_dir:
        review_path = Path(temp_dir) / "training_task_reviews.json"
        result = TrainingAutomationWorkflow(review_store_path=review_path).run({"mode": "auto"})
        summary = result["training_overview"]
        payload = result["hermes_result_payload"]
        serialized = json.dumps(result, ensure_ascii=False).lower()

        assert result["workflow_template"]["template_id"] == "athena.training_automation.v1"
        assert result["workflow_instance"]["version"] == "v0.113.1"
        assert result["workflow_instance"]["automation_mode"] == "local_auto_evaluation"
        assert result["workflow_instance"]["real_hermes_connected"] is False
        assert result["workflow_instance"]["model_weight_finetuning"] is False
        assert result["workflow_instance"]["write_actions_blocked"] is True
        assert summary["automation_state"] == "auto_training_available"
        assert summary["target_persona"] == "tianpai_general_manager"
        assert summary["total_task_count"] >= 9
        assert summary["auto_evaluated_task_count"] == summary["total_task_count"]
        assert summary["passed_task_count"] >= 1
        assert summary["needs_data_task_count"] >= 1
        assert summary["failed_task_count"] == 0
        assert summary["average_score"] >= 0.75
        assert payload["schema"] == "hermes.training_result.v1"
        assert payload["scope"] == "tenant"
        assert payload["tenant_id"] == "tianpai"
        assert payload["promotion_status"] == "candidate"
        assert result["playbook_regression_queue"]["schema_id"] == "athena.playbook_regression_queue.v1"
        assert result["playbook_regression_queue"]["candidate_count"] == 8
        assert result["playbook_regression_queue"]["ready_regression_count"] == 0
        assert result["playbook_regression_queue"]["blocked_regression_count"] == 8
        assert all(item["ready_for_regression"] is False for item in result["playbook_regression_queue"]["regression_candidates"])
        assert "auto_generate_regression_without_approved_playbook" in result["playbook_regression_queue"]["blocked_actions"]
        assert payload["playbook_regression_queue"]["blocked_regression_count"] == 8
        assert all(item["auto_evaluated"] is True for item in result["training_tasks"])
        assert all(item["evaluation_checks"]["resolved_evidence_refs"] for item in result["training_tasks"])
        assert any(item["status"] == "needs_data" for item in result["training_tasks"])
        assert any(item["type"] == "data_request" for item in result["codex_patch_queue"])
        assert any(item["source"] == "data_gap" for item in result["next_training_tasks"])
        assert any(item["kpi"] == "playbook_regression_candidate_count" for item in result["kpi_log"])
        assert "1qaz" not in serialized
        assert "password" not in serialized
        assert "store_credentials_or_tokens" in result["blocked_actions"]


def test_training_playbook_regression_queue_promotes_only_approved_playbooks():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        follow_up_path = temp_path / "production_follow_up_reviews.json"
        playbook_review_path = temp_path / "hermes_playbook_reviews.json"
        training_review_path = temp_path / "training_task_reviews.json"

        production = ProductionOperationsWorkflow(follow_up_store_path=follow_up_path)
        action_id = production.follow_up_loop()["decision_loop"]["action_items"][0]["action_id"]
        production.apply_follow_up_review(
            {
                "action_id": action_id,
                "review_status": "closed",
                "review_note": "Owner closed the issue after checking evidence.",
                "evidence_note": "Accepted machine alarm and defect inspection evidence.",
            }
        )
        hermes = HermesIntegrationWorkflow(
            playbook_review_path=playbook_review_path,
            production_workflow=production,
        )
        candidate = next(
            item
            for item in hermes.playbook()["organization_memory_playbook"]["playbook_candidates"]
            if item["ready_for_playbook_review"]
        )
        hermes.apply_playbook_review(
            {
                "candidate_id": candidate["candidate_id"],
                "review_status": "approved",
                "review_note": "Approved as local Tianpai regression playbook.",
            }
        )

        workflow = TrainingAutomationWorkflow(
            review_store_path=training_review_path,
            hermes_workflow=hermes,
        )
        result = workflow.run({"mode": "auto"})
        queue = result["playbook_regression_queue"]

        assert queue["schema_id"] == "athena.playbook_regression_queue.v1"
        assert queue["ready_regression_count"] == 1
        assert queue["blocked_regression_count"] == 7
        assert any(item["ready_for_regression"] is True for item in queue["regression_candidates"])
        assert any(item["type"] == "playbook_regression_candidate" for item in result["codex_patch_queue"])
        assert any(item["source"] == "approved_playbook" for item in result["next_training_tasks"])
        assert workflow.playbook_regression()["workflow_instance"]["scenario"] == "playbook_regression_queue"
        regression = workflow.regression_run()
        assert regression["workflow_instance"]["scenario"] == "automatic_regression_run"
        assert regression["regression_overview"]["playbook_ready_case_count"] == 1
        assert any(item["source"] == "approved_playbook" and item["regression_status"] == "passed" for item in regression["regression_cases"])
        assert any(item["source"] == "blocked_playbook_candidate" and item["regression_status"] == "blocked" for item in regression["regression_cases"])
        gate = workflow.regression_gate()
        assert gate["workflow_instance"]["scenario"] == "regression_gate"
        assert gate["regression_gate"]["schema_id"] == "athena.regression_gate.v1"
        assert gate["regression_gate"]["automatic_loop_allowed"] is True
        assert gate["regression_gate"]["human_review_required"] is True
        assert gate["regression_gate"]["blocked_case_count"] == 7
        assert gate["hermes_feedback_payload"]["schema"] == "hermes.regression_gate_feedback.v1"
        assert any(item["type"] == "continue_next_iteration" for item in gate["codex_next_action_queue"])
        handoff = workflow.next_loop_handoff()
        assert handoff["workflow_instance"]["scenario"] == "next_loop_handoff"
        assert handoff["next_loop_handoff"]["schema_id"] == "athena.next_loop_handoff.v1"
        assert handoff["next_loop_handoff"]["automatic_loop_allowed"] is True
        assert handoff["next_loop_handoff"]["queue_summary"]["human_review_count"] >= 2
        assert handoff["hermes_handoff_payload"]["schema"] == "hermes.next_loop_handoff.v1"
        assert any(item["type"] == "prepare_next_training_iteration" for item in handoff["next_loop_handoff"]["automatic_work_queue"])
        review_item = handoff["next_loop_handoff"]["human_review_queue"][0]
        handoff_review = workflow.apply_handoff_review(
            {
                "handoff_item_id": review_item["handoff_item_id"],
                "review_status": "deferred",
                "review_note": "Keep this blocked until playbook evidence is closed.",
                "item_type": review_item["type"],
                "source": review_item["source"],
                "related_case_id": review_item.get("related_case_id", ""),
            }
        )
        refreshed_handoff = workflow.next_loop_handoff()
        refreshed_item = next(
            item
            for item in refreshed_handoff["next_loop_handoff"]["human_review_queue"]
            if item["handoff_item_id"] == review_item["handoff_item_id"]
        )
        assert handoff_review["handoff_review_state"]["review_count"] == 1
        assert refreshed_item["handoff_review"]["review_status"] == "deferred"
        assert refreshed_handoff["next_loop_handoff"]["queue_summary"]["handoff_deferred_count"] == 1
        assert handoff_review["handoff_review"]["contains_raw_file"] is False
        assert handoff_review["handoff_review"]["contains_credentials"] is False
        closure = workflow.next_loop_closure()
        assert closure["workflow_instance"]["scenario"] == "next_loop_closure_gate"
        assert closure["next_loop_closure"]["schema_id"] == "athena.next_loop_closure_gate.v1"
        assert closure["next_loop_closure"]["local_iteration_allowed"] is True
        assert closure["next_loop_closure"]["closure_complete"] is False
        assert closure["next_loop_closure"]["open_item_count"] >= 1
        assert closure["hermes_closure_payload"]["schema"] == "hermes.next_loop_closure_gate.v1"
        proposal = workflow.iteration_proposal()
        assert proposal["workflow_instance"]["scenario"] == "training_iteration_proposal"
        assert proposal["training_iteration_proposal"]["schema_id"] == "athena.training_iteration_proposal.v1"
        assert proposal["training_iteration_proposal"]["proposal_ready"] is True
        assert proposal["training_iteration_proposal"]["open_watch_item_count"] >= 1
        assert proposal["hermes_iteration_payload"]["schema"] == "hermes.training_iteration_proposal.v1"
        assert "auto_execute_training_iteration_proposal" in proposal["training_iteration_proposal"]["blocked_actions"]
        proposal_review = workflow.apply_iteration_proposal_review(
            {
                "proposal_id": proposal["training_iteration_proposal"]["proposal_id"],
                "review_status": "approved_for_codex_queue",
                "review_note": "Approved for future queue preparation only.",
                "proposal_status": proposal["training_iteration_proposal"]["proposal_status"],
                "task_seed_count": proposal["training_iteration_proposal"]["task_seed_count"],
                "open_watch_item_count": proposal["training_iteration_proposal"]["open_watch_item_count"],
            }
        )
        reviewed_proposal = workflow.iteration_proposal()
        assert proposal_review["proposal_review_state"]["approved_for_codex_queue_count"] == 1
        assert reviewed_proposal["training_iteration_proposal"]["proposal_review"]["review_status"] == "approved_for_codex_queue"
        assert reviewed_proposal["training_iteration_proposal"]["approved_for_codex_queue"] is True
        assert reviewed_proposal["training_iteration_proposal"]["next_iteration_contract"]["code_change_automatic"] is False
        packets = workflow.codex_work_packets()
        packet_queue = packets["codex_work_packet_queue"]
        assert packets["workflow_instance"]["scenario"] == "codex_work_packet_queue"
        assert packet_queue["schema_id"] == "athena.codex_work_packet_queue.v1"
        assert packet_queue["queue_ready"] is True
        assert packet_queue["packet_count"] >= 1
        assert packets["hermes_work_packet_payload"]["schema"] == "hermes.codex_work_packet_queue.v1"
        assert "auto_execute_codex_work_packet" in packet_queue["blocked_actions"]
        assert all(packet["code_change_automatic"] is False for packet in packet_queue["work_packets"])
        patch_contract = workflow.codex_patch_queue()
        patch_queue = patch_contract["codex_patch_queue_contract"]
        assert patch_contract["workflow_instance"]["scenario"] == "codex_patch_queue_contract"
        assert patch_queue["schema_id"] == "athena.codex_patch_queue_contract.v1"
        assert patch_queue["queue_ready"] is True
        assert patch_queue["patch_candidate_count"] >= 1
        assert patch_contract["hermes_patch_queue_payload"]["schema"] == "hermes.codex_patch_queue_contract.v1"
        assert "auto_apply_codex_patch" in patch_queue["blocked_actions"]
        assert all(candidate["code_change_automatic"] is False for candidate in patch_queue["patch_candidates"])
        execution_gate_payload = workflow.codex_execution_gate()
        execution_gate = execution_gate_payload["codex_execution_gate"]
        assert execution_gate_payload["workflow_instance"]["scenario"] == "codex_execution_gate"
        assert execution_gate["schema_id"] == "athena.codex_execution_gate.v1"
        assert execution_gate["gate_ready"] is True
        assert execution_gate["automatic_execution_allowed"] is False
        assert execution_gate["human_confirmation_required"] is True
        assert execution_gate["execution_candidate_count"] >= 1
        assert execution_gate_payload["hermes_execution_gate_payload"]["schema"] == "hermes.codex_execution_gate.v1"
        assert "auto_execute_codex_patch" in execution_gate["blocked_actions"]
        execution_candidate = execution_gate["execution_candidates"][0]
        execution_review = workflow.apply_codex_execution_review(
            {
                "execution_candidate_id": execution_candidate["execution_candidate_id"],
                "review_status": "approved_for_worktree_preparation",
                "review_note": "Approve metadata-only worktree preparation; do not execute automatically.",
                "source_patch_candidate_id": execution_candidate["source_patch_candidate_id"],
                "source_packet_id": execution_candidate["source_packet_id"],
                "gate_status": execution_gate["gate_status"],
                "candidate_type": execution_candidate["type"],
                "priority": execution_candidate["priority"],
            }
        )
        reviewed_execution_gate = workflow.codex_execution_gate()
        reviewed_candidate = reviewed_execution_gate["codex_execution_gate"]["execution_candidates"][0]
        assert execution_review["execution_review_state"]["approved_for_worktree_preparation_count"] == 1
        assert reviewed_candidate["execution_review"]["review_status"] == "approved_for_worktree_preparation"
        assert reviewed_candidate["worktree_preparation_allowed"] is True
        assert reviewed_execution_gate["codex_execution_gate"]["automatic_execution_allowed"] is False
        worktree_prep = workflow.codex_worktree_preparation_queue()
        worktree_queue = worktree_prep["codex_worktree_preparation_queue"]
        assert worktree_prep["workflow_instance"]["scenario"] == "codex_worktree_preparation_queue"
        assert worktree_queue["schema_id"] == "athena.codex_worktree_preparation_queue.v1"
        assert worktree_queue["queue_ready"] is True
        assert worktree_queue["preparation_task_count"] >= 1
        assert worktree_prep["hermes_worktree_preparation_payload"]["schema"] == "hermes.codex_worktree_preparation_queue.v1"
        assert "auto_create_codex_worktree" in worktree_queue["blocked_actions"]
        assert all(task["worktree_creation_automatic"] is False for task in worktree_queue["preparation_tasks"])
        launch_payload = workflow.codex_worktree_launch_gate()
        launch_gate = launch_payload["codex_worktree_launch_gate"]
        assert launch_payload["workflow_instance"]["scenario"] == "codex_worktree_launch_gate"
        assert launch_gate["schema_id"] == "athena.codex_worktree_launch_gate.v1"
        assert launch_gate["launch_ready"] is True
        assert launch_gate["launch_request_count"] >= 1
        assert launch_payload["hermes_worktree_launch_payload"]["schema"] == "hermes.codex_worktree_launch_gate.v1"
        assert "auto_launch_codex_worktree" in launch_gate["blocked_actions"]
        assert all(request["worktree_creation_automatic"] is False for request in launch_gate["launch_requests"])
        assert all(request["patch_application_automatic"] is False for request in launch_gate["launch_requests"])
        launch_request = launch_gate["launch_requests"][0]
        result = workflow.apply_codex_worktree_result(
            {
                "launch_request_id": launch_request["launch_request_id"],
                "result_status": "validation_passed",
                "result_summary": "Small fix completed in user-launched Codex worktree.",
                "source_preparation_task_id": launch_request["source_preparation_task_id"],
                "source_execution_candidate_id": launch_request["source_execution_candidate_id"],
                "source_patch_candidate_id": launch_request["source_patch_candidate_id"],
                "source_packet_id": launch_request["source_packet_id"],
                "changed_files": ["src/agent_core/workflows/training_automation_workflow.py", "tests/test_main_agent.py"],
                "validation_results": [
                    {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed"},
                    {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed"},
                ],
                "blocked_actions": ["commit", "push", "open_pr"],
            }
        )
        assert result["codex_worktree_result"]["validation_contract"]["contract_complete"] is True
        result_payload = workflow.codex_worktree_results()
        result_intake = result_payload["codex_worktree_result_intake"]
        assert result_payload["workflow_instance"]["scenario"] == "codex_worktree_result_intake"
        assert result_intake["schema_id"] == "athena.codex_worktree_result_intake.v1"
        assert result_intake["intake_status"] == "worktree_result_validation_passed"
        assert result_intake["result_count"] == 1
        assert result_intake["automatic_merge_allowed"] is False
        assert result_payload["hermes_worktree_result_payload"]["schema"] == "hermes.codex_worktree_result_intake.v1"
        assert "auto_merge_codex_worktree_result" in result_intake["blocked_actions"]
        review_gate_payload = workflow.codex_worktree_result_review_gate()
        review_gate = review_gate_payload["codex_worktree_result_review_gate"]
        assert review_gate_payload["workflow_instance"]["scenario"] == "codex_worktree_result_review_gate"
        assert review_gate["schema_id"] == "athena.codex_worktree_result_review_gate.v1"
        assert review_gate["gate_status"] == "ready_for_worktree_result_review"
        assert review_gate["review_candidate_count"] == 1
        assert review_gate["automatic_promotion_allowed"] is False
        assert review_gate_payload["hermes_worktree_result_review_payload"]["schema"] == "hermes.codex_worktree_result_review_gate.v1"
        assert "auto_promote_worktree_result_to_regression" in review_gate["blocked_actions"]
        result_review = workflow.apply_codex_worktree_result_review(
            {
                "launch_request_id": launch_request["launch_request_id"],
                "review_status": "approved_for_regression_and_memory",
                "review_note": "Approved as metadata-only regression and Hermes memory candidates.",
                "result_status": "validation_passed",
                "changed_file_count": 2,
                "validation_contract_complete": True,
            }
        )
        assert result_review["codex_worktree_result_review_state"]["approved_for_regression_baseline_count"] == 1
        reviewed_gate = workflow.codex_worktree_result_review_gate()["codex_worktree_result_review_gate"]
        assert reviewed_gate["gate_status"] == "result_review_approved_for_promotion_candidates"
        assert reviewed_gate["regression_promotion_candidate_count"] == 1
        assert reviewed_gate["hermes_memory_candidate_count"] == 1
        assert reviewed_gate["automatic_promotion_allowed"] is False
        promotion_payload = workflow.codex_promotion_candidates()
        promotion_queue = promotion_payload["codex_promotion_candidate_queue"]
        assert promotion_payload["workflow_instance"]["scenario"] == "codex_promotion_candidate_queue"
        assert promotion_queue["schema_id"] == "athena.codex_promotion_candidate_queue.v1"
        assert promotion_queue["queue_status"] == "ready_for_promotion_candidate_handoff"
        assert promotion_queue["queue_ready"] is True
        assert promotion_queue["regression_promotion_candidate_count"] == 1
        assert promotion_queue["hermes_memory_promotion_candidate_count"] == 1
        assert promotion_queue["automatic_promotion_allowed"] is False
        assert promotion_payload["hermes_promotion_candidate_payload"]["schema"] == "hermes.codex_promotion_candidate_queue.v1"
        assert "auto_promote_regression_baseline" in promotion_queue["blocked_actions"]
        approval_gate_payload = workflow.codex_promotion_approval_gate()
        approval_gate = approval_gate_payload["codex_promotion_approval_gate"]
        assert approval_gate_payload["workflow_instance"]["scenario"] == "codex_promotion_approval_gate"
        assert approval_gate["schema_id"] == "athena.codex_promotion_approval_gate.v1"
        assert approval_gate["gate_status"] == "ready_for_promotion_approval"
        assert approval_gate["promotion_candidate_count"] == 2
        assert approval_gate["pending_approval_count"] == 2
        assert approval_gate["automatic_execution_allowed"] is False
        assert approval_gate_payload["hermes_promotion_approval_payload"]["schema"] == "hermes.codex_promotion_approval_gate.v1"
        regression_candidate = promotion_queue["regression_baseline_promotion_candidates"][0]
        memory_candidate = promotion_queue["hermes_memory_promotion_candidates"][0]
        workflow.apply_codex_promotion_approval(
            {
                "promotion_candidate_id": regression_candidate["promotion_candidate_id"],
                "promotion_type": regression_candidate["promotion_type"],
                "launch_request_id": regression_candidate["launch_request_id"],
                "source_patch_candidate_id": regression_candidate["source_patch_candidate_id"],
                "source_packet_id": regression_candidate["source_packet_id"],
                "review_status": "approved_for_future_promotion",
                "review_note": "Approved for future regression baseline promotion only.",
                "changed_file_count": regression_candidate["changed_file_count"],
            }
        )
        memory_approval = workflow.apply_codex_promotion_approval(
            {
                "promotion_candidate_id": memory_candidate["promotion_candidate_id"],
                "promotion_type": memory_candidate["promotion_type"],
                "launch_request_id": memory_candidate["launch_request_id"],
                "source_patch_candidate_id": memory_candidate["source_patch_candidate_id"],
                "source_packet_id": memory_candidate["source_packet_id"],
                "review_status": "approved_for_future_promotion",
                "review_note": "Approved for future Hermes memory write only.",
                "changed_file_count": memory_candidate["changed_file_count"],
            }
        )
        assert memory_approval["codex_promotion_approval_state"]["approved_for_future_promotion_count"] == 2
        approved_gate = workflow.codex_promotion_approval_gate()["codex_promotion_approval_gate"]
        assert approved_gate["gate_status"] == "promotion_candidates_approved_for_future_action"
        assert approved_gate["approved_future_action_count"] == 2
        assert approved_gate["regression_future_action_count"] == 1
        assert approved_gate["hermes_memory_future_action_count"] == 1
        assert approved_gate["future_action_plan"][0]["execution_status"] == "approved_but_not_executed"
        assert approved_gate["automatic_execution_allowed"] is False
        assert "auto_execute_codex_promotion" in approved_gate["blocked_actions"]
        handoff_payload = workflow.codex_promotion_handoff()
        handoff = handoff_payload["codex_promotion_handoff_queue"]
        assert handoff_payload["workflow_instance"]["scenario"] == "codex_promotion_handoff_queue"
        assert handoff["schema_id"] == "athena.codex_promotion_handoff_queue.v1"
        assert handoff["handoff_status"] == "ready_for_manual_promotion_handoff"
        assert handoff["handoff_ready"] is True
        assert handoff["handoff_item_count"] == 2
        assert handoff["regression_handoff_count"] == 1
        assert handoff["hermes_memory_handoff_count"] == 1
        assert handoff["automatic_execution_allowed"] is False
        assert all(item["manual_execution_required"] is True for item in handoff["handoff_items"])
        assert all(item["automatic_execution_allowed"] is False for item in handoff["handoff_items"])
        assert handoff_payload["hermes_promotion_handoff_payload"]["schema"] == "hermes.codex_promotion_handoff_queue.v1"
        assert "auto_execute_codex_promotion_handoff" in handoff["blocked_actions"]
        readiness_payload = workflow.codex_promotion_execution_readiness()
        readiness = readiness_payload["codex_promotion_execution_readiness_gate"]
        assert readiness_payload["workflow_instance"]["scenario"] == "codex_promotion_execution_readiness_gate"
        assert readiness["schema_id"] == "athena.codex_promotion_execution_readiness_gate.v1"
        assert readiness["readiness_status"] == "blocked_until_execution_prerequisites_confirmed"
        assert readiness["readiness_ready"] is False
        assert readiness["readiness_item_count"] == 2
        assert readiness["blocked_readiness_item_count"] == 2
        assert readiness["regression_readiness_count"] == 1
        assert readiness["hermes_memory_readiness_count"] == 1
        assert readiness["automatic_execution_allowed"] is False
        assert all(item["automatic_execution_allowed"] is False for item in readiness["readiness_items"])
        assert any("live_hermes_endpoint" in item["missing_readiness_inputs"] for item in readiness["readiness_items"])
        assert readiness_payload["hermes_promotion_execution_readiness_payload"]["schema"] == "hermes.codex_promotion_execution_readiness_gate.v1"
        assert "auto_execute_promotion_readiness_gate" in readiness["blocked_actions"]
        for item in readiness["readiness_items"]:
            review = workflow.apply_codex_promotion_readiness_review(
                {
                    "readiness_item_id": item["readiness_item_id"],
                    "source_handoff_id": item["source_handoff_id"],
                    "promotion_candidate_id": item["promotion_candidate_id"],
                    "promotion_type": item["promotion_type"],
                    "review_status": "confirmed_ready_for_manual_execution",
                    "review_note": "Confirmed metadata-only execution prerequisites.",
                    "confirmed_inputs": item["original_missing_readiness_inputs"],
                    "validation_summary": "compileall and harness validation confirmed.",
                    "rollback_summary": "Rollback plan confirmed before manual execution.",
                    "execution_evidence_plan": "Capture final execution evidence after manual confirmation.",
                }
            )
            assert review["codex_promotion_readiness_review"]["automatic_execution_allowed"] is False
            assert review["codex_promotion_readiness_review_state"]["readiness_review_count"] >= 1
        reviewed_readiness_payload = workflow.codex_promotion_execution_readiness()
        reviewed_readiness = reviewed_readiness_payload["codex_promotion_execution_readiness_gate"]
        assert reviewed_readiness["readiness_status"] == "ready_for_manual_execution_confirmation"
        assert reviewed_readiness["readiness_ready"] is True
        assert reviewed_readiness["blocked_readiness_item_count"] == 0
        assert reviewed_readiness["confirmed_readiness_item_count"] == 2
        assert reviewed_readiness["automatic_execution_allowed"] is False
        assert all(item["readiness_status"] == "execution_prerequisites_confirmed" for item in reviewed_readiness["readiness_items"])
        assert reviewed_readiness["readiness_review_state"]["schema_id"] == "athena.codex_promotion_readiness_review_state.v1"
        assert reviewed_readiness["readiness_review_state"]["confirmed_ready_count"] == 2
        assert reviewed_readiness_payload["hermes_promotion_execution_readiness_payload"]["readiness_review_count"] == 2
        result_intake_payload = workflow.codex_promotion_execution_results()
        result_intake = result_intake_payload["codex_promotion_execution_result_intake"]
        assert result_intake_payload["workflow_instance"]["scenario"] == "codex_promotion_execution_result_intake"
        assert result_intake["schema_id"] == "athena.codex_promotion_execution_result_intake.v1"
        assert result_intake["intake_status"] == "waiting_for_manual_promotion_execution_result"
        assert result_intake["manual_execution_result_required"] is True
        assert result_intake["automatic_execution_allowed"] is False
        first_ready_item = reviewed_readiness["readiness_items"][0]
        execution_result = workflow.apply_codex_promotion_execution_result(
            {
                "readiness_item_id": first_ready_item["readiness_item_id"],
                "promotion_candidate_id": first_ready_item["promotion_candidate_id"],
                "promotion_type": first_ready_item["promotion_type"],
                "result_status": "manual_execution_recorded",
                "result_summary": "Manual promotion completed outside the demo and recorded as metadata.",
                "execution_reference": "manual-result-reference",
                "changed_records": [first_ready_item["promotion_candidate_id"]],
                "validation_summary": "compileall and harness passed after manual promotion.",
                "rollback_summary": "Rollback plan remains documented.",
                "validation_results": [
                    {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed"},
                    {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed"},
                ],
            }
        )
        assert execution_result["codex_promotion_execution_result"]["automatic_execution_allowed"] is False
        assert execution_result["codex_promotion_execution_result"]["result_contract"]["contract_complete"] is True
        recorded_intake = workflow.codex_promotion_execution_results()["codex_promotion_execution_result_intake"]
        assert recorded_intake["intake_status"] == "promotion_execution_result_recorded"
        assert recorded_intake["result_count"] == 1
        assert recorded_intake["contract_complete_count"] == 1
        assert "auto_execute_recorded_promotion_result" in recorded_intake["blocked_actions"]
        partial_audit_payload = workflow.codex_promotion_closure_audit()
        partial_audit = partial_audit_payload["codex_promotion_closure_audit"]
        assert partial_audit_payload["workflow_instance"]["scenario"] == "codex_promotion_closure_audit"
        assert partial_audit["schema_id"] == "athena.codex_promotion_closure_audit.v1"
        assert partial_audit["closure_status"] == "promotion_closure_partial_results"
        assert partial_audit["expected_result_count"] == 2
        assert partial_audit["complete_result_count"] == 1
        assert partial_audit["sync_audit_candidate_count"] == 1
        assert partial_audit["automatic_sync_allowed"] is False
        assert partial_audit_payload["hermes_promotion_closure_audit_payload"]["schema"] == "hermes.codex_promotion_closure_audit.v1"
        assert "auto_write_live_hermes_memory_from_closure_audit" in partial_audit["blocked_actions"]
        second_ready_item = reviewed_readiness["readiness_items"][1]
        workflow.apply_codex_promotion_execution_result(
            {
                "readiness_item_id": second_ready_item["readiness_item_id"],
                "promotion_candidate_id": second_ready_item["promotion_candidate_id"],
                "promotion_type": second_ready_item["promotion_type"],
                "result_status": "manual_execution_recorded",
                "result_summary": "Second manual promotion completed outside the demo and recorded as metadata.",
                "execution_reference": "manual-result-reference-2",
                "changed_records": [second_ready_item["promotion_candidate_id"]],
                "validation_summary": "compileall and harness passed after second manual promotion.",
                "rollback_summary": "Rollback plan remains documented for second promotion.",
                "validation_results": [
                    {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed"},
                    {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed"},
                ],
            }
        )
        closure_audit = workflow.codex_promotion_closure_audit()["codex_promotion_closure_audit"]
        assert closure_audit["closure_status"] == "promotion_closure_ready_for_sync_audit"
        assert closure_audit["closure_ready"] is True
        assert closure_audit["complete_result_count"] == 2
        assert closure_audit["missing_result_count"] == 0
        assert closure_audit["sync_audit_candidate_count"] == 2
        assert closure_audit["future_hermes_sync_audit_required"] is True
        assert any(item["target_system"] == "live_hermes_memory" for item in closure_audit["sync_audit_candidates"])
        assert closure_audit["automatic_closure_allowed"] is False
        sync_gate_payload = workflow.codex_promotion_sync_review_gate()
        sync_gate = sync_gate_payload["codex_promotion_sync_review_gate"]
        assert sync_gate_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_review_gate"
        assert sync_gate["schema_id"] == "athena.codex_promotion_sync_review_gate.v1"
        assert sync_gate["gate_status"] == "ready_for_promotion_sync_review"
        assert sync_gate["gate_ready"] is True
        assert sync_gate["sync_candidate_count"] == 2
        assert sync_gate["approved_future_sync_count"] == 0
        assert sync_gate["automatic_sync_allowed"] is False
        assert sync_gate_payload["hermes_promotion_sync_review_payload"]["schema"] == "hermes.codex_promotion_sync_review_gate.v1"
        assert "auto_write_live_hermes_memory_from_sync_review" in sync_gate["blocked_actions"]
        for candidate in sync_gate["sync_review_candidates"]:
            review = workflow.apply_codex_promotion_sync_review(
                {
                    "sync_audit_id": candidate["sync_audit_id"],
                    "readiness_item_id": candidate["readiness_item_id"],
                    "promotion_candidate_id": candidate["promotion_candidate_id"],
                    "promotion_type": candidate["promotion_type"],
                    "target_system": candidate["target_system"],
                    "review_status": "approved_for_future_sync",
                    "review_note": "Approved as future sync metadata only.",
                    "confirmed_sync_checks": candidate["required_sync_checks"],
                }
            )
            assert review["codex_promotion_sync_review"]["automatic_sync_allowed"] is False
            assert review["codex_promotion_sync_review_state"]["sync_review_count"] >= 1
        approved_sync_gate = workflow.codex_promotion_sync_review_gate()["codex_promotion_sync_review_gate"]
        assert approved_sync_gate["gate_status"] == "promotion_sync_reviews_approved_for_future_execution"
        assert approved_sync_gate["approved_future_sync_count"] == 2
        assert approved_sync_gate["future_sync_action_count"] == 2
        assert approved_sync_gate["future_sync_action_plan"][0]["execution_status"] == "approved_but_not_executed"
        assert approved_sync_gate["automatic_sync_allowed"] is False
        assert any(item["target_system"] == "live_hermes_memory" for item in approved_sync_gate["future_sync_action_plan"])
        sync_handoff_payload = workflow.codex_promotion_sync_handoff()
        sync_handoff = sync_handoff_payload["codex_promotion_sync_handoff_queue"]
        assert sync_handoff_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_handoff_queue"
        assert sync_handoff["schema_id"] == "athena.codex_promotion_sync_handoff_queue.v1"
        assert sync_handoff["handoff_status"] == "ready_for_manual_sync_handoff"
        assert sync_handoff["handoff_ready"] is True
        assert sync_handoff["handoff_item_count"] == 2
        assert sync_handoff["hermes_sync_handoff_count"] == 1
        assert sync_handoff["regression_sync_handoff_count"] == 1
        assert sync_handoff["automatic_execution_allowed"] is False
        assert all(item["manual_execution_required"] is True for item in sync_handoff["handoff_items"])
        assert any(item["owner_role"] == "hermes_admin" for item in sync_handoff["handoff_items"])
        assert sync_handoff_payload["hermes_promotion_sync_handoff_payload"]["schema"] == "hermes.codex_promotion_sync_handoff_queue.v1"
        assert "auto_write_live_hermes_memory_from_sync_handoff" in sync_handoff["blocked_actions"]
        sync_readiness_payload = workflow.codex_promotion_sync_execution_readiness()
        sync_readiness = sync_readiness_payload["codex_promotion_sync_execution_readiness_gate"]
        assert sync_readiness_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_execution_readiness_gate"
        assert sync_readiness["schema_id"] == "athena.codex_promotion_sync_execution_readiness_gate.v1"
        assert sync_readiness["readiness_status"] == "blocked_until_sync_execution_prerequisites_confirmed"
        assert sync_readiness["readiness_ready"] is False
        assert sync_readiness["readiness_item_count"] == 2
        assert sync_readiness["blocked_readiness_item_count"] == 2
        assert sync_readiness["automatic_sync_execution_allowed"] is False
        assert any("explicit_product_owner_sync_execution_confirmation" in item["missing_readiness_inputs"] for item in sync_readiness["readiness_items"])
        assert sync_readiness_payload["hermes_promotion_sync_execution_readiness_payload"]["schema"] == "hermes.codex_promotion_sync_execution_readiness_gate.v1"
        assert "auto_write_live_hermes_memory_from_sync_readiness" in sync_readiness["blocked_actions"]
        for item in sync_readiness["readiness_items"]:
            review = workflow.apply_codex_promotion_sync_readiness_review(
                {
                    "readiness_item_id": item["readiness_item_id"],
                    "source_sync_handoff_item_id": item["source_sync_handoff_item_id"],
                    "source_sync_audit_id": item["source_sync_audit_id"],
                    "promotion_candidate_id": item["promotion_candidate_id"],
                    "promotion_type": item["promotion_type"],
                    "target_system": item["target_system"],
                    "review_status": "confirmed_ready_for_manual_sync_execution",
                    "review_note": "Confirmed as metadata-only sync readiness.",
                    "confirmed_inputs": item["original_missing_readiness_inputs"],
                    "validation_summary": "Validation evidence confirmed as metadata.",
                    "rollback_summary": "Rollback path confirmed as metadata.",
                    "execution_evidence_plan": "Capture sync execution evidence after explicit manual execution.",
                }
            )
            assert review["codex_promotion_sync_readiness_review"]["automatic_sync_execution_allowed"] is False
            assert review["codex_promotion_sync_readiness_review_state"]["readiness_review_count"] >= 1
        reviewed_sync_readiness_payload = workflow.codex_promotion_sync_execution_readiness()
        reviewed_sync_readiness = reviewed_sync_readiness_payload["codex_promotion_sync_execution_readiness_gate"]
        assert reviewed_sync_readiness["readiness_status"] == "ready_for_manual_sync_execution_confirmation"
        assert reviewed_sync_readiness["readiness_ready"] is True
        assert reviewed_sync_readiness["confirmed_readiness_item_count"] == 2
        assert reviewed_sync_readiness["readiness_review_state"]["schema_id"] == "athena.codex_promotion_sync_readiness_review_state.v1"
        assert reviewed_sync_readiness_payload["codex_promotion_sync_readiness_review_state"]["confirmed_ready_count"] == 2
        sync_result_payload = workflow.codex_promotion_sync_execution_results()
        sync_result_intake = sync_result_payload["codex_promotion_sync_execution_result_intake"]
        assert sync_result_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_execution_result_intake"
        assert sync_result_intake["schema_id"] == "athena.codex_promotion_sync_execution_result_intake.v1"
        assert sync_result_intake["intake_status"] == "waiting_for_manual_sync_execution_result"
        assert sync_result_intake["manual_sync_execution_result_required"] is True
        assert sync_result_intake["automatic_sync_execution_allowed"] is False
        for item in reviewed_sync_readiness["readiness_items"]:
            sync_result = workflow.apply_codex_promotion_sync_execution_result(
                {
                    "readiness_item_id": item["readiness_item_id"],
                    "source_sync_handoff_item_id": item["source_sync_handoff_item_id"],
                    "source_sync_audit_id": item["source_sync_audit_id"],
                    "promotion_candidate_id": item["promotion_candidate_id"],
                    "promotion_type": item["promotion_type"],
                    "target_system": item["target_system"],
                    "result_status": "manual_sync_execution_recorded",
                    "result_summary": "Manual sync completed outside the demo and recorded as metadata.",
                    "execution_reference": "manual-sync-result-reference",
                    "changed_records": [item["promotion_candidate_id"], item["target_system"]],
                    "validation_summary": "compileall and harness passed after manual sync.",
                    "rollback_summary": "Rollback path remains documented for sync.",
                    "validation_results": [
                        {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed"},
                        {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed"},
                    ],
                }
            )
            assert sync_result["codex_promotion_sync_execution_result"]["automatic_sync_execution_allowed"] is False
            assert sync_result["codex_promotion_sync_execution_result"]["result_contract"]["contract_complete"] is True
        recorded_sync_result_payload = workflow.codex_promotion_sync_execution_results()
        recorded_sync_result_intake = recorded_sync_result_payload["codex_promotion_sync_execution_result_intake"]
        assert recorded_sync_result_intake["intake_status"] == "sync_execution_result_recorded"
        assert recorded_sync_result_intake["result_count"] == 2
        assert recorded_sync_result_intake["contract_complete_count"] == 2
        assert recorded_sync_result_payload["hermes_promotion_sync_execution_result_payload"]["schema"] == "hermes.codex_promotion_sync_execution_result_intake.v1"
        assert "auto_execute_recorded_sync_result" in recorded_sync_result_intake["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_sync_execution_result_contract_complete_count" for item in recorded_sync_result_payload["kpi_log"])
        sync_closure_payload = workflow.codex_promotion_sync_closure_audit()
        sync_closure = sync_closure_payload["codex_promotion_sync_closure_audit"]
        assert sync_closure_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_closure_audit"
        assert sync_closure["schema_id"] == "athena.codex_promotion_sync_closure_audit.v1"
        assert sync_closure["closure_status"] == "sync_closure_ready_for_final_review"
        assert sync_closure["closure_ready"] is True
        assert sync_closure["expected_result_count"] == 2
        assert sync_closure["complete_result_count"] == 2
        assert sync_closure["missing_result_count"] == 0
        assert sync_closure["final_closure_candidate_count"] == 2
        assert sync_closure["automatic_sync_allowed"] is False
        assert any(item["target_system"] == "live_hermes_memory" for item in sync_closure["final_sync_closure_candidates"])
        assert sync_closure_payload["hermes_promotion_sync_closure_audit_payload"]["schema"] == "hermes.codex_promotion_sync_closure_audit.v1"
        assert "auto_write_live_hermes_memory_from_sync_closure" in sync_closure["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_sync_closure_ready" for item in sync_closure_payload["kpi_log"])
        sync_closure_review_payload = workflow.codex_promotion_sync_closure_review_gate()
        sync_closure_review_gate = sync_closure_review_payload["codex_promotion_sync_closure_review_gate"]
        assert sync_closure_review_payload["workflow_instance"]["scenario"] == "codex_promotion_sync_closure_review_gate"
        assert sync_closure_review_gate["schema_id"] == "athena.codex_promotion_sync_closure_review_gate.v1"
        assert sync_closure_review_gate["gate_status"] == "ready_for_sync_closure_review"
        assert sync_closure_review_gate["candidate_count"] == 2
        assert sync_closure_review_gate["automatic_final_sync_allowed"] is False
        assert sync_closure_review_payload["hermes_promotion_sync_closure_review_payload"]["schema"] == "hermes.codex_promotion_sync_closure_review_gate.v1"
        for candidate in sync_closure_review_gate["sync_closure_review_candidates"]:
            review = workflow.apply_codex_promotion_sync_closure_review(
                {
                    "final_closure_id": candidate["final_closure_id"],
                    "readiness_item_id": candidate["readiness_item_id"],
                    "source_sync_audit_id": candidate["source_sync_audit_id"],
                    "promotion_candidate_id": candidate["promotion_candidate_id"],
                    "promotion_type": candidate["promotion_type"],
                    "target_system": candidate["target_system"],
                    "review_status": "approved_for_final_sync",
                    "review_note": "Approved as final sync closure metadata only.",
                    "confirmed_final_checks": candidate["required_final_checks"],
                    "validation_summary": "Final sync validation summary confirmed as metadata.",
                    "rollback_summary": "Final sync rollback path confirmed as metadata.",
                }
            )
            assert review["codex_promotion_sync_closure_review"]["automatic_final_sync_allowed"] is False
            assert review["codex_promotion_sync_closure_review_state"]["closure_review_count"] >= 1
        approved_sync_closure_review = workflow.codex_promotion_sync_closure_review_gate()["codex_promotion_sync_closure_review_gate"]
        assert approved_sync_closure_review["gate_status"] == "sync_closure_reviews_approved_for_future_execution"
        assert approved_sync_closure_review["approved_final_sync_count"] == 2
        assert approved_sync_closure_review["future_real_sync_action_count"] == 2
        assert any(item["target_system"] == "live_hermes_memory" for item in approved_sync_closure_review["future_real_sync_action_plan"])
        assert "auto_write_live_hermes_memory_from_sync_closure_review" in approved_sync_closure_review["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_sync_closure_review_count" for item in sync_closure_review_payload["kpi_log"])
        final_sync_handoff_payload = workflow.codex_promotion_final_sync_handoff()
        final_sync_handoff = final_sync_handoff_payload["codex_promotion_final_sync_handoff_queue"]
        assert final_sync_handoff_payload["workflow_instance"]["scenario"] == "codex_promotion_final_sync_handoff_queue"
        assert final_sync_handoff["schema_id"] == "athena.codex_promotion_final_sync_handoff_queue.v1"
        assert final_sync_handoff["handoff_status"] == "ready_for_manual_final_sync_handoff"
        assert final_sync_handoff["handoff_ready"] is True
        assert final_sync_handoff["handoff_item_count"] == 2
        assert final_sync_handoff["automatic_execution_allowed"] is False
        assert any(item["target_system"] == "live_hermes_memory" for item in final_sync_handoff["handoff_items"])
        assert final_sync_handoff_payload["hermes_promotion_final_sync_handoff_payload"]["schema"] == "hermes.codex_promotion_final_sync_handoff_queue.v1"
        assert "auto_write_live_hermes_memory_from_final_sync_handoff" in final_sync_handoff["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_sync_handoff_item_count" for item in final_sync_handoff_payload["kpi_log"])
        final_sync_readiness_payload = workflow.codex_promotion_final_sync_execution_readiness()
        final_sync_readiness = final_sync_readiness_payload["codex_promotion_final_sync_execution_readiness_gate"]
        assert final_sync_readiness_payload["workflow_instance"]["scenario"] == "codex_promotion_final_sync_execution_readiness_gate"
        assert final_sync_readiness["schema_id"] == "athena.codex_promotion_final_sync_execution_readiness_gate.v1"
        assert final_sync_readiness["readiness_status"] == "blocked_until_final_sync_execution_prerequisites_confirmed"
        assert final_sync_readiness["readiness_item_count"] == 2
        assert final_sync_readiness["blocked_readiness_item_count"] == 2
        assert final_sync_readiness["automatic_execution_allowed"] is False
        assert any("explicit_product_owner_final_sync_execution_confirmation" in item["missing_real_sync_inputs"] for item in final_sync_readiness["readiness_items"])
        assert final_sync_readiness_payload["hermes_promotion_final_sync_execution_readiness_payload"]["schema"] == "hermes.codex_promotion_final_sync_execution_readiness_gate.v1"
        assert "auto_write_live_hermes_memory_from_final_sync_readiness" in final_sync_readiness["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_sync_execution_blocked_item_count" for item in final_sync_readiness_payload["kpi_log"])
        confirmed_final_sync_inputs = sorted(
            {
                input_name
                for item in final_sync_handoff["handoff_items"]
                for input_name in item["required_real_sync_inputs"]
            }
            | {
                "explicit_product_owner_final_sync_execution_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
                "execution_evidence_capture_plan",
            }
        )
        ready_final_sync = workflow.codex_promotion_final_sync_execution_readiness(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )["codex_promotion_final_sync_execution_readiness_gate"]
        assert ready_final_sync["readiness_status"] == "ready_for_manual_final_sync_execution_confirmation"
        assert ready_final_sync["readiness_ready"] is True
        assert ready_final_sync["confirmed_readiness_item_count"] == 2
        assert ready_final_sync["blocked_readiness_item_count"] == 0
        final_sync_result_payload = workflow.codex_promotion_final_sync_execution_results(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        final_sync_result_intake = final_sync_result_payload["codex_promotion_final_sync_execution_result_intake"]
        assert final_sync_result_payload["workflow_instance"]["scenario"] == "codex_promotion_final_sync_execution_result_intake"
        assert final_sync_result_intake["schema_id"] == "athena.codex_promotion_final_sync_execution_result_intake.v1"
        assert final_sync_result_intake["intake_status"] == "waiting_for_manual_final_sync_execution_result"
        assert final_sync_result_intake["expected_result_count"] == 2
        assert final_sync_result_intake["automatic_execution_allowed"] is False
        assert final_sync_result_payload["hermes_promotion_final_sync_execution_result_payload"]["schema"] == "hermes.codex_promotion_final_sync_execution_result_intake.v1"
        assert "auto_write_live_hermes_memory_from_final_sync_result" in final_sync_result_intake["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_sync_execution_result_count" for item in final_sync_result_payload["kpi_log"])
        for item in ready_final_sync["readiness_items"]:
            result = workflow.apply_codex_promotion_final_sync_execution_result(
                {
                    "readiness_item_id": item["readiness_item_id"],
                    "source_final_sync_handoff_item_id": item["source_final_sync_handoff_item_id"],
                    "source_action_id": item["source_action_id"],
                    "final_closure_id": item["final_closure_id"],
                    "source_sync_audit_id": item["source_sync_audit_id"],
                    "promotion_candidate_id": item["promotion_candidate_id"],
                    "promotion_type": item["promotion_type"],
                    "target_system": item["target_system"],
                    "result_status": "manual_final_sync_execution_recorded",
                    "result_summary": "Manual final sync execution completed outside the demo.",
                    "execution_reference": "manual_final_sync_execution_outside_demo",
                    "changed_records": [item["promotion_candidate_id"], item["target_system"]],
                    "validation_summary": "Current validation evidence confirmed after final sync execution.",
                    "rollback_summary": "Rollback or reversal path remains available.",
                    "validation_results": [
                        {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed"},
                        {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed"},
                    ],
                }
            )
            assert result["codex_promotion_final_sync_execution_result"]["automatic_execution_allowed"] is False
            assert result["codex_promotion_final_sync_execution_result"]["result_contract"]["contract_complete"] is True
        recorded_final_sync_result_payload = workflow.codex_promotion_final_sync_execution_results(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        recorded_final_sync_result = recorded_final_sync_result_payload["codex_promotion_final_sync_execution_result_intake"]
        assert recorded_final_sync_result["intake_status"] == "final_sync_execution_result_recorded"
        assert recorded_final_sync_result["result_count"] == 2
        assert recorded_final_sync_result["contract_complete_count"] == 2
        assert recorded_final_sync_result["result_state"]["manual_final_sync_execution_recorded_count"] == 2
        final_sync_closure_payload = workflow.codex_promotion_final_sync_closure_audit(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        final_sync_closure = final_sync_closure_payload["codex_promotion_final_sync_closure_audit"]
        assert final_sync_closure_payload["workflow_instance"]["scenario"] == "codex_promotion_final_sync_closure_audit"
        assert final_sync_closure["schema_id"] == "athena.codex_promotion_final_sync_closure_audit.v1"
        assert final_sync_closure["closure_status"] == "final_sync_closure_ready_for_completion_review"
        assert final_sync_closure["closure_ready"] is True
        assert final_sync_closure["expected_result_count"] == 2
        assert final_sync_closure["complete_result_count"] == 2
        assert final_sync_closure["missing_result_count"] == 0
        assert final_sync_closure["final_closure_candidate_count"] == 2
        assert final_sync_closure["automatic_closure_allowed"] is False
        assert final_sync_closure["automatic_project_memory_write_allowed"] is False
        assert any(item["target_system"] == "live_hermes_memory" for item in final_sync_closure["final_closure_candidates"])
        assert final_sync_closure_payload["hermes_promotion_final_sync_closure_audit_payload"]["schema"] == "hermes.codex_promotion_final_sync_closure_audit.v1"
        assert "auto_write_live_hermes_memory_from_final_sync_closure" in final_sync_closure["blocked_actions"]
        assert "auto_publish_project_memory_from_final_sync_closure" in final_sync_closure["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_sync_closure_ready" for item in final_sync_closure_payload["kpi_log"])
        final_completion_review_payload = workflow.codex_promotion_final_completion_review_gate(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        final_completion_review_gate = final_completion_review_payload["codex_promotion_final_completion_review_gate"]
        assert final_completion_review_payload["workflow_instance"]["scenario"] == "codex_promotion_final_completion_review_gate"
        assert final_completion_review_gate["schema_id"] == "athena.codex_promotion_final_completion_review_gate.v1"
        assert final_completion_review_gate["gate_status"] == "ready_for_final_completion_review"
        assert final_completion_review_gate["candidate_count"] == 2
        assert final_completion_review_gate["automatic_completion_allowed"] is False
        assert final_completion_review_gate["automatic_project_memory_write_allowed"] is False
        assert final_completion_review_payload["hermes_promotion_final_completion_review_payload"]["schema"] == "hermes.codex_promotion_final_completion_review_gate.v1"
        for candidate in final_completion_review_gate["final_completion_review_candidates"]:
            review = workflow.apply_codex_promotion_final_completion_review(
                {
                    "final_sync_completion_id": candidate["final_sync_completion_id"],
                    "readiness_item_id": candidate["readiness_item_id"],
                    "final_closure_id": candidate["final_closure_id"],
                    "source_action_id": candidate["source_action_id"],
                    "source_sync_audit_id": candidate["source_sync_audit_id"],
                    "promotion_candidate_id": candidate["promotion_candidate_id"],
                    "promotion_type": candidate["promotion_type"],
                    "target_system": candidate["target_system"],
                    "review_status": "approved_final_completion",
                    "review_note": "Approved as final completion metadata only.",
                    "confirmed_completion_checks": candidate["required_completion_checks"],
                    "validation_summary": "Final completion validation summary confirmed as metadata.",
                    "rollback_summary": "Final completion rollback path confirmed as metadata.",
                }
            )
            assert review["codex_promotion_final_completion_review"]["automatic_completion_allowed"] is False
            assert review["codex_promotion_final_completion_review"]["automatic_project_memory_write_allowed"] is False
            assert review["codex_promotion_final_completion_review_state"]["final_completion_review_count"] >= 1
        approved_final_completion_review = workflow.codex_promotion_final_completion_review_gate(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )["codex_promotion_final_completion_review_gate"]
        assert approved_final_completion_review["gate_status"] == "final_completion_reviews_approved_for_future_publication"
        assert approved_final_completion_review["approved_final_completion_count"] == 2
        assert approved_final_completion_review["future_publication_action_count"] == 2
        assert any(item["target_system"] == "live_hermes_memory" for item in approved_final_completion_review["final_completion_publication_plan"])
        assert "auto_publish_project_memory_from_final_completion_review" in approved_final_completion_review["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_completion_review_count" for item in final_completion_review_payload["kpi_log"])
        final_publication_handoff_payload = workflow.codex_promotion_final_publication_handoff(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        final_publication_handoff = final_publication_handoff_payload["codex_promotion_final_publication_handoff_queue"]
        assert final_publication_handoff_payload["workflow_instance"]["scenario"] == "codex_promotion_final_publication_handoff_queue"
        assert final_publication_handoff["schema_id"] == "athena.codex_promotion_final_publication_handoff_queue.v1"
        assert final_publication_handoff["handoff_status"] == "ready_for_manual_final_publication_handoff"
        assert final_publication_handoff["handoff_ready"] is True
        assert final_publication_handoff["handoff_item_count"] == 2
        assert final_publication_handoff["automatic_publication_allowed"] is False
        assert final_publication_handoff["project_memory_publication_allowed"] is False
        assert any(item["target_system"] == "live_hermes_memory" for item in final_publication_handoff["handoff_items"])
        assert any("publication_reference" in item["publication_evidence_required"] for item in final_publication_handoff["handoff_items"])
        assert final_publication_handoff_payload["hermes_promotion_final_publication_handoff_payload"]["schema"] == "hermes.codex_promotion_final_publication_handoff_queue.v1"
        assert "auto_write_live_hermes_memory_from_final_publication_handoff" in final_publication_handoff["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_publication_handoff_item_count" for item in final_publication_handoff_payload["kpi_log"])
        final_publication_readiness_payload = workflow.codex_promotion_final_publication_readiness(
            {"confirmed_real_sync_inputs": confirmed_final_sync_inputs}
        )
        final_publication_readiness = final_publication_readiness_payload["codex_promotion_final_publication_readiness_gate"]
        assert final_publication_readiness_payload["workflow_instance"]["scenario"] == "codex_promotion_final_publication_readiness_gate"
        assert final_publication_readiness["schema_id"] == "athena.codex_promotion_final_publication_readiness_gate.v1"
        assert final_publication_readiness["readiness_status"] == "blocked_until_final_publication_prerequisites_confirmed"
        assert final_publication_readiness["readiness_item_count"] == 2
        assert final_publication_readiness["blocked_readiness_item_count"] == 2
        assert final_publication_readiness["automatic_publication_allowed"] is False
        assert final_publication_readiness["project_memory_publication_allowed"] is False
        assert any("explicit_product_owner_final_publication_confirmation" in item["missing_publication_inputs"] for item in final_publication_readiness["readiness_items"])
        assert final_publication_readiness_payload["hermes_promotion_final_publication_readiness_payload"]["schema"] == "hermes.codex_promotion_final_publication_readiness_gate.v1"
        assert "auto_write_live_hermes_memory_from_final_publication_readiness" in final_publication_readiness["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_publication_readiness_item_count" for item in final_publication_readiness_payload["kpi_log"])
        confirmed_publication_inputs = sorted(
            {
                input_name
                for item in final_publication_handoff["handoff_items"]
                for input_name in [
                    *item["required_publication_inputs"],
                    "explicit_product_owner_final_publication_confirmation",
                    "current_compileall_validation_output",
                    "current_test_harness_validation_output",
                    "publication_evidence_capture_plan",
                    "publication_rollback_plan",
                ]
            }
        )
        ready_final_publication = workflow.codex_promotion_final_publication_readiness(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )["codex_promotion_final_publication_readiness_gate"]
        assert ready_final_publication["readiness_status"] == "ready_for_manual_final_publication_confirmation"
        assert ready_final_publication["confirmed_readiness_item_count"] == 2
        assert ready_final_publication["blocked_readiness_item_count"] == 0
        assert ready_final_publication["automatic_publication_allowed"] is False
        assert ready_final_publication["project_memory_publication_allowed"] is False
        final_publication_result_payload = workflow.codex_promotion_final_publication_results(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )
        final_publication_result_intake = final_publication_result_payload["codex_promotion_final_publication_result_intake"]
        assert final_publication_result_payload["workflow_instance"]["scenario"] == "codex_promotion_final_publication_result_intake"
        assert final_publication_result_intake["schema_id"] == "athena.codex_promotion_final_publication_result_intake.v1"
        assert final_publication_result_intake["intake_status"] == "waiting_for_manual_final_publication_result"
        assert final_publication_result_intake["expected_result_count"] == 2
        assert final_publication_result_intake["automatic_publication_allowed"] is False
        assert final_publication_result_intake["project_memory_publication_allowed"] is False
        first_publication_item = ready_final_publication["readiness_items"][0]
        publication_result = workflow.apply_codex_promotion_final_publication_result(
            {
                "readiness_item_id": first_publication_item["readiness_item_id"],
                "source_final_publication_handoff_item_id": first_publication_item["source_final_publication_handoff_item_id"],
                "source_publication_action_id": first_publication_item["source_publication_action_id"],
                "source_action_id": first_publication_item["source_action_id"],
                "final_sync_completion_id": first_publication_item["final_sync_completion_id"],
                "final_closure_id": first_publication_item["final_closure_id"],
                "source_sync_audit_id": first_publication_item["source_sync_audit_id"],
                "promotion_candidate_id": first_publication_item["promotion_candidate_id"],
                "promotion_type": first_publication_item["promotion_type"],
                "target_system": first_publication_item["target_system"],
                "result_status": "manual_final_publication_recorded",
                "result_summary": "Manual final publication metadata recorded outside demo.",
                "publication_reference": "manual_final_publication_outside_demo",
                "published_records": [first_publication_item["promotion_candidate_id"], first_publication_item["target_system"]],
                "validation_summary": "Post-publication validation summary confirmed as metadata.",
                "rollback_summary": "Publication rollback path confirmed as metadata.",
                "validation_results": [
                    {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed before recording manual final publication result"},
                    {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed before recording manual final publication result"},
                ],
            }
        )
        assert publication_result["codex_promotion_final_publication_result"]["result_contract"]["contract_complete"] is True
        assert publication_result["codex_promotion_final_publication_result"]["automatic_publication_allowed"] is False
        recorded_publication_results = workflow.codex_promotion_final_publication_results(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )
        recorded_publication_intake = recorded_publication_results["codex_promotion_final_publication_result_intake"]
        assert recorded_publication_intake["intake_status"] == "final_publication_result_recorded"
        assert recorded_publication_intake["result_count"] == 1
        assert recorded_publication_intake["contract_complete_count"] == 1
        assert recorded_publication_results["hermes_promotion_final_publication_result_payload"]["schema"] == "hermes.codex_promotion_final_publication_result_intake.v1"
        assert "auto_write_live_hermes_memory_from_final_publication_result" in recorded_publication_intake["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_publication_result_contract_complete_count" for item in recorded_publication_results["kpi_log"])
        final_publication_closure_payload = workflow.codex_promotion_final_publication_closure_audit(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )
        final_publication_closure = final_publication_closure_payload["codex_promotion_final_publication_closure_audit"]
        assert final_publication_closure_payload["workflow_instance"]["scenario"] == "codex_promotion_final_publication_closure_audit"
        assert final_publication_closure["schema_id"] == "athena.codex_promotion_final_publication_closure_audit.v1"
        assert final_publication_closure["closure_status"] == "final_publication_closure_partial_results"
        assert final_publication_closure["expected_result_count"] == 2
        assert final_publication_closure["recorded_result_count"] == 1
        assert final_publication_closure["complete_result_count"] == 1
        assert final_publication_closure["missing_result_count"] == 1
        assert final_publication_closure["final_closure_candidate_count"] == 1
        assert final_publication_closure["automatic_closure_allowed"] is False
        assert final_publication_closure["automatic_project_memory_write_allowed"] is False
        assert final_publication_closure_payload["hermes_promotion_final_publication_closure_audit_payload"]["schema"] == "hermes.codex_promotion_final_publication_closure_audit.v1"
        assert "auto_write_live_hermes_memory_from_final_publication_closure" in final_publication_closure["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_publication_closure_missing_result_count" for item in final_publication_closure_payload["kpi_log"])
        partial_release_review = workflow.codex_promotion_final_release_review_gate(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )["codex_promotion_final_release_review_gate"]
        assert partial_release_review["gate_status"] == "blocked_until_final_publication_closure_complete"
        assert partial_release_review["release_review_candidate_count"] == 1
        assert partial_release_review["blocked_release_review_candidate_count"] == 1
        assert partial_release_review["automatic_release_allowed"] is False
        assert partial_release_review["live_hermes_write_allowed"] is False
        second_publication_item = ready_final_publication["readiness_items"][1]
        workflow.apply_codex_promotion_final_publication_result(
            {
                "readiness_item_id": second_publication_item["readiness_item_id"],
                "source_final_publication_handoff_item_id": second_publication_item["source_final_publication_handoff_item_id"],
                "source_publication_action_id": second_publication_item["source_publication_action_id"],
                "source_action_id": second_publication_item["source_action_id"],
                "final_sync_completion_id": second_publication_item["final_sync_completion_id"],
                "final_closure_id": second_publication_item["final_closure_id"],
                "source_sync_audit_id": second_publication_item["source_sync_audit_id"],
                "promotion_candidate_id": second_publication_item["promotion_candidate_id"],
                "promotion_type": second_publication_item["promotion_type"],
                "target_system": second_publication_item["target_system"],
                "result_status": "manual_final_publication_recorded",
                "result_summary": "Second manual final publication metadata recorded outside demo.",
                "publication_reference": "manual_final_publication_outside_demo_second",
                "published_records": [second_publication_item["promotion_candidate_id"], second_publication_item["target_system"]],
                "validation_summary": "Second post-publication validation summary confirmed as metadata.",
                "rollback_summary": "Rollback owner confirmed outside demo.",
                "validation_results": [
                    {"command": "python -m compileall src scripts tests", "status": "passed", "summary": "compileall passed before second manual final publication result"},
                    {"command": "tests/test_main_agent.py harness", "status": "passed", "summary": "harness passed before second manual final publication result"},
                ],
            }
        )
        ready_release_payload = workflow.codex_promotion_final_release_review_gate(
            {
                "confirmed_real_sync_inputs": confirmed_final_sync_inputs,
                "confirmed_publication_inputs": confirmed_publication_inputs,
            }
        )
        ready_release_gate = ready_release_payload["codex_promotion_final_release_review_gate"]
        assert ready_release_payload["workflow_instance"]["scenario"] == "codex_promotion_final_release_review_gate"
        assert ready_release_gate["schema_id"] == "athena.codex_promotion_final_release_review_gate.v1"
        assert ready_release_gate["gate_status"] == "ready_for_product_owner_final_release_review"
        assert ready_release_gate["gate_ready"] is True
        assert ready_release_gate["release_review_candidate_count"] == 2
        assert ready_release_gate["blocked_release_review_candidate_count"] == 0
        assert ready_release_gate["automatic_release_allowed"] is False
        assert ready_release_gate["automatic_archive_allowed"] is False
        assert ready_release_gate["project_memory_publication_allowed"] is False
        assert ready_release_gate["live_hermes_write_allowed"] is False
        assert ready_release_payload["hermes_promotion_final_release_review_payload"]["schema"] == "hermes.codex_promotion_final_release_review_gate.v1"
        assert "auto_write_live_hermes_memory_from_release_review_gate" in ready_release_gate["blocked_actions"]
        assert any(item["kpi"] == "codex_promotion_final_release_review_candidate_count" for item in ready_release_payload["kpi_log"])


def test_training_review_and_data_intake_store_metadata_only():
    with TemporaryDirectory() as temp_dir:
        review_path = Path(temp_dir) / "training_task_reviews.json"
        workflow = TrainingAutomationWorkflow(review_store_path=review_path)

        review = workflow.apply_task_review(
            {
                "task_id": "TPI-GM-DELIVERY-001",
                "review_status": "approved",
                "review_note": "Confirmed as useful for Tianpai GM training.",
            }
        )
        source = workflow.register_data_source(
            {
                "task_id": "TPI-GM-DELIVERY-001",
                "data_status": "registered",
                "source_type": "APS export",
                "source_label": "June weaving schedule export",
                "source_reference": "owner: APS engineer; file stays outside repo",
                "field_notes": "Needs order_id, planned machine, planned quantity, start/end time.",
                "sensitivity_level": "internal",
            }
        )
        result = workflow.run({"mode": "auto"})
        serialized_store = review_path.read_text(encoding="utf-8").lower()

        assert review["review"]["review_status"] == "approved"
        assert source["data_source"]["contains_raw_file"] is False
        assert source["data_source"]["contains_credentials"] is False
        assert result["review_state"]["approved_count"] == 1
        assert result["review_state"]["registered_data_source_count"] == 1
        delivery_task = next(item for item in result["training_tasks"] if item["task_id"] == "TPI-GM-DELIVERY-001")
        assert delivery_task["review"]["review_status"] == "approved"
        assert delivery_task["data_intake"]["latest_data_status"] == "registered"
        assert any(item["type"] == "data_ingestion_candidate" for item in result["codex_patch_queue"])
        assert "file stays outside repo" in serialized_store
        assert "password" not in serialized_store
        assert "raw_file" in serialized_store

        try:
            workflow.apply_task_review(
                {
                    "task_id": "TPI-GM-DELIVERY-001",
                    "review_status": "note_only",
                    "review_note": "password should not be saved",
                }
            )
        except ValueError as exc:
            assert "credentials" in str(exc)
        else:
            raise AssertionError("credential-like review note was not rejected")


def test_training_round_summary_promotes_approved_baseline():
    with TemporaryDirectory() as temp_dir:
        review_path = Path(temp_dir) / "training_task_reviews.json"
        workflow = TrainingAutomationWorkflow(review_store_path=review_path)
        initial = workflow.run({"mode": "auto"})

        for task in initial["training_tasks"]:
            workflow.apply_task_review(
                {
                    "task_id": task["task_id"],
                    "review_status": "approved",
                    "review_note": "Approved for automatic regression.",
                }
            )

        workflow.register_data_source(
            {
                "task_id": "TPI-GM-DELIVERY-001",
                "data_status": "registered",
                "source_type": "APS export",
                "source_label": "APS Planned Task delivery-time export 2026-06-08",
                "source_reference": "local attachment filename only",
                "field_notes": "127 rows with produce_order_code, machine_id, style_code, planned quantity, produced quantity, timing fields, status, and delivery_time.",
            }
        )
        workflow.register_data_source(
            {
                "task_id": "TPI-GM-COST-001",
                "data_status": "not_available",
                "source_type": "customer purchasing and labor cost",
                "field_notes": "Real customer cost data is unavailable.",
            }
        )
        workflow.register_data_source(
            {
                "task_id": "TPI-PROCESS-STAGES-001",
                "data_status": "not_available",
                "source_type": "stage-level production records",
                "field_notes": "Stage-level downstream records are unavailable.",
            }
        )

        summary = workflow.round_summary()
        promoted = workflow.promote_baseline({"promoted_by": "product_owner"})
        serialized = json.dumps(promoted, ensure_ascii=False).lower()

        assert summary["schema"] == "athena.training_round_summary.v1"
        assert summary["baseline_status"] == "ready_for_regression"
        assert summary["promoted_task_count"] == summary["total_task_count"]
        assert summary["capability_regression_count"] >= 6
        assert summary["data_gap_regression_count"] == 3
        assert len(summary["data_decisions"]) == 3
        assert any(item["coverage"] == "partial_aps_schedule_delivery_coverage" for item in summary["data_decisions"])
        assert any(item["coverage"] == "not_available_customer_cost_data" for item in summary["data_decisions"])
        assert promoted["status"] == "baseline_promoted"
        assert promoted["hermes_baseline_payload"]["schema"] == "hermes.baseline_promotion.v1"
        assert promoted["hermes_baseline_payload"]["promotion_status"] == "approved"
        assert promoted["review_state"]["baseline_promotion_count"] == 1
        regression = workflow.regression_run()
        assert regression["regression_overview"]["schema_id"] == "athena.automatic_regression_run.v1"
        assert regression["workflow_instance"]["automation_mode"] == "local_regression_evaluation"
        assert regression["regression_overview"]["baseline_case_count"] == summary["promoted_task_count"]
        assert regression["regression_overview"]["executable_case_count"] >= summary["promoted_task_count"]
        assert regression["regression_overview"]["passed_case_count"] >= summary["promoted_task_count"]
        assert regression["regression_overview"]["failed_case_count"] == 0
        assert regression["regression_overview"]["pass_rate"] == 1
        assert any(item["source"] == "training_baseline" and item["regression_status"] == "passed" for item in regression["regression_cases"])
        assert any(item["kpi"] == "regression_pass_rate" for item in regression["kpi_log"])
        gate = workflow.regression_gate()
        assert gate["regression_gate"]["gate_status"] == "ready_for_next_loop_with_blocked_playbooks"
        assert gate["regression_gate"]["automatic_loop_allowed"] is True
        assert gate["regression_gate"]["failed_case_count"] == 0
        assert gate["regression_gate"]["blocked_case_count"] == 8
        assert gate["regression_gate"]["codex_patch_allowed"] == "small_fix_only"
        assert any(item["type"] == "human_review_queue" for item in gate["codex_next_action_queue"])
        assert gate["hermes_feedback_payload"]["automatic_loop_allowed"] is True
        handoff = workflow.next_loop_handoff()
        assert handoff["next_loop_handoff"]["handoff_status"] == "automatic_small_fix_ready_with_review_items"
        assert handoff["next_loop_handoff"]["queue_summary"]["automatic_action_count"] >= 1
        assert handoff["next_loop_handoff"]["queue_summary"]["human_review_count"] >= 3
        assert handoff["next_loop_handoff"]["queue_summary"]["data_request_count"] == 3
        assert handoff["next_loop_handoff"]["code_change_automatic"] is False
        assert handoff["hermes_handoff_payload"]["contains_raw_file"] is False
        assert "write_live_hermes_memory" in handoff["next_loop_handoff"]["blocked_actions"]
        data_item = handoff["next_loop_handoff"]["data_request_queue"][0]
        review = workflow.apply_handoff_review(
            {
                "handoff_item_id": data_item["handoff_item_id"],
                "review_status": "needs_data",
                "review_note": "Keep the APS/IOT join rule as an explicit data request.",
                "item_type": data_item["type"],
                "related_task_id": data_item.get("related_task_id", ""),
            }
        )
        reviewed = workflow.next_loop_handoff()
        assert review["handoff_review_state"]["needs_data_count"] == 1
        assert reviewed["next_loop_handoff"]["queue_summary"]["handoff_needs_data_count"] == 1
        assert reviewed["handoff_review_state"]["schema_id"] == "athena.next_loop_handoff_review_state.v1"
        closure = workflow.next_loop_closure()
        assert closure["next_loop_closure"]["closure_status"] == "ready_for_local_iteration_with_open_handoff_items"
        assert closure["next_loop_closure"]["open_item_count"] >= 1
        assert closure["next_loop_closure"]["local_iteration_plan"]["allowed"] is True
        assert "auto_execute_local_iteration_plan" in closure["next_loop_closure"]["blocked_actions"]
        proposal = workflow.iteration_proposal()
        assert proposal["training_iteration_proposal"]["proposal_status"] == "proposal_ready_with_open_items"
        assert proposal["training_iteration_proposal"]["task_seed_count"] >= 1
        assert proposal["training_iteration_proposal"]["next_iteration_contract"]["code_change_automatic"] is False
        assert proposal["hermes_iteration_payload"]["contains_raw_file"] is False
        proposal_review = workflow.apply_iteration_proposal_review(
            {
                "proposal_id": proposal["training_iteration_proposal"]["proposal_id"],
                "review_status": "needs_changes",
                "review_note": "Keep the open watchlist visible before queue preparation.",
                "proposal_status": proposal["training_iteration_proposal"]["proposal_status"],
                "task_seed_count": proposal["training_iteration_proposal"]["task_seed_count"],
                "open_watch_item_count": proposal["training_iteration_proposal"]["open_watch_item_count"],
            }
        )
        reviewed_proposal = workflow.iteration_proposal()
        assert proposal_review["proposal_review_state"]["needs_changes_count"] == 1
        assert reviewed_proposal["training_iteration_proposal"]["proposal_review"]["review_status"] == "needs_changes"
        assert reviewed_proposal["training_iteration_proposal"]["codex_queue_allowed"] is False
        packets = workflow.codex_work_packets()
        assert packets["codex_work_packet_queue"]["queue_status"] == "blocked_proposal_needs_changes"
        assert packets["codex_work_packet_queue"]["queue_ready"] is False
        assert packets["codex_work_packet_queue"]["packet_count"] == 0
        patch_contract = workflow.codex_patch_queue()
        assert patch_contract["codex_patch_queue_contract"]["queue_status"] == "blocked_patch_proposal_needs_changes"
        assert patch_contract["codex_patch_queue_contract"]["queue_ready"] is False
        assert patch_contract["codex_patch_queue_contract"]["patch_candidate_count"] == 0
        execution_gate = workflow.codex_execution_gate()
        assert execution_gate["codex_execution_gate"]["gate_status"] == "blocked_execution_proposal_needs_changes"
        assert execution_gate["codex_execution_gate"]["gate_ready"] is False
        assert execution_gate["codex_execution_gate"]["execution_candidate_count"] == 0
        worktree_prep = workflow.codex_worktree_preparation_queue()
        assert worktree_prep["codex_worktree_preparation_queue"]["queue_status"] == "blocked_worktree_proposal_needs_changes"
        assert worktree_prep["codex_worktree_preparation_queue"]["queue_ready"] is False
        assert worktree_prep["codex_worktree_preparation_queue"]["preparation_task_count"] == 0
        launch_payload = workflow.codex_worktree_launch_gate()
        assert launch_payload["codex_worktree_launch_gate"]["launch_status"] == "blocked_launch_proposal_needs_changes"
        assert launch_payload["codex_worktree_launch_gate"]["launch_ready"] is False
        assert launch_payload["codex_worktree_launch_gate"]["launch_request_count"] == 0
        result_payload = workflow.codex_worktree_results()
        assert result_payload["codex_worktree_result_intake"]["intake_status"] == "blocked_until_codex_worktree_launch_ready"
        assert result_payload["codex_worktree_result_intake"]["result_count"] == 0
        assert result_payload["codex_worktree_result_intake"]["automatic_merge_allowed"] is False
        review_gate = workflow.codex_worktree_result_review_gate()["codex_worktree_result_review_gate"]
        assert review_gate["gate_status"] == "blocked_until_codex_worktree_result_ready"
        assert review_gate["review_candidate_count"] == 0
        assert review_gate["automatic_promotion_allowed"] is False
        promotion_queue = workflow.codex_promotion_candidates()["codex_promotion_candidate_queue"]
        assert promotion_queue["queue_status"] == "blocked_until_codex_result_review_ready"
        assert promotion_queue["queue_ready"] is False
        assert promotion_queue["promotion_candidate_count"] == 0
        approval_gate = workflow.codex_promotion_approval_gate()["codex_promotion_approval_gate"]
        assert approval_gate["gate_status"] == "blocked_until_promotion_candidates_ready"
        assert approval_gate["gate_ready"] is False
        assert approval_gate["promotion_candidate_count"] == 0
        assert approval_gate["future_action_plan"] == []
        handoff = workflow.codex_promotion_handoff()["codex_promotion_handoff_queue"]
        assert handoff["handoff_status"] == "blocked_until_promotion_candidates_ready"
        assert handoff["handoff_ready"] is False
        assert handoff["handoff_item_count"] == 0
        assert handoff["automatic_execution_allowed"] is False
        readiness = workflow.codex_promotion_execution_readiness()["codex_promotion_execution_readiness_gate"]
        assert readiness["readiness_status"] == "blocked_until_promotion_candidates_ready"
        assert readiness["readiness_ready"] is False
        assert readiness["readiness_item_count"] == 0
        assert readiness["automatic_execution_allowed"] is False
        assert readiness["readiness_review_state"]["readiness_review_count"] == 0
        result_intake = workflow.codex_promotion_execution_results()["codex_promotion_execution_result_intake"]
        assert result_intake["intake_status"] == "blocked_until_promotion_execution_ready"
        assert result_intake["result_count"] == 0
        assert result_intake["automatic_execution_allowed"] is False
        closure_audit = workflow.codex_promotion_closure_audit()["codex_promotion_closure_audit"]
        assert closure_audit["closure_status"] == "blocked_until_promotion_execution_result_ready"
        assert closure_audit["sync_audit_candidate_count"] == 0
        assert closure_audit["automatic_sync_allowed"] is False
        sync_gate = workflow.codex_promotion_sync_review_gate()["codex_promotion_sync_review_gate"]
        assert sync_gate["gate_status"] == "blocked_until_promotion_closure_ready"
        assert sync_gate["sync_candidate_count"] == 0
        assert sync_gate["future_sync_action_count"] == 0
        assert sync_gate["automatic_sync_allowed"] is False
        sync_handoff = workflow.codex_promotion_sync_handoff()["codex_promotion_sync_handoff_queue"]
        assert sync_handoff["handoff_status"] == "blocked_until_promotion_closure_ready"
        assert sync_handoff["handoff_item_count"] == 0
        assert sync_handoff["automatic_execution_allowed"] is False
        sync_readiness = workflow.codex_promotion_sync_execution_readiness()["codex_promotion_sync_execution_readiness_gate"]
        assert sync_readiness["readiness_status"] == "blocked_until_promotion_closure_ready"
        assert sync_readiness["readiness_item_count"] == 0
        assert sync_readiness["automatic_sync_execution_allowed"] is False
        assert sync_readiness["readiness_review_state"]["readiness_review_count"] == 0
        sync_result_intake = workflow.codex_promotion_sync_execution_results()["codex_promotion_sync_execution_result_intake"]
        assert sync_result_intake["intake_status"] == "blocked_until_sync_execution_ready"
        assert sync_result_intake["result_count"] == 0
        assert sync_result_intake["automatic_sync_execution_allowed"] is False
        sync_closure = workflow.codex_promotion_sync_closure_audit()["codex_promotion_sync_closure_audit"]
        assert sync_closure["closure_status"] == "blocked_until_sync_execution_result_ready"
        assert sync_closure["expected_result_count"] == 0
        assert sync_closure["complete_result_count"] == 0
        assert sync_closure["automatic_sync_allowed"] is False
        sync_closure_review = workflow.codex_promotion_sync_closure_review_gate()["codex_promotion_sync_closure_review_gate"]
        assert sync_closure_review["gate_status"] == "blocked_until_sync_closure_ready"
        assert sync_closure_review["candidate_count"] == 0
        assert sync_closure_review["future_real_sync_action_count"] == 0
        assert sync_closure_review["automatic_final_sync_allowed"] is False
        final_sync_handoff = workflow.codex_promotion_final_sync_handoff()["codex_promotion_final_sync_handoff_queue"]
        assert final_sync_handoff["handoff_status"] == "blocked_until_sync_closure_ready"
        assert final_sync_handoff["handoff_item_count"] == 0
        assert final_sync_handoff["automatic_execution_allowed"] is False
        final_sync_readiness = workflow.codex_promotion_final_sync_execution_readiness()["codex_promotion_final_sync_execution_readiness_gate"]
        assert final_sync_readiness["readiness_status"] == "blocked_until_sync_closure_ready"
        assert final_sync_readiness["readiness_item_count"] == 0
        assert final_sync_readiness["automatic_execution_allowed"] is False
        final_sync_result_intake = workflow.codex_promotion_final_sync_execution_results()["codex_promotion_final_sync_execution_result_intake"]
        assert final_sync_result_intake["intake_status"] == "blocked_until_final_sync_execution_ready"
        assert final_sync_result_intake["result_count"] == 0
        assert final_sync_result_intake["automatic_execution_allowed"] is False
        final_sync_closure = workflow.codex_promotion_final_sync_closure_audit()["codex_promotion_final_sync_closure_audit"]
        assert final_sync_closure["closure_status"] == "blocked_until_final_sync_execution_result_ready"
        assert final_sync_closure["expected_result_count"] == 0
        assert final_sync_closure["complete_result_count"] == 0
        assert final_sync_closure["automatic_closure_allowed"] is False
        assert final_sync_closure["automatic_project_memory_write_allowed"] is False
        final_completion_review = workflow.codex_promotion_final_completion_review_gate()["codex_promotion_final_completion_review_gate"]
        assert final_completion_review["gate_status"] == "blocked_until_final_sync_closure_ready"
        assert final_completion_review["candidate_count"] == 0
        assert final_completion_review["automatic_completion_allowed"] is False
        assert final_completion_review["automatic_project_memory_write_allowed"] is False
        final_publication_handoff = workflow.codex_promotion_final_publication_handoff()["codex_promotion_final_publication_handoff_queue"]
        assert final_publication_handoff["handoff_status"] == "blocked_until_final_sync_closure_ready"
        assert final_publication_handoff["handoff_item_count"] == 0
        assert final_publication_handoff["automatic_publication_allowed"] is False
        assert final_publication_handoff["project_memory_publication_allowed"] is False
        final_publication_readiness = workflow.codex_promotion_final_publication_readiness()["codex_promotion_final_publication_readiness_gate"]
        assert final_publication_readiness["readiness_status"] == "blocked_until_final_sync_closure_ready"
        assert final_publication_readiness["readiness_item_count"] == 0
        assert final_publication_readiness["automatic_publication_allowed"] is False
        assert final_publication_readiness["project_memory_publication_allowed"] is False
        final_publication_results = workflow.codex_promotion_final_publication_results()["codex_promotion_final_publication_result_intake"]
        assert final_publication_results["intake_status"] == "blocked_until_final_publication_ready"
        assert final_publication_results["result_count"] == 0
        assert final_publication_results["automatic_publication_allowed"] is False
        assert final_publication_results["project_memory_publication_allowed"] is False
        final_publication_closure = workflow.codex_promotion_final_publication_closure_audit()["codex_promotion_final_publication_closure_audit"]
        assert final_publication_closure["closure_status"] == "blocked_until_final_publication_result_ready"
        assert final_publication_closure["expected_result_count"] == 0
        assert final_publication_closure["complete_result_count"] == 0
        assert final_publication_closure["missing_result_count"] == 0
        assert final_publication_closure["automatic_closure_allowed"] is False
        assert final_publication_closure["automatic_project_memory_write_allowed"] is False
        final_release_review = workflow.codex_promotion_final_release_review_gate()["codex_promotion_final_release_review_gate"]
        assert final_release_review["gate_status"] == "blocked_until_final_publication_closure_ready"
        assert final_release_review["release_review_candidate_count"] == 0
        assert final_release_review["automatic_release_allowed"] is False
        assert final_release_review["live_hermes_write_allowed"] is False
        assert "1qaz" not in serialized
        assert "password" not in serialized


def test_training_page_exposes_auto_training_console_and_language_switch():
    web_root = Path("src/web_app")
    page = (web_root / "training.html").read_text(encoding="utf-8")
    script = (web_root / "training.js").read_text(encoding="utf-8")
    docs = (web_root / "docs.html").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert "Santoni Athena - Training Console" in page
    assert "Run Auto Training" in page
    assert '/i18n.js?v=0.113.1' in page
    assert '/training.js?v=0.113.1' in page
    assert "/api/training/overview" in script
    assert "/api/training/run" in script
    assert "/api/training/review" in script
    assert "/api/training/data-source" in script
    assert "/api/training/handoff-review" in script
    assert "/api/training/round-summary" in script
    assert "/api/training/promote-baseline" in script
    assert "/api/training/playbook-regression" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/regression-run" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/regression-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/next-loop" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/handoff-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/next-loop-closure" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/iteration-proposal" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/iteration-proposal-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/iteration-proposal-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-work-packets" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-patch-queue" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-execution-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-execution-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-execution-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-prep" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-launch" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-results" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-result" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-result-review-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-result-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-worktree-result-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-candidates" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-approval-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-approvals" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-approval" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-handoff" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-execution-readiness" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-readiness-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-readiness-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-execution-results" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-execution-result" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-closure-audit" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-review-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-handoff" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-readiness" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-readiness-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-readiness-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-execution-results" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-execution-result" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-sync-closure-audit" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-sync-handoff" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-sync-readiness" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-sync-execution-results" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-sync-execution-result" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-sync-closure-audit" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-completion-review-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-completion-reviews" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-completion-review" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-publication-closure-audit" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "/api/training/codex-promotion-final-release-review-gate" in Path("scripts/run_web_demo.py").read_text(encoding="utf-8")
    assert "Review / Data Intake State" in page
    assert "Register Data Source" in script
    assert "Training Round Summary / Promote Baseline" in page
    assert "Promote Approved Baseline" in page
    assert "Playbook Regression Queue" in page
    assert "Automatic Regression Run" in page
    assert "Run Regression" in page
    assert "Regression Gate" in page
    assert "Next Loop Handoff" in page
    assert "Next Loop Closure Gate" in page
    assert "Training Iteration Proposal" in page
    assert "Codex Work Packet Queue" in page
    assert "Codex Patch Queue Contract" in page
    assert "Codex Execution Gate" in page
    assert "Codex Worktree Preparation Queue" in page
    assert "Codex Worktree Launch Gate" in page
    assert "Codex Worktree Result Intake" in page
    assert "Codex Worktree Result Review Gate" in page
    assert "Codex Promotion Candidate Queue" in page
    assert "Codex Promotion Approval Gate" in page
    assert "Codex Promotion Handoff Queue" in page
    assert "Codex Promotion Execution Readiness Gate" in page
    assert "Codex Promotion Execution Readiness Review" in page
    assert "Codex Promotion Execution Result Intake" in page
    assert "Codex Promotion Closure / Hermes Sync Audit" in page
    assert "Codex Promotion Sync Review Gate" in page
    assert "Codex Promotion Sync Handoff Queue" in page
    assert "Codex Promotion Sync Execution Readiness Gate" in page
    assert "Codex Promotion Sync Execution Readiness Review" in page
    assert "Codex Promotion Sync Execution Result Intake" in page
    assert "Codex Promotion Sync Closure Audit" in page
    assert "Codex Promotion Final Sync Handoff Queue" in page
    assert "Codex Promotion Final Sync Execution Readiness Gate" in page
    assert "Codex Promotion Final Sync Execution Result Intake" in page
    assert "Codex Promotion Final Sync Closure Audit" in page
    assert "Codex Promotion Final Completion Review Gate" in page
    assert "Codex Promotion Final Publication Closure Audit" in page
    assert "Read Only" in page
    assert "Local Contract" in page
    assert 'id="playbookRegressionQueue"' in page
    assert 'id="trainingRegressionRun"' in page
    assert 'id="trainingRegressionGate"' in page
    assert 'id="trainingNextLoopHandoff"' in page
    assert 'id="trainingNextLoopClosure"' in page
    assert 'id="trainingIterationProposal"' in page
    assert 'id="codexWorkPacketQueue"' in page
    assert 'id="worktreeLaunchGate"' in page
    assert 'id="worktreeResultIntake"' in page
    assert 'id="worktreeResultReviewGate"' in page
    assert 'id="promotionCandidateQueue"' in page
    assert 'id="promotionApprovalGate"' in page
    assert 'id="promotionHandoffQueue"' in page
    assert 'id="promotionReadinessGate"' in page
    assert 'id="promotionExecutionResultIntake"' in page
    assert 'id="promotionClosureAudit"' in page
    assert 'id="promotionSyncReviewGate"' in page
    assert 'id="promotionSyncHandoffQueue"' in page
    assert 'id="promotionSyncReadinessGate"' in page
    assert 'id="promotionSyncExecutionResultIntake"' in page
    assert 'id="promotionSyncClosureAudit"' in page
    assert 'id="promotionFinalSyncHandoffQueue"' in page
    assert 'id="promotionFinalSyncReadinessGate"' in page
    assert 'id="promotionFinalSyncExecutionResultIntake"' in page
    assert 'id="promotionFinalSyncClosureAudit"' in page
    assert 'id="promotionFinalCompletionReviewGate"' in page
    assert 'id="promotionFinalPublicationHandoffQueue"' in page
    assert 'id="promotionFinalPublicationReadinessGate"' in page
    assert 'id="promotionFinalPublicationResultIntake"' in page
    assert 'id="promotionFinalPublicationClosureAudit"' in page
    assert 'id="promotionFinalReleaseReviewGate"' in page
    assert "renderPlaybookRegressionQueue" in script
    assert "renderRegressionRun" in script
    assert "renderRegressionGate" in script
    assert "renderNextLoopHandoff" in script
    assert "renderNextLoopClosure" in script
    assert "renderIterationProposal" in script
    assert "renderCodexWorkPackets" in script
    assert "renderCodexPatchQueue" in script
    assert "renderCodexExecutionGate" in script
    assert "renderCodexWorktreePrep" in script
    assert "renderCodexWorktreeLaunchGate" in script
    assert "renderCodexWorktreeResults" in script
    assert "renderCodexWorktreeResultReviewGate" in script
    assert "saveCodexWorktreeResultReview" in script
    assert "renderCodexPromotionCandidates" in script
    assert "renderCodexPromotionApprovalGate" in script
    assert "renderCodexPromotionHandoff" in script
    assert "renderCodexPromotionReadiness" in script
    assert "renderCodexPromotionExecutionResults" in script
    assert "renderCodexPromotionClosureAudit" in script
    assert "renderCodexPromotionSyncReviewGate" in script
    assert "renderCodexPromotionSyncHandoff" in script
    assert "renderCodexPromotionSyncReadiness" in script
    assert "renderCodexPromotionSyncExecutionResults" in script
    assert "renderCodexPromotionSyncClosureAudit" in script
    assert "renderCodexPromotionFinalSyncHandoff" in script
    assert "renderCodexPromotionFinalSyncReadiness" in script
    assert "renderCodexPromotionFinalSyncExecutionResults" in script
    assert "renderCodexPromotionFinalSyncClosureAudit" in script
    assert "renderCodexPromotionFinalCompletionReviewGate" in script
    assert "renderCodexPromotionFinalPublicationHandoff" in script
    assert "renderCodexPromotionFinalPublicationReadiness" in script
    assert "renderCodexPromotionFinalPublicationResults" in script
    assert "renderCodexPromotionFinalPublicationClosureAudit" in script
    assert "saveCodexPromotionFinalCompletionReview" in script
    assert "saveCodexPromotionSyncReadinessReview" in script
    assert "saveCodexPromotionSyncExecutionResult" in script
    assert "saveCodexPromotionFinalSyncExecutionResult" in script
    assert "saveCodexPromotionSyncReview" in script
    assert "saveCodexPromotionReadinessReview" in script
    assert "saveCodexPromotionExecutionResult" in script
    assert "saveCodexPromotionApproval" in script
    assert "saveCodexExecutionReview" in script
    assert "saveIterationProposalReview" in script
    assert "data-iteration-review" in script
    assert "saveHandoffReview" in script
    assert "data-handoff-review" in script
    assert "runRegressionButton" in script
    assert "playbook_regression_queue" in script
    assert "regression_overview" in script
    assert "regression_gate" in script
    assert "next_loop_handoff" in script
    assert "next_loop_closure" in script
    assert "training_iteration_proposal" in script
    assert "codex_work_packet_queue" in script
    assert "codex_patch_queue_contract" in script
    assert "codex_execution_gate" in script
    assert "codex_worktree_preparation_queue" in script
    assert "codex_worktree_launch_gate" in script
    assert "codex_worktree_result_intake" in script
    assert "codex_worktree_result_review_gate" in script
    assert "codex_promotion_candidate_queue" in script
    assert "codex_promotion_approval_gate" in script
    assert "codex_promotion_handoff_queue" in script
    assert "codex_promotion_execution_readiness_gate" in script
    assert "codex_promotion_closure_audit" in script
    assert "codex_promotion_sync_review_gate" in script
    assert "codex_promotion_sync_handoff_queue" in script
    assert "codex_promotion_sync_execution_readiness_gate" in script
    assert "codex_promotion_sync_readiness_review_state" in script
    assert "codex_promotion_sync_execution_result_intake" in script
    assert "codex_promotion_sync_closure_audit" in script
    assert "codex_promotion_sync_closure_review_gate" in script
    assert "codex_promotion_final_sync_handoff_queue" in script
    assert "codex_promotion_final_sync_execution_readiness_gate" in script
    assert "codex_promotion_final_sync_execution_result_intake" in script
    assert "codex_promotion_final_sync_closure_audit" in script
    assert "codex_promotion_final_completion_review_gate" in script
    assert "codex_promotion_final_publication_handoff_queue" in script
    assert "codex_promotion_final_publication_readiness_gate" in script
    assert "codex_promotion_final_publication_result_intake" in script
    assert "codex_promotion_final_publication_closure_audit" in script
    assert "codex_promotion_final_release_review_gate" in script
    assert "promotionSyncClosureReviewGate" in page
    assert "promotionFinalSyncHandoffQueue" in page
    assert "promotionFinalSyncReadinessGate" in page
    assert "promotionFinalSyncExecutionResultIntake" in page
    assert "promotionFinalSyncClosureAudit" in page
    assert "promotionFinalCompletionReviewGate" in page
    assert "promotionFinalPublicationHandoffQueue" in page
    assert "promotionFinalPublicationReadinessGate" in page
    assert "promotionFinalPublicationResultIntake" in page
    assert "promotionFinalReleaseReviewGate" in page
    assert "renderCodexPromotionFinalReleaseReviewGate" in script
    assert "renderCodexPromotionSyncClosureReviewGate" in script
    assert "data-promotion-readiness-review" in script
    assert "data-promotion-execution-result" in script
    assert "data-promotion-sync-review" in script
    assert "data-promotion-sync-readiness-review" in script
    assert "data-promotion-sync-execution-result" in script
    assert "data-promotion-sync-closure-review" in script
    assert "data-promotion-final-sync-execution-result" in script
    assert "data-promotion-final-completion-review" in script
    assert "data-promotion-final-publication-result" in script
    assert "data-result-review" in script
    assert "data-promotion-approval" in script
    assert "data-execution-review" in script
    assert "approved_for_worktree_preparation" in script
    assert "approved_for_codex_queue" in script
    assert "handoff_review" in script
    assert "raw files are not uploaded or stored" in script
    assert "Hermes Result JSON" in page
    assert "model-weight fine-tuning" in script
    assert "Open Athena Training Console" in docs
    assert "Athena Automatic Training Console" in changelog
    assert "Playbook Regression Queue" in changelog
    assert "Automatic Regression Runner" in changelog
    assert "Regression Gate" in changelog
    assert "Next Loop Handoff" in changelog
    assert "Next Loop Handoff Review" in changelog
    assert "Next Loop Closure Gate" in changelog
    assert "Training Iteration Proposal" in changelog
    assert "Training Iteration Proposal Review" in changelog
    assert "Codex Work Packet Queue" in changelog
    assert "Codex Patch Queue Contract" in changelog
    assert "Codex Execution Gate" in changelog
    assert "Codex Execution Gate Review" in changelog
    assert "Codex Worktree Preparation Queue" in changelog
    assert "Codex Worktree Launch Gate" in changelog
    assert "Codex Worktree Result Intake" in changelog
    assert "Codex Worktree Result Review Gate" in changelog
    assert "Codex Promotion Candidate Queue" in changelog
    assert "Codex Promotion Approval Gate" in changelog
    assert "Codex Promotion Handoff Queue" in changelog
    assert "Codex Promotion Execution Readiness Gate" in changelog
    assert "Codex Promotion Execution Readiness Review" in changelog
    assert "Codex Promotion Execution Result Intake" in changelog
    assert "Codex Promotion Closure / Hermes Sync Audit" in changelog
    assert "Codex Promotion Sync Review Gate" in changelog
    assert "Codex Promotion Sync Handoff Queue" in changelog
    assert "Codex Promotion Sync Execution Readiness Gate" in changelog
    assert "Codex Promotion Sync Execution Readiness Review" in changelog
    assert "Codex Promotion Sync Execution Result Intake" in changelog
    assert "Codex Promotion Sync Closure Audit" in changelog
    assert "Codex Promotion Sync Closure Review Gate" in changelog
    assert "Codex Promotion Final Sync Handoff Queue" in changelog
    assert "Codex Promotion Final Sync Execution Readiness Gate" in changelog
    assert "Codex Promotion Final Sync Execution Result Intake" in changelog
    assert "Codex Promotion Final Sync Closure Audit" in changelog
    assert "Codex Promotion Final Completion Review Gate" in changelog
    assert "Codex Promotion Final Publication Handoff Queue" in changelog
    assert "Codex Promotion Final Publication Readiness Gate" in changelog
    assert "Codex Promotion Final Publication Result Intake" in changelog
    assert "Codex Promotion Final Publication Closure Audit" in changelog
    assert "Codex Promotion Final Release / Archive Review Gate" in changelog
    assert "Training Review and Data Intake" in changelog
    assert "Training Round Summary and Baseline Promotion" in changelog


def test_design_intake_page_explains_structuring_scope():
    web_root = Path("src/web_app")
    page = (web_root / "athena-mvp.html").read_text(encoding="utf-8")
    script = (web_root / "athena-mvp.js").read_text(encoding="utf-8")
    athena_architecture = Path("docs/Athena.html").read_text(encoding="utf-8")

    assert "Design Intake Structuring Console" in page
    assert "Design Agent data-structuring middleware test page" in page
    assert "not the full Athena MVP" in page
    assert "not a manual design-exhaustion tool" in page
    assert "Athena Core Value Proposition" in page
    assert "workflow-native onsite workforce" in page
    assert "turns management questions into decision loops" in page
    assert "Hermes-governed memory events, playbooks, and regression cases" in page
    assert "Athena Three Core Capabilities" in athena_architecture
    assert "Workflow-native onsite workforce" in athena_architecture
    assert "Management decision-loop agent" in athena_architecture
    assert "Hermes-governed self-evolution" in athena_architecture
    assert "Future role after design-software or file import" in page
    assert "Constraint discovery and training should be automated" in page
    assert "Run Structuring Test" in page
    assert "Engineering Brief Candidate" in page
    assert "design-intake-structuring-evidence" in script


def test_athena_mvp_workflow_outputs_structured_objects_and_evidence():
    result = AthenaMvpWorkflow().run(
        {
            "source_type": "style3d",
            "product_category": "seamless running top",
            "target_user": "women performance runners",
            "use_case": "summer running",
            "functional_requirements": "breathability, quick dry, light compression, small logo pattern",
            "sampling_feedback": "Round 1: support zone feels slightly stiff.",
            "defect_signals": "support zone stiffness, logo elasticity variation",
        }
    )

    assert result["workflow_template"]["template_id"] == "athena.design_to_production_readiness.v1"
    assert result["workflow_instance"]["not_a_chatbot"] is True
    assert result["workflow_instance"]["not_a_generic_design_agent"] is True
    assert set(result["data_objects"]) == {
        "design_request",
        "engineering_brief",
        "manufacturability_check",
        "sampling_feedback",
        "revision_suggestion",
        "production_readiness",
    }
    assert result["data_objects"]["engineering_brief"]["target_system"] == "SWS/Arachne"
    assert result["data_objects"]["manufacturability_check"]["risk_checks"]
    assert result["data_objects"]["production_readiness"]["gate"] in {
        "ready_for_pilot_production",
        "sample_round_required",
        "engineering_revision_required",
    }
    assert len(result["stages"]) == 6
    assert len(result["evidence_log"]) == 6
    assert any(item["kpi"] == "production_readiness_score" for item in result["kpi_log"])
    assert any(tool["tool"] == "SWS/Arachne Engineering Brief Adapter" for tool in result["tool_interfaces"])


def test_tianpai_aps_erp_export_adapter_reads_no_header_csv_by_ddl_order():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "field_schema.sql").write_text(
            """
create table aps.Produce_Order (
    id bigint,
    code varchar(255),
    delivery_time datetime,
    status tinyint
);
create table aps.Weaving_Part_Order (
    id bigint,
    produce_order_code varchar(128),
    sku_code varchar(128),
    part varchar(64),
    quantity int,
    produced_quantity int,
    planned_quantity int,
    finish_time datetime,
    status tinyint
);
create table aps.Planned_Task (
    id bigint,
    produce_order_code varchar(255),
    weaving_part_order_id bigint,
    machine_id bigint,
    sku_code varchar(255),
    part varchar(128),
    produced_quantity int,
    planned_quantity int,
    plan_start_time datetime,
    plan_end_time datetime,
    status tinyint
);
create table aps.Manual_Machine_Production (
    id bigint,
    task_id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(255),
    device_id varchar(255),
    date varchar(64),
    operator_quantity int,
    operator_defects int,
    operator_discards double,
    inspector_defects int
);
create table aps.Style_Component (
    id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(128),
    cylinder_diameter int,
    needle_spacing int,
    expected_produce_time decimal(10,2),
    yarn_usage text
);
create table aps.Style_Sku (
    id bigint,
    produce_order_code varchar(255),
    style_code varchar(255),
    code varchar(255),
    size varchar(128),
    expected_produce_time decimal(10,2)
);
create table T_Machine_Info (
    f_machine_id bigint,
    f_machine_code varchar(255),
    f_cylinder_diameter varchar(255),
    f_needle_spacing varchar(255)
);
""",
            encoding="utf-8",
        )
        (root / "Produce_Order.csv").write_text("1,PO-001,2026-06-20 00:00:00,3\n", encoding="utf-8")
        (root / "Weaving_Part_Order.csv").write_text("10,PO-001,SKU-001,澶ц韩,100,40,80,2026-06-20 00:00:00,3\n", encoding="utf-8")
        (root / "Planned_Task.csv").write_text("100,PO-001,10,900,SKU-001,澶ц韩,40,80,2026-06-12 08:00:00,2026-06-13 18:00:00,3\n", encoding="utf-8")
        (root / "Manual_Machine_Production.csv").write_text("1000,100,PO-001,SKU-001,澶ц韩,M-001,2026-06-12,42,0,0,0\n", encoding="utf-8")
        (root / "Style_Component.csv").write_text("20,PO-001,SKU-001,澶ц韩,14,28,160,[]\n", encoding="utf-8")
        (root / "Style_Sku.csv").write_text("30,PO-001,STYLE-001,SKU-001,S,160\n", encoding="utf-8")
        (root / "T_Machine_Info.csv").write_text("900,M-001,14瀵?28G\n", encoding="utf-8")

        report = TianpaiApsErpExportAdapter(root).report()

    joins = {item["join_id"]: item for item in report["data_quality_report"]["join_quality"]}

    assert report["adapter_status"] == "read_only_external_csv"
    assert report["read_only"] is True
    assert report["raw_file_stored_in_repo"] is False
    assert report["tables"]["Produce_Order"]["fields"] == ["id", "code", "delivery_time", "status"]
    assert report["standard_objects"]["object_counts"]["production_order"] == 1
    assert report["standard_objects"]["actual_snapshot_metrics"]["planned_quantity"] == 80
    assert report["standard_objects"]["actual_snapshot_metrics"]["manual_report_good_quantity"] == 42
    assert report["standard_objects"]["actual_snapshot_metrics"]["machine_plan_load_candidate_count"] == 1
    assert report["standard_objects"]["actual_snapshot_metrics"]["machine_style_spec_mismatch_candidate_count"] == 0
    assert report["standard_objects"]["machine_plan_load"][0]["machine_code"] == "M-001"
    assert report["standard_objects"]["machine_plan_load"][0]["planned_quantity"] == 80
    assert joins["weaving_part_order_to_produce_order"]["match_rate"] == 1.0
    assert joins["planned_task_to_weaving_part_order"]["match_rate"] == 1.0
    assert joins["manual_report_to_planned_task"]["match_rate"] == 1.0
    assert "copy_raw_customer_csv_into_repo" in report["blocked_actions"]


def test_tianpai_aps_erp_export_adapter_filters_deleted_rows_and_marks_sanity_flags():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "field_schema.sql").write_text(
            """
create table aps.Produce_Order (
    id bigint,
    code varchar(255),
    delivery_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Weaving_Part_Order (
    id bigint,
    produce_order_code varchar(128),
    sku_code varchar(128),
    part varchar(64),
    quantity int,
    produced_quantity int,
    planned_quantity int,
    finish_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Planned_Task (
    id bigint,
    produce_order_code varchar(255),
    weaving_part_order_id bigint,
    machine_id bigint,
    produced_quantity int,
    planned_quantity int,
    plan_start_time datetime,
    plan_end_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Manual_Machine_Production (
    id bigint,
    task_id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(255),
    device_id varchar(255),
    date varchar(64),
    operator_quantity int,
    deleted_at bigint
);
create table aps.Style_Component (
    id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(128),
    cylinder_diameter int,
    needle_spacing int,
    deleted_at bigint
);
create table aps.Style_Sku (
    id bigint,
    produce_order_code varchar(255),
    style_code varchar(255),
    code varchar(255),
    deleted_at bigint
);
create table T_Machine_Info (
    f_machine_id bigint,
    f_machine_code varchar(255),
    f_cylinder_diameter varchar(255),
    f_needle_spacing varchar(255),
    f_deleted bigint
);
""",
            encoding="utf-8",
        )
        (root / "Produce_Order.csv").write_text(
            "1,STALE,2000-01-01 00:00:00,0,0\n"
            "2,ACTIVE,,0,0\n"
            "3,GAP,2999-01-01 00:00:00,0,0\n"
            "4,DONE_RECON,,0,0\n",
            encoding="utf-8",
        )
        (root / "Weaving_Part_Order.csv").write_text(
            "10,STALE,SKU,澶ц韩,50000,0,0,2000-01-01 00:00:00,0,999\n"
            "11,STALE,SKU,澶ц韩,100,0,100,2000-01-01 00:00:00,0,0\n"
            "12,ACTIVE,SKU,澶ц韩,1000,0,0,,0,0\n"
            "13,GAP,SKU,澶ц韩,100,0,100,2999-01-01 00:00:00,0,0\n"
            "14,DONE_RECON,SKU,澶ц韩,200,100,100,,0,0\n",
            encoding="utf-8",
        )
        (root / "Planned_Task.csv").write_text(
            "100,STALE,11,900,0,100,2026-06-01 00:00:00,2026-06-02 00:00:00,0,0\n"
            "101,GAP,13,900,0,100,2026-06-01 00:00:00,2026-06-02 00:00:00,0,0\n"
            "102,DONE_RECON,14,900,100,100,2026-06-01 00:00:00,2026-06-02 00:00:00,0,0\n",
            encoding="utf-8",
        )
        (root / "Manual_Machine_Production.csv").write_text(
            "1000,101,GAP,SKU,澶ц韩,M-001,2026-06-02,20000,0\n"
            "1001,102,DONE_RECON,SKU,澶ц韩,M-001,2026-06-02,20000,0\n",
            encoding="utf-8",
        )
        (root / "Style_Component.csv").write_text("", encoding="utf-8")
        (root / "Style_Sku.csv").write_text("", encoding="utf-8")
        (root / "T_Machine_Info.csv").write_text("900,M-001,14,28,0\n", encoding="utf-8")

        adapter = TianpaiApsErpExportAdapter(root)
        report = adapter.report()
        delivery = adapter.answer_management_question("delivery risk")
        delivery_alias = adapter.answer_management_question("哪个订单最可能影响交付？")
        gap = adapter.answer_management_question("planned vs reported quantity gap")
        review_queue = adapter.delivery_evidence_review_queue(language="en")
        review_answer = adapter.answer_management_question("which orders are evidence review candidates?")
        loads = adapter._load_tables()
        tables = {name: adapter._active_rows(name, load.rows) for name, load in loads.items()}
        done_recon = next(item for item in adapter._order_aggregates(tables) if item["produce_order_code"] == "DONE_RECON")

    assert report["version"] == "v0.113.1"
    assert report["tables"]["Weaving_Part_Order"]["raw_row_count"] == 5
    assert report["tables"]["Weaving_Part_Order"]["row_count"] == 4
    assert report["tables"]["Weaving_Part_Order"]["excluded_deleted_row_count"] == 1
    delivery_codes = {item["produce_order_code"] for item in delivery["actual_evidence_chains"]}
    assert "STALE" not in delivery_codes
    assert "ACTIVE" in delivery_codes
    assert "DONE_RECON" not in delivery_codes
    assert delivery_alias["actual_data_mode"] is True
    assert delivery_alias["metric"] == "order_delay"
    assert done_recon["plan_completion_rate"] == 1
    assert any(driver["classification"] == "data_reconciliation" for driver in done_recon["delivery_risk_drivers"])
    assert delivery["metric_snapshot"]["delivery_reconciliation_candidate_count"] >= 1
    gap_chain = next(item for item in gap["actual_evidence_chains"] if item["produce_order_code"] == "GAP")
    assert gap_chain["quantity_gap_review_status"] == "needs_reconciliation"
    assert "extreme_manual_report_vs_plan_gap_needs_reconciliation" in gap_chain["data_sanity_flags"]
    assert gap["confidence"] == "medium_with_reconciliation_needed"
    assert review_queue["schema_id"] == "athena.production_evidence_review_queue.v1"
    assert review_queue["read_only"] is True
    queue_card = next(item for item in review_queue["review_queue"] if item["produce_order_code"] == "DONE_RECON")
    assert queue_card["why_not_delivery_risk"]
    assert queue_card["reconciliation_drivers"]
    assert queue_card["field_sources"]
    assert queue_card["suggested_confirmation_owner"] == "Planning Manager / APS Owner"
    assert queue_card["suggested_confirmation_action"]
    assert queue_card["cannot_conclude_reason"]
    assert queue_card["read_only_boundary"]["read_only"] is True
    assert review_answer["metric"] == "evidence_review"
    assert review_answer["confidence"] == "medium_with_reconciliation_needed"


def test_tianpai_aps_erp_export_adapter_machine_style_mismatch_has_required_vs_actual_values():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "field_schema.sql").write_text(
            """
create table aps.Produce_Order (
    id bigint,
    code varchar(255),
    delivery_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Weaving_Part_Order (
    id bigint,
    produce_order_code varchar(128),
    sku_code varchar(128),
    part varchar(64),
    quantity int,
    produced_quantity int,
    planned_quantity int,
    finish_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Planned_Task (
    id bigint,
    produce_order_code varchar(255),
    weaving_part_order_id bigint,
    machine_id bigint,
    style_code varchar(255),
    sku_code varchar(255),
    part varchar(128),
    produced_quantity int,
    planned_quantity int,
    plan_start_time datetime,
    plan_end_time datetime,
    status tinyint,
    deleted_at bigint
);
create table aps.Manual_Machine_Production (
    id bigint,
    task_id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(255),
    device_id varchar(255),
    date varchar(64),
    operator_quantity int,
    deleted_at bigint
);
create table aps.Style_Component (
    id bigint,
    produce_order_code varchar(255),
    sku_code varchar(255),
    part varchar(128),
    cylinder_diameter int,
    needle_spacing int,
    deleted_at bigint
);
create table aps.Style_Sku (
    id bigint,
    produce_order_code varchar(255),
    style_code varchar(255),
    code varchar(255),
    deleted_at bigint
);
create table T_Machine_Info (
    f_machine_id bigint,
    f_machine_code varchar(255),
    f_cylinder_diameter varchar(255),
    f_needle_spacing varchar(255),
    f_deleted bigint
);
""",
            encoding="utf-8",
        )
        (root / "Produce_Order.csv").write_text("1,PO-MIS,2999-01-01 00:00:00,0,0\n", encoding="utf-8")
        (root / "Weaving_Part_Order.csv").write_text("10,PO-MIS,SKU-MIS,澶ц韩,100,0,100,2999-01-01 00:00:00,0,0\n", encoding="utf-8")
        (root / "Planned_Task.csv").write_text("238,PO-MIS,10,970,STYLE-MIS,SKU-MIS,澶ц韩,0,100,2026-06-01 00:00:00,2026-06-02 00:00:00,0,0\n", encoding="utf-8")
        (root / "Manual_Machine_Production.csv").write_text("", encoding="utf-8")
        (root / "Style_Component.csv").write_text("20,PO-MIS,SKU-MIS,澶ц韩,18,28,0\n", encoding="utf-8")
        (root / "Style_Sku.csv").write_text("", encoding="utf-8")
        (root / "T_Machine_Info.csv").write_text("970,C7-U12,17,28,0\n", encoding="utf-8")

        result = TianpaiApsErpExportAdapter(root).answer_management_question("machine style mismatch cylinder")

    chain = result["actual_evidence_chains"][0]
    cause = result["root_causes"][0]["cause"]
    detail = chain["mismatch_details"][0]

    assert result["metric"] == "machine_style_mismatch"
    assert chain["planned_task_id"] == "238"
    assert chain["machine_code"] == "C7-U12"
    assert detail["field"] == "cylinder_diameter"
    assert detail["required_value"] == "18"
    assert detail["actual_machine_value"] == "17"
    assert detail["required_field_source"] == "Style_Component.cylinder_diameter"
    assert detail["actual_field_source"] == "T_Machine_Info.f_cylinder_diameter"
    assert "requires 18" in cause
    assert "has 17" in cause


def test_production_operations_workflow_outputs_read_only_management_console():
    result = ProductionOperationsWorkflow().overview()
    stage_ids = {stage["id"] for stage in result["workflow_stages"]}
    resource_keys = set(result["resource_lens"])
    kpis = {item["kpi"] for item in result["kpi_log"]}

    assert result["workflow_template"]["template_id"] == "athena.production_operations.v1"
    assert result["workflow_instance"]["read_only"] is True
    assert result["workflow_instance"]["version"] == "v0.113.1"
    assert result["production_object_model"]["schema_id"] == "athena.production_object_model.v1"
    assert result["production_object_model"]["canonical_workflow_key"]["field"] == "order_id"
    assert result["skill_registry"]["schema_id"] == "athena.production_skill_registry.v1"
    assert result["skill_registry"]["version"] == "v0.113.1"
    assert result["skill_registry"]["read_only"] is True
    assert {
        "gm_daily_brief_skill",
        "delivery_risk_skill",
        "machine_fit_skill",
        "material_constraint_skill",
        "bottleneck_detection_skill",
        "quality_or_scrap_skill",
        "service_escalation_skill",
        "follow_up_action_skill",
    }.issubset({item["skill_id"] for item in result["skill_registry"]["skills"]})
    assert {"order", "style", "machine", "material_inventory", "process_stage", "production_signal", "evidence", "decision", "action", "follow_up", "memory_event"}.issubset(
        {item["object"] for item in result["production_object_model"]["objects"]}
    )
    assert result["material_risk"]["schema_id"] == "athena.production_material_risk.v1"
    assert result["material_risk"]["source_summary"]["raw_file_stored_in_repo"] is False
    assert result["material_risk"]["inventory_structure"]["row_count"] == 8146
    assert result["material_risk"]["inventory_structure"]["unique_yarn_code_count"] == 128
    assert result["material_risk"]["balance_exceptions"]["zero_balance_rows"] == 968
    assert result["material_risk"]["balance_exceptions"]["negative_balance_rows"] == 4055
    assert "claim_order_delay_without_erp_aps_join" in result["material_risk"]["blocked_actions"]
    assert result["data_readiness"]["schema_id"] == "athena.tianpai_data_readiness.v1"
    assert result["data_readiness"]["source_status"]["erp_orders"] == "not_available"
    assert result["data_readiness"]["source_status"]["material_inventory"] == "available_aggregate"
    assert result["data_readiness"]["question_coverage"]["question_count"] == 17
    assert "DATA-ERP-ORDER-MIN" in {item["request_id"] for item in result["data_readiness"]["next_data_requests"]}
    assert result["general_manager_question_bank"]["schema_id"] == "athena.general_manager_question_bank.v1"
    assert result["general_manager_question_bank"]["status"] == "hypothesis_pending_voc"
    assert result["general_manager_question_bank"]["question_count"] == 17
    assert all(item["verification_status"] == "hypothesis" for item in result["general_manager_question_bank"]["questions"])
    assert result["management_priority_brief"]["brief_id"].startswith("MGMT-BRIEF-v0.113.1")
    assert result["management_priority_brief"]["priority_policy"]["kpi_priority"] == ["delivery", "quality", "cost"]
    assert result["management_priority_brief"]["priority_policy"]["card_themes"] == [
        "delivery_risk_order",
        "equipment_or_spec_risk",
        "material_or_quantity_control_risk",
    ]
    assert 3 <= len(result["management_priority_brief"]["daily_brief"]["summary"]) <= 5
    assert 3 <= len(result["management_priority_brief"]["daily_brief"]["summary_zh"]) <= 5
    assert any("Delivery:" in item for item in result["management_priority_brief"]["daily_brief"]["summary"])
    assert any("交付" in item for item in result["management_priority_brief"]["daily_brief"]["summary_zh"])
    assert any("data boundary" in item.lower() for item in result["management_priority_brief"]["daily_brief"]["summary"])
    assert len(result["management_priority_brief"]["top_priorities"]) == 3
    assert [item["management_theme"] for item in result["management_priority_brief"]["top_priorities"]] == ["delivery", "equipment", "material"]
    assert all(item.get("data_source_mode") for item in result["management_priority_brief"]["top_priorities"])
    assert all(item.get("actual_evidence_chains") or item.get("evidence_refs") for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["field_sources"] for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["skills_used"] for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["skill_execution_trace"] for item in result["management_priority_brief"]["top_priorities"])
    assert all(
        {"step_id", "skill_id", "evidence_refs", "evidence_level", "limitation_or_data_gap"}.issubset(
            item["skill_execution_trace"][0]
        )
        for item in result["management_priority_brief"]["top_priorities"]
    )
    assert all(item["internal_demo_ready"] is True for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["risk_level"] in {"red", "yellow", "gray"} for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["risk_level_label"] for item in result["management_priority_brief"]["top_priorities"])
    assert all(len(item["evidence_claims"]) >= 1 for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["evidence_refs"] for item in result["management_priority_brief"]["top_priorities"])
    assert all(item["action_candidate"]["requires_human_confirmation"] is True for item in result["management_priority_brief"]["top_priorities"])
    assert result["management_priority_brief"]["future_handoff_contract"]["next_engine"] == "decision_loop_follow_up_engine"
    assert result["evidence_review_queue"]["schema_id"] == "athena.production_evidence_review_queue.v1"
    assert result["evidence_review_queue"]["read_only"] is True
    assert result["evidence_review_queue"]["review_queue"]
    assert all(item["why_not_delivery_risk"] for item in result["evidence_review_queue"]["review_queue"])
    assert all(item["field_sources"] for item in result["evidence_review_queue"]["review_queue"])
    assert result["decision_loop"]["schema_id"] == "athena.production_decision_loop.v1"
    assert result["decision_loop"]["source_brief_id"] == result["management_priority_brief"]["brief_id"]
    assert result["decision_loop"]["closed_loop_contract"] == [
        "management_priority",
        "decision",
        "action",
        "follow_up",
        "owner_confirmation",
        "evidence_check",
        "memory_event_candidate",
    ]
    assert len(result["decision_loop"]["decision_items"]) >= 3
    assert len(result["decision_loop"]["action_items"]) >= 3
    assert len(result["decision_loop"]["follow_up_items"]) >= 3
    assert len(result["decision_loop"]["memory_event_candidates"]) >= 3
    assert {"pending_confirmation", "confirmed", "needs_more_data", "resolved", "dismissed"}.issubset(
        set(result["decision_loop"]["lifecycle"])
    )
    assert result["decision_loop"]["loop_kpis"]["open_follow_up_count"] >= 3
    assert set(item["status"] for item in result["decision_loop"]["follow_up_items"]).issubset(
        {"pending_confirmation", "assigned", "waiting_evidence", "confirmed", "closed", "unable_to_process"}
    )
    assert all(item["human_owner_required"] is True for item in result["decision_loop"]["follow_up_items"])
    assert all(item["linked_risk_card_id"] for item in result["decision_loop"]["follow_up_items"])
    assert all(item["linked_risk_level"] in {"red", "yellow", "gray"} for item in result["decision_loop"]["follow_up_items"])
    assert "auto_close_follow_up_without_evidence" in result["decision_loop"]["blocked_actions"]
    assert result["permission_boundary"]["schema_id"] == "athena.production_permission_boundary.v1"
    assert result["permission_boundary"]["final_confirmation_owner"] == "General Manager"
    assert "generate_local_follow_up_items" in result["permission_boundary"]["allowed_actions"]
    assert "modify_schedule_automatically" in result["permission_boundary"]["blocked_actions"]
    assert "dispatch_service_automatically" in result["permission_boundary"]["blocked_actions"]
    assert "evaluate_employee_performance_directly" in result["permission_boundary"]["blocked_actions"]
    assert "claim_certain_conclusion_when_evidence_is_insufficient" in result["permission_boundary"]["blocked_actions"]
    assert "replace_general_manager_decision" in result["permission_boundary"]["blocked_actions"]
    assert "individual employee performance" in result["permission_boundary"]["evidence_policy"]["employee_policy"]
    assert result["mvp_demo_story"]["schema_id"] == "athena.production_mvp_demo_story.v1"
    assert result["mvp_demo_story"]["source_prd_section"] == "16. MVP Demo Story"
    assert len(result["mvp_demo_story"]["story_steps"]) == 5
    assert "top_three_priorities_visible" in result["mvp_demo_story"]["success_criteria"]
    assert "final_confirmation_boundary_visible" in result["mvp_demo_story"]["success_criteria"]
    assert result["mvp_demo_story"]["read_only"] is True
    assert any(
        "service" in step["title"].lower() or "Service" in step["title"]
        for step in result["mvp_demo_story"]["story_steps"]
    )
    stable_pack = result["stable_demo_story_pack"]
    assert stable_pack["schema_id"] == "athena.production_stable_demo_story_pack.v1"
    assert stable_pack["version"] == "v0.113.1"
    assert stable_pack["read_only"] is True
    assert stable_pack["pack_id"].startswith("STABLE-DEMO-PACK-v0.113.1")
    assert len(stable_pack["stories"]) == 3
    assert [story["story_id"] for story in stable_pack["stories"]] == [
        "STABLE-DEMO-001-REAL-DELIVERY",
        "STABLE-DEMO-002-REAL-MACHINE-FIT",
        "STABLE-DEMO-003-HYBRID-SERVICE-IMPACT",
    ]
    assert all(story.get("evidence_mode") for story in stable_pack["stories"])
    assert all(story["chatbi_question"] for story in stable_pack["stories"])
    assert all(story["evidence_refs"] for story in stable_pack["stories"])
    assert stable_pack["stories"][0].get("actual_evidence_chains") or stable_pack["stories"][0].get("evidence_refs") is not None
    assert stable_pack["stories"][1].get("actual_evidence_chains") or stable_pack["stories"][1].get("evidence_refs") is not None
    assert stable_pack["stories"][2]["mock_supplements"]
    assert "live IOT alarm duration and OEE" in stable_pack["mock_needed_for_demo"]
    assert "claim_boundary" in stable_pack["demo_policy"]
    assert result["mvp_success_check"]["schema_id"] == "athena.production_mvp_success_check.v1"
    assert result["mvp_success_check"]["source_prd_section"] == "17. Success Criteria"
    assert result["mvp_success_check"]["within_three_minutes_ready"] is True
    assert result["mvp_success_check"]["readiness_status"] == "demo_ready_with_mock_evidence"
    assert result["mvp_success_check"]["readiness_score"] == 1.0
    assert result["mvp_success_check"]["criteria_summary"]["pass_count"] == 5
    assert len(result["mvp_success_check"]["criteria_checks"]) == 5
    assert {item["criterion_id"] for item in result["mvp_success_check"]["criteria_checks"]} == {
        "success_top_three_things",
        "success_why_they_matter",
        "success_evidence_support",
        "success_next_owner_confirmation",
        "success_missing_data_visible",
    }
    assert all(item["status"] == "pass" for item in result["mvp_success_check"]["criteria_checks"])
    assert "Level 1" in result["mvp_success_check"]["current_evidence_level"]
    assert "Real ERP/APS/IOT joins are not connected." in result["mvp_success_check"]["remaining_data_boundary"]
    assert result["prd_alignment_audit"]["schema_id"] == "athena.production_prd_alignment_audit.v1"
    assert result["prd_alignment_audit"]["source_prd"] == "docs/product/athena_prd_v0.1.md"
    assert len(result["prd_alignment_audit"]["section_checks"]) == 18
    assert result["prd_alignment_audit"]["read_only"] is True
    assert any(
        item["section"] == "17. Success Criteria" and item["status"] == "covered"
        for item in result["prd_alignment_audit"]["section_checks"]
    )
    assert any(
        item["section"] == "18. Open Questions For Later PRD Versions" and item["status"] == "open_by_design"
        for item in result["prd_alignment_audit"]["section_checks"]
    )
    assert "not prove live customer deployment readiness" in result["prd_alignment_audit"]["blocked_completion_claim"]
    assert result["tianpai_aps_erp_export"]["adapter_id"] == "athena.tianpai_aps_erp_export_adapter.v1"
    assert result["tianpai_aps_erp_export"]["read_only"] is True
    assert result["tianpai_aps_erp_export"]["raw_file_stored_in_repo"] is False
    assert "copy_raw_customer_csv_into_repo" in result["tianpai_aps_erp_export"]["blocked_actions"]
    assert result["tianpai_aps_erp_export"]["tables"]["Produce_Order"]["fields"][0] == "id"
    assert result["tianpai_aps_erp_export"]["standard_objects"]["schema_id"] == "athena.tianpai_aps_erp_standard_objects.v1"
    assert result["tianpai_aps_erp_export"]["standard_objects"]["canonical_join_chain"] == [
        "Produce_Order.code",
        "Weaving_Part_Order.produce_order_code",
        "Planned_Task.weaving_part_order_id",
        "Manual_Machine_Production.task_id",
    ]
    actual_metrics = result["tianpai_aps_erp_export"]["standard_objects"]["actual_snapshot_metrics"]
    assert actual_metrics["total_order_count"] >= 1
    assert actual_metrics["planned_task_count"] >= 1
    assert actual_metrics["task_machine_coverage_rate"] >= 0
    assert actual_metrics["machine_plan_load_candidate_count"] >= 1
    assert "machine_style_spec_mismatch_candidate_count" in actual_metrics
    assert result["actual_data_snapshot"]["schema_id"] == "athena.production_actual_data_snapshot.v1"
    assert result["actual_data_snapshot"]["current_data_source_label"] == "Mock / Tianpai APS Export"
    assert result["actual_data_snapshot"]["kpis"]["total_order_count"] == actual_metrics["total_order_count"]
    assert result["actual_data_snapshot"]["kpis"]["near_due_order_count"] == actual_metrics["near_due_order_count"]
    assert result["actual_data_snapshot"]["kpis"]["scheduled_weaving_part_order_count"] == actual_metrics["scheduled_weaving_part_order_count"]
    assert result["actual_data_snapshot"]["kpis"]["unscheduled_weaving_part_order_count"] == actual_metrics["unscheduled_weaving_part_order_count"]
    assert result["actual_data_snapshot"]["kpis"]["plan_completion_rate"] == actual_metrics["plan_completion_rate"]
    assert result["actual_data_snapshot"]["kpis"]["manual_report_completion_rate"] == actual_metrics["manual_report_completion_rate"]
    assert result["actual_data_snapshot"]["machine_plan_load_top"]
    assert "candidate_count_total" in result["actual_data_snapshot"]["machine_style_spec_mismatch_candidates"]
    join_quality = {
        item["join_id"]: item
        for item in result["tianpai_aps_erp_export"]["data_quality_report"]["join_quality"]
    }
    assert "manual_report_to_planned_task" in join_quality
    assert "planned_task_to_machine" in join_quality
    assert len(result["workflow_stages"]) == 6
    assert {"order_intake", "erp_input", "aps_scheduling", "iot_execution", "production_monitoring", "garment_output"}.issubset(stage_ids)
    assert resource_keys == {"people", "machine", "material", "method", "environment", "measurement"}
    assert "upload_co_file" in result["workflow_instance"]["blocked_actions"]
    assert "upload_cx_file" in result["workflow_instance"]["blocked_actions"]
    assert any(tool["adapter"] == "Santoni IOT Adapter" for tool in result["tool_interfaces"])
    assert result["adapter_contract"]["contract_id"] == "athena.production_aps_iot_read_only_contract.v1"
    assert result["workflow_template"]["workflow_primary_key"]["field"] == "order_id"
    assert result["workflow_primary_key"]["role"] == "unique_workflow_spine"
    assert result["production_overview"]["total_style_count"] >= 1
    assert result["data_source"]["mode"] == "static_mock_json"
    assert result["data_source"]["dynamic_aps_iot_scraping"] is False
    assert "capacity_occupation_rate" in result["production_overview"]
    assert "scrap_rate" in result["production_overview"]
    assert all(
        machine_signal["evidence_ref"]
        for machine_signal in result["resource_lens"]["machine"]["signals"]
    )
    assert all(candidate["service_request_candidate"] is True for candidate in result["service_escalations"])
    assert all(candidate["auto_dispatch"] is False for candidate in result["service_escalations"])
    assert result["first_screen_service_risk"]["schema_id"] == "athena.production_first_screen_service_risk.v1"
    assert result["first_screen_service_risk"]["read_only"] is True
    assert result["first_screen_service_risk"]["write_scope"] == "local_metadata_only"
    assert result["first_screen_service_risk"]["service_risk_cards"]
    assert all(card["local_follow_up_supported"] is True for card in result["first_screen_service_risk"]["service_risk_cards"])
    assert all(card["auto_dispatch"] is False for card in result["first_screen_service_risk"]["service_risk_cards"])
    assert all(card["evidence_refs"] for card in result["first_screen_service_risk"]["service_risk_cards"])
    assert all(card["field_sources"] for card in result["first_screen_service_risk"]["service_risk_cards"])
    assert "dispatch_service_automatically" in result["first_screen_service_risk"]["blocked_actions"]
    assert result["internal_demo_readiness_mode"]["schema_id"] == "athena.internal_demo_readiness_mode.v1"
    assert result["internal_demo_readiness_mode"]["status"] == "ready_for_internal_demo"
    assert result["internal_demo_readiness_mode"]["read_only"] is True
    assert result["internal_demo_readiness_mode"]["demo_kpis"]["top_priority_count"] == 3
    assert "/" in result["internal_demo_readiness_mode"]["visible_pages"]
    assert {
        "oee",
        "downtime_minutes",
        "order_delay_risk",
        "material_risk",
        "labor_efficiency",
        "quality_risk",
        "waste_cost_opportunity",
        "capacity_occupation",
        "scrap_rate",
        "adapter_contract_coverage",
        "management_priority_items",
        "material_inventory_join_readiness",
        "data_readiness_score",
        "question_bank_coverage",
        "prd_alignment_coverage",
        "tianpai_actual_export_readiness",
        "actual_data_evidence_chain_coverage",
        "skill_registry_coverage",
        "skill_execution_trace_coverage",
    }.issubset(kpis)
    assert result["optimization_signals"]
    assert all(item["evidence_ref"] for item in result["optimization_signals"])


def test_production_chatbi_agent_explains_scrap_rate_with_evidence():
    result = ProductionOperationsWorkflow().chatbi(
        {"question": "为什么废弃率是 4%？从款式、机台、物料和工艺上拆一下原因。"}
    )
    categories = {item["category"] for item in result["root_causes"]}
    serialized = json.dumps(result, ensure_ascii=False)

    assert result["agent"]["agent_id"] == "athena.production_chatbi_agent.v1"
    assert result["agent"]["name"] == "Santoni Athena"
    assert result["metric"] == "scrap_rate"
    assert result["read_only"] is True
    assert result["write_actions_blocked"] is True
    assert result["executive_answer"]["template"] == "缁撹 + 鍘熷洜/璇佹嵁 + 椋庨櫓 + 寤鸿 + 鏁版嵁缂哄彛"
    assert result["executive_answer"]["conclusion"] == result["answer_summary"]
    assert result["skill_registry"]["schema_id"] == "athena.production_skill_registry.v1"
    assert result["skill_execution_trace"]
    assert all(step["skill_id"] for step in result["skill_execution_trace"])
    assert all(step["evidence_refs"] for step in result["skill_execution_trace"])
    verification = result["verification_process"]
    assert verification["schema_id"] == "athena.manager_verification_process.v1"
    assert verification["version"] == "v0.113.1"
    assert verification["checked_objects"]
    assert verification["findings"]
    assert verification["evidence_level"]
    assert verification["cannot_conclude"]
    assert verification["data_gap"]
    assert verification["suggested_confirmation_owner"]
    assert verification["raw_debug_trace_hidden"] is True
    assert verification["read_only"] is True
    assert "confirm_schedule" in verification["blocked_actions"]
    assert result["data_gaps"]
    assert result["metric_snapshot"]["scrap_rate"] > 0
    assert {"style_quality", "machine", "material", "method"}.issubset(categories)
    assert all(item["evidence_refs"] for item in result["root_causes"])
    assert any(item["impact"].get("causal_status") == "not_primary_current_scrap_driver" for item in result["root_causes"])
    assert ".co" in serialized
    assert ".cx" in serialized
    assert "confirm_schedule" in result["blocked_actions"]


def test_production_chatbi_handles_management_frequent_questions():
    workflow = ProductionOperationsWorkflow()
    delivery = workflow.chatbi({"question": "Which orders have delivery risk?"})
    machine = workflow.chatbi({"question": "Which machines are current bottlenecks?"})
    labor = workflow.chatbi({"question": "Why is TECH-01 labor effective-hour risk high?"})
    gaps = workflow.chatbi({"question": "当前数据还不能回答什么？"})

    priority = workflow.chatbi({"question": "\u603b\u7ecf\u7406\u4eca\u5929\u5148\u770b\u54ea\u4e09\u4ef6\u4e8b\uff1f"})

    assert delivery["metric"] == "order_delay"
    assert delivery["actual_data_mode"] is True
    assert delivery["executive_answer"]["risk"]
    assert delivery["actual_evidence_chains"]
    assert delivery["actual_evidence_chains"][0]["produce_order_code"]
    assert delivery["actual_evidence_chains"][0]["field_source"]
    assert machine["metric"] == "machine_bottleneck"
    assert machine["metric_snapshot"]["top_bottleneck_machine"]
    assert any(item["category"] == "machine_bottleneck" for item in machine["root_causes"])
    assert labor["metric"] == "labor_efficiency"
    assert labor["metric_snapshot"]["labor_efficiency"] > 0
    assert any(item["category"] == "labor" for item in labor["root_causes"])
    assert gaps["metric"] == "data_gap"
    assert gaps["metric_snapshot"]["missing_scope_count"] >= 4
    assert any("APS" in item or "data" in item.lower() for item in gaps["data_gaps"])


    assert priority["metric"] == "management_priority"
    assert priority["management_priority_brief"]["top_priorities"][0]["management_theme"] == "delivery"
    assert [item["management_theme"] for item in priority["management_priority_brief"]["top_priorities"]] == ["delivery", "equipment", "material"]
    assert priority["management_priority_brief"]["top_priorities"][0]["action_candidate"]["status"] == "pending_confirmation"
    assert priority["decision_loop"]["loop_kpis"]["follow_up_count"] >= 3
    assert priority["executive_answer"]["conclusion"]


def test_production_chatbi_answers_actual_export_management_questions_with_evidence_chains():
    workflow = ProductionOperationsWorkflow()
    cases = [
        ("哪些订单有交付风险？", "order_delay", "produce_order_code"),
        ("哪些部件单还没有排满？", "unscheduled_weaving_part_order", "weaving_part_order_id"),
        ("哪些机台负载最高？", "machine_plan_load", "machine_code"),
        ("哪些款式可能因为机台规格不匹配导致风险？", "machine_style_mismatch", "planned_task_id"),
        ("哪些订单计划量和报工量差异最大？", "quantity_report_gap", "produce_order_code"),
    ]

    for question, metric, required_key in cases:
        result = workflow.chatbi({"question": question})
        chain = result["actual_evidence_chains"][0]

        assert result["metric"] == metric
        assert result["actual_data_mode"] is True
        assert result["confidence"] in {"medium_high", "medium_with_reconciliation_needed"}
        assert result["source_objects"][0] == "Tianpai APS Export"
        assert result["actual_evidence_chains"]
        assert result["skill_execution_trace"]
        assert result["skill_execution_trace"][0]["evidence_level"]
        assert result["evidence_log"]
        assert chain.get(required_key)
        assert chain.get("field_source")
        assert chain.get("evidence_refs")
        if metric == "machine_style_mismatch":
            assert chain["mismatch_details"]
            assert chain["mismatch_details"][0]["required_value"]
            assert chain["mismatch_details"][0]["actual_machine_value"]
            assert "Style_Component.cylinder_diameter" in chain["mismatch_details"][0]["required_field_source"]
            assert "T_Machine_Info.f_cylinder_diameter" in chain["mismatch_details"][0]["actual_field_source"]
            cause = result["root_causes"][0]["cause"]
            assert "requires" in cause or "瑕佹眰" in cause
            assert "machine" in cause or "鏈哄彴" in cause
        assert result["evidence_log"][0]["adapter_status"] == "read_only_external_csv"
        assert "evidence_chain" in result["evidence_log"][0]


def test_production_gm_priority_cards_feed_local_follow_up_contracts():
    result = ProductionOperationsWorkflow().overview()
    priorities = result["management_priority_brief"]["top_priorities"]
    follow_ups = result["decision_loop"]["follow_up_items"]
    actions = result["decision_loop"]["action_items"]

    assert len(priorities) == 3
    assert len(follow_ups) >= 3
    assert len(actions) >= 3
    assert {item.get("source_card_type") for item in follow_ups}.issuperset({"hard_risk"})
    for priority, follow_up, action in zip(priorities, follow_ups, actions):
        assert priority["risk_theme"] in {"delivery", "quality", "cost", "equipment", "labor", "material"}
        assert priority["affected_objects"]
        assert priority.get("actual_evidence_chains") or priority.get("evidence_refs")
        assert priority["field_sources"]
        assert priority["skills_used"]
        assert priority["skill_execution_trace"]
        assert priority["internal_demo_ready"] is True
        assert follow_up["linked_risk_card_id"] == priority["priority_id"]
        assert follow_up.get("actual_evidence_chains") or follow_up.get("evidence_refs")
        assert follow_up["field_sources"]
        assert follow_up["skills_used"]
        assert follow_up["skill_execution_trace"]
        assert follow_up.get("drilldown_question") or follow_up.get("confirmation_need")
        assert follow_up["write_scope"] == "local_metadata_only"
        assert follow_up["writes_real_system"] is False
        assert action["follow_up_contract"]["writes_real_system"] is False
        assert action["skills_used"]
        assert action["skill_execution_trace"]
        assert {"APS", "ERP", "IOT"}.issubset(set(action["follow_up_contract"]["blocked_systems"]))


def test_production_skill_registry_contract_and_trace_fields_are_agent_ready():
    workflow = ProductionOperationsWorkflow()
    registry = workflow.skill_registry()
    overview = workflow.overview()
    priority = overview["management_priority_brief"]["top_priorities"][0]
    trace = priority["skill_execution_trace"]

    assert registry["schema_id"] == "athena.production_skill_registry.v1"
    assert registry["version"] == "v0.113.1"
    assert registry["read_only"] is True
    assert registry["skill_count"] >= 8
    skill_ids = {item["skill_id"] for item in registry["skills"]}
    assert {
        "gm_daily_brief_skill",
        "delivery_risk_skill",
        "machine_fit_skill",
        "material_constraint_skill",
        "bottleneck_detection_skill",
        "quality_or_scrap_skill",
        "service_escalation_skill",
        "follow_up_action_skill",
    }.issubset(skill_ids)
    assert "delivery" in registry["theme_skill_map"]
    assert priority["skills_used"]
    assert trace
    assert all(step["step_id"] for step in trace)
    assert all(step["skill_id"] in skill_ids for step in trace)
    assert all(step["data_objects_checked"] for step in trace)
    assert all(step["evidence_refs"] for step in trace)
    assert all(step["limitation_or_data_gap"] for step in trace)
    assert all(step["read_only"] is True for step in trace)


def test_athena_v0109_v0110_evidence_review_and_gm_hierarchy_reports_are_linked():
    evidence_report_path = Path("docs/product/athena_evidence_review_queue_v0.109.0.md")
    hierarchy_report_path = Path("docs/product/athena_gm_first_screen_hierarchy_v0.110.0.md")
    athena_html = Path("docs/Athena.html").read_text(encoding="utf-8")

    assert evidence_report_path.exists()
    assert hierarchy_report_path.exists()
    evidence_report = evidence_report_path.read_text(encoding="utf-8")
    hierarchy_report = hierarchy_report_path.read_text(encoding="utf-8")
    assert "Evidence Review Queue v0.109.0" in evidence_report
    assert "hard delivery risk" in evidence_report
    assert "needs_reconciliation" in evidence_report
    assert "read-only" in evidence_report
    assert "GM First Screen Hierarchy v0.110.0" in hierarchy_report
    assert "KPI dashboard" in hierarchy_report
    assert "Evidence Review Queue" in hierarchy_report
    assert "original chat stream" in hierarchy_report
    assert "product/athena_evidence_review_queue_v0.109.0.md" in athena_html
    assert "product/athena_gm_first_screen_hierarchy_v0.110.0.md" in athena_html


def test_user_page_general_manager_dashboard_hierarchy_and_compact_drilldown():
    web_root = Path("src/web_app")
    page = (web_root / "index.html").read_text(encoding="utf-8")
    script = (web_root / "user-app.js").read_text(encoding="utf-8")
    styles = (web_root / "styles.css").read_text(encoding="utf-8")

    assert 'id="gmKpiDashboard"' in page
    assert "renderGeneralManagerKpiDashboard" in script
    assert "General Manager Dashboard" in script
    assert "日常关键指标" in script
    assert "交付风险" in script
    assert "排单状态" in script
    assert "计划完成" in script
    assert "设备风险" in script
    assert "Service" in script
    assert "数据可信度" in script
    assert "appendProductionAthenaAnswer" in script
    assert "gm-user-analysis-compact" in script
    assert "gm-user-analysis-details" in script
    assert "查看完整证据与边界" in script
    assert "gm-user-dashboard" in styles
    assert "gm-user-kpi" in styles
    assert "gm-user-analysis-compact" in styles
    assert "gm-user-analysis-details" in styles


def test_production_priority_brief_api_contract_is_read_only():
    result = ProductionOperationsWorkflow().priority_brief()
    brief = result["management_priority_brief"]
    server = Path("scripts/run_web_demo.py").read_text(encoding="utf-8")

    assert result["workflow_instance"]["scenario"] == "management_priority_brief"
    assert 'path == "/api/production/evidence-review"' in server
    assert result["production_object_model"]["schema_id"] == "athena.production_object_model.v1"
    assert brief["automation_status"] == "actual_export_first_priority_engine"
    assert brief["priority_policy"]["human_confirmation_required_before_action"] is True
    assert brief["priority_policy"]["kpi_priority"] == ["delivery", "quality", "cost"]
    assert [item["management_theme"] for item in brief["top_priorities"]] == ["delivery", "equipment", "material"]
    assert all(item["drilldown_question"] for item in brief["top_priorities"])
    assert all(item["evidence_level"] == "Level 2: external APS/ERP export evidence" for item in brief["top_priorities"])
    assert all(item["action_candidate"]["write_scope"] == "local_metadata_only" for item in brief["top_priorities"])
    assert [item["rank"] for item in brief["top_priorities"]] == [1, 2, 3]
    assert all(item["decision_gate"] for item in brief["top_priorities"])
    assert all(item["data_gaps"] for item in brief["top_priorities"])
    assert "change_production_schedule" in result["production_object_model"]["blocked_actions"]
    assert "upload_co_file" in result["blocked_actions"]


def test_production_stable_demo_story_pack_contract_is_read_only():
    result = ProductionOperationsWorkflow().demo_story_pack()
    pack = result["stable_demo_story_pack"]

    assert result["workflow_instance"]["scenario"] == "stable_demo_story_pack"
    assert pack["schema_id"] == "athena.production_stable_demo_story_pack.v1"
    assert pack["version"] == "v0.113.1"
    assert pack["read_only"] is True
    assert len(pack["stories"]) == 3
    assert pack["actual_data_available"]["evidence_level"] == "Level 2: external APS/ERP export evidence"
    assert "delivery risk from Produce_Order / Weaving_Part_Order / Planned_Task / Manual_Machine_Production" in pack["actual_data_available"]["usable_for_demo"]
    assert "real service ticket dispatch status" in pack["mock_needed_for_demo"]
    assert pack["stories"][0]["story_type"] == "real_data_main_line"
    assert pack["stories"][0]["actual_evidence_chains"]
    assert pack["stories"][2]["story_type"] == "hybrid_real_order_mock_iot_service"
    assert pack["stories"][2]["mock_supplements"]
    assert all(story["read_only"] is True for story in pack["stories"])
    assert all("no_machine_control" in story["blocked_actions"] or "control_machine" in story["blocked_actions"] for story in pack["stories"])


def test_production_internal_demo_candidate_contract_covers_v098_to_v0107():
    result = ProductionOperationsWorkflow().internal_demo_candidate()
    candidate = result["internal_demo_candidate"]

    assert result["workflow_instance"]["scenario"] == "internal_demo_candidate"
    assert candidate["schema_id"] == "athena.production_internal_demo_candidate.v1"
    assert candidate["version"] == "v0.113.1"
    assert candidate["guided_demo_flow"]["status"] == "ready_for_internal_demo"
    assert len(candidate["guided_demo_flow"]["steps"]) == 6
    assert candidate["guided_demo_flow"]["demo_reset_policy"]["does_not_write_external_systems"] is True
    assert "stable_story_shortcuts" in candidate["user_page_gm_demo_entry"]["visible_sections"]
    assert candidate["presenter_mode"]["recommended_questions"]
    modes = candidate["evidence_boundary_layer"]["modes"]
    assert {"actual_export", "mock_contract", "hybrid", "data_gap"}.issubset(modes)
    regression = candidate["gm_question_regression_set"]
    assert len(regression["questions"]) >= 6
    assert {"conclusion", "evidence", "recommendation", "data_gap", "read_only_boundary"}.issubset(regression["minimum_answer_contract"])
    requests = candidate["data_request_wizard"]["requests"]
    assert requests
    assert all({"fields", "purpose", "priority", "sensitivity_level"}.issubset(request) for request in requests)
    service = candidate["service_risk_confirmation_flow"]
    assert service["auto_dispatch"] is False
    assert service["create_real_ticket"] is False
    assert service["control_machine"] is False
    skill_process = candidate["visible_athena_skill_process"]
    assert skill_process["raw_debug_visible"] is False
    assert skill_process["raw_payload_visible"] is False
    hermes = candidate["hermes_training_memory_review"]
    assert hermes["candidates"]
    assert hermes["live_hermes_write"] is False
    for memory_event in hermes["candidates"]:
        assert {"scope", "tenant_id", "factory_id", "source", "retention_policy", "sensitivity_level", "promotion_status"}.issubset(memory_event)
    assert candidate["internal_demo_candidate_report"]["path"] == "docs/product/athena_daily_brief_narrative_v0.113.0.md"
    assert candidate["read_only_boundary"]["read_only"] is True


def test_production_material_readiness_and_question_bank_contracts():
    workflow = ProductionOperationsWorkflow()
    material = workflow.material_risk()
    readiness = workflow.data_readiness()
    bank = workflow.question_bank()

    assert material["workflow_instance"]["scenario"] == "tianpai_material_risk"
    assert material["material_risk"]["schema_id"] == "athena.production_material_risk.v1"
    assert material["material_risk"]["adapter_status"] == "mock_contract"
    assert material["material_risk"]["source_summary"]["raw_file_stored_in_repo"] is False
    assert material["material_risk"]["balance_exceptions"]["interpretation_required"] is True
    assert "claim_material_quality_root_cause_without_quality_join" in material["material_risk"]["blocked_actions"]
    assert readiness["workflow_instance"]["scenario"] == "tianpai_data_readiness"
    assert readiness["data_readiness"]["status"] == "partial_ready"
    assert readiness["data_readiness"]["source_status"]["erp_orders"] == "not_available"
    assert readiness["data_readiness"]["source_status"]["material_inventory"] == "available_aggregate"
    assert bank["workflow_instance"]["scenario"] == "general_manager_question_bank"
    assert bank["general_manager_question_bank"]["status"] == "hypothesis_pending_voc"
    assert any(item["question_id"] == "GMQ-006" for item in bank["general_manager_question_bank"]["questions"])
    assert "treat_hypothesis_as_confirmed_voc" in bank["general_manager_question_bank"]["blocked_actions"]


def test_production_follow_up_loop_updates_metadata_only_reviews():
    with TemporaryDirectory() as temp_dir:
        review_path = Path(temp_dir) / "production_follow_up_reviews.json"
        workflow = ProductionOperationsWorkflow(follow_up_store_path=review_path)
        initial = workflow.follow_up_loop()
        action_id = initial["decision_loop"]["action_items"][0]["action_id"]

        updated = workflow.apply_follow_up_review(
            {
                "action_id": action_id,
                "review_status": "waiting_evidence",
                "review_note": "Owner assigned; waiting for inspection result.",
                "evidence_note": "Need defect inspection row and machine alarm history.",
            }
        )
        store = json.loads(review_path.read_text(encoding="utf-8"))
        serialized = json.dumps(updated, ensure_ascii=False).lower()

        assert initial["workflow_instance"]["scenario"] == "decision_loop_follow_up"
        assert all(item["status"] == "pending_confirmation" for item in initial["decision_loop"]["follow_up_items"])
        assert updated["decision_loop"]["review_state"]["review_count"] == 1
        assert updated["decision_loop"]["loop_kpis"]["waiting_evidence_count"] == 1
        assert any(item["status"] == "waiting_evidence" for item in updated["decision_loop"]["follow_up_items"])
        assert store["metadata_only"] is True
        assert store["reviews"][0]["contains_raw_file"] is False
        assert store["reviews"][0]["contains_credentials"] is False
        assert "write_to_aps_or_iot" in updated["decision_loop"]["blocked_actions"]
        assert "password" not in serialized

        unable = workflow.apply_follow_up_review(
            {
                "action_id": action_id,
                "review_status": "unable_to_process",
                "review_note": "Owner cannot process until missing evidence arrives.",
            }
        )
        assert unable["decision_loop"]["loop_kpis"]["unable_to_process_count"] == 1
        assert any(item["status"] == "unable_to_process" for item in unable["decision_loop"]["follow_up_items"])

        try:
            workflow.apply_follow_up_review(
                {
                    "action_id": action_id,
                    "review_status": "closed",
                    "review_note": "password should not be accepted",
                }
            )
        except ValueError as exc:
            assert "credentials" in str(exc)
        else:
            raise AssertionError("credential-like follow-up note was not rejected")


def test_production_adapter_contract_maps_aps_iot_fields_without_credentials():
    contract = ProductionOperationsWorkflow().adapter_contract()
    mapping_objects = {item["object"] for item in contract["field_mapping"]}
    source_systems = {item["system"] for item in contract["source_systems"]}
    serialized = json.dumps(contract, ensure_ascii=False).lower()

    assert contract["version"] == "v0.113.1"
    assert {"APS", "Santoni IOT", "ERP / Yarn Inventory"}.issubset(source_systems)
    assert {
        "production_order",
        "yarn_material_forecast",
        "aps_schedule_capacity",
        "iot_machine_execution",
        "iot_program_evidence",
        "garment_quality_output",
        "production_task_material_balance",
    }.issubset(mapping_objects)
    assert "weaving_monitor" in serialized
    assert "iot_monitor" in serialized
    assert ".co" in serialized
    assert ".cx" in serialized
    assert "cn_program" not in serialized
    assert ".cn" not in serialized
    assert "password" not in serialized
    assert "1qaz" not in serialized
    assert "start_auto_scheduling" in contract["blocked_actions"]
    assert "upload_co_file" in contract["blocked_actions"]


def test_production_operations_analyze_keeps_filters_and_blocks_writes():
    result = ProductionOperationsWorkflow().analyze({"filters": {"order_id": "ORD-20260605-002"}, "scenario": "quality_hold_review"})

    assert result["analysis_request"]["scenario"] == "quality_hold_review"
    assert result["analysis_request"]["write_actions_blocked"] is True
    assert result["workflow_instance"]["filters"] == {"order_id": "ORD-20260605-002"}
    assert result["production_overview"]["order_count"] == 1
    assert result["service_escalations"]


def test_excel_importer_generates_draft_cases():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        xlsx_path = temp_path / "service.xlsx"
        output_path = temp_path / "draft.json"
        _write_minimal_xlsx(
            xlsx_path,
            [
                [
                    "Intervention description",
                    "WO Number",
                    "Serial",
                    "Machine Model",
                    "Fault Category",
                    "Fault Type",
                    "Fault Component",
                    "Fault Action",
                    "Engeneer notes",
                ],
                [
                    "错花，申请义达电子选针器",
                    "0052591",
                    "9009452",
                    "TOP2-FAST",
                    "Fabric defect 布面问题",
                    "Wrong pattern 错花",
                    "Selector 选针器",
                    "replace selector 更换选针器",
                    "索赔选针器、电源盒、选针器线缆，工作完成",
                ],
                [
                    "油箱分油嘴漏油",
                    "0052594",
                    "9009424",
                    "TOP2-FAST",
                    "Mechanical 机械",
                    "Oil leak 漏油",
                    "Oil distributor 分油嘴",
                    "replace distributor 更换分油嘴",
                    "工作完成，索赔油箱分油嘴",
                ],
            ],
        )

        summary = ServiceCaseExcelImporter().import_file(xlsx_path, output_path)
        cases = json.loads(output_path.read_text(encoding="utf-8"))
    assert summary.source_rows == 2
    assert summary.draft_cases == 2
    assert any(case["review_status"] == "draft_needs_review" for case in cases)
    assert any(case["issue_category"] == "fabric_defect" for case in cases)
    assert any(case["issue_category"] == "mechanical" for case in cases)
    assert all(case["customer_visible"] is False for case in cases)


def test_approved_draft_case_enters_customer_facing_matching():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        draft_path = temp_path / "draft_cases.json"
        review_path = temp_path / "reviews.json"
        draft_case = {
            "case_id": "SVC-DRAFT-TEST-001",
            "title": "Draft test selector issue",
            "machine_models": ["TOP2-FAST"],
            "issue_category": "fabric_defect",
            "symptom_keywords": ["testwrongpattern"],
            "alarm_codes": [],
            "production_impact": "quality_risk",
            "severity": "P2",
            "online_solvable": True,
            "online_resolution_steps": ["Check selector cable."],
            "online_resolution_steps_zh": ["Check selector cable."],
            "safety_warnings": ["Stop machine first."],
            "dispatch_triggers": ["Issue repeats after check."],
        }
        draft_path.write_text(json.dumps([draft_case], ensure_ascii=False), encoding="utf-8")

        kb = ServiceCaseKnowledgeBase()
        kb.cases = []
        kb.draft_cases_path = draft_path
        kb.review_records_path = review_path

        before = kb.match({"machine_model": "TOP2-FAST", "symptoms": ["testwrongpattern"]}, "testwrongpattern", "en")
        assert before["case_database_status"] == "mock_no_match"

        review = kb.apply_review("SVC-DRAFT-TEST-001", "approved", "Approved for test")
        assert review["approved_count"] == 1
        assert json.loads(review_path.read_text(encoding="utf-8"))["SVC-DRAFT-TEST-001"]["review_status"] == "approved"

        after = kb.match({"machine_model": "TOP2-FAST", "symptoms": ["testwrongpattern"]}, "testwrongpattern", "en")
        assert after["case_database_status"] == "mock_matched"
        assert after["matched_case_id"] == "SVC-DRAFT-TEST-001"


def test_service_manager_console_edits_case_and_reports_diff():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        draft_path = temp_path / "draft_cases.json"
        review_path = temp_path / "reviews.json"
        draft_case = {
            "case_id": "SVC-DRAFT-EDIT-001",
            "title": "Draft oil issue",
            "machine_models": ["TOP2-FAST"],
            "issue_category": "mechanical",
            "symptom_keywords": ["oldleak"],
            "alarm_codes": [],
            "production_impact": "quality_risk",
            "severity": "P2",
            "online_solvable": True,
            "online_resolution_steps": ["Old check."],
            "safety_warnings": ["Stop first."],
            "dispatch_triggers": ["Old trigger."],
        }
        draft_path.write_text(json.dumps([draft_case], ensure_ascii=False), encoding="utf-8")

        kb = ServiceCaseKnowledgeBase()
        kb.cases = []
        kb.draft_cases_path = draft_path
        kb.review_records_path = review_path

        review = kb.apply_review(
            "SVC-DRAFT-EDIT-001",
            "approved",
            "Service manager revised the oil-leak case.",
            {
                "symptom_keywords": ["newleak"],
                "online_resolution_steps": ["Clean oil area.", "Take photos of distributor."],
                "dispatch_triggers": ["Leak reaches electrical components."],
            },
        )

        edited = review["cases"][0]
        assert edited["review_status"] == "approved"
        assert edited["customer_visible"] is True
        assert "symptom_keywords" in edited["changed_fields"]
        assert edited["online_resolution_steps"] == ["Clean oil area.", "Take photos of distributor."]
        assert edited["handoff_payload_preview"]["case_id"] == "SVC-DRAFT-EDIT-001"

        match = kb.match({"machine_model": "TOP2-FAST", "symptoms": ["newleak"]}, "newleak", "en")
        assert match["case_database_status"] == "mock_matched"
        assert match["matched_case_id"] == "SVC-DRAFT-EDIT-001"
        assert match["suggested_steps"] == ["Clean oil area.", "Take photos of distributor."]


def test_imported_service_case_matches_selector_wrong_pattern():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2-FAST 序列号9009452，机器错花，怀疑选针器或线缆问题，生产布面不稳定",
        )
    )
    online_assist = response.payload["online_assist"]
    assert online_assist["matched_case_id"] == "SVC-IMPORT-202605-001"
    assert online_assist["skill"] == "service_case_online_assist_mock"
    assert online_assist["matched_reasons"]
    assert online_assist["suggested_steps"]


def test_imported_service_case_matches_system_screen_fault():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="SM8 TOP2 MP2 序列号C000981，机器死机白屏，显示屏触摸没有反应，现场不能生产",
        )
    )
    online_assist = response.payload["online_assist"]
    assert online_assist["matched_case_id"] == "SVC-IMPORT-202605-002"
    assert online_assist["online_solvable"] is False
    assert any("display" in cause or "PCB" in cause for cause in online_assist["probable_causes"])


def test_imported_service_case_matches_oil_leak():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2-FAST 序列号9009424，油箱分油嘴漏油，担心污染布面",
        )
    )
    online_assist = response.payload["online_assist"]
    assert online_assist["matched_case_id"] == "SVC-IMPORT-202605-003"
    assert online_assist["suggested_steps"]


def test_service_followup_identifiers_do_not_switch_to_activation_case():
    agent = MainAgent()
    session_id = "service-followup-context"
    first = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="机器错花了，怎么办？",
        )
    )
    assert first.payload["online_assist"]["matched_case_id"] == "SVC-IMPORT-202605-001"

    second = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="TOP2-FAST，序列号9009452",
        )
    )
    assert second.payload["known_info"]["machine_model"] == "TOP2-FAST"
    assert second.payload["known_info"]["serial_number"] == "9009452"
    assert second.payload["known_info"]["issue_type"] == "fabric_defect"
    assert second.payload["online_assist"]["matched_case_id"] == "SVC-IMPORT-202605-001"
    assert "machine_code_or_lock_screen" not in second.payload["missing_info"]


def test_service_case_guides_wrong_pattern_fixed_feed_question():
    agent = MainAgent()
    session_id = "wrong-pattern-guidance"
    agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="机器错花了，怎么办？",
        )
    )
    response = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="错花是否固定出现在同一路？",
        )
    )
    assert response.payload["known_info"]["online_guidance_request"] == "wrong_pattern_fixed_feed_check"
    assert response.summary


def test_service_case_records_wrong_pattern_fixed_same_feed_answer():
    agent = MainAgent()
    session_id = "wrong-pattern-fixed-answer"
    agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="机器错花了，怎么办？",
        )
    )
    response = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="固定在同一路",
        )
    )
    assert "wrong_pattern_fixed_same_feed" in response.payload["known_info"]["diagnostic_observations"]
    assert any("same feed" in step for step in response.payload["known_info"]["online_steps_attempted"])
    assert response.summary


def test_top2mp_activation_password_routes_to_service_case():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2MP 更换主板后锁定，需要生成激活密码，序列号12345678，机器码ABCD-1234",
        )
    )
    assert response.workflow == "service_assist"
    assert response.payload["known_info"]["machine_model"] == "TOP2MP"
    assert response.payload["online_assist"]["matched_case_id"] == "SVC-MOCK-0002"
    assert response.payload["online_assist"]["tool_candidate"] == "activation_password_generator"
    assert response.payload["online_assist"]["tool_result"]["status"] == "success"
    assert response.payload["online_assist"]["tool_result"]["activation_password"].startswith("MOCK-")
    assert response.payload["missing_info"] == []
    assert "派工" not in response.summary
    assert response.summary


def test_natural_machine_locked_routes_to_activation_intake():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="my machine is locked"))
    assert response.workflow == "service_assist"
    assert response.payload["known_info"]["issue_type"] == "activation_password_lock"
    assert response.payload["online_assist"]["matched_case_id"] == "SVC-MOCK-0002"
    assert response.payload["online_assist"]["tool_result"]["status"] == "missing_input"
    assert "machine_model" in response.payload["missing_info"]
    assert "serial_number" in response.payload["missing_info"]
    assert "machine_code_or_lock_screen" in response.payload["missing_info"]


def test_lock_machine_activation_quick_prompt_routes_to_activation_intake():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="机器出现锁机激活相关问题，我需要协助处理。"))
    assert response.workflow == "service_assist"
    assert response.payload["known_info"]["issue_type"] == "activation_password_lock"
    assert response.payload["online_assist"]["matched_case_id"] == "SVC-MOCK-0002"
    assert response.payload["online_assist"]["tool_result"]["status"] == "missing_input"
    assert "machine_model" in response.payload["missing_info"]
    assert "serial_number" in response.payload["missing_info"]
    assert "machine_code_or_lock_screen" in response.payload["missing_info"]


def test_top2mp_activation_password_expired_requires_manual_escalation():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2MP 锁定，需要生成激活密码，序列号87654321，机器码LOCK-9999",
        )
    )
    tool_result = response.payload["online_assist"]["tool_result"]
    assert tool_result["status"] == "manual_escalation_required"
    assert tool_result["reason"] == "lease_expired"
    assert response.payload["missing_info"] == []
    assert response.summary


def test_top2mp_activation_password_unknown_serial_requires_manual_escalation():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2MP 锁定，需要生成激活密码，序列号9999999，机器码LOCK-9999",
        )
    )
    tool_result = response.payload["online_assist"]["tool_result"]
    assert tool_result["status"] == "manual_escalation_required"
    assert tool_result["reason"] == "serial_number_not_found"


def test_top2_hie_machine_model_is_extracted():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="序列号：3003658\n机器型号：TOP2-HIE\n机器码：EB324A483DC90B3EECF52D9BA4ED8412",
        )
    )
    assert response.payload["known_info"]["machine_model"] == "TOP2-HIE"


def test_screenshot_serial_uses_activation_password_mock_record():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2-HIE 机器锁定，需要生成激活密码，序列号3004116，机器码F11D3E503E404CD3756BD4B902D4516E",
        )
    )
    tool_result = response.payload["online_assist"]["tool_result"]
    assert tool_result["status"] == "success"
    assert tool_result["machine_model"] == "TOP2-HIE"
    assert tool_result["activation_password"].startswith("MOCK-")


def test_lock_request_does_not_invent_tool_inputs():
    response = MainAgent().handle(AgentRequest(user_role="auto", message="我的机器锁了，帮我解锁"))
    assert response.workflow == "service_assist"
    assert "machine_model" in response.payload["missing_info"]
    assert "serial_number" in response.payload["missing_info"]
    assert "machine_code_or_lock_screen" in response.payload["missing_info"]
    assert response.payload["known_info"].get("machine_model") != "TOP2MP"
    assert response.payload["known_info"].get("serial_number") != "12345678"


def test_activation_tool_maps_postback_and_dialog_fields():
    tool = ActivationPasswordTool()
    html = """
      <form>
        <table><tr>
          <td><input name="MainRadGridview$ctl00$ctl04$columnSelectCheckBox" type="checkbox"></td>
          <td>3004116</td>
        </tr></table>
        <a href="javascript:__doPostBack(&#39;MainRadGridview$ctl00$ctl02$ctl00$RadToolBar1&#39;,&#39;generateActivation&#39;)">鐢熸垚婵€娲诲瘑鐮?/a>
        <label>婵€娲荤爜:</label><input name="Window$txtActivateCode" value="">
        <label>婵€娲诲瘑鐮?</label><input name="Window$txtActivatePassword" value="REAL-PASSWORD-123">
      </form>
    """
    assert tool._find_row_checkbox_name(html, "3004116") == "MainRadGridview$ctl00$ctl04$columnSelectCheckBox"
    assert tool._find_postback_near_text(html, "generate") == {
        "target": "MainRadGridview$ctl00$ctl02$ctl00$RadToolBar1",
        "argument": "generateActivation",
    }
    assert tool._input_name_after_label(html, "Activate") in {"Window$txtActivateCode", None}
    assert tool._extract_activation_password(html) == "REAL-PASSWORD-123"


def test_activation_tool_derives_toolbar_postback_candidates_from_client_state():
    tool = ActivationPasswordTool()
    html = """
      <input id="MainRadGridview_ctl00_ctl02_ctl00_RadToolBar1_ClientState"
             name="MainRadGridview_ctl00_ctl02_ctl00_RadToolBar1_ClientState"
             value='{"items":[{"text":"新增机器","commandName":"Add"},{"text":"生成激活密码","commandName":"GenerateActivationPassword"},{"text":"删除数据","commandName":"Delete"}]}'>
    """
    candidates = tool._toolbar_activation_postback_candidates(html)
    assert {
        "target": "MainRadGridview$ctl00$ctl02$ctl00$RadToolBar1",
        "argument": "onclick#GenerateActivationPassword",
        "source": "toolbar_client_state",
    } in candidates
    assert all("Delete" not in candidate["argument"] for candidate in candidates)


def test_activation_tool_detects_login_page():
    tool = ActivationPasswordTool()
    login_html = "<html><title>閸︼絼绗㈢亸鑲╊潳鐠т礁鐦戦惍浣洪兇缂?閻ц缍?/title><input name='txtid'><input name='txtpwd'></html>"
    home_html = "<html><title>閸︼絼绗㈢亸鑲╊潳鐠т礁鐦戦惍浣洪兇缂?妫ｆ牠銆?/title><input name='MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_serial_num'>閻㈢喐鍨氬┑鈧ú璇茬槕閻?/html>"
    assert tool._looks_like_login_page(login_html) is True
    assert tool._looks_like_login_page(home_html) is False


def test_activation_tool_rejects_grid_filter_as_activation_code_field():
    tool = ActivationPasswordTool()
    html = """
      <span>濠碘偓濞茬粯婧€閸ｃ劎鐖?/span>
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
      <div id="radwindowactive"></div>
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) is None


def test_activation_tool_prefers_radwindowactive_code_field():
    tool = ActivationPasswordTool()
    html = """
      <span>濠碘偓濞茶崵鐖?/span><input name="radwindowactive$C$MachineCodeTextBox" value="">
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) == "radwindowactive$C$MachineCodeTextBox"


def test_activation_tool_finds_machine_code_input_near_label():
    tool = ActivationPasswordTool()
    html = """
      <div id="radwindowactive">
        <span>濠?濞茬粯婧€閸ｃ劎鐖?/span>
        <table><tr><td><input type="text" name="RADwindowactive$C$txtMachineCode" value=""></td></tr></table>
      </div>
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) == "RADwindowactive$C$txtMachineCode"


def test_activation_tool_near_label_still_rejects_grid_filter():
    tool = ActivationPasswordTool()
    html = """
      <span>濠?濞茬粯婧€閸ｃ劎鐖?/span>
      <input type="text" name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) is None


def test_activation_tool_prefers_same_window_submit_button():
    tool = ActivationPasswordTool()
    html = """
      <span>濠?濞茬粯婧€閸ｃ劎鐖?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="">
      <input type="submit" name="radwindowfulledit$C$RadButton15_input" value="绾喖鐣?>"
      <input type="submit" name="radwindownew$C$RadButton2_input" value="閻㈢喐鍨氬┑?濞茶鐦?>"
    """
    candidates = tool._activation_submit_candidates(html, "radwindownew$C$RadMaskedTextBox2")
    assert candidates[0]["name"] == "radwindownew$C$RadButton2_input"


def test_activation_tool_ignores_cancel_submit_button():
    tool = ActivationPasswordTool()
    html = """
      <span>濠?濞茬粯婧€閸ｃ劎鐖?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="">
      <input type="submit" name="radwindownew$C$RadButtonCancel_input" value="閸欐牗绉?>"
      <input type="submit" name="radwindownew$C$RadButtonOk_input" value="绾喖鐣?>"
    """
    candidates = tool._activation_submit_candidates(html, "radwindownew$C$RadMaskedTextBox2")
    assert candidates[0]["name"] == "radwindownew$C$RadButtonOk_input"
    assert all("Cancel" not in item["name"] for item in candidates)


def test_activation_tool_reads_password_from_precise_label():
    tool = ActivationPasswordTool()
    html = """
      <span>濠碘偓濞茶崵鐖?</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="F11D-3E50-3E40-4CD3-756B-D4B9-02D4-516E">
      <span>濠碘偓濞茶鐦戦惍?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox3" value="9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A">
    """
    assert (
        tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E")
        == "9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A"
    )


def _write_minimal_xlsx(path: Path, rows: list[list[str]]) -> None:
    shared_strings = []
    shared_index = {}
    cell_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row, start=1):
            if value not in shared_index:
                shared_index[value] = len(shared_strings)
                shared_strings.append(value)
            cell_ref = f"{_xlsx_column(column_index)}{row_index}"
            cells.append(f'<c r="{cell_ref}" t="s"><v>{shared_index[value]}</v></c>')
        cell_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    shared_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        + "".join(f"<si><t>{_xml_escape(value)}</t></si>" for value in shared_strings)
        + "</sst>"
    )
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(cell_rows)}</sheetData>'
        "</worksheet>"
    )
    with ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "")
        archive.writestr("xl/sharedStrings.xml", shared_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def _xlsx_column(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def test_activation_tool_does_not_read_machine_code_as_password():
    tool = ActivationPasswordTool()
    html = """
      <span>濠碘偓濞茶鐦戦惍?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="F11D-3E50-3E40-4CD3-756B-D4B9-02D4-516E">
    """
    assert tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E") == ""


def test_activation_tool_reads_password_from_telerik_client_state():
    tool = ActivationPasswordTool()
    html = """
      <span>濠碘偓濞茶鐦戦惍?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox3" id="radwindownew_C_RadMaskedTextBox3" value="">
      <input type="hidden" name="radwindownew_C_RadMaskedTextBox3_ClientState"
             id="radwindownew_C_RadMaskedTextBox3_ClientState"
             value="{&quot;valueAsString&quot;:&quot;9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A&quot;}">
    """
    assert (
        tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E")
        == "9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A"
    )


def test_activation_tool_reads_password_from_ajax_fragment_near_label():
    tool = ActivationPasswordTool()
    html = """
      123|updatePanel|radwindownew_C|<span>濠碘偓濞茶鐦戦惍?/span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox3" value="">
      <script>var generated='9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A';</script>|456
    """
    assert (
        tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E")
        == "9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A"
    )










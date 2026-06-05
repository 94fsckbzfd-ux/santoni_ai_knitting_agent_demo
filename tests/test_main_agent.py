import json

from agent_core.main_agent import AgentRequest, MainAgent
from agent_core.operating_model import project_documentation
from agent_core.tools.lease_password_tool import ActivationPasswordTool
from agent_core.tools.service_case_importer import ServiceCaseExcelImporter
from agent_core.tools.service_case_knowledge import ServiceCaseKnowledgeBase
from agent_core.workflows.athena_mvp_workflow import AthenaMvpWorkflow
from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow

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
    response = MainAgent().handle(AgentRequest(user_role="designer", message="帮我设计一款迪卡侬无缝跑步上衣，要透气快干"))
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


def test_designer_generates_only_when_requested():
    response = MainAgent().handle(AgentRequest(user_role="designer", message="请生成打版方案：迪卡侬无缝跑步上衣，夏季跑步，女性用户，透气快干"))
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
            message="帮我设计一款迪卡侬无缝跑步上衣，要透气快干，男性，夏季跑步，入门款，160到190cm",
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
    response = MainAgent().handle(AgentRequest(user_role="auto", message="我机器坏了，能不能帮我排查一下"))
    assert response.workflow == "service_assist"


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
            message="SM8-TOP2V 序列号12312312，张力报警停机，已经重启一次还是报警",
        )
    )
    online_assist = response.payload["online_assist"]
    assert online_assist["skill"] == "service_case_online_assist_mock"
    assert online_assist["case_database_status"] == "mock_matched"
    assert online_assist["matched_case_id"] == "SVC-MOCK-0001"
    assert online_assist["online_solvable"] is True
    assert any("纱路" in step for step in online_assist["suggested_steps"])
    assert any("安全" in warning for warning in online_assist["safety_warnings"])


def test_service_case_knowledge_reports_no_match_for_unknown_case():
    result = ServiceCaseKnowledgeBase().match(
        {
            "machine_model": "UNKNOWN-MODEL",
            "issue_type": "unusual request",
            "symptoms": ["unknown symptom"],
            "production_status": "running",
            "urgency": "P3",
        },
        "客户询问培训资料，不是机器故障",
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
    assert docs["version"] == "v0.25.3"
    assert any(item["name"] == "Service Case Library review page" for item in docs["implemented_features"])
    assert any(item["name"] == "Operation guide page" for item in docs["implemented_features"])
    assert any(item["name"] == "Excel auto importer" for item in docs["implemented_features"])
    assert any(item["name"] == "Case approval workflow" for item in docs["implemented_features"])
    assert any(item["name"] == "Customer-facing interaction page" for item in docs["implemented_features"])
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
    assert any(item["name"] == "Production order-id workflow spine" for item in docs["implemented_features"])
    assert any(item["name"] == "Real SWS/Arachne adapter" for item in docs["planned_features"])
    assert any(item["name"] == "Real APS/IOT production adapters" for item in docs["planned_features"])
    assert len(docs["athena_mvp_state_flow"]) == 6
    assert len(docs["production_operations_state_flow"]) == 6


def test_all_web_pages_include_bilingual_language_switch():
    web_root = Path("src/web_app")
    html_files = list(web_root.glob("*.html"))

    assert html_files
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8")
        assert '/i18n.js?v=0.25.3' in content

    i18n_script = (web_root / "i18n.js").read_text(encoding="utf-8")
    assert "santoniDemoLanguage" in i18n_script
    assert "language-toggle" in i18n_script
    assert "Chinese / English" in (web_root / "README.md").read_text(encoding="utf-8")


def test_production_page_defaults_to_chinese_customer_display():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")

    assert '<html lang="zh-CN">' in production_html
    assert "Athena 生产运营控制台" in production_html
    assert '/production.js?v=0.25.3' in production_html
    assert "attention_required" in production_script
    assert "需关注" in production_script
    assert "Production Console Chinese display" in (web_root / "changelog.html").read_text(encoding="utf-8")


def test_production_page_uses_site_flow_layout():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")

    assert "production site flow".lower() in (web_root / "changelog.html").read_text(encoding="utf-8").lower()
    assert "生产现场链路" in production_html
    assert 'id="operationsStack"' in production_html
    assert "renderOperationsStack" in production_script
    assert "Backlog Orders" in production_script
    assert "Scheduling" in production_script
    assert "Fault Machines" in production_script
    assert "Average Yield" in production_script
    assert "废料率 / 不良率代理" in production_script
    assert "APS / IOT Field Mapping" in production_html
    assert 'id="adapterContract"' in production_html
    assert "/api/production/adapter-contract" in production_script


def test_production_page_includes_santoni_athena_panel():
    web_root = Path("src/web_app")
    production_html = (web_root / "production.html").read_text(encoding="utf-8")
    production_script = (web_root / "production.js").read_text(encoding="utf-8")
    changelog = (web_root / "changelog.html").read_text(encoding="utf-8")

    assert "Santoni Athena" in production_html
    assert "订单号是串联接单、ERP、APS、IOT、生产、服务候选和成衣输出的唯一工作流主键。" in production_html
    assert 'id="chatbiForm"' in production_html
    assert "废弃率分析" in production_html
    assert "/api/production/chatbi" in production_script
    assert "renderChatbi" in production_script
    assert "Santoni Athena Production Insight Naming" in changelog


def test_design_intake_page_explains_structuring_scope():
    web_root = Path("src/web_app")
    page = (web_root / "athena-mvp.html").read_text(encoding="utf-8")
    script = (web_root / "athena-mvp.js").read_text(encoding="utf-8")

    assert "Design Intake Structuring Console" in page
    assert "Design Agent data-structuring middleware test page" in page
    assert "not the full Athena MVP" in page
    assert "not a manual design-exhaustion tool" in page
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


def test_production_operations_workflow_outputs_read_only_management_console():
    result = ProductionOperationsWorkflow().overview()
    stage_ids = {stage["id"] for stage in result["workflow_stages"]}
    resource_keys = set(result["resource_lens"])
    kpis = {item["kpi"] for item in result["kpi_log"]}

    assert result["workflow_template"]["template_id"] == "athena.production_operations.v1"
    assert result["workflow_instance"]["read_only"] is True
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
    }.issubset(kpis)
    assert result["optimization_signals"]
    assert all(item["evidence_ref"] for item in result["optimization_signals"])


def test_production_chatbi_agent_explains_scrap_rate_with_evidence():
    result = ProductionOperationsWorkflow().chatbi(
        {"question": "为什么废弃率是4%？从款式、机台、物料和工艺上拆一下原因。"}
    )
    categories = {item["category"] for item in result["root_causes"]}
    serialized = json.dumps(result, ensure_ascii=False)

    assert result["agent"]["agent_id"] == "athena.production_chatbi_agent.v1"
    assert result["agent"]["name"] == "Santoni Athena"
    assert result["metric"] == "scrap_rate"
    assert result["read_only"] is True
    assert result["write_actions_blocked"] is True
    assert result["metric_snapshot"]["scrap_rate"] > 0
    assert {"style_quality", "machine", "material", "method"}.issubset(categories)
    assert all(item["evidence_refs"] for item in result["root_causes"])
    assert any(item["impact"].get("causal_status") == "not_primary_current_scrap_driver" for item in result["root_causes"])
    assert ".co" in serialized
    assert ".cx" in serialized
    assert "confirm_schedule" in result["blocked_actions"]


def test_production_adapter_contract_maps_aps_iot_fields_without_credentials():
    contract = ProductionOperationsWorkflow().adapter_contract()
    mapping_objects = {item["object"] for item in contract["field_mapping"]}
    source_systems = {item["system"] for item in contract["source_systems"]}
    serialized = json.dumps(contract, ensure_ascii=False).lower()

    assert contract["version"] == "v0.25.3"
    assert source_systems == {"APS", "Santoni IOT"}
    assert {
        "production_order",
        "yarn_material_forecast",
        "aps_schedule_capacity",
        "iot_machine_execution",
        "iot_program_evidence",
        "garment_quality_output",
    }.issubset(mapping_objects)
    assert "织造监控" in serialized
    assert "实时监控" in serialized
    assert ".co" in serialized
    assert ".cx" in serialized
    assert "cn程序" not in serialized
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
                    "错花，申请义大电子选针器",
                    "0052591",
                    "9009452",
                    "TOP2-FAST",
                    "Spare parts delivery issue 配件交付问题",
                    "Broken part delivered 交付的配件损坏",
                    "Broken part delivered 交付配件损坏",
                    "arrange new delivery 安排重新交付",
                    "索赔选针器、电源盒、选针器扁线。工作完成",
                ],
                [
                    "油箱分油嘴漏油",
                    "0052594",
                    "9009424",
                    "TOP2-FAST",
                    "Spare parts delivery issue 配件交付问题",
                    "Broken part delivered 交付的配件损坏",
                    "Broken part delivered 交付配件损坏",
                    "arrange new delivery 安排重新交付",
                    "工作完成 索赔油箱分油嘴",
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
            "online_resolution_steps_zh": ["检查选针器线缆。"],
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
    assert any("选针" in reason for reason in online_assist["matched_reasons"])
    assert any("选针" in step for step in online_assist["suggested_steps"])


def test_imported_service_case_matches_system_screen_fault():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="SM8 TOP2 MP2 序列号E000981，机器死机白屏，显示屏触摸没有反应，现场不能生产",
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
    assert any("漏油" in step for step in online_assist["suggested_steps"])


def test_service_followup_identifiers_do_not_switch_to_activation_case():
    agent = MainAgent()
    session_id = "service-followup-context"
    first = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="机器错花了，怎么办",
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
            message="机器错花了，怎么办",
        )
    )
    response = agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="错花是否固定出现在同一路",
        )
    )
    assert response.payload["known_info"]["online_guidance_request"] == "wrong_pattern_fixed_feed_check"
    assert "固定" in response.summary
    assert "选针器" in response.summary


def test_service_case_records_wrong_pattern_fixed_same_feed_answer():
    agent = MainAgent()
    session_id = "wrong-pattern-fixed-answer"
    agent.handle(
        AgentRequest(
            user_role="customer_equipment_engineer",
            session_id=session_id,
            message="机器错花了，怎么办",
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
    assert "该路" in response.summary


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
    assert "激活密码" in response.summary


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
    assert "人工介入" in response.summary


def test_top2mp_activation_password_unknown_serial_requires_manual_escalation():
    response = MainAgent().handle(
        AgentRequest(
            user_role="auto",
            message="TOP2MP 锁定，需要生成激活密码，序列号99999999，机器码LOCK-9999",
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
        <a href="javascript:__doPostBack(&#39;MainRadGridview$ctl00$ctl02$ctl00$RadToolBar1&#39;,&#39;generateActivation&#39;)">生成激活密码</a>
        <label>激活码:</label><input name="Window$txtActivateCode" value="">
        <label>激活密码:</label><input name="Window$txtActivatePassword" value="REAL-PASSWORD-123">
      </form>
    """
    assert tool._find_row_checkbox_name(html, "3004116") == "MainRadGridview$ctl00$ctl04$columnSelectCheckBox"
    assert tool._find_postback_near_text(html, "生成激活密码") == {
        "target": "MainRadGridview$ctl00$ctl02$ctl00$RadToolBar1",
        "argument": "generateActivation",
    }
    assert tool._input_name_after_label(html, "激活码") == "Window$txtActivateCode"
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
    login_html = "<html><title>圣东尼租赁密码系统--登录</title><input name='txtid'><input name='txtpwd'></html>"
    home_html = "<html><title>圣东尼租赁密码系统--首页</title><input name='MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_serial_num'>生成激活密码</html>"
    assert tool._looks_like_login_page(login_html) is True
    assert tool._looks_like_login_page(home_html) is False


def test_activation_tool_rejects_grid_filter_as_activation_code_field():
    tool = ActivationPasswordTool()
    html = """
      <span>激活机器码</span>
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
      <div id="radwindowactive"></div>
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) is None


def test_activation_tool_prefers_radwindowactive_code_field():
    tool = ActivationPasswordTool()
    html = """
      <span>激活码：</span><input name="radwindowactive$C$MachineCodeTextBox" value="">
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) == "radwindowactive$C$MachineCodeTextBox"


def test_activation_tool_finds_machine_code_input_near_label():
    tool = ActivationPasswordTool()
    html = """
      <div id="radwindowactive">
        <span>激活机器码</span>
        <table><tr><td><input type="text" name="RADwindowactive$C$txtMachineCode" value=""></td></tr></table>
      </div>
      <input name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) == "RADwindowactive$C$txtMachineCode"


def test_activation_tool_near_label_still_rejects_grid_filter():
    tool = ActivationPasswordTool()
    html = """
      <span>激活机器码</span>
      <input type="text" name="MainRadGridview$ctl00$ctl02$ctl03$FilterTextBox_machine_code" value="">
    """
    payload = tool._form_payload(html)
    assert tool._activation_code_field(html, payload) is None


def test_activation_tool_prefers_same_window_submit_button():
    tool = ActivationPasswordTool()
    html = """
      <span>激活机器码</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="">
      <input type="submit" name="radwindowfulledit$C$RadButton15_input" value="确定">
      <input type="submit" name="radwindownew$C$RadButton2_input" value="生成激活密码">
    """
    candidates = tool._activation_submit_candidates(html, "radwindownew$C$RadMaskedTextBox2")
    assert candidates[0]["name"] == "radwindownew$C$RadButton2_input"


def test_activation_tool_ignores_cancel_submit_button():
    tool = ActivationPasswordTool()
    html = """
      <span>激活机器码</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="">
      <input type="submit" name="radwindownew$C$RadButtonCancel_input" value="取消">
      <input type="submit" name="radwindownew$C$RadButtonOk_input" value="确定">
    """
    candidates = tool._activation_submit_candidates(html, "radwindownew$C$RadMaskedTextBox2")
    assert candidates[0]["name"] == "radwindownew$C$RadButtonOk_input"
    assert all("Cancel" not in item["name"] for item in candidates)


def test_activation_tool_reads_password_from_precise_label():
    tool = ActivationPasswordTool()
    html = """
      <span>激活码:</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="F11D-3E50-3E40-4CD3-756B-D4B9-02D4-516E">
      <span>激活密码:</span>
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
      <span>激活密码:</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox2" value="F11D-3E50-3E40-4CD3-756B-D4B9-02D4-516E">
    """
    assert tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E") == ""


def test_activation_tool_reads_password_from_telerik_client_state():
    tool = ActivationPasswordTool()
    html = """
      <span>激活密码:</span>
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
      123|updatePanel|radwindownew_C|<span>激活密码:</span>
      <input type="text" name="radwindownew$C$RadMaskedTextBox3" value="">
      <script>var generated='9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A';</script>|456
    """
    assert (
        tool._extract_activation_password(html, "F11D3E503E404CD3756BD4B902D4516E")
        == "9F53-2000-3C96-BACD-3E2E-89FF-F499-B42A"
    )

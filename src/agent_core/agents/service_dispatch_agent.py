"""Service Dispatch Agent skeleton."""

import json

from agent_core.language import choose
from agent_core.llm_client import LLMClient
from agent_core.schemas import SERVICE_DISPATCH_PLAN_SCHEMA


class ServiceDispatchAgent:
    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, issue: str, language: str = "en", image_context: dict | None = None, parsed_issue: dict | None = None) -> dict:
        parsed_issue = parsed_issue or {}
        generated, status = self.llm.generate_json(
            schema_name="service_dispatch_plan",
            schema=SERVICE_DISPATCH_PLAN_SCHEMA,
            system_prompt=(
                "You are Santoni's Service Dispatch Agent. Create and dispatch a service ticket only after the main agent has collected required information and the user has confirmed dispatch. "
                "Use realistic service dispatch logic based on production status, urgency, machine model, parts clues, and image context. "
                "Preserve exact machine model, serial number, alarm, and production status from parsed_issue when present. "
                "List missing information for the assigned engineer to collect, but do not overwrite known user-provided facts with generic values."
            ),
            user_prompt=json.dumps(
                {
                    "language": language,
                    "original_issue": issue,
                    "parsed_issue": parsed_issue,
                    "image_context": image_context or {},
                    "mock_engineers": [
                        {
                            "name": choose(language, "Li Wei", "李伟"),
                            "region": "Vietnam / South China",
                            "skills": ["SM8-TOP2V", "installation", "onsite troubleshooting"],
                            "available_from": "today 15:30",
                        }
                    ],
                    "mock_parts": ["Needle set", "Yarn tension sensor", "Installation calibration kit", "Bearing SKF-6205"],
                },
                ensure_ascii=False,
            ),
        )
        if generated and "_llm_error" not in generated:
            generated["machine_model"] = parsed_issue.get("machine_model") or generated.get("machine_model")
            generated["serial_number"] = parsed_issue.get("serial_number") or generated.get("serial_number")
            generated["production_status"] = parsed_issue.get("production_status") or generated.get("production_status")
            generated["factory_location"] = parsed_issue.get("factory_location") or generated.get("factory_location")
            generated["customer_contact"] = parsed_issue.get("customer_contact") or generated.get("customer_contact")
            generated["online_steps_attempted"] = parsed_issue.get("online_steps_attempted") or generated.get("online_steps_attempted", [])
            generated["parser_status"] = parsed_issue.get("parser_status", "unknown")
            generated["reasoning_status"] = status
            generated["symptoms"] = parsed_issue.get("symptoms", [])
            generated["source_issue"] = issue
            if image_context:
                generated["image_evidence"] = choose(
                    language,
                    "Uploaded image used as dispatch evidence and pre-check context.",
                    "上传图片已作为派工证据和工程师预判断依据。",
                )
            return generated

        urgency = parsed_issue.get("urgency", "P1")
        issue_type = parsed_issue.get("issue_type") or choose(language, "machine alarm / onsite support", "机器报警 / 现场服务支持")
        machine_model = parsed_issue.get("machine_model") or "SM8-TOP2V"
        parts_clues = parsed_issue.get("parts_clues", [])

        parts = [choose(language, "Needle set x 20", "织针套件 x 20")]
        if any("tension" in str(item).lower() or "张力" in str(item) for item in parts_clues + [parsed_issue.get("alarm_info", "")]):
            parts = [choose(language, "Yarn tension sensor x 1", "纱线张力传感器 x 1"), choose(language, "Needle set x 20", "织针套件 x 20")]
        elif "installation" in str(issue_type).lower() or "安装" in str(issue_type):
            parts = [choose(language, "Installation calibration kit x 1", "安装校准工具包 x 1"), choose(language, "Standard spare needle set x 1", "标准备用织针套件 x 1")]

        priority = {
            "P1": choose(language, "P1 - production stopped", "P1 - 生产停机"),
            "P2": choose(language, "P2 - production risk", "P2 - 生产风险"),
            "P3": choose(language, "P3 - planned support", "P3 - 计划支持"),
        }.get(urgency, choose(language, "P2 - production risk", "P2 - 生产风险"))

        result = {
            "ticket_id": "STN-SVC-20260515-001",
            "issue_category": issue_type,
            "machine_model": machine_model,
            "serial_number": parsed_issue.get("serial_number", "unknown"),
            "production_status": parsed_issue.get("production_status", "unknown"),
            "priority": priority,
            "factory_location": parsed_issue.get("factory_location", "unknown"),
            "customer_contact": parsed_issue.get("customer_contact", "unknown"),
            "assigned_engineer": choose(language, "Li Wei", "李伟"),
            "recommended_parts": parts,
            "eta": choose(language, "Today 15:30", "今天 15:30"),
            "status": choose(language, "Created -> Dispatched", "已创建 -> 已派发"),
            "dispatch_rationale": [
                choose(language, "Engineer is within same region", "工程师位于同一区域，响应时间最短"),
                choose(language, f"Engineer has {machine_model} experience", f"工程师具备 {machine_model} 现场经验"),
                choose(language, "Required spare parts are available", "所需备件当前有库存"),
            ],
            "online_steps_attempted": parsed_issue.get("online_steps_attempted", []),
            "symptoms": parsed_issue.get("symptoms", []),
            "missing_info": parsed_issue.get("missing_info", []),
            "parser_status": parsed_issue.get("parser_status", "local_static"),
            "reasoning_status": status,
            "source_issue": issue,
        }

        if image_context:
            result["image_evidence"] = choose(
                language,
                "Uploaded image used as dispatch evidence and pre-check context.",
                "上传图片已作为派工证据和工程师预判断依据。",
            )

        return result

"""LLM-backed text understanding with local rule-based fallback."""

from __future__ import annotations

from agent_core.language import detect_language
from agent_core.llm_client import LLMClient
from agent_core.schemas import DESIGN_BRIEF_SCHEMA, SERVICE_ISSUE_SCHEMA


class UnderstandingAgent:
    def __init__(self) -> None:
        self.llm = LLMClient()

    def parse_design_brief(self, brief: str, language: str = "en", image_context: dict | None = None) -> dict:
        parsed, status = self.llm.extract_json(
            schema_name="design_brief",
            schema=DESIGN_BRIEF_SCHEMA,
            system_prompt=(
                "You extract structured knitting product requirements for Santoni AI Knitting Agent. "
                "Return only JSON matching the schema. Use the user's language field as zh or en. "
                "Prefer concrete textile and knitting terms when present. Do not invent unavailable facts."
            ),
            user_prompt=f"Language: {language}\nBrief: {brief}\nImage context: {image_context or {}}",
        )
        if parsed and "_llm_error" not in parsed:
            parsed["parser_status"] = status
            return parsed

        fallback = self._fallback_design(brief, language)
        fallback["parser_status"] = status
        if parsed and parsed.get("_llm_error"):
            fallback["parser_error"] = parsed["_llm_error"]
        return fallback

    def parse_service_issue(self, issue: str, language: str = "en", image_context: dict | None = None) -> dict:
        parsed, status = self.llm.extract_json(
            schema_name="service_issue",
            schema=SERVICE_ISSUE_SCHEMA,
            system_prompt=(
                "You extract structured service ticket information for Santoni knitting machine support. "
                "Return only JSON matching the schema. Do not claim the machine is safe to operate. "
                "Classify urgency from P1 to P3 based on production impact. "
                "Extract serial number, machine code, factory location, customer contact, evidence status, and online steps attempted when present. "
                "For TOP2/TOP2MP activation password lock screens, classify the issue as activation_password_lock. "
                "The platform action is generating an activation password, even if the machine also has lease/rental status."
            ),
            user_prompt=f"Language: {language}\nIssue: {issue}\nImage context: {image_context or {}}",
        )
        if parsed and "_llm_error" not in parsed:
            parsed["parser_status"] = status
            return parsed

        fallback = self._fallback_service(issue, language)
        fallback["parser_status"] = status
        if parsed and parsed.get("_llm_error"):
            fallback["parser_error"] = parsed["_llm_error"]
        return fallback

    def _fallback_design(self, brief: str, language: str) -> dict:
        text = brief.lower()
        detected_language = detect_language(brief) if language == "auto" else language
        category = "seamless running top"
        if any(word in text for word in ["yoga", "瑜伽"]):
            category = "seamless yoga top"
        elif any(word in text for word in ["sock", "袜"]):
            category = "performance sock"
        elif any(word in text for word in ["legging", "裤", "紧身"]):
            category = "seamless leggings"

        functions = []
        if any(word in text for word in ["breath", "透气", "ventilation"]):
            functions.append("breathability")
        if any(word in text for word in ["quick dry", "快干", "dry"]):
            functions.append("quick dry")
        if any(word in text for word in ["stretch", "弹"]):
            functions.append("high stretch")
        if not functions:
            functions = ["comfort", "stable fit"]

        return {
            "language": detected_language,
            "product_category": category,
            "target_user": "Decathlon sports consumer",
            "use_case": "sports performance",
            "style_keywords": ["seamless", "functional", "clean"],
            "functional_requirements": functions,
            "material_preferences": ["Coolmax cotton blend"],
            "constraints": [],
            "missing_info": ["target price band", "color range", "sample size"],
        }

    def _fallback_service(self, issue: str, language: str) -> dict:
        text = issue.lower()
        detected_language = detect_language(issue) if language == "auto" else language
        stopped = any(word in text for word in ["stop", "stopped", "停机"])
        install = any(word in text for word in ["install", "installation", "安装", "调试"])
        alarm = any(word in text for word in ["alarm", "报警"])
        tension = any(word in text for word in ["tension", "张力"])
        activation_lock = any(
            word in text
            for word in [
                "激活密码",
                "生成激活密码",
                "激活机器码",
                "租赁锁定",
                "锁机激活",
                "锁机",
                "机器锁定",
                "锁屏",
                "锁定",
                "解锁",
                "解锁机器",
                "机器码",
                "activation password",
                "activate password",
                "lease",
                "rental password",
                "lock screen",
                "machine is locked",
                "machine locked",
                "locked machine",
                "machine lock",
                "unlock machine",
                "unlock the machine",
            ]
        )

        return {
            "language": detected_language,
            "machine_model": "TOP2MP" if "top2mp" in text else "TOP2-HIE" if "top2-hie" in text else "SM8-TOP2V" if "sm8" in text else "unknown",
            "serial_number": "unknown",
            "machine_code": "unknown",
            "issue_type": "activation_password_lock" if activation_lock else "installation" if install else "machine alarm" if alarm else "maintenance request",
            "symptoms": ["activation password lock screen"] if activation_lock else ["production stopped"] if stopped else ["requires service support"],
            "alarm_info": "activation password required after motherboard replacement or machine lock" if activation_lock else "yarn tension alarm" if tension else "unknown",
            "production_status": "stopped" if stopped or activation_lock else "unknown",
            "urgency": "P1" if stopped or activation_lock else "P2" if alarm or install else "P3",
            "onsite_required": False if activation_lock else stopped or install,
            "parts_clues": ["yarn tension sensor"] if tension else [],
            "evidence_status": "unknown",
            "factory_location": "unknown",
            "customer_contact": "unknown",
            "online_steps_attempted": [],
            "missing_info": ["machine serial number", "alarm photo", "factory location"],
        }

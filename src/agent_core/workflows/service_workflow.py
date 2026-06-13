"""Service workflow skeleton."""

from agent_core.agents.service_dispatch_agent import ServiceDispatchAgent
from agent_core.agents.understanding_agent import UnderstandingAgent
from agent_core.language import choose
from agent_core.tools.lease_password_tool import ActivationPasswordTool
from agent_core.tools.service_case_knowledge import ServiceCaseKnowledgeBase


class ServiceWorkflow:
    def __init__(self) -> None:
        self.understanding_agent = UnderstandingAgent()
        self.service_dispatch_agent = ServiceDispatchAgent()
        self.activation_password_tool = ActivationPasswordTool()
        self.service_case_knowledge = ServiceCaseKnowledgeBase()

    def run(self, issue: str, language: str = "en", image_context: dict | None = None) -> dict:
        parsed_issue = self.understanding_agent.parse_service_issue(issue, language, image_context)
        return self.run_prepared(issue, language, image_context, parsed_issue)

    def run_prepared(self, issue: str, language: str = "en", image_context: dict | None = None, parsed_issue: dict | None = None) -> dict:
        parsed_issue = parsed_issue or self.understanding_agent.parse_service_issue(issue, language, image_context)
        result = self.service_dispatch_agent.run(issue, language, image_context, parsed_issue)
        result["understanding"] = parsed_issue
        if image_context:
            result["image_understanding"] = image_context
        return result

    def prepare(
        self,
        issue: str,
        language: str = "en",
        image_context: dict | None = None,
        memory: dict | None = None,
        ready_to_dispatch: bool = False,
        platform_tool: dict | None = None,
    ) -> dict:
        parsed = self.understanding_agent.parse_service_issue(issue, language, image_context)
        parsed = self._sanitize_unverified_tool_inputs(parsed, issue, memory or {})
        parsed = self._enrich_from_user_text(parsed, issue)
        parsed = self._enrich_from_image_context(parsed, image_context)
        parsed = self._preserve_followup_context(parsed, issue, memory or {})
        merged = self._merge_memory(memory or {}, parsed)
        missing = self._required_missing(merged)
        online_assist = self._online_assist(merged, language, platform_tool or {})
        tool_terminal = self._is_tool_terminal(online_assist.get("tool_result", {}))
        if tool_terminal:
            missing = []
        if not missing and not ready_to_dispatch and not tool_terminal:
            missing = ["dispatch_confirmation"]
        return {
            "ready": len(missing) == 0 and not tool_terminal,
            "understanding": merged,
            "known_info": self._known_info(merged),
            "missing_info": missing,
            "questions": self._questions_for_case(merged, online_assist, language) + self._questions_for_missing(missing, language),
            "online_assist": online_assist,
            "memory": merged,
        }

    def _merge_memory(self, memory: dict, parsed: dict) -> dict:
        merged = dict(memory)
        for key, value in parsed.items():
            if key in {"parser_status", "parser_error"}:
                merged[key] = value
                continue
            if key == "urgency" and self._urgency_rank(value) < self._urgency_rank(merged.get(key)):
                continue
            if key == "onsite_required" and merged.get(key) is True and value is False:
                continue
            if self._has_value(value):
                merged[key] = value
            elif key not in merged:
                merged[key] = value
        return merged

    def _urgency_rank(self, urgency) -> int:
        return {"P1": 3, "P2": 2, "P3": 1}.get(str(urgency), 0)

    def _has_value(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return bool(value.strip()) and value.strip() not in {"unknown", "待确认", "未指定", "n/a"}
        if isinstance(value, list):
            return any(self._has_value(item) for item in value)
        return True

    def _required_missing(self, parsed: dict) -> list[str]:
        missing = []
        if not self._has_value(parsed.get("machine_model")):
            missing.append("machine_model")
        if not self._has_value(parsed.get("serial_number")):
            missing.append("serial_number")
        if not self._has_value(parsed.get("issue_type")) and not self._has_value(parsed.get("symptoms")):
            missing.append("symptoms")
        if not self._has_value(parsed.get("production_status")) or parsed.get("production_status") == "unknown":
            missing.append("production_status")
        is_stopped = parsed.get("production_status") == "stopped" or parsed.get("urgency") == "P1"
        if not self._has_value(parsed.get("alarm_info")) and is_stopped:
            missing.append("alarm_info_or_photo")
        if self._is_activation_password_case(parsed):
            if not self._has_value(parsed.get("machine_code")):
                missing.append("machine_code_or_lock_screen")
            return missing
        if not self._has_value(parsed.get("evidence_status")):
            missing.append("photo_or_video_evidence")
        if not self._has_value(parsed.get("factory_location")):
            missing.append("factory_location")
        if not self._has_value(parsed.get("customer_contact")):
            missing.append("customer_contact")
        if not self._has_value(parsed.get("online_steps_attempted")):
            missing.append("online_steps_attempted")
        return missing

    def _known_info(self, parsed: dict) -> dict:
        keys = [
            "machine_model",
            "serial_number",
            "machine_code",
            "issue_type",
            "symptoms",
            "alarm_info",
            "production_status",
            "urgency",
            "onsite_required",
            "parts_clues",
            "evidence_status",
            "factory_location",
            "customer_contact",
            "online_steps_attempted",
            "diagnostic_observations",
            "online_guidance_request",
        ]
        return {key: parsed.get(key) for key in keys if self._has_value(parsed.get(key))}

    def _questions_for_case(self, parsed: dict, online_assist: dict, language: str) -> list[str]:
        if online_assist.get("matched_case_id") == "SVC-IMPORT-202605-001":
            observations = parsed.get("diagnostic_observations") or []
            if "wrong_pattern_fixed_same_feed" not in observations and "wrong_pattern_random" not in observations:
                return [
                    choose(
                        language,
                        "Is the wrong pattern fixed on the same feed/position, or random across the fabric?",
                        "错花是固定出现在同一路/同一位置，还是随机出现在布面？",
                    )
                ]
            if "wrong_pattern_fixed_same_feed" in observations and not self._has_value(parsed.get("online_steps_attempted")):
                return [
                    choose(
                        language,
                        "Please check the actuator cable and selector area for that feed, then tell me whether the defect repeats at low speed.",
                        "请先检查该路选针器线缆和选针区域，然后告诉我低速测试是否还重复错花。",
                    )
                ]
        return []

    def _questions_for_missing(self, missing: list[str], language: str) -> list[str]:
        labels = {
            "machine_model": ("Which machine model and serial number is affected?", "请提供机器型号和序列号。"),
            "serial_number": ("What is the machine serial number?", "请提供机器序列号。"),
            "symptoms": ("What exactly happened: alarm, fabric defect, abnormal sound, failed startup, or something else?", "具体发生了什么：报警、布面瑕疵、异响、无法开机，还是其他？"),
            "production_status": ("Is production stopped, reduced speed, or still running?", "目前是完全停机、降速运行，还是还能正常生产？"),
            "alarm_info_or_photo": ("Please provide the alarm code/message or upload a control-panel photo.", "请提供报警代码/报警信息，或上传控制面板照片。"),
            "machine_code_or_lock_screen": (
                "Please provide the machine code shown on the lock screen, or upload a clear lock-screen photo.",
                "请提供锁定界面显示的机器码，或上传清晰的锁定界面照片。",
            ),
            "photo_or_video_evidence": ("Please upload an alarm photo, short video, or control-panel screenshot.", "请上传报警照片、短视频或控制面板截图。"),
            "factory_location": ("Which factory/site is the machine in?", "机器所在工厂/现场位置是哪里？"),
            "customer_contact": ("Who should Santoni contact for this issue?", "Santoni 应该联系谁处理这个问题？请提供姓名和电话/邮箱。"),
            "online_steps_attempted": (
                "What online checks have already been tried: restart, yarn path check, tensioner check, or none yet?",
                "目前已经尝试过哪些在线排查：重启、纱路检查、张力器检查，还是还没有尝试？",
            ),
            "dispatch_confirmation": (
                "I have enough information to prepare a ticket. Should I create and dispatch it now, or continue online troubleshooting first?",
                "我已经有足够信息准备工单。现在创建并派工，还是继续先在线排查？",
            ),
        }
        return [labels[item][1 if language == "zh" else 0] for item in missing[:3]]

    def _sanitize_unverified_tool_inputs(self, parsed: dict, issue: str, memory: dict) -> dict:
        """Do not let the LLM invent identifiers used by service tools."""
        import re

        sanitized = dict(parsed)
        explicit_model = re.search(r"\b(SM8(?:[-\s]?[A-Z0-9]+)*|TOP2(?:MP|[-A-Z0-9]*))\b", issue, re.IGNORECASE)
        explicit_serial = re.search(r"(?:序列号|serial\s+number|serial|sn|s/n)[:：\s]*([A-Z0-9]{5,})", issue, re.IGNORECASE) or re.search(
            r"(?<![A-Z0-9])(?:[A-Z]\d{5,}|\d{6,})(?![A-Z0-9])", issue, re.IGNORECASE
        )
        explicit_machine_code = re.search(r"(?:机器码|machine code)[:：\s]*([A-Za-z0-9-]{4,})", issue, re.IGNORECASE)

        if not explicit_model and not self._has_value(memory.get("machine_model")):
            sanitized["machine_model"] = "unknown"
        if not explicit_serial and not self._has_value(memory.get("serial_number")):
            sanitized["serial_number"] = "unknown"
        if not explicit_machine_code and not self._has_value(memory.get("machine_code")):
            sanitized["machine_code"] = "unknown"
        return sanitized

    def _enrich_from_user_text(self, parsed: dict, issue: str) -> dict:
        import re

        enriched = dict(parsed)
        lowered = issue.lower()
        model_match = re.search(r"\b(SM8(?:[-\s]?[A-Z0-9]+)*|TOP2(?:MP|[-A-Z0-9]*))\b", issue, re.IGNORECASE)
        if model_match:
            enriched["machine_model"] = model_match.group(1).replace(" ", "-").upper()
        serial_match = re.search(r"(?:序列号|serial\s+number|serial|sn|s/n)[:：\s]*([A-Z0-9]{5,})", issue, re.IGNORECASE) or re.search(
            r"(?<![A-Z0-9])(?:[A-Z]\d{5,}|\d{6,})(?![A-Z0-9])", issue, re.IGNORECASE
        )
        if serial_match:
            enriched["serial_number"] = (serial_match.group(1) if serial_match.lastindex else serial_match.group(0)).upper()
        machine_code_match = re.search(r"(?:机器码|machine code)[:：\s]*([A-Za-z0-9-]{4,})", issue, re.IGNORECASE)
        if machine_code_match:
            enriched["machine_code"] = machine_code_match.group(1).strip()

        is_activation_request = self._has_explicit_activation_intent(issue)
        if is_activation_request:
            enriched["issue_type"] = "activation_password_lock"
            enriched["alarm_info"] = "activation password required after motherboard replacement or machine lock"
            enriched["production_status"] = "stopped"
            enriched["urgency"] = "P1"
            enriched["onsite_required"] = False

        if any(word in issue for word in ["错花", "选针", "漏针"]):
            enriched["issue_type"] = "fabric_defect"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["错花", "选针错误"]))
            enriched["production_status"] = "quality_risk"
            enriched["urgency"] = "P2"
            enriched["onsite_required"] = False
        if "错花是否固定" in issue or ("错花" in issue and "是否固定" in issue):
            enriched["online_guidance_request"] = "wrong_pattern_fixed_feed_check"
        elif any(word in issue for word in ["固定在同一路", "固定同一路", "同一路", "同一位置"]) and not any(
            word in issue for word in ["是否", "吗", "不固定", "随机"]
        ):
            enriched["diagnostic_observations"] = list(
                dict.fromkeys((enriched.get("diagnostic_observations") or []) + ["wrong_pattern_fixed_same_feed"])
            )
            enriched["parts_clues"] = list(dict.fromkeys((enriched.get("parts_clues") or []) + ["选针器", "选针器线缆", "该路选针区域"]))
            enriched["online_steps_attempted"] = list(
                dict.fromkeys((enriched.get("online_steps_attempted") or []) + ["confirmed wrong pattern fixed on same feed/position"])
            )
        elif any(word in issue for word in ["不固定", "随机", "不是固定"]):
            enriched["diagnostic_observations"] = list(
                dict.fromkeys((enriched.get("diagnostic_observations") or []) + ["wrong_pattern_random"])
            )
            enriched["online_steps_attempted"] = list(
                dict.fromkeys((enriched.get("online_steps_attempted") or []) + ["confirmed wrong pattern appears randomly"])
            )

        if any(word in issue for word in ["漏油", "油箱", "分油器", "分油嘴"]):
            enriched["issue_type"] = "mechanical"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["漏油"] ))
            enriched["production_status"] = "quality_risk"
            enriched["urgency"] = "P2"
            enriched["onsite_required"] = False
        if any(word in issue for word in ["死机", "白屏", "显示屏", "触摸没有反应", "不能改日期", "系统错乱", "程序错乱"]):
            enriched["issue_type"] = "electrical"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["系统/显示屏故障"] ))
            enriched["production_status"] = "stopped"
            enriched["urgency"] = "P1"
            enriched["onsite_required"] = True
        if any(word in issue for word in ["坏针", "打针", "撞针", "护针板", "三角断裂"]):
            enriched["issue_type"] = "mechanical"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["打针/坏针"] ))
            enriched["production_status"] = "stopped"
            enriched["urgency"] = "P1"
            enriched["onsite_required"] = True
        if any(word in issue for word in ["马达", "驱动器", "ECODD", "伺服"]):
            enriched["issue_type"] = "electrical"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["马达/驱动器故障"] ))
            enriched["production_status"] = "stopped"
            enriched["urgency"] = "P1"
            enriched["onsite_required"] = True
        if any(word in issue for word in ["电子眼", "输纱器", "传感器", "学习"]):
            enriched["issue_type"] = "calibration"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["电子眼/输纱器校准"] ))

        if "张力" in issue or "tension" in lowered:
            enriched["issue_type"] = "machine alarm"
            enriched["alarm_info"] = "yarn tension alarm"
            enriched["symptoms"] = list(dict.fromkeys((enriched.get("symptoms") or []) + ["张力报警"] ))
            enriched["parts_clues"] = list(dict.fromkeys((enriched.get("parts_clues") or []) + ["yarn tension sensor"] ))
        if "停机" in issue or "恢复生产" in issue or "stopped" in lowered or "locked" in lowered:
            enriched["production_status"] = "stopped"
            enriched["urgency"] = "P1"
            enriched["onsite_required"] = False if is_activation_request else True
        if any(word in lowered for word in ["photo", "video", "screenshot"]) or any(word in issue for word in ["照片", "图片", "视频", "截图"]):
            enriched["evidence_status"] = "provided in conversation"

        contact_match = re.search(r"((?:\+?\d[\d -]{8,}\d)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", issue)
        if contact_match:
            enriched["customer_contact"] = contact_match.group(1).strip()
        location_match = re.search(r"(?:工厂|现场|地址|location|site)[:：\s]*([^,，。?？\n]+)", issue, re.IGNORECASE)
        if location_match:
            enriched["factory_location"] = location_match.group(1).strip()

        attempted_steps = []
        attempted_keywords = [
            ("restart", "restart"),
            ("reboot", "restart"),
            ("重启", "重启"),
            ("复位", "复位"),
            ("yarn path", "yarn path check"),
            ("纱路", "纱路检查"),
            ("tensioner", "tensioner check"),
            ("张力器", "张力器检查"),
            ("还没", "none yet"),
            ("没有尝试", "none yet"),
            ("not tried", "none yet"),
        ]
        for keyword, label in attempted_keywords:
            if keyword in lowered or keyword in issue:
                attempted_steps.append(label)
        if attempted_steps:
            enriched["online_steps_attempted"] = list(dict.fromkeys(attempted_steps))
        return enriched

    def _preserve_followup_context(self, parsed: dict, issue: str, memory: dict) -> dict:
        if not memory:
            return parsed
        if not self._has_value(memory.get("issue_type")):
            return parsed
        if self._is_activation_password_case(memory):
            return parsed
        if self._has_explicit_activation_intent(issue):
            return parsed
        if not self._is_identifier_only_followup(issue):
            return parsed

        preserved = dict(parsed)
        for key in [
            "issue_type",
            "symptoms",
            "alarm_info",
            "production_status",
            "urgency",
            "onsite_required",
            "parts_clues",
            "diagnostic_observations",
        ]:
            if self._has_value(memory.get(key)):
                preserved[key] = memory[key]
        preserved["context_preserved_from_memory"] = True
        return preserved

    def _is_identifier_only_followup(self, issue: str) -> bool:
        import re

        stripped = re.sub(r"\b(SM8(?:[-\s]?[A-Z0-9]+)*|TOP2(?:MP|[-A-Z0-9]*))\b", " ", issue, flags=re.IGNORECASE)
        stripped = re.sub(r"(?<![A-Z0-9])(?:[A-Z]\d{5,}|\d{6,})(?![A-Z0-9])", " ", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"(机器型号|机型|型号|序列号|serial|sn|s/n|machine|model|[:：,，。；;、\s-])", " ", stripped, flags=re.IGNORECASE)
        return not stripped.strip()

    def _has_explicit_activation_intent(self, issue: str) -> bool:
        lowered = issue.lower()
        return any(
            word in lowered
            for word in [
                "activation password",
                "activate password",
                "rental password",
                "lock screen",
                "machine is locked",
                "machine locked",
                "locked machine",
                "machine lock",
                "unlock machine",
                "unlock the machine",
            ]
        ) or any(word in issue for word in ["激活密码", "生成激活密码", "锁机激活", "锁机", "锁定", "锁屏", "解锁", "机器码"])
    def _enrich_from_image_context(self, parsed: dict, image_context: dict | None) -> dict:
        enriched = dict(parsed)
        if not image_context:
            return enriched

        signals = " ".join(str(item) for item in image_context.get("detected_signals", []))
        enriched["evidence_status"] = f"uploaded image: {image_context.get('primary_image', 'image')}"
        if self._is_activation_password_case(enriched) and not self._has_value(enriched.get("machine_code")):
            enriched["machine_code"] = "pending OCR from lock-screen photo"
        if not self._has_value(enriched.get("alarm_info")) and ("alarm" in signals.lower() or "报警" in signals):
            enriched["alarm_info"] = signals
        if not self._has_value(enriched.get("parts_clues")) and ("tension" in signals.lower() or "张力" in signals):
            enriched["parts_clues"] = ["yarn tension sensor"]
        return enriched

    def _online_assist(self, parsed: dict, language: str, platform_tool: dict | None = None) -> dict:
        issue = " ".join([str(parsed.get("issue_type", "")), str(parsed.get("alarm_info", "")), " ".join(parsed.get("symptoms", []))]).lower()
        if self._is_activation_password_case(parsed):
            steps = [
                (
                    "Collect TOP2MP serial number from nameplate photo and machine code from the lock screen.",
                    "收集 TOP2MP 机器铭牌序列号，以及锁定界面显示的机器码。",
                ),
                (
                    "Mock tool step: check the activation-password platform by serial number and verify whether the machine status allows password generation.",
                    "模拟工具步骤：按序列号查询激活密码平台，确认机器状态允许生成密码。",
                ),
                (
                    "If the serial number is found and the platform status allows it, generate the activation password and send it back to the onsite technician.",
                    "如果序列号存在且平台状态允许，则生成激活密码并反馈给现场技术人员。",
                ),
                (
                    "Escalate to Santoni service staff if the serial number is missing from the platform or the lease expiry date is earlier than today.",
                    "如果平台查不到序列号，或租赁到期日期早于今天，则升级给 Santoni 服务人员人工介入。",
                ),
            ]
            return {
                "case_database_status": "mock_matched",
                "matched_case_id": "SVC-MOCK-0002",
                "tool_candidate": "activation_password_generator",
                "tool_status": "real_platform_attempt" if (platform_tool or {}).get("mode") == "real_attempt" else "mock_only_no_real_platform_login",
                "tool_result": self.activation_password_tool.run(
                    serial_number=parsed.get("serial_number"),
                    machine_code=parsed.get("machine_code"),
                    tool_mode=(platform_tool or {}).get("mode", "mock"),
                    credentials=(platform_tool or {}).get("credentials", {}),
                ),
                "suggested_steps": [item[1 if language == "zh" else 0] for item in steps],
                "manual_escalation_triggers": [
                    choose(language, "serial number not found in platform", "平台查不到机器序列号"),
                    choose(language, "lease expiry date is earlier than today", "租赁到期日期早于今天"),
                    choose(language, "customer cannot provide serial number or lock-screen machine code", "客户无法提供序列号或锁定界面机器码"),
                ],
            }
        matched_case = self.service_case_knowledge.match(parsed, issue, language)
        if matched_case.get("case_database_status") == "mock_matched":
            return matched_case

        steps = [
            ("Collect machine model, serial number, alarm/photo, and recent maintenance history.", "先收集机器型号、序列号、报警/照片和最近维护记录。"),
            ("I will compare it with service cases once the case database is available.", "服务案例库接入后，我会优先匹配历史案例。"),
        ]
        return {
            "case_database_status": "mock_pending",
            "skill": "service_case_online_assist_mock",
            "suggested_steps": [item[1 if language == "zh" else 0] for item in steps],
        }

    def _is_activation_password_case(self, parsed: dict) -> bool:
        text = " ".join(
            [
                str(parsed.get("machine_model", "")),
                str(parsed.get("issue_type", "")),
                str(parsed.get("alarm_info", "")),
                " ".join(parsed.get("symptoms", [])),
            ]
        ).lower()
        has_top2 = "top2" in text
        explicit_activation_issue = "activation_password_lock" in text
        has_password_intent = any(
            word in text
            for word in [
                "activation_password",
                "activation password",
                "activate password",
                "lease_password",
                "lease password",
                "rental password",
                "lock screen",
                "machine is locked",
                "machine locked",
                "locked machine",
                "machine lock",
                "unlock machine",
                "unlock the machine",
                "激活密码",
                "生成激活密码",
                "锁机激活",
                "锁机",
                "锁定",
                "锁屏",
                "解锁",
                "机器码",
            ]
        )
        return explicit_activation_issue or (has_top2 and has_password_intent)
    def _is_tool_terminal(self, tool_result: dict) -> bool:
        return tool_result.get("status") in {
            "success",
            "manual_escalation_required",
            "real_platform_login_discovered",
            "real_platform_login_not_completed",
            "real_platform_serial_filter_mapping_required",
            "real_platform_serial_not_found",
            "real_platform_activation_dialog_mapping_required",
            "real_platform_activation_submit_mapping_required",
            "real_platform_activation_password_not_found",
        }



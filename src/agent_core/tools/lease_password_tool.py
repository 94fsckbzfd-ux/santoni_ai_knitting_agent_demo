"""Mock activation password generator for TOP2 service cases.

This adapter intentionally does not connect to the real Santoni platform and
does not store platform credentials. It models the future tool contract only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import html as html_lib
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from datetime import date
from pathlib import Path


class ActivationPasswordTool:
    def __init__(self, records_path: Path | None = None, today: date | None = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.records_path = records_path or root / "mock_data" / "activation_password_records.json"
        self.today = today or date.today()

    def run(
        self,
        *,
        serial_number: str | None,
        machine_code: str | None,
        tool_mode: str = "mock",
        credentials: dict | None = None,
    ) -> dict:
        serial = self._normalize(serial_number)
        code = self._normalize(machine_code)
        if self._is_missing(serial) or self._is_missing(code) or code.startswith("PENDING OCR"):
            return {
                "tool": "activation_password_generator",
                "status": "missing_input",
                "required_inputs": ["serial_number", "machine_code"],
                "message": "Serial number and lock-screen machine code are required before the mock tool can generate an activation password.",
            }

        if tool_mode == "real_attempt":
            return self._run_real_attempt(serial_number=serial, machine_code=code, credentials=credentials or {})

        record = self._find_record(serial)
        if not record:
            return {
                "tool": "activation_password_generator",
                "status": "manual_escalation_required",
                "reason": "serial_number_not_found",
                "serial_number": serial,
                "message": "Mock platform did not find this serial number. Santoni service staff must verify it manually.",
            }

        expiry = date.fromisoformat(record["lease_expiry_date"])
        lease_status = record.get("lease_status", "unknown")
        if expiry < self.today and lease_status not in {"paid_up", "no_active_lease"}:
            return {
                "tool": "activation_password_generator",
                "status": "manual_escalation_required",
                "reason": "lease_expired",
                "serial_number": serial,
                "lease_expiry_date": record["lease_expiry_date"],
                "message": "Mock platform shows the lease/rental expiry date is earlier than today. Santoni service staff must intervene.",
            }

        return {
            "tool": "activation_password_generator",
            "status": "success",
            "serial_number": serial,
            "machine_model": record.get("machine_model", "TOP2MP"),
            "lease_status": lease_status,
            "lease_expiry_date": record["lease_expiry_date"],
            "activation_password": self._generate_password(serial, code),
            "message": "Mock activation password generated. In production this would come from the controlled platform tool.",
        }

    def _find_record(self, serial_number: str) -> dict | None:
        records = json.loads(self.records_path.read_text(encoding="utf-8"))
        for record in records:
            if self._normalize(record.get("serial_number")) == serial_number:
                return record
        return None

    def _generate_password(self, serial_number: str, machine_code: str) -> str:
        digest = hashlib.sha256(f"{serial_number}:{machine_code}".encode("utf-8")).hexdigest().upper()
        return f"MOCK-{serial_number[-4:]}-{digest[:6]}"

    def _normalize(self, value: str | None) -> str:
        return str(value or "").strip().upper()

    def _is_missing(self, value: str) -> bool:
        return value in {"", "UNKNOWN", "未指定", "待确认", "N/A"}

    def _run_real_attempt(self, *, serial_number: str, machine_code: str, credentials: dict) -> dict:
        username = credentials.get("username") or os.environ.get("SANTONI_PLATFORM_USERNAME", "")
        password = credentials.get("password") or os.environ.get("SANTONI_PLATFORM_PASSWORD", "")
        login_url = os.environ.get("SANTONI_PLATFORM_LOGIN_URL", "http://platform.santoni.cn:9090/Login.aspx")

        if not username or not password:
            return {
                "tool": "activation_password_generator",
                "mode": "real_attempt",
                "status": "missing_credentials",
                "required_inputs": ["platform_username", "platform_password"],
                "message": "Real platform mode requires credentials from the UI or environment variables.",
            }

        try:
            cookie_jar = CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
            login_page_response = opener.open(login_url, timeout=12)
            login_page = login_page_response.read().decode("utf-8", errors="ignore")
            login_fields = self._discover_form_fields(login_page)
            login_payload = self._build_login_payload(login_page, username, password)
            login_request = urllib.request.Request(
                login_url,
                data=urllib.parse.urlencode(login_payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Santoni-AI-Agent-Demo/0.14",
                },
                method="POST",
            )
            post_login_response = opener.open(login_request, timeout=15)
            post_login_url = post_login_response.geturl()
            post_login_page = post_login_response.read().decode("utf-8", errors="ignore")
            if self._looks_like_login_page(post_login_page):
                default_url = urllib.parse.urljoin(login_url, "Default2.aspx")
                default_response = opener.open(default_url, timeout=15)
                default_page = default_response.read().decode("utf-8", errors="ignore")
                if not self._looks_like_login_page(default_page):
                    post_login_url = default_response.geturl()
                    post_login_page = default_page

            post_login_summary = self._discover_post_login_page(post_login_page, post_login_url)
            if self._looks_like_login_page(post_login_page):
                return {
                    "tool": "activation_password_generator",
                    "mode": "real_attempt",
                    "status": "real_platform_login_not_completed",
                    "serial_number": serial_number,
                    "machine_code": machine_code,
                    "login_url": login_url,
                    "login_fields": login_fields,
                    "post_login_summary": post_login_summary,
                    "platform_steps": ["login_post_submitted", "default_page_retry_failed"],
                    "message": "Submitted the real login form, but the platform still returned the login page.",
                }

            generation_result = self._try_generate_activation_password(
                opener=opener,
                page_html=post_login_page,
                page_url=post_login_url,
                serial_number=serial_number,
                machine_code=machine_code,
            )
            if generation_result.get("status") == "success":
                return {
                    "tool": "activation_password_generator",
                    "mode": "real_attempt",
                    "status": "success",
                    "serial_number": serial_number,
                    "machine_code": machine_code,
                    "activation_password": generation_result.get("activation_password", ""),
                    "platform_steps": generation_result.get("platform_steps", []),
                    "message": "Real platform generated an activation password.",
                }

            return {
                "tool": "activation_password_generator",
                "mode": "real_attempt",
                "status": generation_result.get("status", "real_platform_generation_mapping_required"),
                "serial_number": serial_number,
                "machine_code": machine_code,
                "login_url": login_url,
                "login_fields": login_fields,
                "post_login_summary": post_login_summary,
                "platform_steps": generation_result.get("platform_steps", []),
                "mapping_hint": generation_result.get("mapping_hint", {}),
                "message": generation_result.get("message", "Real platform mapping is incomplete."),
            }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return {
                "tool": "activation_password_generator",
                "mode": "real_attempt",
                "status": "real_platform_connection_failed",
                "serial_number": serial_number,
                "machine_code": machine_code,
                "message": str(exc),
            }

    def _discover_form_fields(self, html: str) -> dict:
        fields = re.findall(r"<input\b[^>]*?(?:name|id)=['\"]?([^'\"\s>]+)", html, flags=re.IGNORECASE)
        safe_fields = [field for field in fields if "password" not in field.lower() and "pwd" not in field.lower()]
        return {
            "input_count": len(fields),
            "safe_input_names": safe_fields[:20],
        }

    def _build_login_payload(self, html: str, username: str, password: str) -> dict:
        fields: dict[str, str] = {}
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            name = self._attr(tag, "name")
            if not name:
                continue
            fields[name] = self._attr(tag, "value") or ""

        username_field = self._pick_field(fields, ["txtid", "username", "userid", "user", "login"])
        password_field = self._pick_field(fields, ["txtpwd", "password", "pwd", "pass"])
        submit_field = self._pick_field(fields, ["button1", "login", "submit"])

        if username_field:
            fields[username_field] = username
        if password_field:
            fields[password_field] = password
        if submit_field and not fields.get(submit_field):
            fields[submit_field] = "Login"
        return fields

    def _discover_post_login_page(self, html: str, base_url: str) -> dict:
        page_text = self._compact_text(html)
        links = []
        for href, text in re.findall(r"<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", html, flags=re.IGNORECASE | re.DOTALL):
            label = self._compact_text(text)
            if label:
                links.append({"text": label[:80], "href": urllib.parse.urljoin(base_url, href)})

        candidate_terms = ["生成激活密码", "激活密码", "激活机器码", "租赁", "密码", "激活", "机器", "序列", "lease", "password", "activate", "machine", "serial"]
        matched_terms = [term for term in candidate_terms if term.lower() in page_text.lower()]
        return {
            "page_title": self._page_title(html),
            "input_fields": self._discover_form_fields(html),
            "safe_links": links[:20],
            "matched_terms": matched_terms,
        }

    def _looks_like_login_page(self, html: str) -> bool:
        title = self._page_title(html)
        text = self._compact_text(html)
        has_login_fields = "txtid" in html and ("txtpwd" in html or "password" in html.lower())
        has_grid = "MainRadGridview" in html or "生成激活密码" in text
        return ("登录" in title or has_login_fields) and not has_grid

    def _try_generate_activation_password(
        self,
        *,
        opener,
        page_html: str,
        page_url: str,
        serial_number: str,
        machine_code: str,
    ) -> dict:
        steps = ["login_success"]
        working_html = page_html
        working_url = page_url

        if serial_number not in working_html:
            filtered = self._post_serial_filter(opener, working_html, working_url, serial_number)
            if filtered.get("html"):
                working_html = filtered["html"]
                working_url = filtered["url"]
                steps.append("serial_filter_submitted")
            else:
                return {
                    "status": "real_platform_serial_filter_mapping_required",
                    "platform_steps": steps,
                    "mapping_hint": filtered.get("mapping_hint", {}),
                    "message": "Logged in, but could not submit the serial-number filter mapping.",
                }

        if serial_number not in working_html:
            return {
                "status": "real_platform_serial_not_found",
                "platform_steps": steps,
                "mapping_hint": {"serial_number": serial_number},
                "message": "Logged in and filtered, but the serial number was not found on the real platform page.",
            }

        dialog = self._post_open_activation_dialog(opener, working_html, working_url, serial_number)
        if not dialog.get("html"):
            return {
                "status": "real_platform_activation_dialog_mapping_required",
                "platform_steps": steps,
                "mapping_hint": dialog.get("mapping_hint", {}),
                "message": "Logged in and found the serial number, but could not map the toolbar postback for the activation-password dialog.",
            }

        steps.append("activation_dialog_opened")
        submitted = self._post_activation_dialog(opener, dialog["html"], dialog["url"], machine_code)
        if not submitted.get("html"):
            return {
                "status": "real_platform_activation_submit_mapping_required",
                "platform_steps": steps,
                "mapping_hint": submitted.get("mapping_hint", {}),
                "message": "Opened the activation-password dialog, but could not map the activation-code input or submit button.",
            }

        steps.append("activation_code_submitted")
        activation_password = self._extract_activation_password(submitted["html"], machine_code)
        if activation_password:
            steps.append("activation_password_read")
            return {
                "status": "success",
                "platform_steps": steps,
                "activation_password": activation_password,
            }

        return {
            "status": "real_platform_activation_password_not_found",
            "platform_steps": steps,
            "mapping_hint": {
                "visible_terms": [term for term in ["激活密码", "激活码", "生成激活密码"] if term in self._compact_text(submitted["html"])],
                "candidate_inputs": self._text_input_names(submitted["html"])[:20],
                "activation_password_label_inputs": self._near_label_input_candidates(submitted["html"], ["激活密码"]),
            },
            "message": "Submitted the activation code, but could not read a non-empty activation password from the response page.",
        }

    def _post_serial_filter(self, opener, html: str, url: str, serial_number: str) -> dict:
        payload = self._form_payload(html)
        serial_field = self._pick_field(payload, ["filtertextbox_serial_num", "serial_num", "serial"])
        filter_field = self._pick_field(payload, ["filter_serial_num"])
        if not serial_field:
            return {"mapping_hint": {"candidate_inputs": self._text_input_names(html)[:20]}}

        payload[serial_field] = serial_number
        if filter_field:
            payload[filter_field] = ""
            payload[f"{filter_field}.x"] = "10"
            payload[f"{filter_field}.y"] = "10"
        response = self._post_form(opener, url, payload)
        return response or {"mapping_hint": {"serial_field": serial_field, "filter_field": filter_field}}

    def _post_open_activation_dialog(self, opener, html: str, url: str, serial_number: str) -> dict:
        payload = self._form_payload(html)
        checkbox_name = self._find_row_checkbox_name(html, serial_number)
        if checkbox_name:
            payload[checkbox_name] = "on"

        postback = self._find_postback_near_text(html, "生成激活密码")
        postback_candidates = [postback] if postback else self._toolbar_activation_postback_candidates(html)
        if not postback_candidates:
            return {
                "mapping_hint": {
                    "serial_number": serial_number,
                    "row_checkbox": checkbox_name,
                    "candidate_toolbar_targets": self._toolbar_candidates(html, "生成激活密码"),
                    "toolbar_client_states": self._safe_toolbar_client_states(html),
                }
            }

        attempted = []
        for postback_candidate in postback_candidates:
            candidate_payload = dict(payload)
            candidate_payload["__EVENTTARGET"] = postback_candidate["target"]
            candidate_payload["__EVENTARGUMENT"] = postback_candidate.get("argument", "")
            response = self._post_form(opener, url, candidate_payload)
            attempted.append(postback_candidate)
            if response and ("激活码" in response["html"] or "激活密码" in response["html"]):
                response["mapping_used"] = postback_candidate
                return response

        return {
                "mapping_hint": {
                    "attempted_postbacks": attempted,
                    "row_checkbox": checkbox_name,
                    "toolbar_client_states": self._safe_toolbar_client_states(html),
                }
            }

    def _post_activation_dialog(self, opener, html: str, url: str, machine_code: str) -> dict:
        payload = self._form_payload(html)
        activation_code_field = self._activation_code_field(html, payload)
        if not activation_code_field:
            return {
                "mapping_hint": {
                    "candidate_inputs": self._safe_input_candidates(html),
                    "activation_window_controls": self._activation_window_controls(html),
                    "activation_window_inputs": self._activation_window_input_candidates(html),
                    "activation_label_inputs": self._near_label_input_candidates(html, ["激活码", "激活机器码", "机器码"]),
                    "candidate_submits": self._activation_submit_candidates(html),
                    "rejected_reason": "No precise activation-code input was found. Grid filter fields are intentionally ignored.",
                }
            }

        payload[activation_code_field] = machine_code
        submit = self._find_postback_near_field(html, activation_code_field) or self._find_postback_near_text(html, "生成激活密码")
        if submit:
            payload["__EVENTTARGET"] = submit["target"]
            payload["__EVENTARGUMENT"] = submit.get("argument", "")
        else:
            submit_candidates = self._activation_submit_candidates(html, activation_code_field)
            if not submit_candidates:
                return {
                    "mapping_hint": {
                        "activation_code_field": activation_code_field,
                        "candidate_submits": self._activation_submit_candidates(html),
                        "activation_window_inputs": self._activation_window_input_candidates(html, activation_code_field),
                        "activation_window_controls": self._activation_window_controls(html),
                    }
                }

            attempted = []
            for submit_candidate in submit_candidates[:5]:
                submit_name = submit_candidate.get("name", "")
                if not submit_name:
                    continue
                candidate_payload = dict(payload)
                candidate_payload[submit_name] = submit_candidate.get("value") or self._input_value_by_name(html, submit_name) or "生成激活密码"
                response = self._post_form(opener, url, candidate_payload)
                attempted.append(
                    {
                        "name": submit_name,
                        "value": submit_candidate.get("value", ""),
                        "id": submit_candidate.get("id", ""),
                        "type": submit_candidate.get("type", ""),
                        "score": submit_candidate.get("score", 0),
                    }
                )
                if response and self._activation_submit_response_looks_relevant(response["html"]):
                    response["mapping_used"] = {"submit": submit_candidate}
                    return response

            return {
                "mapping_hint": {
                    "activation_code_field": activation_code_field,
                    "attempted_submits": attempted,
                    "candidate_submits": submit_candidates[:20],
                    "activation_window_inputs": self._activation_window_input_candidates(html, activation_code_field),
                    "activation_window_controls": self._activation_window_controls(html),
                }
            }
        return self._post_form(opener, url, payload) or {
            "mapping_hint": {
                "activation_code_field": activation_code_field,
                "submit": submit or self._activation_submit_name(html, activation_code_field),
            }
        }

    def _form_payload(self, html: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            name = self._attr(tag, "name")
            if not name:
                continue
            input_type = (self._attr(tag, "type") or "text").lower()
            if input_type in {"checkbox", "radio"} and "checked" not in tag.lower():
                continue
            fields[name] = html_lib.unescape(self._attr(tag, "value") or "")
        return fields

    def _post_form(self, opener, url: str, payload: dict[str, str]) -> dict | None:
        request = urllib.request.Request(
            url,
            data=urllib.parse.urlencode(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Santoni-AI-Agent-Demo/0.14",
            },
            method="POST",
        )
        response = opener.open(request, timeout=15)
        return {"url": response.geturl(), "html": response.read().decode("utf-8", errors="ignore")}

    def _find_row_checkbox_name(self, html: str, serial_number: str) -> str | None:
        serial_index = html.find(serial_number)
        if serial_index >= 0:
            row_start = max(0, html.rfind("<tr", 0, serial_index))
            row_end = html.find("</tr>", serial_index)
            row_html = html[row_start : row_end if row_end > row_start else min(len(html), serial_index + 5000)]
            names = re.findall(r"<input\b[^>]*name=['\"]([^'\"]*columnSelectCheckBox[^'\"]*)['\"]", row_html, flags=re.IGNORECASE)
            if names:
                return html_lib.unescape(names[-1])

        names = [
            html_lib.unescape(name)
            for name in re.findall(r"<input\b[^>]*name=['\"]([^'\"]*columnSelectCheckBox[^'\"]*)['\"]", html, flags=re.IGNORECASE)
            if "$ctl02$" not in name
        ]
        return names[0] if names else None

    def _find_postback_near_text(self, html: str, text: str) -> dict | None:
        text_index = html.find(text)
        if text_index < 0:
            return None
        segment = html_lib.unescape(html[max(0, text_index - 3000) : min(len(html), text_index + 3000)])
        match = re.search(
            r"__doPostBack\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]*)['\"]\)",
            segment,
            flags=re.IGNORECASE,
        )
        if match:
            return {"target": html_lib.unescape(match.group(1)), "argument": html_lib.unescape(match.group(2))}
        match = re.search(
            r"WebForm_PostBackOptions\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]*)['\"]",
            segment,
            flags=re.IGNORECASE,
        )
        if match:
            return {"target": html_lib.unescape(match.group(1)), "argument": html_lib.unescape(match.group(2))}
        return None

    def _find_postback_near_field(self, html: str, field_name: str) -> dict | None:
        field_index = html.find(field_name)
        if field_index < 0:
            return None
        segment = html_lib.unescape(html[max(0, field_index - 2000) : min(len(html), field_index + 5000)])
        for pattern in [
            r"__doPostBack\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]*)['\"]\)",
            r"WebForm_PostBackOptions\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]*)['\"]",
        ]:
            for match in re.finditer(pattern, segment, flags=re.IGNORECASE):
                target = html_lib.unescape(match.group(1))
                argument = html_lib.unescape(match.group(2))
                lowered = f"{target} {argument}".lower()
                if any(blocked in lowered for blocked in ["delete", "remove", "cancel", "close", "删除", "取消"]):
                    continue
                if any(token in lowered for token in ["active", "activate", "activation", "generate", "激活", "生成"]):
                    return {"target": target, "argument": argument}
        return None

    def _toolbar_candidates(self, html: str, text: str) -> list[dict]:
        candidates = []
        for match in re.finditer(re.escape(text), html):
            segment = html[max(0, match.start() - 800) : min(len(html), match.end() + 800)]
            candidates.append(
                {
                    "ids": re.findall(r"\bid=['\"]([^'\"]+)['\"]", segment)[:5],
                    "names": re.findall(r"\bname=['\"]([^'\"]+)['\"]", segment)[:5],
                    "has_postback": "__doPostBack" in segment,
                }
            )
        return candidates[:5]

    def _toolbar_activation_postback_candidates(self, html: str) -> list[dict]:
        candidates: list[dict] = []
        for state in self._toolbar_client_states(html):
            target = state["unique_id"]
            commands = self._activation_toolbar_commands(state.get("value", ""))
            for command in commands:
                candidates.append({"target": target, "argument": f"onclick#{command}", "source": "toolbar_client_state"})
            for command in [
                "生成激活密码",
                "GenerateActivatePassword",
                "GenerateActivationPassword",
                "ActivePassword",
                "ActivationPassword",
                "CreateActivePassword",
                "CreateActivationPassword",
                "GenerateActivePwd",
                "GenerateActivationPwd",
            ]:
                candidates.append({"target": target, "argument": f"onclick#{command}", "source": "safe_activation_guess"})

        unique = []
        seen = set()
        for candidate in candidates:
            key = (candidate["target"], candidate["argument"])
            if key not in seen:
                seen.add(key)
                unique.append(candidate)
        return unique[:12]

    def _toolbar_client_states(self, html: str) -> list[dict]:
        states = []
        for tag in re.findall(r"<input\b[^>]*RadToolBar[^>]*ClientState[^>]*>", html, flags=re.IGNORECASE):
            name = self._attr(tag, "name") or self._attr(tag, "id")
            value = html_lib.unescape(self._attr(tag, "value") or "")
            if not name:
                continue
            toolbar_id = re.sub(r"_ClientState$", "", name)
            unique_id = toolbar_id.replace("_", "$")
            states.append(
                {
                    "name": html_lib.unescape(name),
                    "unique_id": unique_id,
                    "activation_index": self._activation_text_index(value),
                    "value_preview": value[:600],
                    "value": value,
                }
            )
        if states:
            return states

        ids = re.findall(r"\bid=['\"]([^'\"]*RadToolBar[^'\"]*)['\"]", html, flags=re.IGNORECASE)
        for toolbar_id in ids:
            if toolbar_id.endswith("_ClientState"):
                continue
            states.append(
                {
                    "name": toolbar_id,
                    "unique_id": toolbar_id.replace("_", "$"),
                    "activation_index": None,
                    "value_preview": "",
                    "value": "",
                }
            )
        return states[:3]

    def _safe_toolbar_client_states(self, html: str) -> list[dict]:
        safe_states = []
        for state in self._toolbar_client_states(html):
            safe_states.append(
                {
                    "name": state.get("name"),
                    "unique_id": state.get("unique_id"),
                    "activation_index": state.get("activation_index"),
                    "value_preview": state.get("value_preview", ""),
                    "activation_commands": self._activation_toolbar_commands(state.get("value", "")),
                }
            )
        return safe_states

    def _activation_toolbar_commands(self, state_value: str) -> list[str]:
        decoded = html_lib.unescape(state_value or "")
        commands = []
        for item in re.finditer(r"(.{0,180}生成激活密码.{0,180})", decoded, flags=re.IGNORECASE | re.DOTALL):
            segment = item.group(1)
            for pattern in [
                r'"(?:commandName|CommandName|command|Command|value|Value)"\s*:\s*"([^"]+)"',
                r"'(?:commandName|CommandName|command|Command|value|Value)'\s*:\s*'([^']+)'",
                r"(?:commandName|CommandName|command|Command|value|Value)['\"]?\s*[:=]\s*['\"]([^'\"]+)",
            ]:
                for command in re.findall(pattern, segment):
                    if self._is_safe_activation_command(command):
                        commands.append(html_lib.unescape(command))
        return list(dict.fromkeys(commands))

    def _activation_text_index(self, state_value: str) -> int | None:
        decoded = html_lib.unescape(state_value or "")
        index = decoded.find("生成激活密码")
        if index < 0:
            return None
        before = decoded[:index]
        return before.count('"text"') + before.count("'text'") + before.count("Text")

    def _is_safe_activation_command(self, command: str) -> bool:
        lowered = command.lower()
        return any(token in lowered for token in ["active", "activate", "activation", "激活"]) and not any(
            danger in lowered for danger in ["delete", "remove", "batch", "export", "mail", "短信", "删除", "批量", "导出"]
        )

    def _input_name_after_label(self, html: str, label: str) -> str | None:
        pattern = rf"{re.escape(label)}\s*[:：]?\s*(?:</[^>]+>\s*){{0,4}}(?:<[^>]+>\s*){{0,8}}(<input\b[^>]*>)"
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        name = html_lib.unescape(self._attr(match.group(1), "name"))
        return name if name and self._is_activation_input_name(name) else None

    def _activation_code_field(self, html: str, payload: dict[str, str]) -> str | None:
        for label in ["激活码", "激活机器码", "机器码"]:
            label_field = self._input_name_after_label(html, label) or self._input_name_near_label(html, label)
            if label_field:
                return label_field

        candidates = []
        for name in payload:
            lower_name = name.lower()
            if not self._is_activation_input_name(name):
                continue
            score = 0
            if "radwindowactive" in lower_name:
                score += 5
            if "$c$" in lower_name or "$C$" in name:
                score += 2
            if any(token in lower_name for token in ["code", "machine", "mc", "activate", "active"]):
                score += 2
            candidates.append((score, name))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]

    def _input_name_near_label(self, html: str, label: str) -> str | None:
        for match in re.finditer(re.escape(label), html, flags=re.IGNORECASE):
            segment = html[match.end() : min(len(html), match.end() + 3000)]
            for tag in re.findall(r"<input\b[^>]*>", segment, flags=re.IGNORECASE):
                input_type = (self._attr(tag, "type") or "text").lower()
                name = html_lib.unescape(self._attr(tag, "name") or "")
                if name and self._is_safe_activation_text_input(name, input_type):
                    return name
        return None

    def _is_activation_input_name(self, name: str) -> bool:
        lower_name = name.lower()
        if any(token in lower_name for token in ["filter", "mainradgridview$ctl00$ctl02$ctl03", "clientstate", "viewstate", "eventvalidation"]):
            return False
        return any(token in lower_name for token in ["radwindowactive", "active", "activate", "activation", "machinecode", "machine_code", "mc_string", "mccode", "code"])

    def _is_safe_activation_text_input(self, name: str, input_type: str) -> bool:
        lower_name = name.lower()
        if input_type not in {"text", "textarea", ""}:
            return False
        if any(token in lower_name for token in ["filter", "viewstate", "eventvalidation", "clientstate", "password", "pwd"]):
            return False
        return bool(name)

    def _submit_name_for_value(self, html: str, value_text: str) -> str | None:
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            value = html_lib.unescape(self._attr(tag, "value") or "")
            if value_text in value:
                name = html_lib.unescape(self._attr(tag, "name"))
                if name and "filter" not in name.lower():
                    return name
        return None

    def _activation_submit_name(self, html: str, activation_code_field: str | None = None) -> str | None:
        exact = self._submit_name_for_value(html, "生成激活密码")
        if exact:
            return exact
        candidates = self._activation_submit_candidates(html, activation_code_field)
        if candidates:
            return candidates[0].get("name") or None
        return None

    def _extract_activation_password(self, html: str, machine_code: str = "") -> str:
        label_value = self._input_value_after_precise_label(html, "激活密码", exclude_values=[machine_code])
        if label_value:
            return label_value

        label_field = self._input_name_after_precise_label(html, "激活密码") or self._input_name_after_label(html, "激活密码")
        if label_field:
            value = self._input_value_by_name(html, label_field)
            if value and not self._same_machine_code(value, machine_code):
                return value
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            name = self._attr(tag, "name").lower()
            value = html_lib.unescape(self._attr(tag, "value") or "").strip()
            if value and ("pwd" in name or "password" in name or "pass" in name) and len(value) >= 8 and not self._same_machine_code(value, machine_code):
                return value
        for value in self._activation_password_value_candidates(html, machine_code):
            return value
        return ""

    def _input_name_after_precise_label(self, html: str, label: str) -> str | None:
        for match in re.finditer(rf"(?<!生成){re.escape(label)}\s*[:：]", html, flags=re.IGNORECASE):
            segment = html[match.end() : min(len(html), match.end() + 3000)]
            for tag in re.findall(r"<input\b[^>]*>", segment, flags=re.IGNORECASE):
                input_type = (self._attr(tag, "type") or "text").lower()
                name = html_lib.unescape(self._attr(tag, "name") or "")
                if name and self._is_safe_activation_text_input(name, input_type):
                    return name
        return None

    def _input_value_after_precise_label(self, html: str, label: str, exclude_values: list[str] | None = None) -> str:
        excluded = exclude_values or []
        for match in re.finditer(rf"(?<!生成){re.escape(label)}\s*[:：]", html, flags=re.IGNORECASE):
            segment = html[match.end() : min(len(html), match.end() + 3000)]
            for tag in re.findall(r"<input\b[^>]*>", segment, flags=re.IGNORECASE):
                input_type = (self._attr(tag, "type") or "text").lower()
                name = html_lib.unescape(self._attr(tag, "name") or "")
                if not self._is_safe_activation_text_input(name, input_type):
                    continue
                value = html_lib.unescape(self._attr(tag, "value") or "").strip() or self._input_value_by_name(html, name)
                if value and not any(self._same_machine_code(value, excluded_value) for excluded_value in excluded):
                    return value
            for value in self._code_like_values_from_text(segment):
                if value and not any(self._same_machine_code(value, excluded_value) for excluded_value in excluded):
                    return value
        return ""

    def _activation_password_value_candidates(self, html: str, machine_code: str) -> list[str]:
        values = []
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            value = html_lib.unescape(self._attr(tag, "value") or "").strip()
            if not value or self._same_machine_code(value, machine_code):
                continue
            compact = value.replace("-", "").upper()
            if re.fullmatch(r"[A-F0-9]{24,64}", compact) and "-" in value:
                values.append(value)
        for value in self._code_like_values_from_text(html):
            if not self._same_machine_code(value, machine_code):
                values.append(value)
        return list(dict.fromkeys(values))

    def _code_like_values_from_text(self, text: str) -> list[str]:
        decoded = html_lib.unescape(text or "")
        values = []
        patterns = [
            r"\b(?:[A-F0-9]{4}-){7}[A-F0-9]{4}\b",
            r"\b[A-F0-9]{32}\b",
        ]
        for pattern in patterns:
            values.extend(match.group(0) for match in re.finditer(pattern, decoded, flags=re.IGNORECASE))

        for json_text in re.findall(r"value\s*=\s*(['\"])(.*?)\1", decoded, flags=re.IGNORECASE | re.DOTALL):
            values.extend(self._code_like_values_from_client_state(json_text[1]))

        return list(dict.fromkeys(value.upper() for value in values))

    def _code_like_values_from_client_state(self, state_value: str) -> list[str]:
        decoded = html_lib.unescape(state_value or "")
        values = self._code_like_values_from_text(decoded) if decoded and decoded != state_value else []
        try:
            data = json.loads(decoded)
        except json.JSONDecodeError:
            data = None
        if data is not None:
            for value in self._walk_string_values(data):
                values.extend(self._code_like_values_from_text(value))
                if re.fullmatch(r"[A-F0-9-]{24,80}", value.strip(), flags=re.IGNORECASE):
                    values.append(value.strip())
        return list(dict.fromkeys(value.upper() for value in values if value))

    def _walk_string_values(self, data) -> list[str]:
        if isinstance(data, str):
            return [data]
        if isinstance(data, dict):
            values = []
            for item in data.values():
                values.extend(self._walk_string_values(item))
            return values
        if isinstance(data, list):
            values = []
            for item in data:
                values.extend(self._walk_string_values(item))
            return values
        return []

    def _same_machine_code(self, value: str, machine_code: str) -> bool:
        if not value or not machine_code:
            return False
        normalize = lambda item: re.sub(r"[^A-F0-9]", "", item.upper())
        return normalize(value) == normalize(machine_code)

    def _input_value_by_name(self, html: str, name: str) -> str:
        client_state_names = []
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            if self._attr(tag, "name") == name:
                value = html_lib.unescape(self._attr(tag, "value") or "").strip()
                if value:
                    return value
                input_id = html_lib.unescape(self._attr(tag, "id") or "")
                if input_id:
                    client_state_names.append(f"{input_id}_ClientState")
                client_state_names.append(f"{name.replace('$', '_')}_ClientState")
        client_state_names = list(dict.fromkeys(client_state_names))
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            tag_name = html_lib.unescape(self._attr(tag, "name") or "")
            tag_id = html_lib.unescape(self._attr(tag, "id") or "")
            if not any(candidate in {tag_name, tag_id} for candidate in client_state_names):
                continue
            state_value = html_lib.unescape(self._attr(tag, "value") or "").strip()
            for value in self._code_like_values_from_client_state(state_value):
                return value
        return ""

    def _text_input_names(self, html: str) -> list[str]:
        names = []
        for tag in re.findall(r"<input\b[^>]*>", html, flags=re.IGNORECASE):
            input_type = (self._attr(tag, "type") or "text").lower()
            if input_type in {"text", "hidden", "password"}:
                name = self._attr(tag, "name")
                if name and "password" not in name.lower() and "pwd" not in name.lower():
                    names.append(html_lib.unescape(name))
        return names

    def _submit_candidates(self, html: str, limit: int = 20) -> list[dict]:
        candidates = []
        for tag in re.findall(r"<(?:input|button)\b[^>]*>", html, flags=re.IGNORECASE):
            value = html_lib.unescape(self._attr(tag, "value") or "")
            name = html_lib.unescape(self._attr(tag, "name") or "")
            input_id = html_lib.unescape(self._attr(tag, "id") or "")
            input_type = (self._attr(tag, "type") or ("button" if tag.lower().startswith("<button") else "text")).lower()
            lowered = f"{name} {input_id}".lower()
            if not (value or name or input_id):
                continue
            if any(token in lowered for token in ["viewstate", "eventvalidation", "clientstate"]):
                continue
            if not (input_type in {"submit", "button", "image"} or "button" in lowered or "radbutton" in lowered):
                continue
            candidates.append({"name": name, "id": input_id, "value": value, "type": input_type})
        return candidates[:limit]

    def _safe_input_candidates(self, html: str) -> list[str]:
        names = self._text_input_names(html)
        preferred = [name for name in names if any(token in name.lower() for token in ["radwindowactive", "active", "activate", "activation", "machine", "code"])]
        filtered = [name for name in preferred if not any(token in name.lower() for token in ["filter", "viewstate", "eventvalidation", "clientstate"])]
        return filtered[:40] or [name for name in names if "filter" not in name.lower()][:40]

    def _activation_window_controls(self, html: str, activation_code_field: str | None = None) -> list[str]:
        controls = []
        if activation_code_field:
            controls.extend(self._window_prefixes_for_field(activation_code_field))
        for pattern in [
            r"(radwindowactive[\w$]*)",
            r"(RADwindowactive[\w$]*)",
            r"(radwindownew[\w$]*)",
            r"(RADwindownew[\w$]*)",
            r"(radwindowactiveonly[\w$]*)",
        ]:
                controls.extend(html_lib.unescape(item) for item in re.findall(pattern, html, flags=re.IGNORECASE))
        return list(dict.fromkeys(controls))[:50]

    def _activation_window_input_candidates(self, html: str, activation_code_field: str | None = None) -> list[dict]:
        candidates = []
        for control in self._activation_window_controls(html, activation_code_field):
            control_index = html.lower().find(control.lower())
            if control_index < 0:
                continue
            segment = html[max(0, control_index - 1000) : min(len(html), control_index + 6000)]
            for tag in re.findall(r"<input\b[^>]*>", segment, flags=re.IGNORECASE):
                name = html_lib.unescape(self._attr(tag, "name") or "")
                input_id = html_lib.unescape(self._attr(tag, "id") or "")
                input_type = (self._attr(tag, "type") or "text").lower()
                if not name and not input_id:
                    continue
                if any(token in f"{name} {input_id}".lower() for token in ["viewstate", "eventvalidation", "password", "pwd"]):
                    continue
                candidates.append(
                    {
                        "control": control,
                        "name": name,
                        "id": input_id,
                        "type": input_type,
                        "value_present": bool(self._attr(tag, "value")),
                    }
                )
        return self._dedupe_dicts(candidates)[:60]

    def _near_label_input_candidates(self, html: str, labels: list[str]) -> list[dict]:
        candidates = []
        for label in labels:
            for match in re.finditer(re.escape(label), html, flags=re.IGNORECASE):
                segment = html[match.end() : min(len(html), match.end() + 3000)]
                for tag in re.findall(r"<input\b[^>]*>", segment, flags=re.IGNORECASE):
                    name = html_lib.unescape(self._attr(tag, "name") or "")
                    input_id = html_lib.unescape(self._attr(tag, "id") or "")
                    input_type = (self._attr(tag, "type") or "text").lower()
                    if name or input_id:
                        candidates.append({"label": label, "name": name, "id": input_id, "type": input_type})
        return self._dedupe_dicts(candidates)[:40]

    def _activation_submit_candidates(self, html: str, activation_code_field: str | None = None) -> list[dict]:
        field_prefixes = self._window_prefixes_for_field(activation_code_field or "")
        candidates = []
        for candidate in self._submit_candidates(html, limit=500):
            name = candidate.get("name", "")
            input_id = candidate.get("id", "")
            value = candidate.get("value", "")
            lower = f"{name} {input_id} {value}".lower()
            if any(token in lower for token in ["delete", "remove", "cancel", "close", "删除", "取消", "退出"]):
                continue

            score = 0
            if field_prefixes and any(name.startswith(prefix) or input_id.startswith(prefix.replace("$", "_")) for prefix in field_prefixes):
                score += 20
            if "生成激活密码" in value:
                score += 10
            if any(token in lower for token in ["active", "activate", "activation", "激活"]):
                score += 6
            if any(token in lower for token in ["generate", "生成", "submit", "button", "radbutton", "确定", "提交"]):
                score += 3
            if score > 0 and name:
                candidate = dict(candidate)
                candidate["score"] = score
                candidates.append(candidate)

        candidates.sort(key=lambda item: item.get("score", 0), reverse=True)
        return candidates[:40]

    def _window_prefixes_for_field(self, field_name: str) -> list[str]:
        if not field_name:
            return []
        prefixes = []
        for separator in ["$C$", "_C_"]:
            if separator in field_name:
                prefixes.append(field_name.split(separator, 1)[0] + separator)
        if "$" in field_name and not prefixes:
            parts = field_name.split("$")
            if len(parts) >= 2:
                prefixes.append("$".join(parts[:2]) + "$")
        if "_" in field_name:
            parts = field_name.split("_")
            if len(parts) >= 2:
                prefixes.append("_".join(parts[:2]) + "_")
        return list(dict.fromkeys(prefixes))

    def _activation_submit_response_looks_relevant(self, html: str) -> bool:
        if self._extract_activation_password(html):
            return True
        text = self._compact_text(html)
        return "激活密码" in text or "生成激活密码" in text or "激活码" in text

    def _dedupe_dicts(self, items: list[dict]) -> list[dict]:
        unique = []
        seen = set()
        for item in items:
            key = tuple(sorted(item.items()))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    def _matched_generation_terms(self, html: str) -> list[str]:
        text = self._compact_text(html)
        return [term for term in ["生成激活密码", "激活码", "激活密码", "序列号"] if term in text]

    def _pick_field(self, fields: dict[str, str], candidates: list[str]) -> str | None:
        lowered = {key.lower(): key for key in fields}
        for candidate in candidates:
            if candidate.lower() in lowered:
                return lowered[candidate.lower()]
        for key in fields:
            low = key.lower()
            if any(candidate.lower() in low for candidate in candidates):
                return key
        return None

    def _attr(self, tag: str, attr_name: str) -> str:
        match = re.search(rf"{attr_name}\s*=\s*(['\"])(.*?)\1", tag, flags=re.IGNORECASE | re.DOTALL)
        return match.group(2) if match else ""

    def _page_title(self, html: str) -> str:
        match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        return self._compact_text(match.group(1)) if match else ""

    def _compact_text(self, html: str) -> str:
        text = re.sub(r"<[^>]+>", " ", html)
        return re.sub(r"\s+", " ", text).strip()


LeasePasswordTool = ActivationPasswordTool

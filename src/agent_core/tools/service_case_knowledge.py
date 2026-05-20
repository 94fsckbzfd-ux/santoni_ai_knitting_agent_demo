"""Mock service-case knowledge base for online assistance.

This is the second Service Agent mock: a case-based online support skill.
It loads structured service cases and returns safe troubleshooting guidance
without requiring code changes for each new case.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


REVIEW_STATUSES = {"approved", "needs_changes", "internal_only", "draft_needs_review"}


class ServiceCaseKnowledgeBase:
    def __init__(self, cases_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.cases_path = cases_path or root / "mock_data" / "service_cases.example.json"
        self.extra_cases_path = root / "mock_data" / "service_cases.imported_20260418_20260518.json"
        self.draft_cases_path = root / "mock_data" / "service_cases.draft_import.json"
        self.review_records_path = root / "mock_data" / "service_case_reviews.json"
        self.cases = self._load_cases()

    def match(self, parsed: dict, issue_text: str = "", language: str = "en") -> dict:
        scored = []
        text = self._search_text(parsed, issue_text)
        for case in self._customer_facing_cases():
            score, reasons = self._score_case(case, parsed, text)
            has_strong_reason = any(
                reason.startswith(("symptom_keyword:", "alarm_code:", "issue_category:")) for reason in reasons
            )
            if score >= 3 and has_strong_reason:
                scored.append((score, case, reasons))

        if not scored:
            return {
                "case_database_status": "mock_no_match",
                "skill": "service_case_online_assist_mock",
                "message": "No mock service case matched this issue yet.",
            }

        scored.sort(key=lambda item: item[0], reverse=True)
        score, case, reasons = scored[0]
        confidence = min(0.95, round(score / 12, 2))
        return {
            "case_database_status": "mock_matched",
            "skill": "service_case_online_assist_mock",
            "matched_case_id": case.get("case_id"),
            "matched_case_title": case.get("title"),
            "match_confidence": confidence,
            "matched_reasons": reasons[:6],
            "online_solvable": case.get("online_solvable", False),
            "suggested_steps": self._localized_list(case, "online_resolution_steps", language),
            "safety_warnings": self._localized_list(case, "safety_warnings", language),
            "required_customer_info": self._localized_list(case, "required_customer_info", language),
            "required_evidence": self._localized_list(case, "required_evidence", language),
            "probable_causes": self._localized_list(case, "probable_causes", language),
            "recommended_parts": self._localized_list(case, "recommended_parts", language),
            "dispatch_triggers": self._localized_list(case, "dispatch_triggers", language),
            "estimated_resolution_time": self._localized_text(case, "estimated_resolution_time", language),
            "confidence_notes": case.get("confidence_notes", ""),
            "related_cases": case.get("related_cases", []),
        }

    def review_cases(self) -> dict:
        cases = []
        records = self._load_review_records()
        for case in [*self.cases, *self._load_draft_cases()]:
            source, review_status, customer_visible = self._review_state_for_case(case, records)
            record = records.get(str(case.get("case_id", "")), {})
            cases.append(
                {
                    "case_id": str(case.get("case_id", "")),
                    "title": case.get("title", ""),
                    "source": source,
                    "review_status": review_status,
                    "customer_visible": customer_visible,
                    "review_note": record.get("review_note", ""),
                    "reviewed_at": record.get("reviewed_at", ""),
                    "machine_models": case.get("machine_models", []),
                    "issue_category": case.get("issue_category", ""),
                    "severity": case.get("severity", ""),
                    "online_solvable": case.get("online_solvable", False),
                    "symptom_keywords": case.get("symptom_keywords", []),
                    "alarm_codes": case.get("alarm_codes", []),
                    "online_resolution_steps": self._localized_list(case, "online_resolution_steps", "zh"),
                    "safety_warnings": self._localized_list(case, "safety_warnings", "zh"),
                    "dispatch_triggers": self._localized_list(case, "dispatch_triggers", "zh"),
                    "recommended_parts": case.get("recommended_parts", []),
                    "estimated_resolution_time": self._localized_text(case, "estimated_resolution_time", "zh"),
                    "confidence_notes": case.get("confidence_notes", ""),
                    "source_row_count": case.get("source_row_count", 0),
                    "source_wo_numbers": case.get("source_wo_numbers", []),
                    "source_serials": case.get("source_serials", []),
                }
            )

        return {
            "library_name": "Service Case Online Assist Mock",
            "case_count": len(cases),
            "implemented_count": sum(1 for case in cases if case["review_status"] == "implemented_mock"),
            "needs_review_count": sum(1 for case in cases if case["review_status"] == "needs_service_review"),
            "draft_count": sum(1 for case in cases if case["review_status"] == "draft_needs_review"),
            "approved_count": sum(1 for case in cases if case["review_status"] == "approved"),
            "needs_changes_count": sum(1 for case in cases if case["review_status"] == "needs_changes"),
            "internal_only_count": sum(1 for case in cases if case["review_status"] == "internal_only"),
            "planned_features": [
                {
                    "name": "Excel auto importer",
                    "status": "implemented_v0.17.0",
                    "description": "Read monthly service Excel files and generate draft case JSON for human review.",
                },
                {
                    "name": "Case approval workflow",
                    "status": "implemented_v0.18.0",
                    "description": "Mark each case as approved, needs changes, or not customer-visible before it is used in customer-facing support.",
                },
                {
                    "name": "Case edit and diff view",
                    "status": "planned",
                    "description": "Edit online steps, keywords, safety warnings, and dispatch triggers from the review page.",
                },
            ],
            "cases": cases,
        }

    def apply_review(self, case_id: str, review_status: str, review_note: str = "") -> dict:
        case_id = str(case_id or "").strip()
        review_status = str(review_status or "").strip()
        if review_status not in REVIEW_STATUSES:
            raise ValueError(f"Unsupported review status: {review_status}")

        known_ids = {str(case.get("case_id", "")) for case in [*self.cases, *self._load_draft_cases()]}
        if case_id not in known_ids:
            raise ValueError(f"Unknown service case: {case_id}")

        records = self._load_review_records()
        records[case_id] = {
            "review_status": review_status,
            "customer_visible": review_status == "approved",
            "review_note": str(review_note or "").strip(),
            "reviewed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.review_records_path.parent.mkdir(parents=True, exist_ok=True)
        self.review_records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.review_cases()

    def _load_cases(self) -> list[dict]:
        cases: list[dict] = []
        if not self.cases_path.exists():
            return cases
        cases.extend(json.loads(self.cases_path.read_text(encoding="utf-8")))
        if self.extra_cases_path.exists() and self.extra_cases_path != self.cases_path:
            cases.extend(json.loads(self.extra_cases_path.read_text(encoding="utf-8")))
        return cases

    def _load_draft_cases(self) -> list[dict]:
        if not self.draft_cases_path.exists():
            return []
        return json.loads(self.draft_cases_path.read_text(encoding="utf-8"))

    def _load_review_records(self) -> dict:
        if not self.review_records_path.exists():
            return {}
        return json.loads(self.review_records_path.read_text(encoding="utf-8"))

    def _review_state_for_case(self, case: dict, records: dict) -> tuple[str, str, bool]:
        case_id = str(case.get("case_id", ""))
        if case_id.startswith("SVC-DRAFT-"):
            source = "excel_auto_import_draft"
            default_status = "draft_needs_review"
            default_visible = False
        elif case_id.startswith("SVC-IMPORT-202605"):
            source = "imported_20260418_20260518"
            default_status = "needs_service_review"
            default_visible = True
        else:
            source = "base_mock"
            default_status = "implemented_mock"
            default_visible = True

        record = records.get(case_id, {})
        review_status = record.get("review_status", default_status)
        if review_status == "approved":
            return source, review_status, True
        if review_status in {"needs_changes", "internal_only", "draft_needs_review"}:
            return source, review_status, False
        return source, default_status, default_visible

    def _customer_facing_cases(self) -> list[dict]:
        records = self._load_review_records()
        agent_cases = []
        for case in self.cases:
            _, review_status, customer_visible = self._review_state_for_case(case, records)
            if review_status in {"needs_changes", "internal_only", "draft_needs_review"}:
                continue
            if customer_visible:
                agent_cases.append(case)

        for case in self._load_draft_cases():
            _, review_status, customer_visible = self._review_state_for_case(case, records)
            if review_status == "approved" and customer_visible:
                agent_cases.append(case)
        return agent_cases

    def _search_text(self, parsed: dict, issue_text: str) -> str:
        values = [
            issue_text,
            str(parsed.get("machine_model", "")),
            str(parsed.get("issue_type", "")),
            str(parsed.get("alarm_info", "")),
            str(parsed.get("production_status", "")),
            " ".join(parsed.get("symptoms", []) or []),
            " ".join(parsed.get("parts_clues", []) or []),
        ]
        return " ".join(values).lower()

    def _score_case(self, case: dict, parsed: dict, text: str) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []

        model = str(parsed.get("machine_model", "")).upper()
        for case_model in case.get("machine_models", []):
            normalized_case_model = str(case_model).upper()
            if model and (model == normalized_case_model or model.startswith(normalized_case_model) or normalized_case_model in model):
                score += 4
                reasons.append(f"machine_model:{case_model}")
                break

        for alarm_code in case.get("alarm_codes", []):
            if alarm_code and str(alarm_code).lower() in text:
                score += 3
                reasons.append(f"alarm_code:{alarm_code}")

        for keyword in case.get("symptom_keywords", []):
            if self._contains_keyword(text, str(keyword)):
                score += 2
                reasons.append(f"symptom_keyword:{keyword}")

        issue_category = str(case.get("issue_category", "")).lower()
        parsed_issue = str(parsed.get("issue_type", "")).lower()
        if issue_category and issue_category in parsed_issue:
            score += 1
            reasons.append(f"issue_category:{issue_category}")

        production_impact = str(case.get("production_impact", "")).lower()
        if production_impact and production_impact == str(parsed.get("production_status", "")).lower():
            score += 1
            reasons.append(f"production_impact:{production_impact}")

        severity = str(case.get("severity", "")).upper()
        if severity and severity == str(parsed.get("urgency", "")).upper():
            score += 1
            reasons.append(f"severity:{severity}")

        return score, reasons

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        keyword = keyword.strip().lower()
        if not keyword:
            return False
        if re.search(r"[\u4e00-\u9fff]", keyword):
            return keyword in text
        return bool(re.search(rf"\b{re.escape(keyword)}\b", text))

    def _localized_list(self, case: dict, key: str, language: str) -> list[str]:
        localized_key = f"{key}_{language}"
        value = case.get(localized_key)
        if isinstance(value, list) and value:
            return value
        return case.get(key, [])

    def _localized_text(self, case: dict, key: str, language: str) -> str:
        localized_key = f"{key}_{language}"
        value = case.get(localized_key)
        if isinstance(value, str) and value.strip():
            return value
        return case.get(key, "")

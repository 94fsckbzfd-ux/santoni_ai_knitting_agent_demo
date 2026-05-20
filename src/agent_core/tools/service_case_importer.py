"""Excel importer for draft service cases.

The importer intentionally creates draft cases for human review. Drafts are
visible in the Service Case Library but are not used for customer-facing
matching until a reviewer promotes them into the approved/imported case file.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from zipfile import ZipFile


SPREADSHEET_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


@dataclass(frozen=True)
class ImportSummary:
    source_file: str
    output_file: str
    source_rows: int
    draft_cases: int
    skipped_rows: int


class ServiceCaseExcelImporter:
    def __init__(self, import_date: date | None = None) -> None:
        self.import_date = import_date or date.today()

    def import_file(self, xlsx_path: Path, output_path: Path) -> ImportSummary:
        rows = self.read_rows(xlsx_path)
        cases = self.build_draft_cases(rows, xlsx_path.name)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
        return ImportSummary(
            source_file=str(xlsx_path),
            output_file=str(output_path),
            source_rows=len(rows),
            draft_cases=len(cases),
            skipped_rows=max(0, len(rows) - sum(int(case.get("source_row_count", 0)) for case in cases)),
        )

    def read_rows(self, xlsx_path: Path) -> list[dict]:
        with ZipFile(xlsx_path) as archive:
            shared_strings = self._read_shared_strings(archive)
            sheet_name = self._first_sheet_name(archive)
            sheet = ET.fromstring(archive.read(sheet_name))
            raw_rows = []
            for row in sheet.findall(".//a:sheetData/a:row", SPREADSHEET_NS):
                values: dict[int, str] = {}
                for cell in row.findall("a:c", SPREADSHEET_NS):
                    column = self._column_index(cell.attrib.get("r", ""))
                    values[column] = self._cell_text(cell, shared_strings)
                if values:
                    raw_rows.append(values)

        if not raw_rows:
            return []

        headers = {index: self._clean_header(value) for index, value in raw_rows[0].items()}
        rows = []
        for raw in raw_rows[1:]:
            item = {headers[index]: self._clean_text(value) for index, value in raw.items() if headers.get(index)}
            if self._row_has_content(item):
                rows.append(item)
        return rows

    def build_draft_cases(self, rows: list[dict], source_name: str = "") -> list[dict]:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            text = self._row_text(row)
            if not text:
                continue
            profile = self._profile(text)
            grouped[profile].append(row)

        cases = []
        for index, (profile, profile_rows) in enumerate(sorted(grouped.items()), start=1):
            case = self._case_from_group(profile, profile_rows, source_name, index)
            if case:
                cases.append(case)
        return cases

    def _case_from_group(self, profile: str, rows: list[dict], source_name: str, index: int) -> dict:
        config = PROFILE_CONFIG[profile]
        model_counter = Counter(self._value(row, "machine_model") for row in rows)
        models = [model for model, _ in model_counter.most_common(6) if model]
        serials = [self._value(row, "serial") for row in rows if self._value(row, "serial")]
        wo_numbers = [self._value(row, "wo_number") for row in rows if self._value(row, "wo_number")]
        source_rows = []
        for row in rows[:20]:
            source_rows.append(
                {
                    "wo_number": self._value(row, "wo_number"),
                    "serial": self._value(row, "serial"),
                    "machine_model": self._value(row, "machine_model"),
                    "description": self._snippet(self._value(row, "intervention_description")),
                    "engineer_notes": self._snippet(self._value(row, "engeneer_notes")),
                }
            )

        case_id = f"SVC-DRAFT-{self.import_date:%Y%m%d}-{index:03d}"
        return {
            "case_id": case_id,
            "title": config["title"],
            "source": "excel_auto_import",
            "review_status": "draft_needs_review",
            "customer_visible": False,
            "machine_models": models or ["unknown"],
            "issue_category": config["issue_category"],
            "symptom_keywords": config["symptom_keywords"],
            "alarm_codes": self._alarm_codes(rows),
            "production_impact": config["production_impact"],
            "severity": config["severity"],
            "online_solvable": config["online_solvable"],
            "online_resolution_steps": config["online_resolution_steps_en"],
            "online_resolution_steps_zh": config["online_resolution_steps_zh"],
            "safety_warnings": DEFAULT_SAFETY_WARNINGS_EN,
            "safety_warnings_zh": DEFAULT_SAFETY_WARNINGS_ZH,
            "required_customer_info": DEFAULT_REQUIRED_INFO,
            "required_evidence": config["required_evidence"],
            "probable_causes": config["probable_causes"],
            "recommended_parts": self._recommended_parts(rows, config["recommended_parts"]),
            "dispatch_triggers": config["dispatch_triggers_en"],
            "dispatch_triggers_zh": config["dispatch_triggers_zh"],
            "handoff_payload": {
                "ticket_priority": config["severity"],
                "include_images": True,
                "include_online_steps_attempted": True,
                "recommended_engineer_skill": config["engineer_skill"],
            },
            "estimated_resolution_time": config["estimated_resolution_time"],
            "estimated_resolution_time_zh": config["estimated_resolution_time_zh"],
            "confidence_notes": (
                f"Auto-drafted from {len(rows)} Excel row(s). Source file: {source_name}. "
                "Requires Santoni service review before customer-facing use."
            ),
            "data_sources": [source_name] if source_name else [],
            "source_row_count": len(rows),
            "source_serials": serials[:20],
            "source_wo_numbers": wo_numbers[:20],
            "source_rows": source_rows,
            "related_cases": [],
        }

    def _read_shared_strings(self, archive: ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = []
        for item in root.findall("a:si", SPREADSHEET_NS):
            texts = [node.text or "" for node in item.findall(".//a:t", SPREADSHEET_NS)]
            strings.append("".join(texts))
        return strings

    def _first_sheet_name(self, archive: ZipFile) -> str:
        for name in archive.namelist():
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"):
                return name
        raise ValueError("No worksheet found in xlsx file.")

    def _cell_text(self, cell: ET.Element, shared_strings: list[str]) -> str:
        cell_type = cell.attrib.get("t", "")
        if cell_type == "inlineStr":
            return "".join(node.text or "" for node in cell.findall(".//a:t", SPREADSHEET_NS))
        value = cell.find("a:v", SPREADSHEET_NS)
        text = "" if value is None else value.text or ""
        if cell_type == "s" and text.isdigit():
            index = int(text)
            return shared_strings[index] if index < len(shared_strings) else ""
        return text

    def _column_index(self, cell_ref: str) -> int:
        letters = re.sub(r"[^A-Z]", "", cell_ref.upper())
        index = 0
        for letter in letters:
            index = index * 26 + (ord(letter) - ord("A") + 1)
        return index

    def _clean_header(self, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
        aliases = {
            "intervention_description": "intervention_description",
            "wo_number": "wo_number",
            "serial": "serial",
            "machine_model": "machine_model",
            "fault_category": "fault_category",
            "fault_type": "fault_type",
            "fault_component": "fault_component",
            "fault_action": "fault_action",
            "engeneer_notes": "engeneer_notes",
            "engineer_notes": "engeneer_notes",
        }
        return aliases.get(normalized, normalized)

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    def _row_has_content(self, row: dict) -> bool:
        return bool(self._value(row, "intervention_description") or self._value(row, "engeneer_notes"))

    def _row_text(self, row: dict) -> str:
        fields = [
            "intervention_description",
            "fault_category",
            "fault_type",
            "fault_component",
            "fault_action",
            "engeneer_notes",
        ]
        return " ".join(self._value(row, field) for field in fields).lower()

    def _value(self, row: dict, key: str) -> str:
        return self._clean_text(row.get(key, ""))

    def _profile(self, text: str) -> str:
        for profile, config in PROFILE_CONFIG.items():
            if any(keyword.lower() in text for keyword in config["match_keywords"]):
                return profile
        return "parts_claim"

    def _alarm_codes(self, rows: list[dict]) -> list[str]:
        text = " ".join(self._row_text(row) for row in rows)
        return sorted(set(re.findall(r"\b\d{2}\.\d{3}\b", text)))

    def _recommended_parts(self, rows: list[dict], defaults: list[str]) -> list[str]:
        found = set(defaults)
        text = " ".join(self._row_text(row) for row in rows)
        part_keywords = [
            "selector",
            "actuator",
            "display panel",
            "mainboard",
            "pcb",
            "oil pipe",
            "oil distributor",
            "needle",
            "cam",
            "sensor",
            "feeder",
            "选针器",
            "显示屏",
            "主板",
            "油箱",
            "分油嘴",
            "护针板",
            "电子眼",
            "输纱器",
        ]
        for keyword in part_keywords:
            if keyword.lower() in text:
                found.add(keyword)
        return sorted(found)

    def _snippet(self, value: str, limit: int = 180) -> str:
        clean = self._clean_text(value)
        return clean if len(clean) <= limit else f"{clean[:limit]}..."


DEFAULT_REQUIRED_INFO = [
    "machine_model",
    "serial_number",
    "symptom_description",
    "production_status",
    "photos_or_short_video",
    "online_steps_attempted",
]

DEFAULT_SAFETY_WARNINGS_EN = [
    "Stop the machine before touching mechanical, electrical, sensor, or yarn-path components.",
    "Do not bypass safety devices or repeatedly restart if collision, overcurrent, or electrical fault is suspected.",
]

DEFAULT_SAFETY_WARNINGS_ZH = [
    "接触机械、电气、传感器或纱路部件前必须先停机。",
    "如怀疑撞针、过流或电气故障，不要绕过安全保护或反复重启。",
]

PROFILE_CONFIG = {
    "selector_wrong_pattern": {
        "title": "Draft: wrong pattern or selector/actuator issue from Excel import",
        "match_keywords": ["错花", "选针", "漏选", "花型", "actuator", "selector", "pattern"],
        "issue_category": "fabric_defect",
        "symptom_keywords": ["错花", "选针器", "漏选", "花型错误", "actuator", "selector", "wrong pattern"],
        "production_impact": "quality_risk",
        "severity": "P2",
        "online_solvable": True,
        "online_resolution_steps_en": [
            "Confirm whether the defect is fixed on the same feed/position or appears randomly.",
            "Keep fabric photos and a low-speed video showing the repeat interval.",
            "Check visible actuator/selector cable seating before any restart.",
        ],
        "online_resolution_steps_zh": [
            "先确认错花是否固定出现在同一路/同一位置，还是随机出现在布面。",
            "保留能看到循环间距的布面照片和低速视频。",
            "重启前先检查可见的选针器/执行器线缆是否松动或损坏。",
        ],
        "required_evidence": ["fabric_defect_photo", "low_speed_video", "actuator_or_selector_area_photo"],
        "probable_causes": ["actuator/selector issue", "selector cable issue", "pattern/program issue"],
        "recommended_parts": ["actuator", "selector", "actuator cable"],
        "dispatch_triggers_en": ["defect repeats after safe checks", "visible selector/actuator damage", "collision noise or broken needles appear"],
        "dispatch_triggers_zh": ["安全检查后错花仍重复出现", "选针器/执行器有可见损坏", "伴随撞针、异响或坏针"],
        "engineer_skill": "selector and actuator troubleshooting",
        "estimated_resolution_time": "15-30 minutes online if cable/program issue; onsite if hardware damage is found.",
        "estimated_resolution_time_zh": "如为线缆或程序问题，在线约 15-30 分钟；如硬件损坏，需要现场处理。",
    },
    "system_display": {
        "title": "Draft: software, display, PCB, or control panel fault from Excel import",
        "match_keywords": ["程序", "屏", "显示", "触摸", "主板", "pcb", "软件", "白屏", "死机", "日期", "software", "screen", "display"],
        "issue_category": "electrical",
        "symptom_keywords": ["程序错乱", "白屏", "显示屏", "触摸无反应", "主板", "PCB", "software", "display"],
        "production_impact": "stopped",
        "severity": "P1",
        "online_solvable": False,
        "online_resolution_steps_en": [
            "Record the screen status, software version, and whether touch input responds.",
            "Power-cycle once only if allowed by customer procedure.",
            "Do not flash software or replace boards without Santoni confirmation.",
        ],
        "online_resolution_steps_zh": [
            "记录屏幕状态、软件版本，以及触摸屏是否有反应。",
            "在客户流程允许且安全的前提下，只做一次断电重启确认。",
            "未经 Santoni 确认，不要自行刷机或更换主板/显示屏。",
        ],
        "required_evidence": ["screen_photo", "software_version_photo", "short_video_of_touch_response"],
        "probable_causes": ["software issue", "display panel fault", "mainboard/PCB fault"],
        "recommended_parts": ["display panel", "mainboard", "PCB"],
        "dispatch_triggers_en": ["screen remains white", "touch panel does not respond", "software or PCB fault is suspected"],
        "dispatch_triggers_zh": ["屏幕持续白屏", "触摸屏无反应", "怀疑软件、主板或 PCB 故障"],
        "engineer_skill": "software, display, and PCB troubleshooting",
        "estimated_resolution_time": "Remote triage 10-20 minutes; onsite or parts replacement likely if PCB/display is suspected.",
        "estimated_resolution_time_zh": "远程判断约 10-20 分钟；如怀疑主板或显示屏，通常需要现场或备件处理。",
    },
    "oil_leak": {
        "title": "Draft: oil leak or lubrication issue from Excel import",
        "match_keywords": ["漏油", "油箱", "油排", "分油", "油嘴", "油泵", "oil", "lubric"],
        "issue_category": "mechanical",
        "symptom_keywords": ["漏油", "油箱", "油排", "分油嘴", "油泵", "oil leak"],
        "production_impact": "quality_risk",
        "severity": "P2",
        "online_solvable": True,
        "online_resolution_steps_en": [
            "Stop and clean the visible oil area enough to identify the leak point.",
            "Take photos of the oil tank, distributor/nozzle, pipe, and nearby screws.",
            "Do not continue production if oil may contaminate fabric or reach electrical parts.",
        ],
        "online_resolution_steps_zh": [
            "先停机并清洁可见油污区域，确认漏油点。",
            "拍摄油箱、分油嘴、油管和周边螺丝位置。",
            "如油污可能污染布面或接近电气部件，不要继续生产。",
        ],
        "required_evidence": ["leak_point_photo", "oil_tank_or_distributor_photo", "short_video_after_idle_run"],
        "probable_causes": ["oil distributor/nozzle leak", "oil pipe issue", "lubrication fitting failure"],
        "recommended_parts": ["oil distributor", "oil nozzle", "oil pipe"],
        "dispatch_triggers_en": ["leak continues after cleaning", "oil reaches electrical components", "cracked distributor/nozzle/pipe is visible"],
        "dispatch_triggers_zh": ["清洁后仍持续漏油", "油污接近电气部件", "分油嘴、油管或相关部件有可见裂纹"],
        "engineer_skill": "lubrication system troubleshooting",
        "estimated_resolution_time": "10-20 minutes online to confirm source; onsite/parts if leak persists.",
        "estimated_resolution_time_zh": "在线确认漏油源约 10-20 分钟；持续漏油通常需要现场或备件处理。",
    },
    "needle_crash": {
        "title": "Draft: needle crash, broken needle, cam, or mechanical collision from Excel import",
        "match_keywords": ["坏针", "撞针", "打针", "护针板", "三角", "开针", "断裂", "needle", "cam"],
        "issue_category": "mechanical",
        "symptom_keywords": ["坏针", "撞针", "打针", "护针板", "三角", "断裂", "needle crash", "cam"],
        "production_impact": "stopped",
        "severity": "P1",
        "online_solvable": False,
        "online_resolution_steps_en": [
            "Stop the machine immediately and do not continue production.",
            "Keep photos of damaged needles, cam, through-plate, latch opener, or alarm screen.",
            "Prepare affected feed/position and whether collision noise occurred.",
        ],
        "online_resolution_steps_zh": [
            "立即停机，不要继续强行生产。",
            "保留坏针、三角、护针板、开针钩或报警界面照片。",
            "准备发生位置/路数，以及是否有撞击异响。",
        ],
        "required_evidence": ["alarm_screen_photo", "damaged_part_photo", "short_video_if_available"],
        "probable_causes": ["broken needle", "cam damage", "mechanical collision", "incorrect mechanical position"],
        "recommended_parts": ["needles", "cam", "through-plate", "latch opener"],
        "dispatch_triggers_en": ["visible mechanical damage", "repeated collision noise", "customer cannot safely clear the machine"],
        "dispatch_triggers_zh": ["可见机械损坏", "重复出现撞击异响", "客户无法安全清理机器"],
        "engineer_skill": "mechanical collision and needle path repair",
        "estimated_resolution_time": "Online triage only; onsite inspection is usually required.",
        "estimated_resolution_time_zh": "仅适合在线判断风险，通常需要现场检查。",
    },
    "sensor_feeder": {
        "title": "Draft: sensor, electronic eye, feeder, or learning issue from Excel import",
        "match_keywords": ["电子眼", "输纱器", "传感器", "学习", "sensor", "feeder"],
        "issue_category": "calibration",
        "symptom_keywords": ["电子眼", "输纱器", "传感器", "学习", "sensor", "feeder"],
        "production_impact": "running",
        "severity": "P3",
        "online_solvable": True,
        "online_resolution_steps_en": [
            "Confirm whether this is a retrofit/install task or an alarm after production starts.",
            "Check sensor/feeder connection and whether signal changes when yarn passes.",
            "Run learning/calibration only if the customer engineer is trained.",
        ],
        "online_resolution_steps_zh": [
            "确认这是改装/安装任务，还是生产后出现的传感器或输纱器报警。",
            "检查电子眼/输纱器连接，并确认纱线经过时信号是否变化。",
            "只有客户工程师受过培训时，才执行学习/校准步骤。",
        ],
        "required_evidence": ["sensor_wiring_photo", "panel_signal_photo", "short_video_of_signal_change"],
        "probable_causes": ["sensor learning not completed", "sensor wiring issue", "feeder signal issue"],
        "recommended_parts": ["sensor", "feeder", "sensor cable"],
        "dispatch_triggers_en": ["signal does not change", "customer is not trained for calibration", "alarm repeats after calibration"],
        "dispatch_triggers_zh": ["信号无变化", "客户未受训无法校准", "校准后报警仍重复"],
        "engineer_skill": "sensor learning and feeder support",
        "estimated_resolution_time": "20-40 minutes online if wiring and learning are straightforward; onsite if retrofit is unclear.",
        "estimated_resolution_time_zh": "如接线和学习流程清楚，在线约 20-40 分钟；改装状态不清时建议现场。",
    },
    "parts_claim": {
        "title": "Draft: parts claim, broken delivered part, or warranty handling from Excel import",
        "match_keywords": ["索赔", "配件", "交付", "更换", "claim", "warranty", "delivery"],
        "issue_category": "other",
        "symptom_keywords": ["索赔", "配件损坏", "交付配件损坏", "重新交付", "claim", "warranty"],
        "production_impact": "unknown",
        "severity": "P3",
        "online_solvable": False,
        "online_resolution_steps_en": [
            "Collect clear photos of the damaged part, label, packaging, and machine serial number.",
            "Confirm whether the machine is stopped or this is a spare-part claim only.",
            "Do not install visibly damaged parts.",
        ],
        "online_resolution_steps_zh": [
            "收集损坏配件、标签、包装和机器序列号的清晰照片。",
            "确认机器是否停机，还是单纯备件索赔。",
            "不要安装肉眼可见损坏的配件。",
        ],
        "required_evidence": ["damaged_part_photo", "part_label_photo", "machine_nameplate_photo"],
        "probable_causes": ["part damaged before or during delivery", "warranty replacement request", "wrong replacement part"],
        "recommended_parts": [],
        "dispatch_triggers_en": ["machine is stopped and part replacement is urgent", "part identity is unclear", "onsite confirmation is needed"],
        "dispatch_triggers_zh": ["机器停机且备件更换紧急", "配件身份不明确", "需要现场确认后才能处理"],
        "engineer_skill": "warranty and spare parts claim support",
        "estimated_resolution_time": "Online information collection 5-10 minutes; fulfillment depends on parts process.",
        "estimated_resolution_time_zh": "在线收集信息约 5-10 分钟；后续时效取决于备件流程。",
    },
}

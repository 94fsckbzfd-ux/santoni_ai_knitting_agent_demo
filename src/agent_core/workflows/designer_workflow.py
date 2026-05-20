"""Designer workflow skeleton."""

from agent_core.agents.digital_twin_agent import DigitalTwinAgent
from agent_core.agents.translation_agent import TranslationAgent
from agent_core.agents.understanding_agent import UnderstandingAgent


class DesignerWorkflow:
    def __init__(self) -> None:
        self.understanding_agent = UnderstandingAgent()
        self.translation_agent = TranslationAgent()
        self.digital_twin_agent = DigitalTwinAgent()

    def run(self, brief: str, language: str = "en", image_context: dict | None = None) -> dict:
        parsed_brief = self.understanding_agent.parse_design_brief(brief, language, image_context)
        return self.run_prepared(brief, language, image_context, parsed_brief)

    def run_prepared(self, brief: str, language: str = "en", image_context: dict | None = None, parsed_brief: dict | None = None) -> dict:
        parsed_brief = parsed_brief or self.understanding_agent.parse_design_brief(brief, language, image_context)
        design_spec = self.translation_agent.run(brief, language, image_context, parsed_brief)
        twin_result = self.digital_twin_agent.run(design_spec, language, image_context, parsed_brief)
        result = {"understanding": parsed_brief, "design_spec": design_spec, "digital_twin": twin_result}
        if image_context:
            result["image_understanding"] = image_context
        return result

    def prepare(
        self,
        brief: str,
        language: str = "en",
        image_context: dict | None = None,
        memory: dict | None = None,
        ready_to_generate: bool = False,
    ) -> dict:
        parsed = self.understanding_agent.parse_design_brief(brief, language, image_context)
        parsed = self._enrich_from_user_text(parsed, brief)
        merged = self._merge_memory(memory or {}, parsed)
        missing = self._required_missing(merged)
        if not ready_to_generate:
            missing = list(dict.fromkeys(missing + self._designer_depth_missing(merged)))
            if not missing:
                missing = ["generation_confirmation"]
        questions = self._questions_for_missing(missing, language)
        return {
            "ready": len(missing) == 0,
            "understanding": merged,
            "known_info": self._known_info(merged),
            "missing_info": missing,
            "questions": questions,
            "memory": merged,
        }

    def _merge_memory(self, memory: dict, parsed: dict) -> dict:
        merged = dict(memory)
        for key, value in parsed.items():
            if key in {"parser_status", "parser_error"}:
                merged[key] = value
                continue
            if key in merged and self._is_less_specific(key, value, merged.get(key)):
                continue
            if self._has_value(value):
                merged[key] = value
            elif key not in merged:
                merged[key] = value
        return merged

    def _is_less_specific(self, key: str, value, existing) -> bool:
        generic_values = {
            "product_category": {"针织服装", "通用针织产品", "garment", "knitted garment", "general knitted product", "未知"},
            "target_user": {"运动爱好者", "未指定", "unknown", "sports consumer", "未知"},
            "use_case": {"外观样", "未指定", "unknown", "未知"},
        }
        if key in generic_values and str(value).strip() in generic_values[key] and self._has_value(existing):
            return True
        return False

    def _has_value(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip()) and value.strip() not in {"未指定", "unknown", "未知", "n/a"}
        if isinstance(value, list):
            return any(self._has_value(item) for item in value)
        return True

    def _required_missing(self, parsed: dict) -> list[str]:
        missing = []
        if not self._has_value(parsed.get("product_category")):
            missing.append("product_category")
        if not self._has_value(parsed.get("target_user")):
            missing.append("target_user")
        if not self._has_value(parsed.get("use_case")):
            missing.append("use_case")
        if not self._has_value(parsed.get("functional_requirements")):
            missing.append("functional_requirements")
        return missing

    def _known_info(self, parsed: dict) -> dict:
        keys = [
            "product_category",
            "target_user",
            "use_case",
            "style_keywords",
            "functional_requirements",
            "material_preferences",
            "constraints",
            "brand_line",
            "fit_and_size",
            "sample_type",
            "sample_priority",
            "yarn_status",
        ]
        return {key: parsed.get(key) for key in keys if self._has_value(parsed.get(key))}

    def _questions_for_missing(self, missing: list[str], language: str) -> list[str]:
        labels = {
            "product_category": ("What product are we designing: top, leggings, socks, underwear, or something else?", "这次要设计什么产品：上衣、裤子、袜子、内衣，还是其他？"),
            "target_user": ("Who is the target user and market level?", "目标用户是谁？面向入门、中端还是专业运动系列？"),
            "use_case": ("What is the main use case or sport scenario?", "主要使用场景是什么？比如跑步、瑜伽、户外、日常训练？"),
            "functional_requirements": ("Which functions matter most: quick dry, warmth, breathability, compression, support, cost, or hand feel?", "最重要的功能是什么：快干、保暖、透气、压缩支撑、成本，还是手感？"),
            "price_band": ("What target price band or cost ceiling should we design around?", "目标价格带或成本上限是多少？"),
            "brand_line": ("Which brand line should this fit: entry, mid, premium, or performance?", "这款产品属于入门、中端、高端，还是专业运动系列？"),
            "aesthetic_direction": ("What visual direction do you want: minimal, technical, outdoor rugged, premium, or fashion-forward?", "你希望视觉风格偏极简、科技感、户外机能、高端质感，还是更时尚？"),
            "fit_and_size": ("What fit and size range should we target?", "版型和尺码范围怎么定？"),
            "success_metric": ("What would make this design successful: cost, sample speed, comfort, performance, or differentiation?", "你判断这个设计成功的标准是什么：成本、打样速度、舒适度、运动性能，还是差异化？"),
            "generation_confirmation": (
                "I have enough to draft a first product development brief. Should I generate it now or keep exploring details?",
                "我已经有足够信息起草第一版产品开发方案。现在生成，还是继续补充细节？",
            ),
        }
        return [labels[item][1 if language == "zh" else 0] for item in missing[:3]]

    def _designer_depth_missing(self, parsed: dict) -> list[str]:
        missing = []
        constraints = " ".join(str(item) for item in parsed.get("constraints", []))
        style = " ".join(str(item) for item in parsed.get("style_keywords", []))
        if "成本" in constraints or "cost" in constraints.lower():
            missing.append("price_band")
        if not self._has_value(parsed.get("brand_line")):
            missing.append("brand_line")
        if not style:
            missing.append("aesthetic_direction")
        if not self._has_value(parsed.get("fit_and_size")):
            missing.append("fit_and_size")
        if not self._has_value(parsed.get("sample_priority")):
            missing.append("success_metric")
        return missing

    def _enrich_from_user_text(self, parsed: dict, brief: str) -> dict:
        text = brief.lower()
        enriched = dict(parsed)
        if "专业" in brief or "performance" in text:
            enriched["brand_line"] = "专业运动系列"
        elif "高端" in brief or "premium" in text:
            enriched["brand_line"] = "高端系列"
        elif "中端" in brief or "mid" in text:
            enriched["brand_line"] = "中端系列"
        elif "入门" in brief or "entry" in text:
            enriched["brand_line"] = "入门系列"

        import re

        size_match = re.search(r"(\d{2,3})\s*[-~到至]\s*(\d{2,3})", brief)
        if size_match:
            enriched["fit_and_size"] = f"{size_match.group(1)}-{size_match.group(2)}"

        if "外观样" in brief:
            enriched["sample_type"] = "外观样"
        if "功能样" in brief or "量产" in brief:
            enriched["sample_type"] = "功能样 / 量产接近样"
        if "快速" in brief or "最快" in brief or "快" in brief:
            enriched["sample_priority"] = "快速出样"
        if "纱线没有确认" in brief or "纱线未确认" in brief:
            enriched["yarn_status"] = "未确认，需要按现货快干纱线假设"
        return enriched

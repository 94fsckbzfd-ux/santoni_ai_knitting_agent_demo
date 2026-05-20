"""Translation Agent skeleton."""

import json

from agent_core.language import choose
from agent_core.llm_client import LLMClient
from agent_core.schemas import KNITTING_RECOMMENDATION_SCHEMA


class TranslationAgent:
    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, brief: str, language: str = "en", image_context: dict | None = None, parsed_brief: dict | None = None) -> dict:
        parsed_brief = parsed_brief or {}
        generated, status = self.llm.generate_json(
            schema_name="knitting_recommendation",
            schema=KNITTING_RECOMMENDATION_SCHEMA,
            system_prompt=(
                "You are Santoni's Translation Agent for knitting product development. "
                "Generate a practical knitting recommendation from a structured design brief. "
                "Use Santoni and seamless knitting business language. Keep claims realistic. "
                "If the user language is zh, write user-facing values in Chinese; otherwise write English."
            ),
            user_prompt=json.dumps(
                {
                    "language": language,
                    "original_brief": brief,
                    "parsed_brief": parsed_brief,
                    "image_context": image_context or {},
                    "available_machine_examples": ["Santoni SM8-TOP2V", "Santoni XT-Med / sock platform"],
                },
                ensure_ascii=False,
            ),
        )
        if generated and "_llm_error" not in generated:
            generated["parser_status"] = parsed_brief.get("parser_status", "unknown")
            generated["reasoning_status"] = status
            generated["source_brief"] = brief
            if image_context:
                generated["image_reference"] = choose(
                    language,
                    "Image reference used for silhouette, texture, and ventilation-zone hints.",
                    "已参考上传图片中的版型、纹理和透气区域线索。",
                )
            return generated

        category = parsed_brief.get("product_category") or choose(language, "seamless running top", "无缝跑步上衣")
        requirements = parsed_brief.get("functional_requirements", [])
        materials = parsed_brief.get("material_preferences", [])
        category_text = str(category).lower()

        yarn = materials[0] if materials else choose(language, "Coolmax cotton blend, 28G", "Coolmax 棉混纺，28G")
        machine = "Santoni SM8-TOP2V"
        if any(word in category_text for word in ["sock", "袜"]):
            machine = "Santoni XT-Med / sock platform"
            yarn = materials[0] if materials else choose(language, "polyamide elastane blend", "锦纶氨纶混纺")
        elif any(word in category_text for word in ["legging", "裤"]):
            yarn = materials[0] if materials else choose(language, "nylon spandex blend, high stretch", "锦纶氨纶高弹混纺")
        elif any(word in category_text for word in ["yoga", "瑜伽"]):
            yarn = materials[0] if materials else choose(language, "soft nylon spandex blend", "柔软锦纶氨纶混纺")

        structure = choose(language, "seamless body mapping", "无缝人体工学分区")
        if any("breath" in str(item).lower() or "透气" in str(item) for item in requirements):
            structure = choose(language, "mesh ventilation zones with seamless body mapping", "无缝人体工学分区 + 网眼透气结构")
        if any("stretch" in str(item).lower() or "弹" in str(item) for item in requirements):
            structure = choose(language, "high-stretch rib support with seamless body mapping", "高弹罗纹支撑 + 无缝人体工学分区")

        result = {
            "product_category": category,
            "target_user": parsed_brief.get("target_user", choose(language, "Decathlon sports consumer", "迪卡侬运动消费者")),
            "use_case": parsed_brief.get("use_case", choose(language, "sports performance", "运动性能场景")),
            "style_direction": ", ".join(parsed_brief.get("style_keywords", [])) or choose(language, "lightweight, breathable, minimal seams", "轻量、透气、少缝线"),
            "functional_requirements": requirements,
            "yarn": yarn,
            "knit_structure": structure,
            "machine": machine,
            "parser_status": parsed_brief.get("parser_status", "local_static"),
            "reasoning_status": status,
            "source_brief": brief,
        }

        if image_context:
            result["image_reference"] = choose(
                language,
                "Image reference used for silhouette, texture, and ventilation-zone hints.",
                "已参考上传图片中的版型、纹理和透气区域线索。",
            )

        return result

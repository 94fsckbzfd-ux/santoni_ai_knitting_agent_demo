"""Digital Twin Agent skeleton."""

import json

from agent_core.language import choose
from agent_core.llm_client import LLMClient
from agent_core.schemas import DIGITAL_TWIN_PLAN_SCHEMA


class DigitalTwinAgent:
    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, design_spec: dict, language: str = "en", image_context: dict | None = None, parsed_brief: dict | None = None) -> dict:
        parsed_brief = parsed_brief or {}
        generated, status = self.llm.generate_json(
            schema_name="digital_twin_plan",
            schema=DIGITAL_TWIN_PLAN_SCHEMA,
            system_prompt=(
                "You are Santoni's Digital Twin Agent. Generate a simulated SWS 3D and sampling plan. "
                "Use mock estimates, but make them consistent with product category, yarn, machine, and function. "
                "Do not claim an actual SWS file was produced; this is a demo simulation."
            ),
            user_prompt=json.dumps(
                {
                    "language": language,
                    "parsed_brief": parsed_brief,
                    "design_spec": design_spec,
                    "image_context": image_context or {},
                },
                ensure_ascii=False,
            ),
        )
        if generated and "_llm_error" not in generated:
            generated["reasoning_status"] = status
            return generated

        category = str(design_spec.get("product_category", "")).lower()
        requirements = [str(item).lower() for item in parsed_brief.get("functional_requirements", [])]
        preview = choose(language, "Parametric 3D preview generated with breathable mesh zones.", "已生成参数化 3D 预览，包含腋下和背部透气网眼区域。")
        if image_context:
            preview = choose(
                language,
                "Parametric 3D preview generated using image reference cues for silhouette, texture, and mesh placement.",
                "已结合图片参考线索生成参数化 3D 预览，包括版型、纹理和网眼位置。",
            )

        sample_time = choose(language, "2.5 days", "2.5 天")
        unit_cost = choose(language, "USD 12.40", "12.40 美元/件")
        if "sock" in category or "袜" in category:
            sample_time = choose(language, "1.5 days", "1.5 天")
            unit_cost = choose(language, "USD 2.10", "2.10 美元/双")
        elif "legging" in category or "裤" in category:
            sample_time = choose(language, "3.5 days", "3.5 天")
            unit_cost = choose(language, "USD 18.80", "18.80 美元/件")
        elif any("premium" in item or "soft" in item or "柔软" in item for item in requirements):
            unit_cost = choose(language, "USD 14.60", "14.60 美元/件")

        return {
            "sws_project_id": "SWS-DEMO-0001",
            "preview": preview,
            "parameter_package": {
                "gauge": "28G",
                "machine": design_spec.get("machine", "Santoni SM8-TOP2V"),
                "structure": design_spec.get("knit_structure", choose(language, "seamless mapped structure", "无缝分区结构")),
            },
            "estimated_sample_time": sample_time,
            "estimated_unit_cost": unit_cost,
            "estimated_yield": "98.8%",
            "risks": [
                choose(language, "Colorfastness test required", "需要做色牢度测试"),
                choose(language, "Mesh zones need tension validation", "网眼区域需要验证纱线张力稳定性"),
            ],
            "next_actions": [
                choose(language, "Confirm target size range and colorway", "确认目标尺码段和配色"),
                choose(language, "Run first sample tension validation", "进行首件样衣张力验证"),
            ],
            "missing_info": parsed_brief.get("missing_info", []),
            "reasoning_status": status,
        }

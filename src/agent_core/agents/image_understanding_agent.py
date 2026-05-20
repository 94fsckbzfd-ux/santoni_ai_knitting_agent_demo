"""Mock image understanding service.

This is intentionally designed as a shared service rather than a workflow-specific
agent. Future GPT Vision or dedicated CV models can replace this implementation
without changing the Main Agent contract.
"""

from __future__ import annotations

from agent_core.language import choose


class ImageUnderstandingAgent:
    def run(self, attachments: list[dict], workflow_hint: str, language: str = "en") -> dict:
        if not attachments:
            return {}

        first = attachments[0]
        file_name = first.get("name") or first.get("file_name") or choose(language, "uploaded image", "上传图片")

        if workflow_hint == "service":
            return {
                "image_count": len(attachments),
                "primary_image": file_name,
                "image_type": choose(language, "machine alarm / machine component photo", "机器报警 / 设备部件照片"),
                "detected_signals": [
                    choose(language, "possible yarn tension alarm on machine panel", "疑似机器面板纱线张力报警"),
                    choose(language, "onsite troubleshooting may be required", "可能需要现场排查"),
                    choose(language, "spare-part check recommended before dispatch", "派工前建议核对备件"),
                ],
                "workflow_hint": "service",
                "confidence": "mock-high",
            }

        return {
            "image_count": len(attachments),
            "primary_image": file_name,
            "image_type": choose(language, "garment / fabric reference image", "服装 / 面料参考图"),
            "detected_signals": [
                choose(language, "seamless sportswear silhouette", "无缝运动服轮廓"),
                choose(language, "breathable mesh or texture detail", "透气网眼或纹理细节"),
                choose(language, "fitted performance style", "贴身运动性能风格"),
            ],
            "workflow_hint": "designer",
            "confidence": "mock-high",
        }


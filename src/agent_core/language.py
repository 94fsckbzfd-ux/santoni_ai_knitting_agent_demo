"""Language helpers for bilingual demo responses."""

from __future__ import annotations

import re

CHINESE_TEXT_RE = re.compile(r"[\u4e00-\u9fff]")


def detect_language(text: str) -> str:
    """Return zh when Chinese characters are present, otherwise en."""
    return "zh" if CHINESE_TEXT_RE.search(text or "") else "en"


def choose(language: str, english: str, chinese: str) -> str:
    return chinese if language == "zh" else english


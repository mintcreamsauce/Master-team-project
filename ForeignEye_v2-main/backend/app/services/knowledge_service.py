"""
Knowledge Service

High-cost definition stage for newly discovered concepts.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional
from textwrap import dedent

from openai import OpenAI


class KnowledgeService:
    """Service responsible for defining concepts via OpenRouter."""

    MODEL_DEFAULT = "anthropic/claude-3-haiku"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found. Please set it before running the ETL pipeline.")

        self.model = model or self.MODEL_DEFAULT
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://techexplained.project",
                "X-Title": "TechExplained Project"
            }
        )

    def define_concept(self, concept_name: str, article_summary: str) -> Dict:
        """Retrieve a structured definition for the given concept name within article context."""
        prompt = self._build_prompt(concept_name, article_summary)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200
        )

        if not response or not response.choices:
            raise RuntimeError("Empty response from OpenRouter while defining concept")

        ai_content = response.choices[0].message.content.strip()
        try:
            definition = json.loads(ai_content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to parse concept definition JSON: {exc}")

        return self._validate_definition(definition, concept_name)

    def _build_prompt(self, concept_name: str, article_summary: str) -> str:
        return dedent(
            f"""
            당신은 IT 및 기술 분야의 전문 애널리스트입니다.
            다음은 '{concept_name}'라는 개념이 언급된 기사의 요약입니다.

            [기사 요약]
            {article_summary.strip() if article_summary else "(요약 없음)"}
            [기사 요약 끝]

            오직 위 [기사 요약]의 **문맥에 부합하는** '{concept_name}' 개념에 대해서만,
            다음 JSON 형식으로 정의를 반환해주세요.
            만약 문맥과 관련 없는 일반 명사(예: '과일'이나 '배')라면, "parent_concepts", "child_concepts", "related_concepts"를 모두 빈 배열 []로 반환하세요.

            {{
              "description_ko": "문맥에 맞는 개념의 핵심 정의 (3문장 요약)",
              "parent_concepts": ["문맥에 맞는 상위 개념(더 넓은 범주) 리스트"],
              "child_concepts": ["문맥에 맞는 하위 개념(구체적인 분야) 리스트"],
              "related_concepts": ["문맥에 맞는 동등한 수준의 관련 개념 리스트"]
            }}
            """
        ).strip()

    def _validate_definition(self, definition: Dict, concept_name: str) -> Dict:
        required_keys = {"description_ko", "parent_concepts", "child_concepts", "related_concepts"}
        missing = required_keys - definition.keys()
        if missing:
            raise RuntimeError(f"Definition for '{concept_name}' is missing keys: {sorted(missing)}")

        for key in ("parent_concepts", "child_concepts", "related_concepts"):
            value = definition.get(key)
            if not isinstance(value, list):
                raise RuntimeError(f"Definition field '{key}' must be a list")
            cleaned = []
            for item in value:
                if isinstance(item, str):
                    text = item.strip()
                    if text:
                        cleaned.append(text)
            definition[key] = cleaned

        description = definition.get("description_ko", "").strip()
        if not description:
            raise RuntimeError(f"Definition for '{concept_name}' is missing description_ko")
        definition["description_ko"] = description

        return definition

"""
AI 분석기

OpenRouter API를 사용하여 기사를 분석하고 개념을 추출합니다.
"""

import os
import json
import re
from typing import Optional, Dict, List
from openai import OpenAI


class AIAnalyzer:
    """AI 기반 기사 분석 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-3-haiku"):
        """
        Args:
            api_key (str, optional): OpenRouter API 키. None이면 환경 변수에서 로드
            model (str): 사용할 AI 모델 (기본값: claude-3-haiku)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found. Please set it in .env file.")
        
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://techexplained.project",
                "X-Title": "TechExplained Project"
            }
        )
    
    def analyze_article(self, article_text: str) -> Optional[Dict]:
        """
        기사 분석 및 개념 추출
        
        Args:
            article_text (str): 분석할 기사 텍스트
            
        Returns:
            dict: {
                'title_ko': str,
                'summary_ko': str,
                'concept_names': [str]
            } or None on failure
        """
        # 입력 검증
        if not article_text or len(article_text.strip()) < 100:
            print(f"     ✗ Article text too short (length: {len(article_text) if article_text else 0})")
            return None
        
        # 프롬프트 생성
        prompt = self._build_prompt(article_text)
        
        try:
            print("     ⟳ Sending request to OpenRouter AI...")
            print(f"     → Model: {self.model}")
            print(f"     → Article length: {len(article_text)} chars")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=3000
            )
            
            if not response or not response.choices:
                print("     ✗ Empty response from OpenRouter API")
                return None
            
            ai_response = response.choices[0].message.content.strip()
            print(f"     ✓ Received response ({len(ai_response)} chars)")
            
            # JSON 파싱
            analysis_result = self._parse_response(ai_response)

            if analysis_result:
                print(f"     ✓ AI analysis complete!")
                print(f"     ✓ Title (ko): {analysis_result['title_ko'][:50]}...")
                print(f"     ✓ Summary length: {len(analysis_result['summary_ko'])} chars")
                print(f"     ✓ Concepts detected: {len(analysis_result['concept_names'])}")

            return analysis_result
        
        except Exception as e:
            print(f"     ✗ Error during AI analysis: {type(e).__name__}: {e}")
            return None
    
    def _build_prompt(self, article_text: str) -> str:
        """
        AI 분석 프롬프트 생성
        
        Args:
            article_text (str): 기사 텍스트
            
        Returns:
            str: 프롬프트
        """
        # 텍스트 길이 제한 (3000자)
        truncated_text = article_text[:3000]
        
        prompt = f"""
You are 'TechExplained', an expert technology scout.
Analyse the news article below and return ONLY a valid JSON object. No commentary, markdown, or extra text.

Your tasks:
1. Translate the article title into natural Korean (title_ko).
2. Provide a detailed Korean summary in 3-5 sentences that captures the article's key developments, 주요 인물/기업, 그리고 영향 (summary_ko).
3. List up to five distinct technology-related concepts that are explicitly mentioned in the article. Provide only their canonical names (prefer English terms). Do not invent new concepts. Output them as an array "concept_names".

Article text:
{truncated_text}

Return JSON exactly in this shape:
{{
  "title_ko": "한국어 제목",
  "summary_ko": "한국어 요약",
  "concept_names": ["Concept 1", "Concept 2"]
}}

Important rules:
- Respond with JSON only.
- If fewer than five valid concepts exist, return only the ones that are explicitly mentioned.
- Remove duplicates and keep the order they appear in the article.
"""
        
        return prompt
    
    def _parse_response(self, ai_response: str) -> Optional[Dict]:
        """
        AI 응답 파싱
        
        Args:
            ai_response (str): AI 응답 텍스트
            
        Returns:
            dict: 파싱된 분석 결과. 실패 시 None
        """
        # 방법 1: 직접 JSON 파싱
        try:
            analysis_result = json.loads(ai_response)
            print(f"     ✓ Direct JSON parse successful!")
            return self._validate_analysis(analysis_result)
        except json.JSONDecodeError:
            print("     → Direct parse failed, trying regex extraction...")
        
        # 방법 2: 정규식으로 JSON 추출
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        
        if not json_match:
            print(f"     ✗ No JSON object found in AI response")
            self._save_debug_response(ai_response)
            return None
        
        json_string = json_match.group(0)
        
        try:
            analysis_result = json.loads(json_string)
            return self._validate_analysis(analysis_result)
        
        except json.JSONDecodeError as e:
            print(f"     ✗ Failed to parse JSON: {e}")
            self._save_debug_response(json_string, prefix="debug_json")
            return None
    
    def _validate_analysis(self, analysis: Dict) -> Optional[Dict]:
        """
        분석 결과 검증
        
        Args:
            analysis (dict): 분석 결과
            
        Returns:
            dict: 검증된 결과. 실패 시 None
        """
        required_fields = ['title_ko', 'summary_ko', 'concept_names']
        missing_fields = [field for field in required_fields if field not in analysis]
        
        if missing_fields:
            print(f"     ✗ Missing required fields: {missing_fields}")
            return None
        
        if not isinstance(analysis.get('concept_names'), list):
            print("     ✗ 'concept_names' must be a list")
            return None
        
        # concept_names 정리
        cleaned_names = []
        for name in analysis['concept_names']:
            if isinstance(name, str):
                name = name.strip()
                if name:
                    cleaned_names.append(name)
        
        if not cleaned_names:
            print("     ✗ No valid concept names found")
            return None
        
        seen = set()
        unique_names = []
        for name in cleaned_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
            if len(unique_names) == 10:
                break

        analysis['concept_names'] = unique_names

        return analysis
    
    def _save_debug_response(self, content: str, prefix: str = "debug_response"):
        """
        디버그용으로 응답 저장
        
        Args:
            content (str): 저장할 내용
            prefix (str): 파일명 접두사
        """
        try:
            filename = f'{prefix}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"     → Debug response saved to {filename}")
        except Exception:
            pass
    
    def analyze_concept_relations(self, concept_names: List[str]) -> Optional[Dict]:
        """
        개념 간 관계 분석
        
        Args:
            concept_names (List[str]): 분석할 개념 이름 목록
            
        Returns:
            dict: {
                'relations': [
                    {'from': str, 'to': str, 'relation_type': str},
                    ...
                ]
            } or None on failure
        """
        # 입력 검증
        if not concept_names or len(concept_names) < 2:
            print(f"     ✗ Need at least 2 concepts to analyze relations (got {len(concept_names)})")
            return None
        
        # 프롬프트 생성
        prompt = self._build_relation_prompt(concept_names)
        
        try:
            print(f"     ⟳ Analyzing relations for {len(concept_names)} concepts...")
            print(f"     → Model: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=4000
            )
            
            if not response or not response.choices:
                print("     ✗ Empty response from OpenRouter API")
                return None
            
            ai_response = response.choices[0].message.content.strip()
            print(f"     ✓ Received response ({len(ai_response)} chars)")
            
            # JSON 파싱
            relation_result = self._parse_relation_response(ai_response)
            
            if relation_result:
                relations_count = len(relation_result.get('relations', []))
                print(f"     ✓ AI relation analysis complete!")
                print(f"     ✓ Relations detected: {relations_count}")
            
            return relation_result
        
        except Exception as e:
            print(f"     ✗ Error during relation analysis: {type(e).__name__}: {e}")
            return None
    
    def _build_relation_prompt(self, concept_names: List[str]) -> str:
        """
        개념 관계 분석 프롬프트 생성
        
        Args:
            concept_names (List[str]): 개념 이름 목록
            
        Returns:
            str: 프롬프트
        """
        concepts_json = json.dumps(concept_names, ensure_ascii=False)
        
        prompt = f"""
You are a knowledge graph expert. Given a list of technology-related concepts, analyze and find all valid pairwise relationships between them.

Your task:
1. For each pair of concepts, determine if there is a meaningful relationship.
2. Define the relationship type using one of these categories:
   - "IS_A_TYPE_OF": Concept A is a specific type or subcategory of Concept B
   - "USED_IN": Concept A is used in or applied within Concept B
   - "RELATED_TO": Concepts are semantically related but don't fit other categories
   - "ENABLES": Concept A enables or makes possible Concept B
   - "PART_OF": Concept A is a component or part of Concept B

3. Only include relationships that are clearly valid and meaningful.
4. Avoid redundant relationships (e.g., if A→B exists, don't add B→A unless it's a different relation type).

Concept List:
{concepts_json}

Return ONLY a valid JSON object in this exact shape (no markdown, no commentary):
{{
  "relations": [
    {{"from": "Concept Name A", "to": "Concept Name B", "relation_type": "IS_A_TYPE_OF"}},
    {{"from": "Concept Name C", "to": "Concept Name D", "relation_type": "USED_IN"}}
  ]
}}

Important rules:
- Use exact concept names from the input list.
- relation_type must be one of: IS_A_TYPE_OF, USED_IN, RELATED_TO, ENABLES, PART_OF
- Only include high-confidence relationships.
- Return valid JSON only.
"""
        
        return prompt
    
    def _parse_relation_response(self, ai_response: str) -> Optional[Dict]:
        """
        개념 관계 분석 응답 파싱
        
        Args:
            ai_response (str): AI 응답 텍스트
            
        Returns:
            dict: 파싱된 관계 결과. 실패 시 None
        """
        # 방법 1: 직접 JSON 파싱
        try:
            relation_result = json.loads(ai_response)
            print(f"     ✓ Direct JSON parse successful!")
            return self._validate_relation_result(relation_result)
        except json.JSONDecodeError:
            print("     → Direct parse failed, trying regex extraction...")
        
        # 방법 2: 정규식으로 JSON 추출
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        
        if not json_match:
            print(f"     ✗ No JSON object found in AI response")
            self._save_debug_response(ai_response, prefix="debug_relations")
            return None
        
        json_string = json_match.group(0)
        
        try:
            relation_result = json.loads(json_string)
            return self._validate_relation_result(relation_result)
        
        except json.JSONDecodeError as e:
            print(f"     ✗ Failed to parse JSON: {e}")
            self._save_debug_response(json_string, prefix="debug_relations_json")
            return None
    
    def _validate_relation_result(self, result: Dict) -> Optional[Dict]:
        """
        관계 분석 결과 검증
        
        Args:
            result (dict): 분석 결과
            
        Returns:
            dict: 검증된 결과. 실패 시 None
        """
        if 'relations' not in result:
            print("     ✗ Missing required field: 'relations'")
            return None
        
        if not isinstance(result.get('relations'), list):
            print("     ✗ 'relations' must be a list")
            return None
        
        # 각 관계 검증
        valid_relations = []
        valid_relation_types = {'IS_A_TYPE_OF', 'USED_IN', 'RELATED_TO', 'ENABLES', 'PART_OF'}
        
        for rel in result['relations']:
            if not isinstance(rel, dict):
                continue
            
            from_concept = rel.get('from', '').strip()
            to_concept = rel.get('to', '').strip()
            relation_type = rel.get('relation_type', '').strip()
            
            # 필수 필드 검증
            if not all([from_concept, to_concept, relation_type]):
                continue
            
            # relation_type 검증
            if relation_type not in valid_relation_types:
                print(f"     → Skipping invalid relation_type: {relation_type}")
                continue
            
            # 자기 자신과의 관계 제거
            if from_concept == to_concept:
                continue
            
            valid_relations.append({
                'from': from_concept,
                'to': to_concept,
                'relation_type': relation_type
            })
        
        if not valid_relations:
            print("     ✗ No valid relations found")
            return None
        
        result['relations'] = valid_relations
        return result


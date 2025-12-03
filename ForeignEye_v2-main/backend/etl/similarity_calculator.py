"""
개념 유사도 계산기

두 개념 간의 의미적 유사도를 계산합니다.
"""

import re
from typing import Set


class SimilarityCalculator:
    """개념 간 유사도 계산 클래스"""
    
    # 기술 도메인 키워드 (가중치 높음)
    TECH_KEYWORDS = {
        'ai', 'artificial intelligence', '인공지능', 'ml', 'machine learning', '머신러닝',
        'deep learning', '딥러닝', 'neural network', '신경망', 'transformer', '트랜스포머',
        'llm', 'large language model', '거대언어모델', 'gpt', 'bert',
        'computer vision', '컴퓨터비전', 'nlp', 'natural language processing', '자연어처리',
        'data', '데이터', 'algorithm', '알고리즘', 'model', '모델',
        'training', '학습', '훈련', 'inference', '추론', 'optimization', '최적화',
        'api', 'framework', '프레임워크', 'library', '라이브러리',
        'cloud', '클라우드', 'edge', '엣지', 'iot', 'blockchain', '블록체인',
        'quantum', '양자', 'security', '보안', 'encryption', '암호화'
    }
    
    # 불용어 (유사도 계산 시 제외)
    STOPWORDS = {
        '은', '는', '이', '가', '을', '를', '의', '에', '와', '과', '로', '으로',
        'this', 'that', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'
    }
    
    @staticmethod
    def calculate_similarity(concept1, concept2) -> float:
        """
        개념 간 유사도 계산 (다층 분석)
        
        Args:
            concept1: Concept 모델 객체 (name, description_ko 필요)
            concept2: Concept 모델 객체
            
        Returns:
            float: 유사도 점수 (0.0 ~ 1.0)
        """
        # 1. 개념 이름 기반 유사도
        name1 = concept1.name.lower().strip()
        name2 = concept2.name.lower().strip()
        
        # 1-1. 완전 일치
        if name1 == name2:
            return 0.95
        
        # 1-2. 한쪽이 다른 쪽을 포함 (예: "AI" ↔ "AI 모델")
        if name1 in name2 or name2 in name1:
            return 0.8
        
        # 1-3. 단어 단위 비교
        name1_words = set(re.findall(r'[a-zA-Z가-힣]{2,}', name1))
        name2_words = set(re.findall(r'[a-zA-Z가-힣]{2,}', name2))
        
        if name1_words and name2_words:
            name_overlap = len(name1_words & name2_words) / max(len(name1_words), len(name2_words))
            if name_overlap >= 0.5:
                return 0.6 + (name_overlap * 0.2)
        
        # 2. 키워드 추출
        keywords1 = SimilarityCalculator._extract_keywords(
            f"{concept1.name} {concept1.description_ko}"
        )
        keywords2 = SimilarityCalculator._extract_keywords(
            f"{concept2.name} {concept2.description_ko}"
        )
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # 3. 일반 키워드 유사도 (Jaccard)
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2
        
        if not union:
            return 0.0
        
        jaccard_similarity = len(intersection) / len(union)
        
        # 4. 기술 키워드 가중치
        tech_intersection = intersection & SimilarityCalculator.TECH_KEYWORDS
        tech_boost = len(tech_intersection) * 0.15
        
        # 5. 공통 키워드 개수 가중치
        if len(intersection) >= 8:
            jaccard_similarity *= 1.3
        elif len(intersection) >= 5:
            jaccard_similarity *= 1.2
        elif len(intersection) >= 3:
            jaccard_similarity *= 1.1
        
        # 6. 최종 점수
        final_score = jaccard_similarity + tech_boost
        
        return min(final_score, 1.0)
    
    @staticmethod
    def _extract_keywords(text: str) -> Set[str]:
        """
        텍스트에서 키워드 추출
        
        Args:
            text (str): 추출할 텍스트
            
        Returns:
            Set[str]: 키워드 집합
        """
        # 특수문자 제거 후 소문자로 변환
        text = re.sub(r'[^a-zA-Z0-9가-힣\s]', ' ', text.lower())
        words = text.split()
        
        # 2글자 이상, 불용어 제외
        keywords = {
            w for w in words
            if len(w) >= 2 and w not in SimilarityCalculator.STOPWORDS
        }
        
        return keywords


"""
개념 서비스

개념 관련 비즈니스 로직을 처리합니다.
"""

from app.extensions import db
from app.models.concept import Concept
from app.utils.exceptions import NotFoundError


class ConceptService:
    """개념 관련 비즈니스 로직"""
    
    @staticmethod
    def get_concept_by_id(concept_id, include_relations=False, include_articles=False):
        """
        개념 ID로 조회
        
        Args:
            concept_id (int): 개념 ID
            include_relations (bool): 관련 개념 포함 여부
            include_articles (bool): 관련 기사 포함 여부
            
        Returns:
            Concept: 개념 객체
            
        Raises:
            NotFoundError: 개념을 찾을 수 없음
        """
        concept = db.session.get(Concept, concept_id)
        
        if not concept:
            raise NotFoundError('개념', concept_id)
        
        return concept
    
    @staticmethod
    def search_concepts(query, limit=10):
        """
        개념 검색
        
        Args:
            query (str): 검색어
            limit (int): 결과 수 제한
            
        Returns:
            list: 개념 객체 리스트
        """
        concepts = Concept.query.filter(
            Concept.name.like(f'%{query}%')
        ).limit(limit).all()
        
        return concepts
    
    @staticmethod
    def create_concept(name, description_ko, real_world_examples_ko=None):
        """
        새 개념 생성
        
        Args:
            name (str): 개념 이름
            description_ko (str): 한국어 설명
            real_world_examples_ko (list): 실제 사례 배열
            
        Returns:
            Concept: 생성된 개념 객체
        """
        concept = Concept(
            name=name,
            description_ko=description_ko,
            real_world_examples_ko=real_world_examples_ko or []
        )
        
        db.session.add(concept)
        db.session.commit()
        
        return concept
    
    @staticmethod
    def get_or_create_concept(name, description_ko, real_world_examples_ko=None):
        """
        개념 조회 또는 생성
        
        Args:
            name (str): 개념 이름
            description_ko (str): 한국어 설명
            real_world_examples_ko (list): 실제 사례 배열
            
        Returns:
            tuple: (Concept 객체, created: bool)
        """
        concept = Concept.query.filter_by(name=name).first()
        
        if concept:
            return concept, False
        
        concept = ConceptService.create_concept(
            name=name,
            description_ko=description_ko,
            real_world_examples_ko=real_world_examples_ko
        )
        
        return concept, True


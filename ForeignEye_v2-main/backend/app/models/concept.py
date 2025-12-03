"""
Concept 모델

기술 개념 정보를 저장하고 다른 개념들과의 관계를 관리합니다.
"""

from app.extensions import db


class Concept(db.Model):
    """
    개념 모델
    
    Attributes:
        concept_id (int): 개념 ID (Primary Key)
        name (str): 개념 이름 (Unique)
        description_ko (str): 한국어 설명
        real_world_examples_ko (JSON): 실제 사례 배열
        articles (relationship): 이 개념이 등장하는 기사들
        relations_from (relationship): 이 개념에서 시작하는 관계들
        relations_to (relationship): 이 개념으로 향하는 관계들
        collections (relationship): 이 개념을 수집한 사용자들
    """
    
    __tablename__ = 'Concept'
    
    # 컬럼 정의
    concept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description_ko = db.Column(db.Text, nullable=False)
    real_world_examples_ko = db.Column(db.JSON, nullable=True)
    
    # 관계 정의
    articles = db.relationship(
        'Article_Concept',
        backref='concept',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    relations_from = db.relationship(
        'Concept_Relation',
        foreign_keys='Concept_Relation.from_concept_id',
        backref='from_concept',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    relations_to = db.relationship(
        'Concept_Relation',
        foreign_keys='Concept_Relation.to_concept_id',
        backref='to_concept',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    collections = db.relationship(
        'User_Collection',
        backref='concept',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # 시리얼라이저
    def to_dict(self, include_articles=False, include_relations=False, is_collected=None):
        """
        딕셔너리로 변환 (JSON 직렬화용)
        
        Args:
            include_articles (bool): 관련 기사 목록 포함 여부
            include_relations (bool): 관련 개념 목록 포함 여부
            is_collected (bool): 수집 상태 (None이면 포함 안 함)
            
        Returns:
            dict: 개념 정보
        """
        data = {
            'concept_id': self.concept_id,
            'name': self.name,
            'description_ko': self.description_ko,
            'real_world_examples_ko': self.real_world_examples_ko or []
        }
        
        if is_collected is not None:
            data['is_collected'] = is_collected
        
        if include_articles:
            # 관련 기사 목록 (미리보기용)
            data['related_articles'] = [
                {
                    'article_id': ac.article.article_id,
                    'title_ko': ac.article.title_ko or ac.article.title,
                    'created_at': ac.article.created_at.isoformat() + 'Z'
                }
                for ac in self.articles[:5]  # 최대 5개
            ]
        
        if include_relations:
            # 관련 개념 목록
            related = []
            
            # From 관계
            for rel in self.relations_from:
                related.append({
                    'concept_id': rel.to_concept_id,
                    'name': rel.to_concept.name,
                    'relation_type': rel.relation_type,
                    'strength': rel.strength
                })
            
            # To 관계
            for rel in self.relations_to:
                related.append({
                    'concept_id': rel.from_concept_id,
                    'name': rel.from_concept.name,
                    'relation_type': rel.relation_type,
                    'strength': rel.strength
                })
            
            data['related_concepts'] = related
        
        return data
    
    def __repr__(self):
        """디버깅용 문자열 표현"""
        return f'<Concept {self.concept_id}: {self.name}>'


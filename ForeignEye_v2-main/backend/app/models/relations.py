"""
관계 모델들

Article_Concept: 기사-개념 관계 (N:M)
Concept_Relation: 개념-개념 관계 (방향성 그래프)
User_Collection: 사용자-개념 수집 관계 (N:M)
"""

from datetime import datetime
from app.extensions import db


class Article_Concept(db.Model):
    """
    기사-개념 연결 테이블 (N:M 관계)
    
    하나의 기사가 여러 개념을 포함하고,
    하나의 개념이 여러 기사에 등장할 수 있습니다.
    
    Attributes:
        ac_id (int): 연결 ID (Primary Key)
        article_id (int): 기사 ID (Foreign Key)
        concept_id (int): 개념 ID (Foreign Key)
    """
    
    __tablename__ = 'Article_Concept'
    
    ac_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('Article.article_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    concept_id = db.Column(
        db.Integer,
        db.ForeignKey('Concept.concept_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # 복합 인덱스 (성능 최적화)
    __table_args__ = (
        db.Index('idx_article_concept', 'article_id', 'concept_id'),
    )
    
    def __repr__(self):
        return f'<Article_Concept article={self.article_id} concept={self.concept_id}>'


class Concept_Relation(db.Model):
    """
    개념 간 관계 테이블 (방향성 그래프)
    
    개념들 사이의 의미적 관계를 저장합니다.
    strength 필드는 관계의 강도를 나타냅니다 (1-10).
    
    Attributes:
        relation_id (int): 관계 ID (Primary Key)
        from_concept_id (int): 시작 개념 ID (Foreign Key)
        to_concept_id (int): 도착 개념 ID (Foreign Key)
        relation_type (str): 관계 타입 (예: 'related_to', 'is_type_of')
        strength (int): 관계 강도 (1-10)
    """
    
    __tablename__ = 'Concept_Relation'
    
    relation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_concept_id = db.Column(
        db.Integer,
        db.ForeignKey('Concept.concept_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    to_concept_id = db.Column(
        db.Integer,
        db.ForeignKey('Concept.concept_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    relation_type = db.Column(db.String(50), nullable=True)
    strength = db.Column(db.Integer, nullable=False, default=1)
    
    # 복합 인덱스 (성능 최적화)
    __table_args__ = (
        db.Index('idx_from_concept', 'from_concept_id'),
        db.Index('idx_to_concept', 'to_concept_id'),
        db.Index('idx_concept_relation', 'from_concept_id', 'to_concept_id'),
        db.Index('idx_strength', 'strength'),
    )
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'relation_id': self.relation_id,
            'from_concept_id': self.from_concept_id,
            'to_concept_id': self.to_concept_id,
            'relation_type': self.relation_type,
            'strength': self.strength
        }
    
    def __repr__(self):
        return f'<Concept_Relation {self.from_concept_id}→{self.to_concept_id} (strength={self.strength})>'


class User_Collection(db.Model):
    """
    사용자 개념 수집 테이블 (N:M 관계)
    
    사용자가 수집한 개념들을 저장합니다.
    
    Attributes:
        collection_id (int): 수집 ID (Primary Key)
        user_id (int): 사용자 ID (Foreign Key)
        concept_id (int): 개념 ID (Foreign Key)
        collected_at (datetime): 수집 시각
    """
    
    __tablename__ = 'User_Collection'
    
    collection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('User.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    concept_id = db.Column(
        db.Integer,
        db.ForeignKey('Concept.concept_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    collected_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    # 유니크 제약 조건 (중복 수집 방지)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'concept_id', name='user_concept_UNIQUE'),
        db.Index('idx_user_collection', 'user_id', 'concept_id'),
    )
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'collection_id': self.collection_id,
            'user_id': self.user_id,
            'concept_id': self.concept_id,
            'collected_at': self.collected_at.isoformat() + 'Z'
        }
    
    def __repr__(self):
        return f'<User_Collection user={self.user_id} concept={self.concept_id}>'


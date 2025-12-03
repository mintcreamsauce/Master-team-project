"""
Article 모델

뉴스 기사 정보를 저장하고 관련 개념들과의 관계를 관리합니다.
"""

from datetime import datetime
import json
from app.extensions import db


class Article(db.Model):
    """
    기사 모델
    
    Attributes:
        article_id (int): 기사 ID (Primary Key)
        title (str): 원본 영문 제목
        title_ko (str): 한국어 번역 제목
        original_url (str): 원본 기사 URL (Unique)
        summary_ko (str): AI 생성 한국어 요약
        graph_cache (str): 사전 계산된 지식 그래프 JSON
        created_at (datetime): 기사 생성 시각
        concepts (relationship): 기사에 등장하는 개념들
    """
    
    __tablename__ = 'Article'
    
    # 컬럼 정의
    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    title_ko = db.Column(db.String(255), nullable=True)
    original_url = db.Column(db.String(512), unique=True, nullable=False, index=True)
    summary_ko = db.Column(db.Text, nullable=False)
    graph_cache = db.Column(db.Text, nullable=True)  # JSON 형식의 그래프 캐시
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    # 관계 정의
    concepts = db.relationship(
        'Article_Concept',
        backref='article',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # 시리얼라이저
    def to_dict(self, include_preview=False, include_concepts=False, include_graph=False):
        """
        딕셔너리로 변환 (JSON 직렬화용)
        
        Args:
            include_preview (bool): 개념 미리보기 포함 여부
            include_concepts (bool): 전체 개념 목록 포함 여부
            include_graph (bool): 지식 그래프 포함 여부
            
        Returns:
            dict: 기사 정보
        """
        data = {
            'article_id': self.article_id,
            'title': self.title,
            'title_ko': self.title_ko,
            'original_url': self.original_url,
            'summary_ko': self.summary_ko,
            'created_at': self.created_at.isoformat() + 'Z'
        }
        
        if include_preview:
            # 미리보기용 개념 (최대 3개)
            preview_concepts = [
                {
                    'concept_id': ac.concept.concept_id,
                    'name': ac.concept.name
                }
                for ac in self.concepts[:3]
            ]
            data['concept_count'] = len(self.concepts)
            data['preview_concepts'] = preview_concepts
        
        if include_concepts:
            # 전체 개념 목록
            data['concepts'] = [
                ac.concept.to_dict() for ac in self.concepts
            ]
        
        if include_graph and self.graph_cache:
            # 그래프 데이터 파싱
            try:
                data['graph'] = json.loads(self.graph_cache)
            except json.JSONDecodeError:
                data['graph'] = {'nodes': [], 'edges': []}
        
        return data
    
    def set_graph_cache(self, graph_data):
        """
        그래프 데이터를 JSON으로 직렬화하여 캐시에 저장
        
        Args:
            graph_data (dict): {'nodes': [...], 'edges': [...]} 형식의 그래프 데이터
        """
        self.graph_cache = json.dumps(graph_data, ensure_ascii=False)
    
    def get_graph_cache(self):
        """
        캐시된 그래프 데이터를 파싱하여 반환
        
        Returns:
            dict: 그래프 데이터 또는 빈 그래프
        """
        if not self.graph_cache:
            return {'nodes': [], 'edges': []}
        
        try:
            return json.loads(self.graph_cache)
        except json.JSONDecodeError:
            return {'nodes': [], 'edges': []}
    
    def __repr__(self):
        """디버깅용 문자열 표현"""
        return f'<Article {self.article_id}: {self.title[:50]}>'


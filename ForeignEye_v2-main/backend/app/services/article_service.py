"""
기사 서비스

기사 관련 비즈니스 로직을 처리합니다.
"""

from app.extensions import db
from app.models.article import Article
from app.utils.exceptions import NotFoundError


class ArticleService:
    """기사 관련 비즈니스 로직"""
    
    @staticmethod
    def get_articles(page=1, limit=10, sort='created_at', order='desc'):
        """
        기사 목록 조회
        
        Args:
            page (int): 페이지 번호 (1부터 시작)
            limit (int): 페이지당 항목 수
            sort (str): 정렬 기준 ('created_at', 'title')
            order (str): 정렬 순서 ('asc', 'desc')
            
        Returns:
            tuple: (기사 리스트, 전체 개수)
        """
        query = Article.query
        
        # 정렬
        sort_column = getattr(Article, sort, Article.created_at)
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 페이지네이션
        offset = (page - 1) * limit
        articles = query.offset(offset).limit(limit).all()
        total = query.count()
        
        return articles, total
    
    @staticmethod
    def get_article_by_id(article_id):
        """
        기사 ID로 조회
        
        Args:
            article_id (int): 기사 ID
            
        Returns:
            Article: 기사 객체
            
        Raises:
            NotFoundError: 기사를 찾을 수 없음
        """
        article = db.session.get(Article, article_id)
        
        if not article:
            raise NotFoundError('기사', article_id)
        
        return article
    
    @staticmethod
    def get_article_with_graph(article_id, user_id):
        """
        기사와 지식 그래프를 함께 조회
        
        Args:
            article_id (int): 기사 ID
            user_id (int): 사용자 ID
            
        Returns:
            dict: 기사 정보 + 지식 그래프
        """
        from app.services.graph_service import GraphService
        
        article = ArticleService.get_article_by_id(article_id)
        article_data = article.to_dict(include_graph=False)
        
        # 그래프 데이터 추가
        graph_data = GraphService.get_context_map_for_article(article_id, user_id)
        article_data['graph'] = graph_data
        
        return article_data
    
    @staticmethod
    def create_article(title, title_ko, url, summary_ko):
        """
        새 기사 생성
        
        Args:
            title (str): 원본 제목
            title_ko (str): 한국어 제목
            url (str): 원본 URL
            summary_ko (str): 한국어 요약
            
        Returns:
            Article: 생성된 기사 객체
        """
        article = Article(
            title=title,
            title_ko=title_ko,
            original_url=url,
            summary_ko=summary_ko
        )
        
        db.session.add(article)
        db.session.commit()
        
        return article


"""
ETL 서비스

데이터 추출, 변환, 적재 관련 로직을 처리합니다.
(현재는 그래프 캐시 생성 로직만 포함, 추후 확장 예정)
"""

from app.services.graph_service import GraphService


class ETLService:
    """ETL 관련 비즈니스 로직"""
    
    @staticmethod
    def build_graph_cache_for_article(article_id, min_strength=3, max_secondary_nodes=15):
        """
        기사의 지식 그래프 캐시 생성 (GraphService 위임)
        
        Args:
            article_id (int): 기사 ID
            min_strength (int): 최소 관계 강도
            max_secondary_nodes (int): 최대 2차 노드 수
            
        Returns:
            dict: 그래프 데이터
        """
        return GraphService.build_graph_cache_for_article(
            article_id=article_id,
            min_strength=min_strength,
            max_secondary_nodes=max_secondary_nodes
        )


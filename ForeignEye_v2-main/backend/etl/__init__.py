"""
ETL 파이프라인 패키지
뉴스 데이터 추출(Extract), 변환(Transform), 적재(Load)를 처리합니다.
"""

# __init__.py 파일은 자식 모듈(DBLoader, GNewsFetcher 등)을
# 직접 임포트하지 않는 것이 순환 참조를 방지하는 가장 좋은 방법입니다.

# 다른 모듈들이 `from etl.db_loader import DBLoader` 처럼
# 명시적으로 임포트하도록 구조화합니다.

# 이 __all__ 리스트는 `from etl import *` 사용 시 노출될 모듈을 정의합니다.
__all__ = [
    'GNewsFetcher',
    'WebScraper',
    'AIAnalyzer',
    'DBLoader',
    'SimilarityCalculator',
    'neo4j_client' # 새로 추가한 neo4j_client 모듈
]
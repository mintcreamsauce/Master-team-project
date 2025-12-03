"""
Flask 확장 초기화 모듈 (v2.3 M1 최종본)

모든 Flask 확장(SQLAlchemy, JWT 등)을 앱 컨텍스트 외부에서 생성하고,
앱 팩토리에서 init_app()으로 초기화합니다.
Celery 인스턴스가 중앙 관리됩니다.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from celery import Celery
from neo4j import GraphDatabase
import os

# --- DB, Auth, Limiter ---
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)
migrate = Migrate()

# --- Celery (M1 최종본) ---
# [M1] Celery 인스턴스를 중앙에서 정의합니다. (사용자님 제안)
celery_app = Celery(
    'ForeignEye', # (앱 이름)
    broker='redis://redis:6379/0', # (Docker 내부망 Redis 주소)
    backend='redis://redis:6379/1', # (Docker 내부망 Redis 주소)
    # [M1] 이 한 줄이 'unregistered task' 오류를 해결합니다.
    include=['app.celery_tasks'] 
)
# [M1] (사용자님 제안) Celery 추가 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

# --- Neo4j 드라이버 ---
neo4j_driver = None

def get_neo4j_driver():
    """Neo4j 드라이버 싱글톤"""
    global neo4j_driver
    if neo4j_driver is None:
        neo4j_driver = GraphDatabase.driver(
            os.environ.get('NEO4J_URI'), 
            auth=(os.environ.get('NEO4J_USERNAME'), os.environ.get('NEO4J_PASSWORD'))
        )
    return neo4j_driver

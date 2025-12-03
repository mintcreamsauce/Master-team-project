"""
Celery Tasks (M1) - (ETL Task Added)
"""

import os
from celery.utils.log import get_task_logger
from app.extensions import celery_app, get_neo4j_driver, db
from app.models.concept import Concept
from app.models.relations import Concept_Relation, User_Collection

# [M1] v2.0의 ETL 로직 임포트
try:
    from etl.run import run_etl_pipeline
    ETL_LOGIC_FOUND = True
except ImportError:
    print("[경고] 'etl.run' 모듈을 찾을 수 없습니다. 'backend/etl/run.py' 파일이 있는지 확인하세요.")
    ETL_LOGIC_FOUND = False


logger = get_task_logger(__name__)

# [M1] Celery 워커가 Flask 앱 컨텍스트를 사용할 수 있도록 앱 생성
# (참고: 순환 참조를 피하기 위해 함수 내부에서 앱을 생성합니다)
def get_flask_app():
    from app import create_app
    return create_app(os.getenv('FLASK_ENV', 'development'))

# --- (신규) M1(캡스톤) 메인 ETL 작업 ---
@celery_app.task(name='run_main_etl_task')
def run_main_etl_task(max_articles: int = 3):
    """
    GNews/OpenRouter/DBLoader를 비동기(Celery)로 실행하는
    M1(캡스톤)의 메인 ETL 작업입니다.
    """
    if not ETL_LOGIC_FOUND:
        logger.error("ETL 로직을 찾을 수 없어 'run_main_etl_task'를 실행할 수 없습니다.")
        return

    app = get_flask_app()
    with app.app_context():
        logger.info(f"Celery: 'run_main_etl_task' 시작 (Max Articles: {max_articles})...")
        try:
            # v2.0의 ETL 파이프라인 로직을 그대로 호출
            result = run_etl_pipeline(max_articles=max_articles)
            logger.info(f"Celery: 'run_main_etl_task' 성공. 결과: {result}")
            return result
        except Exception as e:
            logger.error(f"Celery: 'run_main_etl_task' 실패. 오류: {e}", exc_info=True)
            raise e

# --- (기존) P4 '유령 상태' 방어용 동기화 작업 ---
@celery_app.task(name='sync_neo4j_task')
def sync_neo4j_task(user_id):
    """
    (P4 방어) 사용자 컬렉션을 기반으로 Neo4j 뷰를 최신 상태로 동기화
    """
    app = get_flask_app()
    with app.app_context():
        # ... (이전과 동일한 P4 동기화 로직) ...
        concept_rows = (
            db.session.query(User_Collection.concept_id)
            .filter(User_Collection.user_id == user_id)
            .all()
        )
        concept_ids = [row[0] for row in concept_rows]
        if not concept_ids:
            logger.info(f'sync_neo4j_task: user {user_id} has no collections.')
            return

        concepts = (
            Concept.query
            .filter(Concept.concept_id.in_(concept_ids))
            .all()
        )
        relations = (
            Concept_Relation.query
            .filter(Concept_Relation.from_concept_id.in_(concept_ids))
            .filter(Concept_Relation.to_concept_id.in_(concept_ids))
            .all()
        )

        driver = get_neo4j_driver()
        database = app.config.get('NEO4J_DATABASE', 'neo4j')
        
        payload_concepts = [{ 'id': c.concept_id, 'name': c.name, 'description': c.description_ko, 'examples': c.real_world_examples_ko or [] } for c in concepts]
        payload_relations = [{ 'from': rel.from_concept_id, 'to': rel.to_concept_id, 'relation_type': rel.relation_type, 'strength': rel.strength } for rel in relations]

        with driver.session(database=database) as session:
            session.execute_write(
                _sync_user_collection,
                user_id,
                payload_concepts,
                payload_relations
            )
        logger.info(f'sync_neo4j_task: user {user_id} synced ({len(payload_concepts)} concepts, {len(payload_relations)} relations).')


def _sync_user_collection(tx, user_id, concepts, relations):
    # ... (이전과 동일한 Neo4j 트랜잭션 헬퍼) ...
    tx.run(
        """
        MERGE (u:User {user_id: })
        WITH u
        UNWIND  AS concept
        MERGE (c:Concept {concept_id: concept.id})
        SET
            c.name = concept.name,
            c.description_ko = concept.description,
            c.real_world_examples_ko = concept.examples
        MERGE (u)-[:COLLECTED]->(c)
        """,
        userId=user_id,
        concepts=concepts
    )
    tx.run(
        """
        UNWIND  AS rel
        MATCH (from:Concept {concept_id: rel.from})
        MATCH (to:Concept {concept_id: rel.to})
        MERGE (from)-[r:RELATED]->(to)
        SET
            r.relation_type = rel.relation_type,
            r.strength = rel.strength
        """,
        relations=relations
    )

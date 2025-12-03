"""
컬렉션 API 라우트
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

# [M1] (P4 방어) Celery 동기화 작업 임포트
from app.celery_tasks import sync_neo4j_task 
from app.utils.response import success_response, error_response
from app.utils.exceptions import NotFoundError, DuplicateEntryError, ValidationError
from app.utils.validators import validate_concept_id, validate_sort_params
from app.extensions import limiter
from app.services.collection_service import CollectionService

bp = Blueprint('collections', __name__)

@bp.route('/concepts', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def collect_concept():
    """
    (P4) 개념 수집 API
    """
    try:
        user_id = int(get_jwt_identity())  # 문자열을 정수로 변환
        data = request.get_json()
        concept_id = validate_concept_id(data.get('concept_id'))

        # 1. MySQL(SoT)에 먼저 저장 (가정)
        result = CollectionService.collect_concept(user_id, concept_id)

        # 2. [M1] (P4 방어) MySQL 저장 성공 시, Celery 비동기 동기화 트리거
        sync_neo4j_task.delay(user_id)

        return success_response({
            'collection': result['collection'].to_dict(),
            'concept_name': result['concept_name'],
            'new_connections': result['new_connections'],
            'message': f"'{result['concept_name']}'를 수집했습니다!" + (
                f" {len(result['new_connections'])}개의 강한 연결을 발견했습니다."
                if result['new_connections'] else ""
            )
        }, status=201)

    except (ValidationError, NotFoundError, DuplicateEntryError):
        raise
    except Exception as exc:
        return error_response('INTERNAL_ERROR', str(exc), 500)

@bp.route('/concepts', methods=['GET'])
# @jwt_required()  # JWT 임시 비활성화
def get_collected_concepts():
    """
    수집한 개념 목록 조회 API
    
    GET /api/v1/collections/concepts
    Returns:
        {
            "data": [
                {"concept_id": 1, "name": "Hardware", "description_ko": "...", ...},
                {"concept_id": 2, "name": "Platform", ...}
            ]
        }
    """
    try:
        # [임시] JWT 대신 user_id=1 하드코딩
        user_id = 1
        # user_id = int(get_jwt_identity())  # 실제 배포 시 사용
        
        # 서비스 호출
        concepts = CollectionService.get_user_collections(user_id, sort='collected_at', order='desc')
        
        # 직렬화
        concepts_data = [concept.to_dict() for concept in concepts]
        
        return success_response(concepts_data)
        
    except Exception as exc:
        return error_response('INTERNAL_ERROR', str(exc), 500)


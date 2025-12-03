"""
지식 맵 API 라우트

P5 기능: 사용자가 수집한 개념들의 전체 지식 맵 조회
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.knowledge_map_service import KnowledgeMapService
from app.utils.response import success_response, error_response

bp = Blueprint('knowledge_map', __name__)


@bp.route('', methods=['GET'])
# @jwt_required()  # JWT 인증 임시 비활성화 (테스트용)
def get_knowledge_map():
    """
    (P5) 현재 유저의 전체 지식 맵 반환 (수집한 개념 기준)
    
    Returns:
        {
            "data": {
                "nodes": [...],  # React Flow 노드 형식
                "edges": [...]   # React Flow 엣지 형식
            },
            "message": "Knowledge map retrieved successfully"
        }
    """
    try:
        # [임시] JWT 대신 user_id=1 하드코딩
        user_id = 1
        # user_id = int(get_jwt_identity())  # 실제 배포 시 사용
        
        # 서비스 호출
        graph_data = KnowledgeMapService.get_user_knowledge_map(user_id)
        
        return success_response(graph_data)
        
    except Exception as exc:
        return error_response('INTERNAL_ERROR', str(exc), 500)

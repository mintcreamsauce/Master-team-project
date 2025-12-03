"""
개념 API 라우트

개념 상세 조회, 개념 검색 API
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.response import success_response, error_response
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.validators import validate_search_query
from app.services.concept_service import ConceptService

bp = Blueprint('concepts', __name__)


@bp.route('/<int:concept_id>', methods=['GET'])
@jwt_required()

def get_concept(concept_id):
    """
    개념 상세 조회 API
    
    GET /api/v1/concepts/{concept_id}
    """
    user_id = get_jwt_identity()
    try:
        # 서비스 호출
        concept = ConceptService.get_concept_by_id(
            concept_id,
            include_relations=True,
            include_articles=True
        )
        
        return success_response({
            'concept': concept.to_dict(include_articles=True, include_relations=True)
        })
        
    except NotFoundError as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


@bp.route('/search', methods=['GET'])
@jwt_required()

def search_concepts():
    """
    개념 검색 API
    
    GET /api/v1/concepts/search?q=transformer&limit=10
    """
    user_id = get_jwt_identity()
    try:
        query_str = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        # 검증
        query_str = validate_search_query(query_str)
        
        if limit < 1 or limit > 50:
            raise ValidationError('제한은 1~50 사이여야 합니다.', 'limit')
        
        # 서비스 호출
        concepts = ConceptService.search_concepts(query_str, limit)
        
        return success_response({
            'results': [c.to_dict() for c in concepts],
            'total_results': len(concepts),
            'query': query_str
        })
        
    except ValidationError as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


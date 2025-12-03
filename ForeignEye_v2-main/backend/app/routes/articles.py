"""
기사 API 라우트

기사 목록 조회, 기사 상세 조회 API
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.response import success_response, paginated_response, error_response
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.validators import validate_pagination, validate_sort_params
from app.services.article_service import ArticleService

bp = Blueprint('articles', __name__)


@bp.route('', methods=['GET'])
# @jwt_required()  # JWT 임시 비활성화
def get_articles():
    """
    기사 목록 조회 API
    
    GET /api/v1/articles?page=1&limit=10&sort=created_at&order=desc
    """
    try:
        # 쿼리 파라미터
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        
        # 검증
        page, limit = validate_pagination(page, limit)
        sort, order = validate_sort_params(sort, order, ['created_at', 'title'])
        
        # 서비스 호출
        articles, total = ArticleService.get_articles(page, limit, sort, order)
        
        # 응답 생성
        articles_data = [a.to_dict(include_preview=True) for a in articles]
        
        return paginated_response(
            items=articles_data,
            page=page,
            total_items=total,
            items_per_page=limit
        )
        
    except ValidationError as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


@bp.route('/<int:article_id>', methods=['GET'])
# @jwt_required()  # JWT 임시 비활성화
def get_article(article_id):
    """
    기사 상세 조회 API (모든 개념 포함)
    
    GET /api/v1/articles/{article_id}
    """
    try:
        # 기사 조회
        article = ArticleService.get_article_by_id(article_id)
        if not article:
            raise NotFoundError('ARTICLE_NOT_FOUND', '기사를 찾을 수 없습니다.')
        
        # 모든 개념 포함하여 직렬화
        article_data = article.to_dict(include_concepts=True)
        
        return success_response(article_data)
        
    except NotFoundError as e:
        raise
    except Exception as e:
        return error_response('INTERNAL_ERROR', str(e), 500)


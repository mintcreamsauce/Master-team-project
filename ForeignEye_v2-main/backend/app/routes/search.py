"""
Search API routes
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.services.search_service import SearchService
from app.utils.response import success_response, error_response
from app.utils.exceptions import ValidationError

bp = Blueprint("search", __name__)


@bp.route("/articles_by_concept", methods=["GET"])
@jwt_required()
def get_articles_by_concept():
    """
    (P2/P3) 개념 이름으로 기사 목록 검색 (친척 개념 30개 포함)
    """
    concept_name = request.args.get("concept_name", "").strip()
    if not concept_name:
        raise ValidationError("concept_name 파라미터는 필수입니다.", "concept_name")

    try:
        # (P3 방어) SearchService가 LIMIT 30을 적용함
        articles = SearchService.get_articles_by_concept(concept_name)
        return success_response({
            "concept": concept_name,
            "total_results": len(articles),
            "articles": articles
        })
    except Exception as exc:
        return error_response("INTERNAL_ERROR", str(exc), 500)


@bp.route("/articles_by_multiple_concepts", methods=["GET"])
@jwt_required()
def get_articles_by_multiple_concepts():
    concepts_param = request.args.get("concepts", "")
    if not concepts_param:
        raise ValidationError("concepts 파라미터는 최소 하나의 개념을 포함해야 합니다.", "concepts")

    concept_names = [name.strip() for name in concepts_param.split(",") if name.strip()]
    if not concept_names:
        raise ValidationError("concepts 파라미터가 유효하지 않습니다.", "concepts")

    try:
        articles = SearchService.get_articles_by_multiple_concepts(concept_names)
        return success_response({
            "concepts": concept_names,
            "total_results": len(articles),
            "articles": articles
        })
    except Exception as exc:
        return error_response("INTERNAL_ERROR", str(exc), 500)


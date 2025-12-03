"""
Search service
"""

from typing import List, Dict

from sqlalchemy import func
from app.extensions import db
from app.models import Article, Concept, Article_Concept
from app.models.relations import Concept_Relation


class SearchService:
    # [M1] (P3 방어) '슈퍼 노드' 함정 방어를 위한 임베딩 제한
    RELATIVE_LIMIT = 10

    @staticmethod
    def get_articles_by_concept(concept_name: str) -> List[Dict]:
        cleaned = (concept_name or "").strip()
        if not cleaned:
            return []

        concept = Concept.query.filter(
            func.lower(Concept.name) == cleaned.lower()
        ).first()
        if not concept:
            return []

        article_ids = (
            db.session.query(Article_Concept.article_id)
            .filter(Article_Concept.concept_id == concept.concept_id)
            .subquery()
        )

        articles = (
            Article.query.filter(Article.article_id.in_(article_ids))
            .order_by(Article.created_at.desc())
            .all()
        )
        return [SearchService._serialize_article(article) for article in articles]

    @staticmethod
    def get_articles_by_multiple_concepts(concept_names: List[str]) -> List[Dict]:
        cleaned_names = [name.strip() for name in concept_names if name and name.strip()]
        if not cleaned_names:
            return []

        concepts = Concept.query.filter(
            func.lower(Concept.name).in_(map(str.lower, cleaned_names))
        ).all()
        if len(concepts) != len(set(name.lower() for name in cleaned_names)):
            return []

        concept_ids = [concept.concept_id for concept in concepts]

        matching_articles_subquery = (
            db.session.query(Article_Concept.article_id)
            .filter(Article_Concept.concept_id.in_(concept_ids))
            .group_by(Article_Concept.article_id)
            .having(func.count(func.distinct(Article_Concept.concept_id)) == len(concept_ids))
            .subquery()
        )

        articles = (
            Article.query.filter(Article.article_id.in_(matching_articles_subquery))
            .order_by(Article.created_at.desc())
            .all()
        )
        return [SearchService._serialize_article(article) for article in articles]

    @staticmethod
    def _serialize_article(article: Article) -> Dict:
        data = article.to_dict(include_preview=True)
        # [M1] (P3 방어) 직렬화 시 '친척 개념'을 임베딩
        data['relative_concepts'] = SearchService._fetch_relative_concepts(article)
        return data

    @staticmethod
    def _fetch_relative_concepts(article: Article) -> List[Dict]:
        """
        [M1] (P3 방어) 기사와 연결된 개념들의 '친척 개념'을 30개 제한으로 가져옴
        [FIX] 중복된 concept_id 제거 (같은 개념이 여러 관계로 연결된 경우 가장 강한 것만 유지)
        """
        concept_ids = [ac.concept_id for ac in article.concepts]
        if not concept_ids:
            return []

        related_rows = (
            db.session.query(Concept_Relation, Concept)
            .join(Concept, Concept.concept_id == Concept_Relation.to_concept_id)
            .filter(Concept_Relation.from_concept_id.in_(concept_ids))
            .order_by(Concept_Relation.strength.desc())
            .limit(SearchService.RELATIVE_LIMIT * 3)  # 중복 제거 전 여유있게 가져옴
            .all()
        )

        # 중복 제거: concept_id를 키로 하고, 가장 강한 관계만 유지
        unique_concepts = {}
        for relation, concept in related_rows:
            cid = concept.concept_id
            # 이미 존재하는 경우, 더 강한 strength를 가진 것만 유지
            if cid not in unique_concepts or relation.strength > unique_concepts[cid]['strength']:
                unique_concepts[cid] = {
                    'concept_id': cid,
                    'name': concept.name,
                    'relation_type': relation.relation_type,
                    'strength': relation.strength
                }
        
        # strength 순으로 정렬 후 RELATIVE_LIMIT만큼만 반환
        relatives = sorted(unique_concepts.values(), key=lambda x: x['strength'], reverse=True)
        return relatives[:SearchService.RELATIVE_LIMIT]

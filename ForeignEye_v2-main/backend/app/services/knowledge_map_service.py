"""
Knowledge Map Service

P5 기능: 사용자가 수집한 개념들의 전체 지식 맵을 생성합니다.
"""

from typing import List, Dict
from app.extensions import db
from app.models.concept import Concept
from app.models.relations import User_Collection, Concept_Relation


class KnowledgeMapService:
    """지식 맵 서비스 (MySQL 기반)"""

    @staticmethod
    def get_user_knowledge_map(user_id: int) -> Dict:
        """
        (P5) 사용자가 수집한 모든 개념과 그들 사이의 관계를 반환합니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict: { 'nodes': [], 'edges': [] }
        """
        
        # 1. 사용자가 수집한 모든 "개념 객체"를 가져옵니다 (MySQL).
        collected_concepts = (
            Concept.query
            .join(User_Collection, User_Collection.concept_id == Concept.concept_id)
            .filter(User_Collection.user_id == user_id)
            .all()
        )
        
        if not collected_concepts:
            return {'nodes': [], 'edges': []}

        # 2. 수집한 개념 ID 목록을 만듭니다.
        collected_concept_ids = {c.concept_id for c in collected_concepts}

        # 3. 수집한 개념들 "사이"의 모든 "관계"를 가져옵니다 (MySQL).
        relations = (
            Concept_Relation.query
            .filter(
                Concept_Relation.from_concept_id.in_(collected_concept_ids),
                Concept_Relation.to_concept_id.in_(collected_concept_ids)
            )
            .all()
        )

        # 4. React Flow 형식에 맞게 'Nodes'를 포맷합니다.
        # (임의의 위치를 지정합니다. 실제 P5에서는 자동 레이아웃이 적용됩니다.)
        nodes = []
        for i, concept in enumerate(collected_concepts):
            nodes.append({
                'id': str(concept.concept_id),
                'type': 'myConceptNode',  # 이미 수집했으므로 파란색 노드
                'position': {'x': (i % 5) * 200, 'y': (i // 5) * 150},
                'data': {
                    'type': 'myConceptNode',
                    'concept': concept.to_dict()
                }
            })

        # 5. React Flow 형식에 맞게 'Edges'를 포맷합니다.
        edges = []
        for rel in relations:
            edges.append({
                'id': f"rel-{rel.relation_id}",
                'source': str(rel.from_concept_id),
                'target': str(rel.to_concept_id),
                'label': rel.relation_type.replace('_', ' ').title(),
                'animated': True,
                'style': {'stroke': '#4299E1', 'strokeWidth': 2}
            })

        return {'nodes': nodes, 'edges': edges}

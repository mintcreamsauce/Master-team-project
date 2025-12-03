"""
그래프 서비스

지식 그래프 생성 및 관리 로직을 처리합니다.
"""

import json
from app.extensions import db
from app.models.article import Article
from app.models.concept import Concept
from app.models.relations import Article_Concept, Concept_Relation, User_Collection
from sqlalchemy.orm import aliased


class GraphService:
    """그래프 관련 비즈니스 로직"""
    
    @staticmethod
    def get_context_map_for_article(article_id, user_id):
        """
        기사의 컨텍스트 맵(지식 그래프) 조회
        
        🚀 [최적화됨] 사전 계산된 그래프를 캐시에서 로드하고 
        사용자의 수집 상태만 동적으로 업데이트합니다.
        
        복잡도: O(N) where N = 노드 수 (이전 O(N*M) 대비 획기적 개선)
        
        Args:
            article_id (int): 기사 ID
            user_id (int): 사용자 ID
            
        Returns:
            dict: {'nodes': [...], 'edges': [...]} 형식의 그래프 데이터
        """
        # 1. 기사 조회
        article = db.session.get(Article, article_id)
        
        if not article:
            return {"nodes": [], "edges": []}
        
        # 2. 캐시된 그래프 확인
        if not article.graph_cache:
            # 캐시가 없으면 즉시 생성
            from app.services.etl_service import ETLService
            graph_data = ETLService.build_graph_cache_for_article(article_id)
            article.graph_cache = json.dumps(graph_data, ensure_ascii=False)
            db.session.commit()
        else:
            # 캐시 파싱
            try:
                graph_data = json.loads(article.graph_cache)
            except json.JSONDecodeError:
                return {"nodes": [], "edges": []}
        
        # 3. 사용자의 수집 상태 조회 (단 1회 쿼리)
        user_collections = User_Collection.query.filter_by(user_id=user_id).all()
        collected_concept_ids = {uc.concept_id for uc in user_collections}
        
        # 4. 노드의 is_collected 플래그 업데이트 (메모리 상 O(N) 연산)
        for node in graph_data.get('nodes', []):
            node['is_collected'] = node['id'] in collected_concept_ids
        
        return graph_data
    
    @staticmethod
    def build_graph_cache_for_article(article_id, min_strength=3, max_secondary_nodes=15):
        """
        기사의 지식 그래프를 사전 계산하여 캐시 생성
        
        🚀 필터링 전략:
        - Primary Nodes: 기사에 직접 등장하는 개념 (모두 포함)
        - Secondary Nodes: 연결된 외부 개념 (strength >= min_strength, 최대 max_secondary_nodes개)
        
        Args:
            article_id (int): 기사 ID
            min_strength (int): 최소 관계 강도 (기본값: 3)
            max_secondary_nodes (int): 최대 2차 노드 수 (기본값: 15)
            
        Returns:
            dict: {'nodes': [...], 'edges': [...]} 형식의 그래프 데이터
        """
        # 1. Primary 개념들 조회
        primary_concepts = db.session.query(Concept).join(
            Article_Concept,
            Concept.concept_id == Article_Concept.concept_id
        ).filter(
            Article_Concept.article_id == article_id
        ).all()
        
        primary_concept_ids = {c.concept_id for c in primary_concepts}
        
        if not primary_concept_ids:
            return {"nodes": [], "edges": []}
        
        # 2. 관계 조회 (필터링 적용)
        C1 = aliased(Concept)
        C2 = aliased(Concept)
        
        # Query 1: (Primary) -> (Other)
        relations_query_1 = db.session.query(Concept_Relation, C2).join(
            C2, Concept_Relation.to_concept_id == C2.concept_id
        ).filter(
            Concept_Relation.from_concept_id.in_(primary_concept_ids),
            Concept_Relation.strength >= min_strength
        ).order_by(Concept_Relation.strength.desc())
        
        # Query 2: (Other) -> (Primary)
        relations_query_2 = db.session.query(Concept_Relation, C1).join(
            C1, Concept_Relation.from_concept_id == C1.concept_id
        ).filter(
            Concept_Relation.to_concept_id.in_(primary_concept_ids),
            Concept_Relation.strength >= min_strength
        ).order_by(Concept_Relation.strength.desc())
        
        # 3. 노드 및 엣지 구축
        nodes_map = {}
        edges_data = []
        secondary_nodes_added = 0
        
        # 3a. Primary 노드 추가
        for concept in primary_concepts:
            nodes_map[concept.concept_id] = {
                "id": concept.concept_id,
                "label": concept.name,
                "description": concept.description_ko,
                "real_world_examples": concept.real_world_examples_ko or [],
                "is_collected": False,  # 동적으로 업데이트됨
                "is_primary": True,
                "borderWidth": 4,
                "color": {"border": "#007bff", "background": "#ffffff"},
                "shape": "dot",
                "size": 25
            }
        
        # 3b. 관계 처리 1: (Primary) -> (Other)
        for relation, concept_to in relations_query_1.all():
            if concept_to.concept_id not in nodes_map:
                if concept_to.concept_id not in primary_concept_ids:
                    if secondary_nodes_added >= max_secondary_nodes:
                        continue
                    secondary_nodes_added += 1
                
                nodes_map[concept_to.concept_id] = {
                    "id": concept_to.concept_id,
                    "label": concept_to.name,
                    "description": concept_to.description_ko,
                    "real_world_examples": concept_to.real_world_examples_ko or [],
                    "is_collected": False,
                    "is_primary": concept_to.concept_id in primary_concept_ids,
                    "shape": "dot",
                    "size": 15
                }
            
            edges_data.append({
                "from": relation.from_concept_id,
                "to": relation.to_concept_id,
                "strength": relation.strength
            })
        
        # 3c. 관계 처리 2: (Other) -> (Primary)
        for relation, concept_from in relations_query_2.all():
            if concept_from.concept_id not in nodes_map:
                if concept_from.concept_id not in primary_concept_ids:
                    if secondary_nodes_added >= max_secondary_nodes:
                        continue
                    secondary_nodes_added += 1
                
                nodes_map[concept_from.concept_id] = {
                    "id": concept_from.concept_id,
                    "label": concept_from.name,
                    "description": concept_from.description_ko,
                    "real_world_examples": concept_from.real_world_examples_ko or [],
                    "is_collected": False,
                    "is_primary": concept_from.concept_id in primary_concept_ids,
                    "shape": "dot",
                    "size": 15
                }
            
            edges_data.append({
                "from": relation.from_concept_id,
                "to": relation.to_concept_id,
                "strength": relation.strength
            })
        
        return {
            "nodes": list(nodes_map.values()),
            "edges": edges_data
        }
    
    @staticmethod
    def get_knowledge_map_for_user(user_id):
        """
        사용자의 통합 지식 맵 생성
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            dict: {
                'graph': {'nodes': [...], 'edges': [...]},
                'stats': {...}
            }
        """
        # 사용자가 수집한 개념들
        collected_concepts = db.session.query(Concept).join(
            User_Collection,
            Concept.concept_id == User_Collection.concept_id
        ).filter(
            User_Collection.user_id == user_id
        ).all()
        
        collected_concept_ids = {c.concept_id for c in collected_concepts}
        
        # 노드 데이터
        nodes = []
        for concept in collected_concepts:
            nodes.append({
                'id': concept.concept_id,
                'label': concept.name,
                'description': concept.description_ko,
                'real_world_examples': concept.real_world_examples_ko or [],
                'is_collected': True,
                'shape': 'dot',
                'size': 20
            })
        
        # 엣지 데이터
        edges = []
        if collected_concept_ids:
            relations = Concept_Relation.query.filter(
                Concept_Relation.from_concept_id.in_(collected_concept_ids),
                Concept_Relation.to_concept_id.in_(collected_concept_ids)
            ).all()
            
            for rel in relations:
                edges.append({
                    'from': rel.from_concept_id,
                    'to': rel.to_concept_id,
                    'label': rel.relation_type,
                    'strength': rel.strength,
                    'width': max(1, rel.strength // 2)
                })
        
        # 통계 계산
        total_concepts = len(nodes)
        total_connections = len(edges)
        strong_connections = sum(1 for edge in edges if edge['strength'] >= 6)
        
        # 가장 연결이 많은 개념
        connection_counts = {}
        for edge in edges:
            connection_counts[edge['from']] = connection_counts.get(edge['from'], 0) + 1
            connection_counts[edge['to']] = connection_counts.get(edge['to'], 0) + 1
        
        most_connected = None
        if connection_counts:
            most_connected_id = max(connection_counts, key=connection_counts.get)
            most_connected_concept = db.session.get(Concept, most_connected_id)
            most_connected = {
                'concept_id': most_connected_concept.concept_id,
                'name': most_connected_concept.name,
                'connection_count': connection_counts[most_connected_id]
            }
        
        return {
            'graph': {
                'nodes': nodes,
                'edges': edges
            },
            'stats': {
                'total_concepts': total_concepts,
                'total_connections': total_connections,
                'strong_connections': strong_connections,
                'average_strength': sum(e['strength'] for e in edges) / len(edges) if edges else 0,
                'most_connected_concept': most_connected
            }
        }


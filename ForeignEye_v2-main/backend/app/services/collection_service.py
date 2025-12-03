"""
컬렉션 서비스

사용자의 개념 수집 관련 비즈니스 로직을 처리합니다.
"""

from app.extensions import db
from app.models.concept import Concept
from app.models.relations import User_Collection, Concept_Relation
from app.utils.exceptions import NotFoundError, DuplicateEntryError


class CollectionService:
    """컬렉션 관련 비즈니스 로직"""
    
    @staticmethod
    def collect_concept(user_id, concept_id):
        """
        개념 수집
        
        Args:
            user_id (int): 사용자 ID
            concept_id (int): 개념 ID
            
        Returns:
            dict: {
                'collection': User_Collection 객체,
                'concept_name': 개념 이름,
                'new_connections': 새로 발견된 강한 연결 리스트
            }
            
        Raises:
            NotFoundError: 개념을 찾을 수 없음
            DuplicateEntryError: 이미 수집한 개념
        """
        # 개념 존재 확인
        concept = db.session.get(Concept, concept_id)
        if not concept:
            raise NotFoundError('개념', concept_id)
        
        # 이미 수집했는지 확인
        existing = User_Collection.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if existing:
            raise DuplicateEntryError('이미 수집한 개념입니다.')
        
        # 수집 추가
        collection = User_Collection(
            user_id=user_id,
            concept_id=concept_id
        )
        db.session.add(collection)
        db.session.commit()
        
        # 새로운 강한 연결 찾기
        new_connections = CollectionService.find_new_strong_connections(
            user_id,
            concept_id
        )
        
        return {
            'collection': collection,
            'concept_name': concept.name,
            'new_connections': new_connections
        }
    
    @staticmethod
    def find_new_strong_connections(user_id, new_concept_id, threshold=3):
        """
        새로 수집한 개념과 기존 개념들 간의 강한 연결 찾기
        
        Args:
            user_id (int): 사용자 ID
            new_concept_id (int): 새로 수집한 개념 ID
            threshold (int): 강한 연결 기준 강도 (기본값: 3)
            
        Returns:
            list: 새로 발견된 강한 연결 리스트
        """
        # 사용자가 이미 수집한 개념들 (새 개념 제외)
        user_collected_ids = db.session.query(User_Collection.concept_id).filter(
            User_Collection.user_id == user_id,
            User_Collection.concept_id != new_concept_id
        ).all()
        user_collected_ids = {c_id[0] for c_id in user_collected_ids}
        
        if not user_collected_ids:
            return []
        
        # 양방향 관계 조회
        # 방향 1: (새 개념) -> (기존 개념)
        query1 = db.session.query(Concept_Relation, Concept).join(
            Concept, Concept.concept_id == Concept_Relation.to_concept_id
        ).filter(
            Concept_Relation.from_concept_id == new_concept_id,
            Concept_Relation.to_concept_id.in_(user_collected_ids),
            Concept_Relation.strength >= threshold
        )
        
        # 방향 2: (기존 개념) -> (새 개념)
        query2 = db.session.query(Concept_Relation, Concept).join(
            Concept, Concept.concept_id == Concept_Relation.from_concept_id
        ).filter(
            Concept_Relation.to_concept_id == new_concept_id,
            Concept_Relation.from_concept_id.in_(user_collected_ids),
            Concept_Relation.strength >= threshold
        )
        
        # 결과 합치기
        new_connections = []
        seen = set()
        
        for relation, connected_concept in query1.all():
            if connected_concept.name not in seen:
                seen.add(connected_concept.name)
                new_connections.append({
                    'concept_id': connected_concept.concept_id,
                    'name': connected_concept.name,
                    'strength': relation.strength,
                    'relation_type': relation.relation_type
                })
        
        for relation, connected_concept in query2.all():
            if connected_concept.name not in seen:
                seen.add(connected_concept.name)
                new_connections.append({
                    'concept_id': connected_concept.concept_id,
                    'name': connected_concept.name,
                    'strength': relation.strength,
                    'relation_type': relation.relation_type
                })
        
        return new_connections
    
    @staticmethod
    def remove_collection(user_id, concept_id):
        """
        개념 수집 취소
        
        Args:
            user_id (int): 사용자 ID
            concept_id (int): 개념 ID
            
        Returns:
            str: 제거된 개념 이름
            
        Raises:
            NotFoundError: 수집된 개념을 찾을 수 없음
        """
        collection = User_Collection.query.filter_by(
            user_id=user_id,
            concept_id=concept_id
        ).first()
        
        if not collection:
            raise NotFoundError('수집된 개념', concept_id)
        
        concept_name = collection.concept.name
        db.session.delete(collection)
        db.session.commit()
        
        return concept_name
    
    @staticmethod
    def get_user_collections(user_id, sort='collected_at', order='desc'):
        """
        사용자의 수집 개념 목록 조회
        
        Args:
            user_id (int): 사용자 ID
            sort (str): 정렬 기준 ('collected_at', 'name')
            order (str): 정렬 순서 ('asc', 'desc')
            
        Returns:
            list: 개념 객체 리스트
        """
        query = db.session.query(Concept).join(
            User_Collection,
            Concept.concept_id == User_Collection.concept_id
        ).filter(
            User_Collection.user_id == user_id
        )
        
        # 정렬
        if sort == 'collected_at':
            sort_column = User_Collection.collected_at
        else:
            sort_column = Concept.name
        
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        return query.all()


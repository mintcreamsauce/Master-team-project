"""
인증 서비스

사용자 인증 관련 비즈니스 로직을 처리합니다.
"""

from app.extensions import db
from app.models.user import User
from app.models.relations import User_Collection, Concept_Relation
from app.utils.exceptions import DuplicateEntryError, UnauthorizedError


class AuthService:
    """인증 관련 비즈니스 로직"""
    
    @staticmethod
    def register_user(username, email, password):
        """
        새 사용자 등록
        
        Args:
            username (str): 사용자명
            email (str): 이메일
            password (str): 비밀번호 (평문)
            
        Returns:
            User: 생성된 사용자 객체
            
        Raises:
            DuplicateEntryError: 중복된 사용자명 또는 이메일
        """
        # 중복 확인
        if User.query.filter_by(username=username).first():
            raise DuplicateEntryError('이미 사용 중인 사용자명입니다.', 'username')
        
        if User.query.filter_by(email=email).first():
            raise DuplicateEntryError('이미 사용 중인 이메일입니다.', 'email')
        
        # 사용자 생성
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate(username, password):
        """
        사용자 인증
        
        Args:
            username (str): 사용자명
            password (str): 비밀번호 (평문)
            
        Returns:
            User: 인증된 사용자 객체
            
        Raises:
            UnauthorizedError: 인증 실패
        """
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            raise UnauthorizedError('사용자명 또는 비밀번호가 올바르지 않습니다.')
        
        return user
    
    @staticmethod
    def get_user_stats(user_id):
        """
        사용자 통계 조회
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            dict: 통계 정보
        """
        # 수집한 개념 수
        collected_count = User_Collection.query.filter_by(user_id=user_id).count()
        
        # 수집한 개념들의 ID
        collected_concept_ids = db.session.query(User_Collection.concept_id).filter(
            User_Collection.user_id == user_id
        ).all()
        collected_concept_ids = {c_id[0] for c_id in collected_concept_ids}
        
        # 총 연결 수
        total_connections = 0
        strong_connections = 0
        
        if collected_concept_ids:
            relations = Concept_Relation.query.filter(
                Concept_Relation.from_concept_id.in_(collected_concept_ids),
                Concept_Relation.to_concept_id.in_(collected_concept_ids)
            ).all()
            
            total_connections = len(relations)
            strong_connections = sum(1 for r in relations if r.strength >= 6)
        
        return {
            'collected_concepts': collected_count,
            'total_connections': total_connections,
            'strong_connections': strong_connections
        }


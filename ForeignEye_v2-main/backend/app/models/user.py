"""
User 모델

사용자 계정 정보를 저장하고 인증 기능을 제공합니다.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """
    사용자 모델
    
    Attributes:
        user_id (int): 사용자 ID (Primary Key)
        username (str): 사용자명 (Unique)
        email (str): 이메일 (Unique)
        password_hash (str): 해싱된 비밀번호
        created_at (datetime): 계정 생성 시각
        collections (relationship): 사용자가 수집한 개념들
    """
    
    __tablename__ = 'User'
    
    # 컬럼 정의
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    
    # 관계 정의
    collections = db.relationship(
        'User_Collection',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )
    
    # 비밀번호 관리 메서드
    def set_password(self, password):
        """
        비밀번호를 해싱하여 저장
        
        Args:
            password (str): 평문 비밀번호
        """
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password):
        """
        비밀번호 검증
        
        Args:
            password (str): 검증할 평문 비밀번호
            
        Returns:
            bool: 비밀번호 일치 여부
        """
        return check_password_hash(self.password_hash, password)
    
    # 시리얼라이저
    def to_dict(self, include_stats=False):
        """
        딕셔너리로 변환 (JSON 직렬화용)
        
        Args:
            include_stats (bool): 통계 정보 포함 여부
            
        Returns:
            dict: 사용자 정보
        """
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() + 'Z'
        }
        
        if include_stats:
            # 통계 정보 추가 (필요시 서비스 레이어에서 계산)
            data['stats'] = {
                'collected_concepts': len(self.collections)
            }
        
        return data
    
    def __repr__(self):
        """디버깅용 문자열 표현"""
        return f'<User {self.username}>'


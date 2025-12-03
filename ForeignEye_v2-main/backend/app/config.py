"""
Flask 애플리케이션 설정 모듈

환경별(개발/프로덕션/테스트) 설정 클래스를 제공합니다.
.env 파일의 환경 변수를 사용합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """기본 설정 클래스"""
    
    # Flask 기본 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database 설정
    DB_USER = os.getenv('DB_USER', 'foreigneye_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '1234')
    DB_HOST = os.getenv('DB_HOST', 'db')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'foreigneye_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'connect_args': {'ssl': False}
    }
    
    # CORS 설정 (개발 단계에서는 모든 도메인 허용)
    CORS_ORIGINS = '*'
    
    # Rate Limiting 설정
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # API Keys
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1시간
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30일
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/techexplained.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False
    
    # JWT 프로덕션 설정
    JWT_COOKIE_SECURE = True  # HTTPS only
    JWT_COOKIE_CSRF_PROTECT = False  # JWT는 CSRF 보호 불필요
    
    # CORS 프로덕션 설정 (실제 도메인으로 변경 필요)
    CORS_ORIGINS = [
        'https://www.techexplained.com',
        'https://techexplained.com'
    ]
    
    # 프로덕션에서는 환경 변수 필수 검증
    @classmethod
    def validate_production_config(cls):
        """프로덕션 필수 환경 변수 검증"""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DB_PASSWORD',
            'GNEWS_API_KEY',
            'OPENROUTER_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"프로덕션 환경에서 필수 환경 변수가 누락되었습니다: {', '.join(missing_vars)}"
            )


class TestingConfig(Config):
    """테스트 환경 설정"""
    DEBUG = True
    TESTING = True
    
    # 테스트용 In-Memory SQLite 데이터베이스
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Rate Limiting 비활성화
    RATELIMIT_ENABLED = False
    
    # JWT 테스트 설정
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5분


def get_config(config_name=None):
    """
    설정 객체 반환
    
    Args:
        config_name (str): 'development', 'production', 'testing' 중 하나
                          None이면 FLASK_ENV 환경 변수 사용
    
    Returns:
        Config: 설정 클래스 객체
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    
    # 프로덕션 환경이면 검증
    if config_name == 'production':
        ProductionConfig.validate_production_config()
    
    return config_class


# [M1 감사 추가] 연결 풀 재활용 및 SQL 디버깅 활성화
SQLALCHEMY_POOL_RECYCLE=300
SQLALCHEMY_ECHO=True 

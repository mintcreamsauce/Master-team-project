"""
Flask 애플리케이션 팩토리 (v2.3 M1 최종본 - Health 포함)
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS

from flask import current_app

from app.config import get_config
from app.extensions import db, jwt, limiter, migrate, celery_app, get_neo4j_driver
from app.cli import seed_db_command

def create_app(config_name=None):
    app = Flask(__name__)
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    register_cli_commands(app)
    
    celery_app.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND')
    )
    celery_app.conf.update(app.config.get('CELERY_CONFIG', {}))
    
    initialize_extensions(app)
    setup_cors(app)
    register_blueprints(app)
    register_error_handlers(app)
    setup_logging(app)
    register_cli_commands(app)
    
    app.logger.info(f'ForeignEye v2.3 앱 시작 (환경: {config_name or "development"})')
    return app

def initialize_extensions(app):
    """Flask 확장 초기화"""
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db) # Flask-Migrate 초기화

    # Neo4j 드라이버 초기화 및 인덱스 생성 (P5 방어)
    with app.app_context():
        try:
            driver = get_neo4j_driver()
            driver.verify_connectivity()
            driver.execute_query(
                "CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name)",
                database_=app.config.get("NEO4J_DATABASE", "neo4j")
            )
            app.logger.info("Neo4j 드라이버 연결 성공 및 'concept_name_index' 보장됨.")
        except Exception as e:
            app.logger.error(f"Neo4j 드라이버 연결 실패. .env 파일을 확인하세요. 오류: {e}")

def setup_cors(app):
    """CORS 설정"""
    CORS(
        app,
        origins=app.config.get('CORS_ORIGINS', []),
        supports_credentials=True,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        expose_headers=['Authorization']
    )

def register_blueprints(app):
    """블루프린트 등록"""
    # [M1 수정] 'health' 블루프린트 임포트
    from app.routes import auth, articles, concepts, collections, knowledge_map, search, health
    
    api_prefix = '/api/v1'
    
    app.register_blueprint(auth.bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(articles.bp, url_prefix=f'{api_prefix}/articles')
    app.register_blueprint(concepts.bp, url_prefix=f'{api_prefix}/concepts')
    app.register_blueprint(collections.bp, url_prefix=f'{api_prefix}/collections')
    app.register_blueprint(knowledge_map.bp, url_prefix=f'{api_prefix}/knowledge-map')
    app.register_blueprint(search.bp, url_prefix=f'{api_prefix}/search')
    # [M1 수정] 'health' 블루프린트 등록
    app.register_blueprint(health.bp, url_prefix=f'{api_prefix}/health')
    
    app.logger.info('블루프린트 등록 완료')

def register_error_handlers(app):
    """전역 에러 핸들러 등록"""
    from app.utils.exceptions import APIException
    from app.utils.response import error_response
    
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        return error_response(code=e.code, message=e.message, status=e.status_code, details=e.details)
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response(code='NOT_FOUND', message='요청한 리소스를 찾을 수 없습니다.', status=404)
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return error_response(code='METHOD_NOT_ALLOWED', message='허용되지 않은 HTTP 메서드입니다.', status=405)
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        return error_response(code='RATE_LIMIT_EXCEEDED', message='요청이 너무 많습니다. 잠시 후 다시 시도해주세요.', status=429)
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        app.logger.error(f'Internal error: {e}', exc_info=True)
        return error_response(code='INTERNAL_ERROR', message='서버 내부 오류가 발생했습니다.', status=500)
    
    app.logger.info('에러 핸들러 등록 완료')

def setup_logging(app):
    """로깅 설정"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/foreigneye.log'),
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 10)
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        app.logger.info('로깅 설정 완료')

def register_cli_commands(app):
    """CLI 명령 등록"""
    @app.cli.command('create-admin')
    def create_admin():
        """관리자 계정 생성 (M1에서 유지)"""
        from app.models.user import User
        username = input('관리자 사용자명: ')
        email = input('이메일: ')
        password = input('비밀번호: ')
        with app.app_context():
            if User.query.filter_by(username=username).first():
                print('✗ 이미 존재하는 사용자명입니다.')
                return
            admin = User(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f'✓ 관리자 계정이 생성되었습니다: {username}')
    
    app.cli.add_command(seed_db_command)        
    app.logger.info('CLI 명령 등록 완료 (Flask-Migrate 사용)')

def test_db_connection():
    try:
        with current_app.app_context():
            result = db.session.execute("SELECT 1").fetchone()
            current_app.logger.info("DB 연결 성공: %s", result)
    except Exception as e:
        current_app.logger.error("DB 연결 실패: %s", e)
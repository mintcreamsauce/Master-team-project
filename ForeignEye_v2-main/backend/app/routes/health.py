"""
Health Check API 라우트
"""
import time
from flask import Blueprint, current_app
from app.extensions import db, get_neo4j_driver
from app.utils.response import success_response, error_response
from sqlalchemy import text # [M1 수정] text() 함수 임포트

bp = Blueprint('health', __name__)

@bp.route('', methods=['GET'])
def get_health_check():
    """
    서비스 상태 확인 API (MySQL, Neo4j 연결 테스트)
    
    GET /api/v1/health
    """
    start_time = time.time()
    
    status = {
        'service': 'ForeignEye-Backend',
        'status': 'OK',
        'checks': {}
    }
    
    # 1. MySQL (SoT) 연결 테스트
    try:
        # [M1 수정] SQLAlchemy 2.0 호환을 위해 text()로 감쌉니다.
        db.session.execute(text('SELECT 1'))
        status['checks']['mysql_sot'] = {
            'status': 'OK',
            'message': 'MySQL (SoT) connection successful.'
        }
    except Exception as e:
        status['status'] = 'ERROR'
        status['checks']['mysql_sot'] = {
            'status': 'ERROR',
            'message': f'MySQL (SoT) connection failed: {str(e)}'
        }
        current_app.logger.error(f"Health Check: MySQL Error: {e}")

    # 2. Neo4j (View) 연결 테스트
    try:
        driver = get_neo4j_driver()
        driver.verify_connectivity()
        status['checks']['neo4j_view'] = {
            'status': 'OK',
            'message': 'Neo4j (View) connection successful.'
        }
    except Exception as e:
        status['status'] = 'ERROR'
        status['checks']['neo4j_view'] = {
            'status': 'ERROR',
            'message': f'Neo4j (View) connection failed: {str(e)}'
        }
        current_app.logger.error(f"Health Check: Neo4j Error: {e}")

    status['response_time_ms'] = round((time.time() - start_time) * 1000)
    
    if status['status'] == 'OK':
        return success_response(status)
    else:
        # 서비스 자체에 오류가 있으므로 HTTP 503 (Service Unavailable) 반환
        return error_response('SERVICE_UNAVAILABLE', 'One or more backend services are down.', 503, details=status)

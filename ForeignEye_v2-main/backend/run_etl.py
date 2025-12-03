"""
M1(캡스톤) 데모 데이터 수동 ETL 트리거 스크립트
"""
import os
from app import create_app

def trigger_etl():
    """
    Celery 워커에게 ETL 작업을 지시합니다.
    """
    print("M1(캡스톤) 데모용 ETL 작업을 Celery 워커에게 요청합니다...")

    try:
        # [M1] app/celery_tasks.py에 정의된 '메인 ETL 작업'을 임포트
        from app.celery_tasks import run_main_etl_task
        
        # [M1] ETL 실행 요청 (기본 3개)
        print("ETL 작업 (run_main_etl_task)을 요청합니다...")
        run_main_etl_task.delay(max_articles=3)
        
        print("\n--- [성공] ---")
        print("Celery 워커에게 ETL 작업을 성공적으로 요청했습니다.")
        print("지금 즉시 'docker-compose logs -f celery-worker' 명령어로")
        print("백그라운드 처리 로그를 확인하세요.")
        print("----------------")
        
    except ImportError:
        print("\n--- [오류] ---")
        print("'run_main_etl_task'를 임포트할 수 없습니다.")
        print("app/celery_tasks.py 파일이 올바른지 확인하세요.")
        print("----------------")


if __name__ == "__main__":
    # Flask 앱 컨텍스트가 필요할 수 있으므로, 앱을 생성합니다.
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        trigger_etl()

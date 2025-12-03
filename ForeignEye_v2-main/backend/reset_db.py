import os
from app import create_app
from app.extensions import db
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 앱 컨텍스트 생성
# FLASK_ENV를 'development' 또는 적절한 환경으로 설정
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

with app.app_context():
    print("데이터베이스 초기화를 시작합니다...")

    # 모든 테이블 삭제
    db.drop_all()
    print("...모든 테이블이 삭제되었습니다.")

    # 모든 테이블 다시 생성
    db.create_all()
    print("...모든 테이블이 새로 생성되었습니다.")

    print("데이터베이스 초기화 완료.")
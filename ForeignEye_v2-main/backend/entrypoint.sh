#!/bin/bash

# 1. DB 연결 대기
until mysql --ssl=0 -h db -u foreigneye_user -p1234 -P 3306 foreigneye_db -e "SELECT 1"; do
  echo "DB 대기 중..."
  sleep 5
done
echo "✅ DB 연결 확인."

# 2. (신규) DB 테이블 자동 생성 (Migrations)
echo "🚀 DB 마이그레이션(테이블 생성) 시작..."
flask db upgrade
echo "✅ DB 마이그레이션 완료."

# 3. (신규) 테스트 사용자(user_id=1) 자동 생성 (Seed)
echo "🌱 DB 시딩(테스트 사용자 생성) 시작..."
flask seed-db
echo "✅ DB 시딩 완료."

# 4. Gunicorn (메인 앱) 실행
echo "🚀 Gunicorn을 시작합니다..."
exec "$@"
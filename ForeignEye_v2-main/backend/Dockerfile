# 1. 기본 이미지: 안정적인 Python 3.11 사용
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y default-mysql-client iputils-ping && rm -rf /var/lib/apt/lists/*

# 4. 앱 코드 복사
COPY . .

# 5. 프로덕션 서버 실행 (Gunicorn)
EXPOSE 8000
# ★★★ CMD 수정: 'app:create_app(...)' 대신 'run:app'을 사용 ★★★
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
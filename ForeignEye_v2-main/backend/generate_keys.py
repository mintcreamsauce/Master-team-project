import secrets

def generate_keys():
    """
    .env.prod 파일에 사용할 강력한 무작위 보안 키를 생성합니다.
    """
    
    # 1. Flask SECRET_KEY 및 JWT_SECRET_KEY 용 (64자 16진수 문자열)
    # 32바이트의 무작위 데이터를 16진수로 변환합니다.
    flask_secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    
    # 2. MySQL DB_PASSWORD 용 (32자 URL-safe 문자열)
    # 24바이트의 무작위 데이터를 URL-safe Base64로 인코딩합니다.
    # (A-Z, a-z, 0-9, -, _ 포함)
    db_password = secrets.token_urlsafe(24)
    
    # 3. MySQL ROOT_PASSWORD 용 (별도 생성)
    root_password = secrets.token_urlsafe(24)

    print("======================================================================")
    print("  ForeignEye 프로덕션(.env.prod) 보안 키 생성기")
    print("======================================================================")
    print("\n아래 값들을 복사하여 .env.prod 파일에 붙여넣으세요.\n")
    
    print(f"FLASK_ENV=production")
    print(f"FLASK_DEBUG=False")
    print(f"SECRET_KEY={flask_secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret_key}")
    
    print("\n# --- DB 설정 ---")
    print(f"DB_USER=foreigneye_user")
    print(f"DB_PASSWORD={db_password}")
    print(f"DB_HOST=db")
    print(f"DB_PORT=3306")
    print(f"DB_NAME=foreigneye_db")
    
    print("\n======================================================================")
    print("\n[docker-compose.yml 용 DB 루트 비밀번호]\n")
    print(f"MYSQL_ROOT_PASSWORD={root_password}")
    print(f"MYSQL_DATABASE=foreigneye_db")
    print(f"MYSQL_USER=foreigneye_user")
    print(f"MYSQL_PASSWORD={db_password}")
    print("\n======================================================================")

if __name__ == "__main__":
    generate_keys()
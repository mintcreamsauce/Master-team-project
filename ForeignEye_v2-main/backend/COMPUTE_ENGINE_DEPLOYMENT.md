# 🚀 ForeignEye Backend - Google Compute Engine 배포 가이드

## 📋 목차
1. [사전 준비 사항](#사전-준비-사항)
2. [Compute Engine VM 프로비저닝](#compute-engine-vm-프로비저닝)
3. [방화벽 및 네트워크 설정](#방화벽-및-네트워크-설정)
4. [서버 환경 구성](#서버-환경-구성)
5. [애플리케이션 배포](#애플리케이션-배포)
6. [서비스 자동화 (systemd)](#서비스-자동화-systemd)
7. [HTTPS 및 프록시 설정 (선택)](#https-및-프록시-설정-선택)
8. [배포 후 확인](#배포-후-확인)
9. [유지 보수 및 모니터링](#유지-보수-및-모니터링)
10. [문제 해결](#문제-해결)

---

## 🎯 사전 준비 사항
- Google Cloud 프로젝트 및 결제 활성화
- Cloud SDK(`gcloud`) 설치 및 로그인
- Docker 설치 여부 (선택적)
- MySQL(Cloud SQL 또는 자체 DB) 자격 증명 확보
- `.env.production` 생성에 필요한 모든 비밀키(SECRET_KEY, JWT_SECRET_KEY, DB_PASSWORD 등)

> **명령 실행 위치 안내**
> - `powershell` 코드 블록: **Windows 로컬 PC**에서 실행 (Google Cloud SDK 설치 필요)
> - `bash` 코드 블록: **Compute Engine VM 내부**에서 실행 (SSH 접속 후)
> - 명령어에 등장하는 변수는 환경에 맞게 치환하세요.

**gcloud 초기 설정 (로컬 PowerShell):**
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set compute/region asia-northeast3
gcloud config set compute/zone asia-northeast3-a
```

---

## 🖥️ Compute Engine VM 프로비저닝

### 1. 인스턴스 생성 (로컬 PowerShell)
```powershell
gcloud compute instances create foreigneye-backend `
  --machine-type=e2-medium `
  --image-family=ubuntu-22-04-lts `
  --image-project=ubuntu-os-cloud `
  --boot-disk-size=30GB `
  --tags=foreigneye-backend `
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

**권장 스펙:**
- **개발/스테이징:** `e2-small` (2vCPU, 2GB RAM)
- **프로덕션 초반:** `e2-medium` (2vCPU, 4GB RAM)
- 트래픽 증가 시 `e2-standard-4` 이상 검토

### 2. SSH 접속 (로컬 PowerShell)
```powershell
gcloud compute ssh foreigneye-backend
```

---

## 🔐 방화벽 및 네트워크 설정

### 1. HTTP/HTTPS 포트 허용 (로컬 PowerShell)
```powershell
gcloud compute firewall-rules create foreigneye-allow-http `
  --direction=INGRESS --priority=1000 --network=default `
  --action=ALLOW --rules=tcp:80,tcp:443 --source-ranges=0.0.0.0/0 `
  --target-tags=foreigneye-backend
```

### 2. SSH, MySQL 접속(선택)
- SSH는 기본 허용 (22번)
- 원격 MySQL 접속 필요 시 별도 방화벽 규칙 설정

### 3. 정적 IP 할당 (선택, 로컬 PowerShell)
```powershell
gcloud compute addresses create foreigneye-ip --region=asia-northeast3
gcloud compute instances update foreigneye-backend `
  --zone=asia-northeast3-a `
  --network-interface=network-tier=PREMIUM,address=foreigneye-ip
```

---

## 🛠️ 서버 환경 구성

### 1. 시스템 패키지 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 필수 패키지 설치
```bash
sudo apt install -y python3 python3-pip python3-venv git build-essential \
  libmysqlclient-dev pkg-config nginx ufw
```

### 3. (선택) Docker 설치
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```
> Docker를 사용할 경우 Dockerfile 기반 배포가 용이합니다.

### 4. 프로젝트 코드 배포
#### 옵션 A: Git 클론
```bash
cd /srv
sudo git clone https://github.com/YOUR_ORG/ForeignEye.git
sudo chown -R $USER:$USER ForeignEye
cd ForeignEye/backend
```

#### 옵션 B: 아카이브 업로드
```bash
scp -r ./ForeignEye/backend foreigneye-backend:~/
```

### 5. 가상환경 생성 및 의존성 설치
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. 환경 변수 파일 설정
```bash
cp .env.production.example .env.production
nano .env.production
```
**필수 변경 항목:**
- `SECRET_KEY`, `JWT_SECRET_KEY`: 64자 무작위 HEX (예: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DB_HOST`: Cloud SQL Public IP 또는 내장 MySQL 주소
- `DB_PASSWORD`: 강력한 비밀번호 (16자 이상)
- `CORS_ORIGINS`: 실제 프런트엔드 도메인 목록

### 7. 데이터베이스 연결 테스트
```bash
mysql -h your-db-host -u foreigneye_user -p foreigneye_db
```

---

## 📦 애플리케이션 배포

### 1. 초기 데이터베이스 세팅 (선택)
```bash
source venv/bin/activate
python reset_db.py  # 기존 데이터 초기화
python -m etl.run   # ETL 파이프라인 실행 (선택)
```

### 2. Gunicorn 수동 실행 테스트
```bash
source venv/bin/activate
export FLASK_ENV=production
export FLASK_DEBUG=False
export $(grep -v '^#' .env.production | xargs -d '\n')

gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### 3. (선택) Docker 배포
```bash
# 로컬에서 이미지 빌드
docker build -t foreigneye-backend .

# 컨테이너 실행
docker run -d --name foreigneye-backend \
  --env-file .env.production \
  -p 8000:8000 foreigneye-backend
```

---

## ⚙️ 서비스 자동화 (systemd)

### 1. 서비스 파일 생성
`/etc/systemd/system/foreigneye.service`
```ini
[Unit]
Description=ForeignEye Backend Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/srv/ForeignEye/backend
EnvironmentFile=/srv/ForeignEye/backend/.env.production
ExecStart=/srv/ForeignEye/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. 서비스 활성화 및 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable foreigneye.service
sudo systemctl start foreigneye.service
sudo systemctl status foreigneye.service
```

### 3. 로그 확인
```bash
journalctl -u foreigneye.service -f
```

---

## 🔒 HTTPS 및 프록시 설정 (선택)
Nginx를 리버스 프록시로 사용하여 SSL 적용을 권장합니다.

### 1. Nginx 사이트 설정 `/etc/nginx/sites-available/foreigneye`
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 사이트 활성화 및 Nginx 재시작
```bash
sudo ln -s /etc/nginx/sites-available/foreigneye /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Let’s Encrypt SSL 인증서 발급
```bash
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## ✅ 배포 후 확인

### 1. 헬스 체크
```bash
curl http://yourdomain.com/api/v1/articles
```

### 2. 로그인/회원가입 테스트
```bash
curl -X POST http://yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"prodtest","email":"prod@test.com","password":"Test123!","password_confirm":"Test123!"}'

curl -X POST http://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"prodtest","password":"Test123!"}'
```

### 3. 로그 모니터링
```bash
journalctl -u foreigneye.service --since "10 minutes ago"
sudo tail -f logs/techexplained.log  # 앱 내부 로그 사용 시
```

### 4. MySQL 연결 상태
```bash
mysql -h your-db-host -u foreigneye_user -p foreigneye_db -e "SHOW PROCESSLIST;"
```

---

## 🔄 유지 보수 및 모니터링

### 1. 시스템 업데이트 (월 1회 권장)
```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart foreigneye.service
```

### 2. 로그 로테이션 구성 (선택)
`/etc/logrotate.d/foreigneye`
```bash
/var/log/foreigneye/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload foreigneye.service > /dev/null 2>/dev/null || true
    endscript
}
```

### 3. 백업 전략
- Cloud SQL 사용 시 자동 백업 활성화
- 자체 MySQL: `mysqldump` cron job 설정
- 애플리케이션 로그: Cloud Storage 연동 검토

### 4. 모니터링 도구 추천
- Google Cloud Monitoring / Logging
- Prometheus + Grafana (선택)
- Sentry (에러 추적)

---

## 🆘 문제 해결

| 증상 | 해결 방법 |
|------|------------|
| 서비스 접속 안 됨 | `systemctl status foreigneye.service`, `journalctl -u foreigneye.service` 확인 |
| 502/504 Gateway 오류 | Nginx ↔ Gunicorn 연결 확인, Gunicorn worker 수 증가 |
| DB 연결 실패 | `.env.production` DB_HOST/DB_PASSWORD 확인, 보안 그룹 검토 |
| CORS 오류 | `.env.production`의 `CORS_ORIGINS` 확인 후 재시작 |
| SSL 인증 실패 | DNS 설정 확인, `certbot renew --dry-run` 테스트 |

---

## 📝 체크리스트

- [ ] Compute Engine VM 생성 및 SSH 접속 완료
- [ ] 방화벽 규칙(HTTP/HTTPS) 설정
- [ ] 프로젝트 코드 배포 및 가상환경 구성
- [ ] `.env.production` 작성 및 민감 정보 설정
- [ ] `gunicorn` 수동 테스트 성공
- [ ] (선택) systemd 서비스 등록 및 자동 시작 확인
- [ ] Nginx/SSL 설정 (선택)
- [ ] API 기본 동작 확인 (회원가입/로그인/기사 조회)
- [ ] 모니터링 및 백업 전략 수립

---

## 📚 추가 참고 문서
- [Compute Engine 공식 문서](https://cloud.google.com/compute/docs)
- [Gunicorn 배포 가이드](https://docs.gunicorn.org/en/stable/deploy.html)
- [Nginx 리버스 프록시 설정](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Let’s Encrypt Certbot](https://certbot.eff.org)

---

**ForeignEye DevOps Team**  
마지막 업데이트: 2025-11-13

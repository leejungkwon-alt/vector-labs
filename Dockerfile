# Python 3.12 슬림 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 전체 복사
COPY . .

# 컨테이너 외부로 노출할 포트 설정
EXPOSE 8000

# Uvicorn 서버를 통해 FastAPI 애플리케이션 구동 (엔트리포인트: app.main:app)
# Step 4-B: non-root 사용자로 실행
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
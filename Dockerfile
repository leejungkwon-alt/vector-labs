FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 비root 사용자로 실행 (컨테이너 탈출/파일 변조 피해 최소화)
RUN groupadd --system --gid 10001 app \
 && useradd  --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --chown=app:app . .

# SQLite 개발/테스트용 쓰기 경로. 운영은 SAJU_DATABASE_URL(PostgreSQL) 사용.
RUN mkdir -p /app/data && chown app:app /app/data

USER app

EXPOSE 8000

# exec 형식: SIGTERM 이 uvicorn 에 직접 전달되어 Cloud Run 에서 정상 종료됨
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

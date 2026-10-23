import os

# [테스트 전용 설정]
# pytest 실행 시 수백 개의 요청을 아주 빠르게 보내므로, 
# 기본 Rate Limit(120회/분)에 걸려 429 에러가 나는 것을 방지합니다.
os.environ["SAJU_RATE_LIMIT_MAX"] = "10000"
os.environ["SAJU_RATE_LIMIT_WINDOW"] = "60"

# 테스트는 항상 SQLite 로 격리. PostgreSQL 백엔드 테스트는 SAJU_TEST_DATABASE_URL 로 명시 실행.
os.environ.pop("SAJU_DATABASE_URL", None)

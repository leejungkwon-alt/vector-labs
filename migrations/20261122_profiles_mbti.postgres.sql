-- ============================================================================
-- 사주×MBTI 대조 — profiles.mbti 컬럼 추가 (PostgreSQL 전용)
--
-- ⚠️ 이 파일은 "작성만" 한 것이며 이번 단계에서 실행하지 않았다(운영 DB 접속 금지).
--
-- 실제 반영 경로(코드 확인 결과)
--   app/auth/repository.py::PostgresRepository._init_schema 가 **앱 기동 시**
--   아래와 동일한 `ALTER TABLE profiles ADD COLUMN IF NOT EXISTS mbti TEXT` 를
--   실행한다(advisory lock 7340301 로 다중 인스턴스 동시 기동 보호).
--   → SAJU_DATABASE_URL 로 PostgreSQL 을 쓰는 배포는 재배포(기동)만으로 반영된다.
--   → 별도 마이그레이션 도구/수동 적용은 **필수 아님**(백업 목적의 기본 SQL).
--
--   * 대상 테이블이 `profiles` 인 이유: 생년월일/성별 등 사주 입력과 같은 1:1 행이며
--     `users` 는 결제/티어 상태만 담는다.
--   * 컬럼 타입 TEXT (nullable): 자기신고 선택 입력. 미입력 = NULL(건너뜀).
--   * 기존 사용자 데이터: nullable 추가라 기본값 마이그레이션/테이블 재작성 없음.
--     기존 행은 mbti = NULL 이 되고 애플리케이션은 NULL 을 "미입력"으로 해석한다.
--   * 롤백: 아래 ROLLBACK 절 주석 해제 후 실행 (앱은 컬럼 부재 시에도 동작해야 함 —
--     단, 이 릴리스 이후 upsert SQL 이 mbti 컬럼을 참조하므로 함께 되돌려야 한다).
-- ============================================================================

BEGIN;

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS mbti TEXT;

-- 값 형식 보증(애플리케이션 Pydantic 검증의 2차 방어선)
--   ^[EI][NS][TF][JP]$  또는 NULL
ALTER TABLE profiles
    ADD CONSTRAINT profiles_mbti_format_chk
    CHECK (mbti IS NULL OR mbti ~ '^[EI][NS][TF][JP]$');

COMMIT;

-- 검증
--   SELECT column_name, data_type, is_nullable
--     FROM information_schema.columns
--    WHERE table_name = 'profiles' AND column_name = 'mbti';
--   SELECT count(*) AS null_mbti FROM profiles WHERE mbti IS NULL;  -- 기존 사용자 전원

-- ROLLBACK (필요 시에만, 앱 롤백과 함께)
-- BEGIN;
--   ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_mbti_format_chk;
--   ALTER TABLE profiles DROP COLUMN IF EXISTS mbti;
-- COMMIT;

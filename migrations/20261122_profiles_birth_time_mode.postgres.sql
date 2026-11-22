-- ============================================================================
-- profiles.birth_time_mode 추가 (PostgreSQL) — 핫픽스 보완
--
-- ⚠️ 작성만 함. 실행하지 않았다(운영 접속 금지).
--
-- 왜 필요한가
--   앱의 PostgresRepository._init_schema 가 이 ALTER 를 수행하지 않아
--   Neon(Postgres) 운영 DB 에 컬럼이 생기지 않았고, upsert SQL 이
--   birth_time_mode 를 참조해 "column does not exist" 로 저장이 실패했다.
--   현재 코드는 기동 시 런타임 ALTER 를 수행하지만, DBA 가 수동/선행 적용할 수
--   있도록 동일 SQL 을 파일로 남긴다.
-- ============================================================================

BEGIN;

-- 다중 인스턴스 동시 적용 대비(앱의 _init_schema 와 같은 advisory lock 키)
SELECT pg_advisory_xact_lock(7340301);

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS birth_time_mode TEXT;

COMMIT;

-- 검증
--   SELECT column_name, data_type, is_nullable
--     FROM information_schema.columns
--    WHERE table_schema = current_schema()
--      AND table_name = 'profiles'
--      AND column_name = 'birth_time_mode';

-- ROLLBACK (신중히; 구버전 코드는 이 컬럼을 읽지 않는다)
-- ALTER TABLE profiles DROP COLUMN IF EXISTS birth_time_mode;

-- ============================================================================
-- birth_time 덮어쓰기 사고 — 영향 규모 추정 / 운영 스키마 확인용 읽기 전용 SQL
--
-- ⚠️ 작성만 함. 이번 작업에서 실행하지 않았다(운영 DB 접속 금지).
--    사용자가 직접 운영 DB(Postgres 또는 SQLite)에서 실행한다.
--    모두 SELECT 만 사용한다(쓰기/DDL 없음).
-- ============================================================================

-- ---------------------------------------------------------------------------
-- (0) 현재 코드 기준 스키마와 운영 DB 가 같은지 확인
--     birth_time_mode 컬럼은 이번 핫픽스에서 **새로 추가**한 것이다.
--     0a2263b(수정 전) 코드에는 이 컬럼이 없었다 → 운영에 없다면 정상.
-- ---------------------------------------------------------------------------

-- (0-a) 운영 profiles 컬럼 목록 (Postgres)
SELECT column_name, data_type, is_nullable
  FROM information_schema.columns
 WHERE table_schema = current_schema()
   AND table_name = 'profiles'
 ORDER BY ordinal_position;

-- (0-b) 같은 확인 (SQLite: 운영이 파일 DB 인 경우)
-- PRAGMA table_info(profiles);

-- (0-c) birth_time_mode 컬럼 존재 여부만 (Postgres)
SELECT EXISTS (
         SELECT 1 FROM information_schema.columns
          WHERE table_schema = current_schema()
            AND table_name = 'profiles'
            AND column_name = 'birth_time_mode'
       ) AS has_birth_time_mode;

-- ---------------------------------------------------------------------------
-- (1) 핵심: birth_time 이 NULL 인 프로필 수 (= /report 422 가 나는 사용자)
--     birth_time_mode 컬럼이 아직 없다면 (1)/(2)/(3) 의 mode 관련 절만 빼고 실행.
-- ---------------------------------------------------------------------------

SELECT count(*) AS total_profiles,
       count(*) FILTER (WHERE birth_time IS NULL)                        AS null_birth_time,
       count(*) FILTER (WHERE birth_time_mode IS NULL)                   AS null_mode,
       count(*) FILTER (WHERE birth_time IS NULL AND birth_time_mode IS NULL) AS null_both
  FROM profiles;

-- (1-b) birth_date 는 있는데 birth_time 만 NULL (= 복구 대상 핵심군)
SELECT count(*) AS recoverable_by_time_entry
  FROM profiles
 WHERE birth_date IS NOT NULL
   AND birth_time IS NULL;

-- ---------------------------------------------------------------------------
-- (2) birth_time_mode 분포 (NULL 포함)
-- ---------------------------------------------------------------------------

SELECT COALESCE(birth_time_mode, '(NULL)') AS mode,
       count(*)                            AS profiles
  FROM profiles
 GROUP BY COALESCE(birth_time_mode, '(NULL)')
 ORDER BY profiles DESC;

-- (3) updated_at 기준 최근 분포 (최근 1일/7일/30일)
SELECT count(*) FILTER (WHERE updated_at >= (now() - interval '1 day'))  AS updated_1d,
       count(*) FILTER (WHERE updated_at >= (now() - interval '7 days')) AS updated_7d,
       count(*) FILTER (WHERE updated_at >= (now() - interval '30 days')) AS updated_30d,
       max(updated_at)                                                   AS last_updated
  FROM profiles;

-- (3-b) 영향군의 최근 수정 분포 (사고 유입 시점 추정)
SELECT date_trunc('day', updated_at::timestamptz) AS day,
       count(*)                                   AS profiles_with_null_time
  FROM profiles
 WHERE birth_time IS NULL
 GROUP BY 1
 ORDER BY 1 DESC
 LIMIT 30;

-- (4) 샘플 확인(개인정보 최소화: id 마스킹 없이 count 용도로만)
SELECT user_id, birth_date, birth_time, birth_time_mode, updated_at
  FROM profiles
 WHERE birth_time IS NULL
 ORDER BY updated_at DESC
 LIMIT 20;

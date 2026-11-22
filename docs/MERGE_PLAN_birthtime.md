# 병합 계획 — `fix/profile-birth-time-overwrite` ←→ `feat/mbti-contrast`

> 두 브랜치를 `main`(0a2263b)에서 갈라 작업했다.
> 핫픽스는 MBTI 코드를 포함하지 않으며, 병합 방향은 **`feat/mbti-contrast` 에 `fix/...` 를 먼저 병합**한 뒤 최종적으로 `main` 으로 가는 것을 권장한다(핫픽스는 별도로 `main` 에도 머지 가능).

## 0. 배포 전 체크리스트

- [ ] **운영 Cloud Run revision 이 `main`(0a2263b)과 동일 커밋인지 확인** — 레포에 기록 없음(`deploy.ps1:12,22` 는 타임스탬프 태그 + 워킹트리 빌드). 확인 전 "운영=main" 가정 금지.
- [ ] 핫픽스 단독 배포 시: `birth_time_mode` 컬럼은 **첫 기동 시점에 런타임 ALTER** 로 추가된다(SQLite/Postgres 모두). 롤백하면 구버전 코드는 컬럼을 읽지 않으므로 무해.
- [ ] `docs/BIRTHTIME_IMPACT_SQL.md` 로 `birth_time IS NULL` 사용자 수 확인.
- [ ] 프론트는 OTA/스토어 배포 필요(핫픽스의 화면 변경). 서버만 먼저 배포해도 422 증가는 없다(보존 로직이 먼저 안전).

## 1. 충돌 예상 지점

| # | 파일 | 핫픽스(`fix/...`) | MBTI 브랜치(`feat/mbti-contrast`) | 충돌 성격 |
|---|---|---|---|---|
| 1 | `app/auth/router.py` | `_PROFILE_KEYED_FIELDS = ("birth_date","birth_time","birth_time_mode")`, `apply_profile_key_presence()`, `_check_birth_time_combination()`, `upsert_my_profile` 에서 사용 | `upsert_my_profile` 안에서 `if "mbti" not in payload.model_fields_set: data.pop("mbti")` **인라인 로직** | **의미 중복**. 두 개의 "키 생략 보존" 구현이 공존 → 설정에 따라 한쪽이 무력화 |
| 2 | `app/schemas/auth.py` | `birth_time_mode` 필드 + `v_birth_time_mode` 검증, `ProfileResponse.birth_time_mode` | `mbti` 필드 + `normalize_mbti`/`MBTI_PATTERN`, `ProfileResponse.mbti` | 같은 클래스의 서로 다른 위치 → 자동 병합 가능하나 **필드 순서/validator 블록 인접**으로 textual 충돌 가능 |
| 3 | `app/auth/repository.py` | `_SCHEMA_STATEMENTS` 에 `birth_time_mode TEXT`, 런타임 ALTER 2곳(SQLite/Postgres), upsert SQL 파라미터 | `mbti TEXT`, 런타임 ALTER 2곳, upsert SQL(컬럼/SET/파라미터) **전부 다른 줄에 추가** → 자동 병합되지만 **파라미터 튜플 순서**가 깨지면 런타임 오류(테스트로 잡힘) | 중간 |
| 4 | `app/services/entitlements.py` | 변경 없음 | fail-closed, `ADDON_UNLOCKED_SECTIONS`, `is_section_rule_defined` | 없음 |
| 5 | `app/services/content/data/*/*.json` | 변경 없음 | `i18n_rule` 추가 | 없음 |
| 6 | `frontend/app/birth-input.tsx` | `handleNext` payload 3필드 + `deriveInitialForm`/`normalizeClock` + 주석 | MBTI 4토글 UI, `mbtiTouched` 조건부 payload, 상태 추가 | **높음** — 같은 함수(`handleNext`)·같은 return 블록. 반드시 수동 병합 |
| 7 | `frontend/types.ts` | 없음(핫픽스는 타입 변경 없음) | `SajuRequest.mbti` | 없음 |
| 8 | `frontend/src/locales/*.json` | 없음 | `birthInput.mbti*` 9키 | 없음(i18n 테스트 확장은 MBTI 브랜치에서 별도 커밋) |
| 9 | `frontend/app/(tabs)/home.tsx` | 없음(에러 유도 버튼은 제안만) | 렌더 함수 등 일부 수정 여부는 3단계에서 결정 | 낮음 |
| 10 | `tests/` | `test_profile_birth_time.py` (신규, `-f` 추적) | `test_profile_mbti.py`, `test_entitlement_coverage.py` | 없음(파일 분리) |

## 2. `router.py` 통합 방법 (핵심)

핫픽스의 헬퍼를 **단일 진입점**으로 유지하고, MBTI 브랜치의 인라인 로직을 제거해 필드 목록에 합류시킨다.

```python
# 병합 후 목표 상태 (feat/mbti-contrast 쪽에서 정리)
_PROFILE_KEYED_FIELDS = ("birth_date", "birth_time", "birth_time_mode", "mbti")

def apply_profile_key_presence(payload, data: dict) -> dict:
    fields_set = getattr(payload, "model_fields_set", set())
    for name in _PROFILE_KEYED_FIELDS:
        if name not in fields_set:
            data.pop(name, None)
    return data

@router.put("/me/profile", response_model=ProfileResponse)
def upsert_my_profile(payload: ProfilePayload, user=Depends(get_current_user)):
    data = apply_profile_key_presence(payload, payload.model_dump())
    fields_set = payload.model_fields_set
    if "birth_time" in fields_set and "birth_time_mode" in fields_set:
        _check_birth_time_combination(payload.birth_time_mode, payload.birth_time)
    ...  # 나머지 동일
```

- 삭제 대상: MBTI 브랜치의 `if "mbti" not in payload.model_fields_set: data.pop("mbti", None)` 블록.
- 의미 차이 주의: 핫픽스 레포는 **null 도 보존**(COALESCE), MBTI 레포는 **명시적 null = 삭제**. 병합 후에는 **핫픽스 스펙(null=보존)** 이 우선이며, MBTI 브랜치의 `test_explicit_null_clears_mbti` 는 "null=보존" 기대로 수정해야 한다. (`mbti` 를 지우고 싶으면 `""` 전송 = `normalize_mbti` → None → 보존이 아니라… → **별도 결정 필요**: mbti 삭제 UX 를 둘 경우 `clear_mbti: true` 같은 명시 플래그 권장)

## 3. `repository.py` 통합 방법

- upsert SQL 은 **컬럼 1개 = 파라미터 1개** 원칙으로 두 브랜치 모두 늘렸으므로, 병합 시
  `INSERT (... birth_time_mode, mbti, updated_at)` / `VALUES (... ?, ?, ?)` / `SET birth_time_mode=..., mbti=...` / 파라미터 튜플에 `data.get("birth_time_mode"), data.get("mbti")` 를 **`updated_at` 바로 앞** 순서로 맞춘다.
- 핫픽스의 noon 우선 규칙(`time_in = None if mode_in == "noon"`)과 `time_set` 분기는 그대로 유지하고, `mbti` 는 영향 없음.
- 런타임 ALTER: 핫픽스 `birth_time_mode`, MBTI `mbti` → 두 줄 모두 남긴다(둘 다 `if not in p_cols` / `IF NOT EXISTS`).

## 4. `birth-input.tsx` 통합 방법

- 충돌 해소 기준: **핫픽스의 3필드 항상 전송**을 유지하고, MBTI 는 `mbtiTouched` 조건부 규칙을 그 위에 얹는다.

```ts
const profileData: any = {
  birth_date: `${yyyy}-${mm}-${dd}`,   // 핫픽스: 항상 전송
  birth_time: timeString,              //   (시간 모름 = null, mode=noon)
  birth_time_mode: timeMode,
  birth_location: isCustomCity ? null : city,
  timezone_str: ..., longitude: finalLongitude, gender,
};
if (mbtiTouched) profileData.mbti = mbtiDraftValue;  // MBTI: 만졌을 때만
```
- `deriveInitialForm()`(핫픽스)와 MBTI 프리필 블록(`profile.mbti` 4축)은 **별개 함수/이펙트**로 유지(둘 다 저장값 우선 규칙).
- 음성검증 기준: 병합 후 `test_profile_birth_time.py` + `test_profile_mbti.py` **모두** 통과해야 한다.

## 5. 병합 순서 (권장)

1. `git switch feat/mbti-contrast && git merge --no-ff fix/profile-birth-time-overwrite`
2. 충돌: `router.py`(§2), `repository.py`(§3), `birth-input.tsx`(§4), `schemas/auth.py`(필드 순서)
3. 병합 커밋에서 MBTI 쪽 `test_explicit_null_clears_mbti` 스펙 조정 + `_PROFILE_KEYED_FIELDS` 에 `mbti` 추가
4. `python -m pytest -q -p no:randomly --import-mode=importlib` 전체 통과
5. 핫픽스만 단독 배포하는 경우: `main` 에 `fix/...` 만 `git merge --no-ff` (MBTI 변화 없음)

# birth_time 소실 사용자 — 복구 경로 조사 결과와 최소 변경 제안

> 조사 시점: `fix/profile-birth-time-overwrite` (기준 `main` = 0a2263b)
> 이 문서는 **제안**이며, (c) 안은 구현하지 않았다.

## 1. 전제 정정 — 실제로 어떤 상태가 "망가진 프로필"인가

| 사실 | 근거 |
|---|---|
| 0a2263b 의 `profiles` 에 `birth_time_mode` 컬럼이 **없음** | `app/auth/repository.py` `_SCHEMA_STATEMENTS`(profiles), 런타임 마이그레이션에도 없음 |
| 따라서 "시간 모름" 선택은 **저장된 적이 없음**(시각만 남음) | `birth-input.tsx` 가 mode 를 payload 에 안 넣고, 서버도 저장 컬럼 없음 |
| `/report` 의 mode 는 프론트가 `profile.birth_time_mode \|\| "exact"` 로 결정 | `frontend/app/(tabs)/home.tsx:58` |
| `exact` + `birth_time=null` → **422** | `app/schemas/saju.py:102-105` |

→ 실사용 "망가진 상태"는 대부분 **`birth_date` 있고 `birth_time` NULL**(mode 는 읽을 수조차 없음).

## 2. (a) 홈에서 422 가 나면 사용자가 설정으로 갈 수 있는 UI 가 있는가?

- 홈 에러 렌더: `if (error) return (... ApiError ? error.detail : message ...)` — **문구만 표시**, 버튼/링크 없음(`home.tsx:123`).
- 하단 탭(`_layout.tsx`)으로 설정 이동은 **가능**(에러 화면에도 탭바는 남음).
- 설정에 "생년월일 재설정" → `/birth-input` 진입 버튼 존재(`settings.tsx:141-143`).
- 종합: **경로는 열려 있으나 안내가 없음**. 사용자는 "오류 문구"만 보고 스스로 탭을 찾아가야 한다. (치명적 아님, 발견성 낮음)

## 3. (b) 재입력 화면에서 시간을 다시 넣고 저장하면 이번 수정으로 복구되는가?

- 예. `birth_time` NULL + mode 미지정 상태에서 `exact` + 시각을 저장하면 정상 저장된다.
- 테스트로 고정: `tests/test_profile_birth_time.py::test_recover_from_null_profile_by_reentering_time`,
  `::test_recovered_profile_can_generate_report` (복구 후 `/report` 200).
- 화면 초기값도 mode/time null 을 안전하게 처리하도록 `deriveInitialForm()` 을 추가(시간 null → "시간 모름" 스위치 ON, 저장하면 `noon`+null 로 일관 기록).

## 4. (c) 추가 최소 변경 **제안** (구현하지 않음)

### 제안 1 — 홈 에러 화면에 "생년월일 다시 입력" 버튼 (권장, 최소)

```tsx
// frontend/app/(tabs)/home.tsx — error 분기(현재 123행)
if (error) {
  const isBirthInputError = error instanceof ApiError && error.status === 422;
  return (
    <View style={styles.center}>
      <Text style={styles.errorText}>{error instanceof ApiError ? error.detail : (error as Error).message}</Text>
      {isBirthInputError && (
        <TouchableOpacity style={styles.retryBtn} onPress={() => router.replace("/birth-input")}>
          <Text>{t("home.reenterBirth")}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}
```
- 필요 i18n 키: `home.reenterBirth` (ko: "생년월일 다시 입력", en: "Re-enter birth details") × 5개 언어.
- 근거: 422 는 "입력 누락"이며 화면 하나로 해결 가능. 500/네트워크 오류와 구분해야 오해가 없다.
- 작업량: S. 리스크: 낮음(기존 렌더에 분기만 추가).

### 제안 2 — 프로필 로드 시 서버가 "누락" 신호를 내려주기

- `GET /auth/me/profile` 응답에 `birth_time_missing: bool` 같은 파생 플래그를 추가해, 홈이 422 를 맞기 전에 안내 배너를 띄운다.
- 근거: 422 를 한 번 겪기 전에 예방. 단 응답 스키마 변경 → 프론트 타입 동시 수정 필요.
- 작업량: M. 리스크: 중(스키마 확장, `feat/mbti-contrast` 와 응답 필드 충돌 가능).

### 제안 3 — 데이터 백필(운영 조치)

- `docs/BIRTHTIME_IMPACT_SQL.md` 의 (1-b) 로 대상 수를 확인한 뒤,
  `birth_date` 는 있고 `birth_time` 은 NULL 인 사용자에게 앱 내 안내(푸시/배너)를 보낸다.
- 근거: 복구는 사용자가 시간을 입력해야만 정확해진다(추정 금지). 자동 `noon` 채움은 시주를 왜곡하므로 **하지 말 것**.
- 작업량: S~M(운영 절차).

# Calculation School Notes

This document describes the calculation model used by the Gyeol engine. The model is deliberately simplified; different lineages (학파) of traditional Four Pillars analysis reach different conclusions from the same chart. Our goal is internal consistency and transparency, not a claim of "correct" interpretation.

If your favorite 만세력 app disagrees with us, this page is the place to check **which rule** we're using.

## 1. Engine contract — 억부 (抑扶) simplified

- **Strength (신강/신약)**: weighted sum of stem + branch contributions.
  - Month branch: **3.0** (계절 = 가장 강한 영향)
  - Day branch: 2.0
  - Hour branch: 1.5
  - Year branch: 1.0
  - Each non-day stem: 1.0
  - Hidden stems: **정기(본기)만** 사용. 中氣/餘氣 무시.
- **Thresholds**: `support_ratio >= 0.60 → 신강`, `<= 0.40 → 신약`, 그 사이 `중화`.
- **Yongsin (用神)**: 억부 기본.
  - 신강 → 식상/재성/관성 (洩·耗·剋)
  - 신약 → 인성/비겁 (生·助)
  - 중화 → 조후(調候). 여름생(巳午未)은 水, 겨울생(亥子丑)은 火.
- **Huising (喜神) / Gisin (忌神)**: 동일 role map 파생.

## 2. Hidden stems — 用(用) 기준

`app/engine/elements.py::BRANCH_MAIN_STEM`은 **用(用)** 기준 본기를 사용합니다. **體(體)** 기준 만세력과 다릅니다.

| Branch | 用 (ours) | 體 (alternative) |
|---|---|---|
| 子 | 癸 | 壬 |
| 午 | 丁 | 丙 |
| 巳 | 丙 | 丁 |
| 亥 | 壬 | 甲 |

다른 표준과 맞추려면 이 표 하나만 교체하면 됩니다. 그 외 나머지 규칙은 그대로.

## 3. Daewoon start age

- **규칙**: 3일 = 1년, 1일 = 4개월.
- **반올림**: raw 개월이 6 이상이면 다음 해로 올림. 이렇게 하면 `daewoon_display`(2년 11개월 → 3년 0개월)와 `start_age_first`가 일치.
- **이유**: 한국 만세력 앱마다 반올림 규칙이 다릅니다. 가장 흔한 관례에 맞춰 "왜 앱이랑 숫자가 다르지?" 문의를 줄이는 게 목적.

## 4. Twelve stages (十二運星) — 음간은 역행

- 양간: 장생지에서 순행.
- **음간: 장생지에서 역행** (예: 乙 장생=午 → 다음은 巳, 辰, ...).
- 戊·己는 丙·丁과 동일 (火土同宮).

## 5. Solar terms (節氣)

- `astronomy-engine`으로 태양 황경 교차 시각을 계산.
- 시각은 **UTC instant**입니다. KST로 환산한 clock time이 아닙니다. 자정/새벽 경계에서 이게 결정적입니다.
- 사주의 "solar year"는 출생 instant 이전의 마지막 **입춘(황경 315°)** 기준.

## 6. Sinsal (神煞)

검출하는 것만 나열:

- **삼합 기반 (년지 기준)**: 도화(桃花), 역마(驛馬), 화개(華蓋)
- **일간 기반**: 천을귀인(天乙貴人), 문창귀인(文昌貴人), 양인(羊刃, 양간 한정)
- **일주 기반**: 괴강(魁罡)

**검출하지 않는 것**: 고전 문헌의 나머지 ~100종 신살. 참고표에 우리가 안 잡는 신살이 있으면 이건 버그가 아니라 **스코프 밖**입니다.

## 7. Compatibility (宮合) — complementarity, not 상생상극

오행 축은 단순 상생상극 점수가 아닙니다. **과다/결핍 보완도**입니다.

- A가 X 오행 **>=25%**이고 B가 X **<=10%**이면 → **complement (+)**.
- A와 B **모두 X >=30%**이면 → **tension (–)**.

나머지 축:
- **day_master**: 천간 合·沖, 지지 六合·六沖, 십성 favorability.
- **ten_gods**: money/work/bond mode 일치도.
- **sinsal**: 공유 특성.

가중치: `day_master > elements > ten_gods > sinsal`.

## 8. What this engine is NOT

- **한국 만세력과 100% 동일하지 않습니다.** 학파별로 갈리는 지점:
  - 조자시 vs 야자시 (우리는 조자시, `jasi_boundary=23` 기본)
  - 中氣를 신강 판정에 포함하느냐 (우리는 무시)
  - 體 vs 用 hidden stems (우리는 用)
  - 대운 시작 나이 반올림 (우리는 6개월 이상 → +1)
  - 격국 우선순위 (우리는 투출 → 정기 → 록/양인 특례)
- **예측이 아닙니다.** 결정론적 상징 해석일 뿐. 삶의 결과는 선택·맥락·우연이 결정합니다.
- **의료·금융·심리 조언이 아닙니다.** 각 리포트의 disclaimer를 참조.

## 9. Changing the model

이 엔진을 유지보수하면서 규칙을 바꾸고 싶다면:

1. 규칙은 **한 파일**에 있습니다 (위 표에 명시).
2. 출력 shape이 바뀌면 `meta.schema_version`을 올립니다.
3. `tests/`의 해당 golden test를 업데이트합니다.
4. **이 문서도 업데이트합니다.**

목표는: 리포트의 모든 주장을 이 코드베이스의 특정 규칙으로 역추적할 수 있게 하는 것.
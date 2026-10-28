# SAJU i18n Glossary (canonical)

같은 개념엔 같은 단어. 새 문자열을 추가할 때 이 표를 먼저 확인.

## 원칙
1. **직역 금지** — 영어는 그 기능을 처음 보는 사람이 자연스럽게 읽는 문장.
2. **용어 통일** — 아래 표를 앱 전체에서 동일하게 사용.
3. **숫자·단위** — 통화는 `$2.99`(locale-independent), 시간은 24h `14:30`.
4. **날짜** — `YYYY-MM-DD` (백엔드 표준).

## Section titles (백엔드 `sec.title`)

| id | KO | EN |
|---|---|---|
| core | 당신의 본질 | Your Core |
| energy | 당신의 에너지 지도 | Your Energy Signature |
| lucky_code | 당신에게 필요한 기운 | Your Lucky Code |
| health | 몸과 마음 | Body & Wellness |
| money | 재물과 돈 | Money & Wealth |
| work | 일과 재능 | Work & Craft |
| bonds | 친구와 동료 | Bonds & Belonging |
| year | 올해의 흐름 | This Year |
| timeline | 인생의 궤적 | Your Timeline |
| monthly | 월별 흐름 | Your Monthly Calendar |
| chart | 당신의 네 가지 얼굴 | Your Four Faces |
| sinsal | 특별한 재능 | Special Traits |

## UI 크롬 (프론트)

| Concept | KO | EN |
|---|---|---|
| Shadow | 그림자 | Shadows |
| Advice | 조언 | Advice |
| Personalized insights | 맞춤 인사이트 | Personalized insights |
| Patterns | 패턴 | Patterns |
| More actions | 추가 실천 | More actions |
| Practices | 실천 | Practices |
| Focus | 집중 | Focus |
| Watch out | 주의 | Watch out |
| Locked content | 잠긴 콘텐츠 | Locked content |
| Current | 현재 | Current |
| Life stage | 생애 단계 | Life stage |
| (Core) tag | (본질) | (Core) |

## Compatibility (궁합)

| Concept | KO | EN |
|---|---|---|
| Chemistry | 케미 | Chemistry |
| Romance / Business / Friend / Family | 연애 / 비즈니스 / 친구 / 가족 | Romance / Business / Friend / Family |
| Best match | 최고의 케미 | Best match |
| Challenging match | 주의할 케미 | Challenging match |
| Five Elements axis | 오행 상생 | Five Elements |
| Day master axis | 일간 관계 | Day master |
| Values & mode axis | 가치관/모드 | Values & mode |
| Special traits axis | 신살 공명 | Special traits |

## Auth & Plan

| Concept | KO | EN |
|---|---|---|
| Free tier | 무료 회원 | Free |
| Subscription | 구독자 | Subscription |
| Premium | 프리미엄 회원 | Premium |
| Guest | 게스트 | Guest |
| Plan (settings row) | 이용 등급 | Plan |
| Not signed in | 로그인 안 됨 | Not signed in |
| Receipts | 결제 내역 | Receipts |

## Sub-brand words (번역 금지)
- `Gyeol` — 브랜드명, 영어 그대로
- `Premium` — 브랜드 톤
- 아키타입 이름(`The Radiator`, `The Blade`, ...)은 백엔드 `core.json`이 유일 소스.

## 백로그 (아직 처리 안 됨)
- [ ] `birth_location` raw key(`seoul`, `new_york`) 표시 → 도시 display name 매핑
- [ ] `frontend/app/index.tsx` 스플래시 — "결" 브랜드 표기 정책
- [ ] 백엔드 `en/cross_insight.json`, `en/free_gating.json`, `en/premium_insights.json` 누락


## ⚠️ 파일 편집 인코딩 규칙
- ❌ PowerShell `Add-Content` / `>` / `>>` (PS 5.x 기본 cp949)
- ❌ 인라인 `python -c "..."` (따옴표·경로 이스케이프 취약)
- ✅ VS Code에서 편집 + Ctrl+S (UTF-8)
- ✅ Python `Path.write_text(encoding='utf-8')`
- ✅ 검증/패치는 반드시 `.py` 파일로
- 검증: `python scripts/verify_i18n.py` → `i18n OK` 필수
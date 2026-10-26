# Archived one-off scripts

These scripts were applied to the codebase and committed alongside the changes they made. They are not part of the runtime and should not be re-run without reviewing them first.

If a similar patch is needed again, copy and adapt one of these.

## Moved via git mv (preserve history)

| Path | Purpose | Status |
|---|---|---|
| `auth/` | P1-1 OIDC (Apple/Google/Kakao) 1-A~1-H | Applied |
| `i18n/` | Frontend i18n patches (home/daily/compat/settings/birth) | Applied |
| `_helpers/` | Ad-hoc diagnostic scripts | — |
| `fix_ko_content_corruption.py` | 지지 → 땅의 기운 손상 복원 | Applied |
| `fix_ko_residual_corruption.py` | 잔존 손상 스캔/수정 | Applied |
| `fix_en_awkward_phrases.py` | EN 문구 어색함 수정 | Applied |
| `fix_lichun_solar_year.py` | P0 절기년 (입춘) | Applied |
| `fix_p1_gender_and_loader.py` | P1 gender 화이트리스트 + loader 정리 | Applied |
| `fix_p2a_rounding_and_asset.py` | P2-A 대운 6개월 반올림 + asset fail-fast | Applied |
| `fix_stub_pillars.py` | P3 stub 6필러 완성 | Applied |
| `fix_year_solar_calendar_note.py` | P3-A 절기년 UX 주석 | Applied |
| `show_awkward_context.py` | P2 문맥 덤프 (일회성) | — |
| `smoke_p0_1.py`, `smoke_p0_2.py` | P0-1/P0-2 스모크 (기능 종료) | Redundant w/ tests |

## Added to archive (previously untracked)

| Path | Purpose | Status |
|---|---|---|
| `_common.py` | 위 patch 스크립트 헬퍼 | Dead |

## Kept in scripts/ (active)

- `preview_report.py` — dev preview of full report
- `scan_en_content_gaps.py` — EN content audit

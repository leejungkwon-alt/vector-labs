# 🌐 SAJU i18n 확장 로드맵 (es, ja, zh_cn)

## 🎯 목표
- 기존 지원 언어: `ko`, `en`
- **추가할 언어: `es`(스페인어), `ja`(일본어), `zh_cn`(중국어 간체)**
- (기존 계획에 있던 `zh_tw` 번체는 제외)

---

## 🟢 1단계: 프론트엔드 확장
- [ ] `frontend/src/locales/` 폴더에 `es.json`, `ja.json`, `zh_cn.json` 생성 (en.json 구조 복제 및 번역)
- [ ] `frontend/src/i18n.ts`의 `RESOURCES`에 3개 로케일 추가
- [ ] `frontend/src/i18n.ts`의 `useLang().availableLangs`에 3개 언어 항목 추가
- [ ] `frontend/app/(tabs)/settings.tsx` 언어 선택 UI에 3개 언어 버튼 추가

## 🟡 2단계: 백엔드 API 및 테스트 수정
- [ ] 백엔드 `SUPPORTED_LANGS` 수정: `("en", "ko", "es", "ja", "zh_cn")` 로 변경
- [ ] `app/schemas/saju.py`, `daily.py`, `compatibility.py` 의 `validate_lang` 완화
- [ ] `tests/test_multilingual_api.py`, `tests/test_step4e.py` 제약 해제 및 테스트 케이스 수정
- [ ] `app/services/content/data/` 하위에 `es` 폴더 생성 (en 폴백용)
- [ ] `pytest -q` 전체 통과 확인

## ⚪ 3단계: 마무리
- [ ] `docs/i18n-final-audit.md` 업데이트
- [ ] `hardcoded_scan_full.txt` 재실행
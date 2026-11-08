# scripts/fix_yongsin_dict.py
"""
tagger.py의 _yongsin_elem()이 dict를 처리하도록 수정.
- yongsin이 dict면 yongsin['yongsin'] 또는 ['element'] 추출
- 한자/한글 모두 매핑
- 기존 디버그 print 제거
"""
import ast
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TAG = Path("app/semantic/tagger.py")

txt = TAG.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 1. 기존 디버그 print 제거
# ═══════════════════════════════════════════════════════════
lines = txt.splitlines(keepends=True)
cleaned = []
removed = 0
for line in lines:
    if "[DEBUG-YONGSIN]" in line:
        removed += 1
        continue
    cleaned.append(line)
txt = "".join(cleaned)
print(f"✅ 디버그 print {removed}개 제거")

# ═══════════════════════════════════════════════════════════
# 2. _yongsin_elem 함수 교체 (dict 처리 추가)
# ═══════════════════════════════════════════════════════════
# 기존 함수 찾기
OLD_FUNC = '''    # 용신 element 추출 (str 또는 int 방어)
    def _yongsin_elem(y):
        if isinstance(y, str) and y in ELEMENT_NAMES:
            return y
        if isinstance(y, int) and 0 <= y < len(ELEMENT_NAMES):
            return ELEMENT_NAMES[y]
        return None'''

NEW_FUNC = '''    # 용신 element 추출 (dict/str/int 모두 방어)
    # 한자 오행 매핑
    _HANJA_MAP = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}
    # 한글 오행 매핑
    _KO_MAP = {"목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
               "나무": "木", "불": "火", "흙": "土", "쇠": "金", "물": "水"}
    # 영문 매핑
    _EN_MAP = {"WOOD": "木", "FIRE": "火", "EARTH": "土", "METAL": "金", "WATER": "水",
               "wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}

    def _yongsin_elem(y):
        # dict → 'yongsin' 또는 'element' 키 추출
        if isinstance(y, dict):
            y = y.get("yongsin") or y.get("element") or y.get("yongsin_element")
        if isinstance(y, int) and 0 <= y < len(ELEMENT_NAMES):
            return ELEMENT_NAMES[y]
        if not isinstance(y, str):
            return None
        # 한자
        if y in _HANJA_MAP:
            return _HANJA_MAP[y]
        # 한글
        if y in _KO_MAP:
            return _KO_MAP[y]
        # 영문
        if y in _EN_MAP:
            return _EN_MAP[y]
        return None'''

if OLD_FUNC not in txt:
    print("❌ _yongsin_elem 함수 패턴 못 찾음")
    # 대안: 간단 패턴
    OLD_FUNC_ALT = '''    def _yongsin_elem(y):
        if isinstance(y, str) and y in ELEMENT_NAMES:
            return y
        if isinstance(y, int) and 0 <= y < len(ELEMENT_NAMES):
            return ELEMENT_NAMES[y]
        return None'''
    if OLD_FUNC_ALT in txt:
        txt = txt.replace(OLD_FUNC_ALT, NEW_FUNC, 1)
        print("✅ _yongsin_elem 교체 (alt 패턴)")
    else:
        print("❌ _yongsin_elem 함수 못 찾음 — 수동 확인 필요")
        print("   다음 명령으로 확인:")
        print("   Get-Content 'app/semantic/tagger.py' | Select-String '_yongsin_elem' -Context 0,10")
        sys.exit(1)
else:
    txt = txt.replace(OLD_FUNC, NEW_FUNC, 1)
    print("✅ _yongsin_elem 교체 (dict/str/int 모두 지원)")

# ═══════════════════════════════════════════════════════════
# 3. ast.parse 검증
# ═══════════════════════════════════════════════════════════
try:
    ast.parse(txt)
    print("✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"❌ 문법 오류: line {e.lineno}: {e.msg}")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_yongsin_dict.py --apply")
    sys.exit(0)

TAG.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료")
print("\n다음 명령 (한 줄씩):")
print("   python -c \"import ast; ast.parse(open('app/semantic/tagger.py',encoding='utf-8').read())\"")
print("   .\\deploy.ps1")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix: _resolve_poem의 用神 오행 해석 실패 (FLOW → "흐름(Water)" → null).

_sig_to_yong_elem() 헬퍼로 다단계 fallback:
  1) 표시 문자열 "(English)" 파싱
  2) ELEMENT_SIGNATURES 역매핑
  3) 직접 한자
  4) 한글/영문 키워드 fuzzy

실행:
  $env:PYTHONPATH=(Get-Location).Path
  python scripts\\fix_phase2_poem_elem.py
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CW = ROOT / "app" / "services" / "content_writer.py"
BACKUP_SUFFIX = f".bak_phase2fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

HELPER = '''

def _sig_to_yong_elem(power_sig: str, content_map: dict):
    """用神 시그니처(예: FLOW) → 한자 오행(木/火/土/金/水). 실패 시 None."""
    from app.engine.elements import ELEMENT_NAMES
    import re

    raw = (content_map.get(power_sig) or {}).get("element", "") or ""

    # 1) "흐름(Water)" → Water → 水
    m = re.search(r"\\(([A-Za-z]+)\\)", raw)
    if m:
        eng_map = {"wood": "木", "fire": "火", "earth": "土",
                   "metal": "金", "water": "水"}
        elem = eng_map.get(m.group(1).lower())
        if elem in ELEMENT_NAMES:
            return elem

    # 2) ELEMENT_SIGNATURES 역매핑
    try:
        from app.semantic.tags import ELEMENT_SIGNATURES
        for elem, sig in ELEMENT_SIGNATURES.items():
            if sig == power_sig and elem in ELEMENT_NAMES:
                return elem
    except Exception:
        pass

    # 3) raw가 직접 한자
    if raw in ELEMENT_NAMES:
        return raw

    # 4) fuzzy (한글/영문)
    low = raw.lower()
    for kw, elem in [
        ("water", "水"), ("flow", "水"), ("흐름", "水"), ("수", "水"),
        ("wood", "木"), ("growth", "木"), ("성장", "木"), ("목", "木"),
        ("fire", "火"), ("blaze", "火"), ("불꽃", "火"), ("화", "火"),
        ("earth", "土"), ("대지", "土"), ("토", "土"),
        ("metal", "金"), ("예리", "金"), ("금", "金"),
    ]:
        if kw in low:
            return elem
    return None
'''


def main():
    text = CW.read_text(encoding="utf-8")

    if "_sig_to_yong_elem" in text:
        print("[SKIP] already applied")
        return

    bak = CW.with_name(CW.name + BACKUP_SUFFIX)
    shutil.copy2(CW, bak)
    print(f"[backup] {bak.name}")

    # 1) _resolve_poem 정의 직전에 헬퍼 삽입
    anchor = "\ndef _resolve_poem("
    if text.count(anchor) != 1:
        print(f"[ERR] _resolve_poem anchor not unique: {text.count(anchor)}")
        sys.exit(1)
    text = text.replace(anchor, HELPER + anchor, 1)

    # 2) yong_elem 해석 라인 교체
    old = (
        '    yong_elem = content_map.get(power_sig, {}).get("element", "")\n'
        '    if yong_elem not in ELEMENT_NAMES:\n'
        '        return None\n'
        '    yong_idx = ELEMENT_NAMES.index(yong_elem)'
    )
    new = (
        '    yong_elem = _sig_to_yong_elem(power_sig, content_map)\n'
        '    if yong_elem not in ELEMENT_NAMES:\n'
        '        return None\n'
        '    yong_idx = ELEMENT_NAMES.index(yong_elem)'
    )
    if text.count(old) != 1:
        print(f"[ERR] yong_elem anchor not unique: {text.count(old)}")
        sys.exit(1)
    text = text.replace(old, new, 1)

    CW.write_text(text, encoding="utf-8")
    print(f"[OK]   {CW.relative_to(ROOT)} (+_sig_to_yong_elem)")

    # 3) 검증: ELEMENT_SIGNATURES 확인 + 5관계 계산
    print("\n=== 검증 ===")
    try:
        from app.semantic.tags import ELEMENT_SIGNATURES
        print("  ELEMENT_SIGNATURES:")
        for k, v in ELEMENT_SIGNATURES.items():
            print(f"    {k} → {v}")
    except Exception as e:
        print(f"  [WARN] ELEMENT_SIGNATURES: {e}")

    try:
        from app.services.content_writer import _sig_to_yong_elem, _load_poems
        from app.engine.elements import (
            ELEMENT_NAMES, classify_yongsin_month_relation, POEM_RELATION_KR,
        )

        # 케이스: FLOW / 흐름(Water) / 월건 巳(火)
        fake_content = {"FLOW": {"element": "흐름(Water)"}}
        elem = _sig_to_yong_elem("FLOW", fake_content)
        print(f"  FLOW → {elem}")
        if elem == "水":
            yong_idx = ELEMENT_NAMES.index("水")   # 4
            month_idx = 1                          # 巳 = 火
            rel = classify_yongsin_month_relation(yong_idx, month_idx)
            pid = "su_" + rel
            print(f"  用神=水, 월건=火 → relation={rel} ({POEM_RELATION_KR[rel]})")
            print(f"  예상 poem.id = {pid}")
            poems = _load_poems()
            match = next((p for p in poems if p["id"] == pid), None)
            if match:
                print(f"  [PASS] poems.json에 존재: {match['title'].get('ko')}")
            else:
                print(f"  [FAIL] poems.json에 {pid} 없음")
        else:
            print("  [FAIL] FLOW 해석 실패")
    except Exception as e:
        print(f"  [ERR] 검증: {e}")


if __name__ == "__main__":
    main()
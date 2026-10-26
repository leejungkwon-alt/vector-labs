#!/usr/bin/env python3
"""
스테일 테스트 수정 (action → actions).
- tests/test_full_report.py::test_money_section_shape
- tests/test_ko_report.py::test_ko_bonds_content_is_korean

안전장치: 저장 전 compile() 검증 + .bak 자동 백업.
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

PATCHES = [
    (
        "tests/test_full_report.py",
        'money["action"]',
        'money["actions"] and all(money["actions"])',
        "test_money_section_shape (action→actions, non-empty & truthy)",
    ),
    (
        "tests/test_ko_report.py",
        'for ch in bonds["action"]',
        'for ch in " ".join(bonds["actions"])',
        "test_ko_bonds_content_is_korean (action→actions, joined)",
    ),
]


def patch(path: str, old: str, new: str, label: str) -> bool:
    p = Path(path)
    if not p.exists():
        print(f"❌ SKIP {label}: {p} 없음")
        return False
    src = p.read_text(encoding="utf-8")
    if old not in src:
        print(f"⚠️  SKIP {label}: 패턴 없음 (이미 수정됨?)")
        return False
    new_src = src.replace(old, new, 1)
    try:
        compile(new_src, str(p), "exec")   # 사전 검증
    except SyntaxError as e:
        print(f"❌ FAIL {label}: syntax error → {e.msg} (line {e.lineno})")
        return False
    bak = p.with_suffix(p.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(p, bak)
    p.write_text(new_src, encoding="utf-8")
    print(f"✅ {label}")
    print(f"   └ 백업: {bak.name}")
    return True


def main() -> int:
    ok = sum(patch(*args) for args in PATCHES)
    print(f"\n결과: {ok}/{len(PATCHES)} 패치 완료")
    return 0 if ok == len(PATCHES) else 1


if __name__ == "__main__":
    sys.exit(main())
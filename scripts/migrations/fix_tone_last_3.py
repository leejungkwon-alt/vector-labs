#!/usr/bin/env python3
"""scripts/migrations/fix_tone_last_3.py

마지막 남은 3건의 톤 위반 단어를 완벽하게 제거합니다.
(이전 스크립트의 따옴표 매칭 오류 수정)

실행:
  python scripts/migrations/fix_tone_last_3.py --apply
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

FIXES = [
    # (파일 경로, 기존 문자열, 새 문자열)
    ("en/core_pillars/丙午.json", '"magnetic presence"', '"warm presence"'),
    ("en/core_pillars/丙午.json", 'magnetic presence', 'warm presence'), # 따옴표 없는 배열 요소 대비
    
    ("en/core_pillars/庚申.json", '"unshakeable"', '"steady"'),
    ("en/core_pillars/庚申.json", 'unshakeable', 'steady'),             # 따옴표 없는 배열 요소 대비
    
    ("en/sinsal.json", '"Magnetic Draw"', '"Natural Draw"'),
    ("en/sinsal.json", 'Magnetic Draw', 'Natural Draw'),               # 따옴표 없는 값 대비
]

def main():
    print("=" * 66)
    print(f"  fix_tone_last_3 ({'APPLY' if APPLY else 'DRY-RUN'})")
    print("=" * 66)

    backed_up = set()
    
    for rel_path, old, new in FIXES:
        p = DATA / rel_path
        if not p.exists():
            continue
            
        src = p.read_text(encoding="utf-8")
        if old not in src:
            continue
            
        src = src.replace(old, new)
        
        if APPLY:
            if rel_path not in backed_up:
                shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))
                backed_up.add(rel_path)
            p.write_text(src, encoding="utf-8")
            
        print(f"  {'✅' if APPLY else '🔍'} {rel_path}: '{old.strip(chr(34))}' → '{new.strip(chr(34))}'")

    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    print("=" * 66)

if __name__ == "__main__":
    main()
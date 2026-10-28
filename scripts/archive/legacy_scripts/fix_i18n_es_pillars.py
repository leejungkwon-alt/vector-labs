#!/usr/bin/env python3
"""
es core_pillars (60개 파일) 일괄 번역 전용 스크립트.
기존 auto_translate_es.py 의 핵심 로직을 그대로 가져와서 실행합니다.
"""
import sys
from pathlib import Path

# 같은 scripts 폴더에 있는 auto_translate_es.py 를 모듈로 불러옵니다.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import auto_translate_es as auto

def main():
    auto._load_cache()
    
    # en/core_pillars/ 아래의 모든 .json 파일 목록을 가져옵니다.
    files = sorted(f"core_pillars/{p.name}" for p in (auto.EN_DIR / "core_pillars").glob("*.json"))
    
    if not files:
        print("❌ en/core_pillars 폴더에 파일이 없습니다.")
        return 1

    print(f"🔍 발견된 파일: {len(files)}개\n")

    try:
        tr = auto._Translator()
    except SystemExit as e:
        print(e)
        return 2

    modes = auto._mode_names()
    ok = fail = 0
    
    for f in files:
        try:
            if auto.process(f, tr, modes, False):
                ok += 1
            else:
                fail += 1
        finally:
            auto._save_cache()

    print(f"\n결과: ok={ok}, fail={fail}")
    if auto.REVIEW.exists():
        print(f"리뷰 큐: {auto.REVIEW}")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
content_writer.py의 차트 주석(Note) 생성 버그 수정 V2.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRITER = ROOT / "app" / "services" / "content_writer.py"

def main() -> int:
    if not WRITER.exists():
        print(f"❌ {WRITER} 없음")
        return 1

    text = WRITER.read_text(encoding="utf-8")

    # 덤프된 실제 코드 모양 (8칸 들여쓰기)
    old_block = '''        same = [l for l in layers if l["archetype_key"] == key]
        arch_name = same[0]["archetype"]'''
    
    new_block = '''        same = [l for l in layers if l["archetype_key"] == key]
        # [버그수정] 세부 일주 이름(예: 호수 위의 등불) 대신 공통 아키타입 이름(예: 태양) 사용
        arch_name = arch_content.get(key, {}).get("name", key)'''

    if old_block not in text:
        print("⚠️  여전히 대상 코드를 찾지 못했습니다.")
        return 1

    text = text.replace(old_block, new_block)
    WRITER.write_text(text, encoding="utf-8")
    print("✅ content_writer.py 차트 주석 버그 수정 완료")
    return 0

if __name__ == "__main__":
    sys.exit(main())
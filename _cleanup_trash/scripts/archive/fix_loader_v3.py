#!/usr/bin/env python3
"""
loader.py의 _REGISTRY 참조 블록을 라인 기반으로 완전 제거 (V3, bulletproof).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOADER = ROOT / "app" / "services" / "content" / "loader.py"

def main() -> int:
    if not LOADER.exists():
        print(f"❌ {LOADER} 없음")
        return 1

    text = LOADER.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # 라인 기반 삭제:
    # 'if lang not in _REGISTRY:' 가 나오는 줄부터
    # 'raise KeyError(f"Data file not found:' 가 나오는 줄 직전까지 모두 삭제
    new_lines = []
    skip = False
    removed = 0
    for line in lines:
        if 'if lang not in _REGISTRY:' in line:
            skip = True
            continue
        if skip:
            if 'raise KeyError(f"Data file not found:' in line:
                skip = False
                # 이 줄은 살림 (최종 KeyError)
                new_lines.append(line)
            else:
                removed += 1
            continue
        new_lines.append(line)

    text = ''.join(new_lines)

    # docstring/주석 정리
    text = text.replace("파일이 없으면 기존 _REGISTRY 기반 KeyError.", "파일이 없으면 KeyError.")
    text = text.replace(
        "    # lang은 아래 _REGISTRY 검사에서 KeyError로 fail-fast.",
        "    # 화이트리스트 밖의 lang은 아래에서 KeyError로 fail-fast.",
    )

    LOADER.write_text(text, encoding="utf-8")
    print(f"✅ {removed + 2}줄 제거 완료 (블록 5줄 + docstring/주석 2줄 정리)")

    # 검증
    after = LOADER.read_text(encoding="utf-8")
    if "_REGISTRY" in after:
        left = [f"L{i+1}: {ln}" for i, ln in enumerate(after.splitlines()) if "_REGISTRY" in ln]
        print(f"⚠️  여전히 _REGISTRY 남음 ({len(left)}줄):")
        for ln in left:
            print(f"   {ln}")
        return 1

    print("✅ _REGISTRY 참조 완전 제거됨")
    return 0

if __name__ == "__main__":
    sys.exit(main())
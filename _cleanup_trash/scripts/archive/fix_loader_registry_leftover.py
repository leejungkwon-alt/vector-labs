#!/usr/bin/env python3
"""
loader.py에 남아있는 _REGISTRY 참조 블록을 정확히 제거.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOADER = ROOT / "app" / "services" / "content" / "loader.py"

# 제거할 정확한 문자열 블록
OLD_BLOCK = '''    if lang not in _REGISTRY:
        raise KeyError(f"Language pack not registered: {lang}")
    if section not in _REGISTRY[lang]:
        raise KeyError(f"Section '{section}' not available for lang '{lang}'")
    raise KeyError(f"Data file not found: {data_path}")'''

NEW_BLOCK = '''    raise KeyError(f"Data file not found: {data_path}")'''

def main() -> int:
    if not LOADER.exists():
        print(f"❌ {LOADER} 없음")
        return 1

    text = LOADER.read_text(encoding="utf-8")

    if OLD_BLOCK not in text:
        print("⚠️  정확한 블록을 찾지 못했습니다. loader.py의 50번째 줄 근처를 수동으로 확인하세요.")
        # 컨텍스트 덤프
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if "_REGISTRY" in line:
                print(f"  L{i}: {line}")
        return 1

    # _REGISTRY 참조 블록 제거
    text = text.replace(OLD_BLOCK, NEW_BLOCK)

    # 문서(docstring) 내의 _REGISTRY 문구도 수정
    text = text.replace("파일이 없으면 기존 _REGISTRY 기반 KeyError.", "파일이 없으면 KeyError.")
    text = text.replace("언어별 팩 레지스트리. 새 언어 추가 시 여기만 갱신.", "")
    
    LOADER.write_text(text, encoding="utf-8")
    print("✅ loader.py에서 _REGISTRY 참조 블록 제거 완료")
    return 0

if __name__ == "__main__":
    sys.exit(main())
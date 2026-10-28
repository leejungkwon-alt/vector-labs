#!/usr/bin/env python3
"""zh_cn 번역 파일 내의 영어/한국어 병기 오염을 제거합니다.

Usage:
  python scripts/fix_zh_cn_contamination.py           # dry-run (변경될 내용 미리보기)
  python scripts/fix_zh_cn_contamination.py --apply   # 실제 파일 수정
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# frontend 폴더 하위에서 이름에 'zh'가 들어간 json 파일을 모두 찾음
TARGET_FILES = list((ROOT / "frontend").rglob("*zh*.json"))

# 괄호 안에 영어(a-zA-Z) 또는 한국어(가-힣)가 포함된 패턴
# 예: " (Flow)", " (본질)", " (Twin)"
PAREN_REGEX = re.compile(r'\s*\([a-zA-Z가-힣\s]+\)')

def clean_value(val: str) -> str:
    if not isinstance(val, str):
        return val
    
    # 괄호와 그 안의 내용 제거
    cleaned = PAREN_REGEX.sub('', val)
    
    # 제거 후 남은 불필요한 연속 공백 정리 및 양끝 공백 제거
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def walk_and_clean(data, path=""):
    changes = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                changes.extend(walk_and_clean(v, f"{path}.{k}" if path else k))
            elif isinstance(v, str):
                new_v = clean_value(v)
                if new_v != v:
                    changes.append((f"{path}.{k}" if path else k, v, new_v))
                    data[k] = new_v
    elif isinstance(data, list):
        for i, v in enumerate(data):
            if isinstance(v, (dict, list)):
                changes.extend(walk_and_clean(v, f"{path}[{i}]"))
            elif isinstance(v, str):
                new_v = clean_value(v)
                if new_v != v:
                    changes.append((f"{path}[{i}]", v, new_v))
                    data[i] = new_v
    return changes

def main() -> int:
    apply = "--apply" in sys.argv
    
    if not TARGET_FILES:
        print("[error] zh_cn 번역 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return 1

    total_changes = 0
    for file in TARGET_FILES:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[error] {file.relative_to(ROOT)} 로드 실패: {e}")
            continue

        changes = walk_and_clean(data)
        
        if changes:
            print(f"\n[{file.relative_to(ROOT)}] 오염된 텍스트 {len(changes)}건 발견:")
            for key, old, new in changes:
                print(f"  키: {key}")
                print(f"    - (기존) {old}")
                print(f"    + (수정) {new}")
            total_changes += len(changes)

            if apply:
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  [applied] {file.name} 저장 완료")

    if total_changes == 0:
        print("[OK] 오염된 영어/한국어 텍스트가 발견되지 않았습니다.")
    elif not apply:
        print(f"\n[dry-run] 총 {total_changes}건의 오염 발견. --apply 옵션을 주어 실행하면 수정됩니다.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
1. '지지(地支)' -> '땅의 기운', '천간(天干)' -> '하늘의 기운' 복구
2. '땅의 기운', '하늘의 기운' 뒤에 붙은 잘못된 조사 교정 (예: 기운가 -> 기운이)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "app"

# 조사 결합 교정 사전 (기운은 받침 'ㄴ'으로 끝나므로 '이/을/은/과/으로'가 맞음)
REPLACEMENTS = [
    # 1. 한자어에서 쉬운 말로 복구
    ("지지(地支)", "땅의 기운"),
    ("천간(天干)", "하늘의 기운"),
    
    # 2. 조사 교정 (땅의 기운)
    ("땅의 기운가", "땅의 기운이"),
    ("땅의 기운를", "땅의 기운을"),
    ("땅의 기운는", "땅의 기운은"),
    ("땅의 기운와", "땅의 기운과"),
    ("땅의 기운로", "땅의 기운으로"),
    
    # 3. 조사 교정 (하늘의 기운)
    ("하늘의 기운가", "하늘의 기운이"),
    ("하늘의 기운를", "하늘의 기운을"),
    ("하늘의 기운는", "하늘의 기운은"),
    ("하늘의 기운와", "하늘의 기운과"),
    ("하늘의 기운로", "하늘의 기운으로"),
    
    # 4. 단독으로 남은 '지지', '천간'이 있다면 문맥상 복구 (선택적)
    # (단, '지지하다' 같은 동사는 건드리지 않도록 주의)
]

def main():
    print("=" * 60)
    print("[복구] 쉬운 용어(땅의 기운, 하늘의 기운) 복구 및 조사 교정")
    print("=" * 60)

    changed_files = 0
    for py_file in APP_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        original = text
        
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
            
        if text != original:
            py_file.write_text(text, encoding="utf-8")
            changed_files += 1
            print(f"  [OK] {py_file.relative_to(ROOT)} 복구 완료")
            
    if changed_files == 0:
        print("  ⏭️ 복구할 파일이 없습니다. (이미 정상이거나 커밋 전 상태입니다.)")
    else:
        print(f"\n✅ 총 {changed_files}개 파일 복구 완료")

    print("\n이제 백엔드 서버를 재시작(Ctrl+C -> uvicorn...)하고, 브라우저를 새로고침하세요.")

if __name__ == "__main__":
    sys.exit(main())
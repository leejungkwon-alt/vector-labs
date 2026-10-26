#!/usr/bin/env python3
"""
1. 이번 i18n 작업용 스크립트들을 scripts/archive/로 이동
2. loader.py의 데드코드(_REGISTRY) 제거 및 list_available 폴백 수정
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
ARCHIVE = SCRIPTS / "archive"
LOADER = ROOT / "app" / "services" / "content" / "loader.py"

def archive_scripts():
    print("[1/2] i18n 작업용 스크립트 아카이빙")
    ARCHIVE.mkdir(exist_ok=True)
    files = [
        "fix_i18n_phase2.py", "fix_i18n_phase3_es_data.py",
        "fix_i18n_phase4_locales.py", "fix_i18n_phase4a_es_sections.py",
        "fix_i18n_phase4b1_es_year.py", "fix_i18n_phase4b2_es_year.py",
        "fix_i18n_phase4b3_es_year.py", "fix_i18n_phase4b4_es_year.py",
        "fix_i18n_phase4b5_es_year.py", "fix_consistency_elements_and_branches.py",
        "restore_easier_terms.py", "audit_i18n_gaps.py",
        "copy_missing_i18n_packs.py", "cleanup_final.py"  # 자기 자신도 이동
    ]
    moved = 0
    for f in files:
        src = SCRIPTS / f
        dst = ARCHIVE / f
        if src.exists() and not dst.exists():
            shutil.move(str(src), str(dst))
            moved += 1
    print(f"  [OK] {moved}개 파일 이동 완료")

def cleanup_loader():
    print("\n[2/2] loader.py 데드코드 제거 (_REGISTRY 삭제)")
    if not LOADER.exists():
        print(f"  [ERR] {LOADER} 없음")
        return

    text = LOADER.read_text(encoding="utf-8")
    
    # 1. _REGISTRY 딕셔너리 정의 제거
    text = re.sub(r"_REGISTRY = \{.*?\n\}\n", "", text, flags=re.DOTALL)
    
    # 2. load_pack 내부의 _REGISTRY 참조 if문 제거
    pattern_load = r"    if lang not in _REGISTRY:\n        raise KeyError\(.*?\)\n    if section not in _REGISTRY\[lang\]:\n        raise KeyError\(.*?\)\n"
    text = re.sub(pattern_load, "", text)
    
    # 3. list_available 내부의 폴백 수정
    text = text.replace("    return list(_REGISTRY.get(lang, {}).keys())", "    return []")
    
    LOADER.write_text(text, encoding="utf-8")
    print("  [OK] loader.py 정리 완료")

if __name__ == "__main__":
    archive_scripts()
    cleanup_loader()
    print("\n✅ 정리 완료. 백엔드 테스트를 실행하세요.")
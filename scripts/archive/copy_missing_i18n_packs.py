#!/usr/bin/env python3
"""
누락된 i18n JSON 파일을 en에서 복제 (ja, zh_cn, es).
core_pillars 하위 60개 파일 포함.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"
LANGS = ["ja", "zh_cn", "es"]

def copy_missing(lang: str) -> tuple[int, int]:
    en_dir = DATA / "en"
    lang_dir = DATA / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    copied_top = 0
    copied_pillar = 0

    # 1. 최상위 JSON
    for en_file in en_dir.glob("*.json"):
        dst = lang_dir / en_file.name
        if not dst.exists():
            shutil.copy2(en_file, dst)
            copied_top += 1

    # 2. core_pillars JSON
    en_pillar_dir = en_dir / "core_pillars"
    lang_pillar_dir = lang_dir / "core_pillars"
    if en_pillar_dir.exists():
        lang_pillar_dir.mkdir(parents=True, exist_ok=True)
        for en_file in en_pillar_dir.glob("*.json"):
            dst = lang_pillar_dir / en_file.name
            if not dst.exists():
                shutil.copy2(en_file, dst)
                copied_pillar += 1

    return copied_top, copied_pillar


def main() -> int:
    print("=" * 60)
    print("[copy_missing_i18n_packs] en 기준 누락분 복제")
    print("=" * 60)

    total_copied = 0
    for lang in LANGS:
        top, pillar = copy_missing(lang)
        total_copied += top + pillar
        print(f"[{lang}] 최상위 {top}개, core_pillars {pillar}개 복제")

    print(f"\n✅ 총 {total_copied}개 파일 복제 완료")

    # 검증
    print("\n[verify]")
    import importlib
    import app.services.content.loader as loader
    importlib.reload(loader)

    # 몇 개 스팟 체크
    for lang in LANGS:
        # ja/zh_cn/es 모두 en에서 복제되었으므로 로드되어야 함
        try:
            core = loader.load_pack(lang, "core")
            assert "ARCHETYPE_CONTENT" in core
            print(f"  [OK] {lang}/core.json 로드됨")
        except Exception as e:
            print(f"  [ERR] {lang}/core.json: {e}")
            return 1

        # core_pillars 로드 확인
        try:
            pillar = loader.load_pack(lang, "core_pillars/丁丑")
            assert "narrative" in pillar
            print(f"  [OK] {lang}/core_pillars/丁丑.json 로드됨")
        except Exception as e:
            print(f"  [ERR] {lang}/core_pillars/丁丑.json: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
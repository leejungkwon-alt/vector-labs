#!/usr/bin/env python3
"""
프론트엔드 로케일 파일에 누락된 오행(wood, fire, earth, metal, water) 키 추가.
- 에러 방지를 위해 JSON 파싱 후 저장
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ROOT / "frontend" / "src" / "locales"

TRANSLATIONS = {
    "ko": {
        "wood": "목 (Wood)",
        "fire": "화 (Fire)",
        "earth": "토 (Earth)",
        "metal": "금 (Metal)",
        "water": "수 (Water)",
    },
    "en": {
        "wood": "Wood",
        "fire": "Fire",
        "earth": "Earth",
        "metal": "Metal",
        "water": "Water",
    },
    "ja": {
        "wood": "木 (Wood)",
        "fire": "火 (Fire)",
        "earth": "土 (Earth)",
        "metal": "金 (Metal)",
        "water": "水 (Water)",
    },
    "zh_cn": {
        "wood": "木 (Wood)",
        "fire": "火 (Fire)",
        "earth": "土 (Earth)",
        "metal": "金 (Metal)",
        "water": "水 (Water)",
    },
    "es": {
        "wood": "Madera",
        "fire": "Fuego",
        "earth": "Tierra",
        "metal": "Metal",
        "water": "Agua",
    },
}

def main() -> int:
    print("=" * 60)
    print("[Fix] 프론트엔드 로케일 누락 키(오행) 추가")
    print("=" * 60)

    for lang, data in TRANSLATIONS.items():
        file_path = LOCALES / f"{lang}.json"
        if not file_path.exists():
            print(f"  [ERR] {file_path.name} 없음")
            continue

        content = json.loads(file_path.read_text(encoding="utf-8"))
        
        if "sections" not in content:
            content["sections"] = {}

        # 기존에 있다면 덮어쓰고, 없으면 추가
        content["sections"].update(data)
        
        file_path.write_text(
            json.dumps(content, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print(f"  [OK] {file_path.name} 업데이트 완료")

    print("\n✅ 완료되었습니다. 앱을 새로고침하세요.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
# scripts/patch_i18n_share.py
import json
from pathlib import Path
import sys

SHARE_TEXT = {
    "ko": "공유하기",
    "en": "Share",
    "ja": "シェア",
    "zh_cn": "分享",
    "es": "Compartir"
}

for lang, text in SHARE_TEXT.items():
    path = Path(f"frontend/src/locales/{lang}.json")
    if not path.exists(): continue
    
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    
    # compatibility 섹션에 share 키 추가
    if "compatibility" not in data: data["compatibility"] = {}
    data["compatibility"]["share"] = text
    
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✅ {lang}.json share 키 추가됨")
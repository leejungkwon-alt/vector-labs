#!/usr/bin/env python3
"""scripts/verify_i18n_tone.py

verify_i18n.py 가 못 잡는 톤 위반을 CI 게이트로 추가.
실행: python scripts/verify_i18n_tone.py  → exit 0 이면 OK
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app" / "services" / "content" / "data"

# 하드 게이트: 이건 나오면 실패
HARD_FAIL = {
    "GRADE_EN": {"Peak", "Favorable", "Neutral", "Caution", "Challenging"},
    "SPANGLISH": re.compile(r"\"name\":\s*\"(?:Blade|Deep|Misty|Perfect Gem|Kai Gang)\""),
    "EN_RESIDUE": re.compile(r"\b(the|you|your|and|with|that|this|for|from)\b.{10,}",
                              re.IGNORECASE),
}

ALLOWED_LATIN = {"gyeol", "premium", "saju", "json", "api"}


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def main() -> int:
    fails = []
    for lang in ("zh_cn", "ja", "es"):
        lang_dir = DATA / lang
        if not lang_dir.exists():
            continue
        for fp in lang_dir.rglob("*.json"):
            rel = str(fp.relative_to(DATA))
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                fails.append(f"PARSE: {rel}")
                continue
            for kp, val in walk(data):
                leaf = kp.split(".")[-1]
                # GRADE_EN
                if leaf in HARD_FAIL["GRADE_EN"] and val in HARD_FAIL["GRADE_EN"]:
                    fails.append(f"GRADE_EN: {rel}:{kp}={val}")
                # EN_RESIDUE (짧은 값 skip)
                if len(val) > 25 and lang in ("zh_cn", "ja"):
                    stops = set(m.group(1).lower()
                                for m in HARD_FAIL["EN_RESIDUE"].finditer(val))
                    stops -= ALLOWED_LATIN
                    if len(stops) >= 2:
                        fails.append(f"EN_RESIDUE: {rel}:{kp}={val[:50]}")
                # SPANGLISH (es name 필드만)
                if lang == "es" and leaf == "name":
                    if re.match(r"^(Blade|Deep|Misty|Perfect Gem|Kai Gang)", val):
                        fails.append(f"SPANGLISH: {rel}:{kp}={val}")

    if fails:
        print(f"❌ i18n tone: {len(fails)}건")
        for f in fails[:30]:
            print(f"   {f}")
        return 1
    print("✅ i18n tone OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
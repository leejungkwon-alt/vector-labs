# audit_i18n_tone_fixed.py — 루트/스크립트 양쪽 호환
import json, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = None
for base in [HERE.parent, *HERE.parents]:
    if (base / "app" / "services" / "content" / "data").is_dir():
        ROOT = base
        break
if ROOT is None:
    sys.exit("프로젝트 루트(app/services/content/data)를 찾을 수 없음")
DATA = ROOT / "app" / "services" / "content" / "data"

LANGS = ("zh_cn", "ja", "es", "en", "ko")

EN_STOP = re.compile(
    r"\b(the|you|your|yours|and|with|that|this|these|those|for|from|"
    r"have|has|had|are|was|were|will|would|can|could|should|not|but|"
    r"about|into|which|they|their|them|there|when|where|what|how|why|"
    r"who|because|while|though)\b", re.IGNORECASE,
)
ALLOWED_LATIN = {"gyeol", "premium", "saju", "json", "api"}
SPANGLISH_PATTERNS = [r"\bBlade\b", r"\bDeep\b", r"\bMisty\b",
                      r"\bPerfect Gem\b", r"\bSpring Jade\b", r"\bKai Gang\b"]
FORBIDDEN_EN = ["magnetic", "unshakeable", "sacred", "profound",
                "unbreakable", "soul connection", "unwavering"]
FORBIDDEN_KO = ["유기적", "애정 전선", "버팀목", "심연의", "고결한"]
GRADE_EN_VALS = {"Peak", "Favorable", "Neutral", "Caution", "Challenging"}


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def looks_english(s: str) -> bool:
    if len(s) < 20:
        return False
    ascii_alpha = sum(1 for c in s if c.isascii() and c.isalpha())
    if ascii_alpha / max(len(s), 1) < 0.55:
        return False
    stops = {m.group(1).lower() for m in EN_STOP.finditer(s)} - ALLOWED_LATIN
    return len(stops) >= 2


def audit_lang(lang):
    issues = []
    lang_dir = DATA / lang
    if not lang_dir.exists():
        return [{"type": "MISSING_DIR", "file": lang}]
    for fp in sorted(lang_dir.rglob("*.json")):
        rel = str(fp.relative_to(DATA))
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append({"type": "PARSE", "file": rel, "detail": str(e)})
            continue
        for kp, val in walk_strings(data):
            leaf = kp.split(".")[-1]
            if lang in ("zh_cn", "ja", "es") and looks_english(val):
                issues.append({"type": "EN_RESIDUE", "file": rel, "path": kp, "sample": val[:70]})
            if val in GRADE_EN_VALS:
                issues.append({"type": "GRADE_EN", "file": rel, "path": kp, "sample": f"{leaf}={val}"})
            if lang == "es":
                for pat in SPANGLISH_PATTERNS:
                    if re.search(pat, val):
                        issues.append({"type": "SPANGLISH", "file": rel, "path": kp, "sample": val[:70]})
                        break
            if lang == "en":
                hits = [w for w in FORBIDDEN_EN if w in val.lower()]
                if hits:
                    issues.append({"type": "FORBIDDEN_EN", "file": rel, "path": kp, "sample": f"{hits} | {val[:50]}"})
            if lang == "ko":
                hits = [w for w in FORBIDDEN_KO if w in val]
                if hits:
                    issues.append({"type": "FORBIDDEN_KO", "file": rel, "path": kp, "sample": f"{hits} | {val[:50]}"})
    return issues


def main():
    print("=" * 68); print("  i18n Tone Audit — read-only"); print("=" * 68)
    all_issues = []
    for lang in LANGS:
        all_issues.extend(audit_lang(lang))
    ko_core = DATA / "ko" / "core.json"
    if ko_core.exists():
        n = ko_core.read_text(encoding="utf-8").count("당신")
        if n >= 5:
            all_issues.append({"type": "KO_DANG_SIN", "file": "ko/core.json", "detail": f"'당신' {n}회"})

    by_type = defaultdict(list)
    for it in all_issues:
        by_type[it["type"]].append(it)

    for t in sorted(by_type):
        items = by_type[t]
        print(f"\n── [{t}] {len(items)}건")
        for it in items[:25]:
            print(f"   {it.get('file',''):<40} {it.get('path',''):<40} "
                  f"{it.get('sample') or it.get('detail','')}")
        if len(items) > 25:
            print(f"   ... 외 {len(items)-25}건")

    total = sum(len(v) for v in by_type.values())
    print("\n" + "=" * 68); print(f"  총 {total}건"); print("=" * 68)
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
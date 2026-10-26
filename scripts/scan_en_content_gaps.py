#!/usr/bin/env python3
"""EN 콘텐츠 완성도 · KO와의 구조 패리티 스캔."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA = ROOT / "app/services/content/data"

ISSUES = []

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def chk_compat_relationships():
    """en/compatibility.json의 friend/family 누락 여부."""
    en = load(DATA / "en" / "compatibility.json")
    for section in ("ELEMENT_CONTENT", "DAY_MASTER_CONTENT", "TEN_GODS_CONTENT", "SINSAL_CONTENT"):
        rels = set(en.get(section, {}).keys())
        missing = {"romance", "business", "friend", "family"} - rels
        if missing:
            ISSUES.append(f"en/compatibility.json::{section} missing: {sorted(missing)}")

def chk_monthly_year_variants():
    """EN monthly/year가 KO처럼 list (3 variants)인지."""
    for fname in ("monthly.json", "year.json"):
        en = load(DATA / "en" / fname)
        ko = load(DATA / "ko" / fname)
        for section in (en, ):
            pass
        # 첫 테마 하나 비교
        key = "MONTHLY_THEME_CONTENT" if fname == "monthly.json" else "YEAR_THEME_CONTENT"
        for theme, raw_en in en.get(key, {}).items():
            raw_ko = ko.get(key, {}).get(theme)
            if isinstance(raw_en, dict) and isinstance(raw_ko, list):
                ISSUES.append(
                    f"en/{fname}::{theme}: EN dict (1 variant) vs KO list ({len(raw_ko)})"
                )

def chk_disclaimer():
    from app.compliance.disclaimers import DISCLAIMER_EN
    en = load(DATA / "en" / "sections.json")
    sections_disc = en.get("DISCLAIMER", "")
    if DISCLAIMER_EN.strip() != sections_disc.strip():
        ISSUES.append("DISCLAIMER_EN mismatch (compliance/disclaimers.py ↔ en/sections.json)")

def chk_stub_pillars():
    stub_pillars = []
    for f in (DATA / "en" / "core_pillars").glob("*.json"):
        d = load(f)
        if len(d.get("narrative", [])) <= 2:
            stub_pillars.append(f.stem)
    if stub_pillars:
        ISSUES.append(f"Stub pillars (narrative<=2): {stub_pillars}")

def chk_awkward_phrases():
    suspicious = [
        "such as in",
        "no aversion to",
        "the power to open the way",
        "big life flow",
        "pushing your grain",
        "the protagonist of the stage",
    ]
    for f in (DATA / "en").rglob("*.json"):
        text = f.read_text(encoding="utf-8")
        for pat in suspicious:
            if pat in text:
                ISSUES.append(f"{f.relative_to(DATA)}: awkward '{pat}'")

def chk_korean_leak():
    for f in (DATA / "en").rglob("*.json"):
        text = f.read_text(encoding="utf-8")
        if any("\uac00" <= c <= "\ud7a3" for c in text):
            ISSUES.append(f"{f.relative_to(DATA)}: Korean characters leaked")

def main():
    chk_compat_relationships()
    chk_monthly_year_variants()
    chk_disclaimer()
    chk_stub_pillars()
    chk_awkward_phrases()
    chk_korean_leak()

    if not ISSUES:
        print("✅ 이슈 없음")
        return 0

    print(f"총 {len(ISSUES)}건:\n")
    for iss in ISSUES:
        print(f"  ❌ {iss}")
    return 1

if __name__ == "__main__":   
    sys.exit(main())
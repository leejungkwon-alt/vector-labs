#!/usr/bin/env python3
"""scripts/migrations/fix_tone_p1.py

P1 톤 리라이트 (판단 완료분):
  A. en/compatibility.json — 24건 (magnetic/profound/unshakeable...)
  B. en/core.json, en/core_pillars/*, en/love.json, en/monthly.json,
     en/personalization.json, en/sinsal.json, en/year.json — 15건
  C. ko/compatibility.json + ko/core_pillars/* + ko/year.json +
     ko/personalization.json — 10건 (버팀목/유기적/고결한)
  D. ko/core.json — 문장 시작 '당신' 정규식 제거 (88건)

실행:
  python scripts/migrations/fix_tone_p1.py            # dry-run
  python scripts/migrations/fix_tone_p1.py --apply
"""
from __future__ import annotations
import json, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def walk(obj, fn, path=()):
    if isinstance(obj, dict):
        return {k: walk(v, fn, path + (k,)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, fn, path + (i,)) for i, v in enumerate(obj)]
    return fn(obj, path)


def apply_patches(rel: str, patches: list[tuple[str, str]], label: str) -> int:
    p = DATA / rel
    if not p.exists():
        print(f"  ❌ 없음: {rel}")
        return 0
    data = json.loads(p.read_text(encoding="utf-8"))
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)

    def fixer(val, _path):
        if not isinstance(val, str):
            return val
        for old, new in patches:
            if old in val:
                val = val.replace(old, new)
        return val

    data = walk(data, fixer)
    after = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if before == after:
        print(f"  ➖ {label}: 변경 없음")
        return 0
    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {'✅' if APPLY else '🔍'} {label}")
    return 1


# ============================================================
# A. en/compatibility.json (24건)
# ============================================================
EN_COMPAT_PATCHES = [
    ("unbreakable emotional bedrock", "solid emotional foundation"),
    ("magnetic chemistry", "intense chemistry"),
    ("profound celebration", "deep appreciation"),
    ("unshakeable organizational foundation", "reliable organizational foundation"),
    ("A magnetic soul connection", "A deep, intuitive connection"),
    ("magnetic soul connection", "deep, intuitive connection"),
    ("rare, heartfelt resonance", "deep resonance"),
    ("soul connection", "connection"),
    ("unbreakable mutual devotion", "lasting mutual devotion"),
    ("unshakeable foundation", "solid foundation"),
    ("profound sense", "deep sense"),
    ("profound comfort", "deep comfort"),
    ("unshakeable pillars", "steady pillars"),
    ("profound emotional growth", "deep emotional growth"),
    ("unbreakable family bond", "lasting family bond"),
    ("magnetic charm", "natural charm"),
    ("profound emotional resonance", "deep emotional resonance"),
    ("unbreakable sanctuary", "safe sanctuary"),
    ("profound psychological trust", "deep psychological trust"),
    ("sacred haven", "quiet haven"),
    ("unshakeable source", "reliable source"),
    ("unwavering confidence", "steady confidence"),
    ("magnetic fascination", "intense fascination"),
    ("profound emotional lessons", "deep emotional lessons"),
    ("profound dynamic", "powerful dynamic"),
    ("unshakeable strategic alliance", "reliable strategic alliance"),
    ("profound mutual trust", "deep mutual trust"),
    ("unwavering corporate stability", "steady corporate stability"),
    ("unwavering resolve", "steady resolve"),
    ("profound sense of", "deep sense of"),
    ("unbreakable trust", "lasting trust"),
]

# ============================================================
# B. en (기타 파일 15건)
# ============================================================
EN_MISC = {
    "en/core.json": [
        ("reliable, deeply grounded, and profoundly responsible",
         "reliable, deeply grounded, and deeply responsible"),
        ("unwavering determination", "steady determination"),
    ],
    "en/core_pillars/丙午.json": [
        ('"magnetic presence"', '"warm presence"'),
    ],
    "en/core_pillars/庚申.json": [
        ('"unshakeable"', '"steady"'),
    ],
    "en/core_pillars/甲寅.json": [
        ("unwavering conviction", "steady conviction"),
        ("straight but unbreakable", "straight but lasting"),
    ],
    "en/love.json": [
        ("unwavering center", "steady center"),
    ],
    "en/monthly.json": [
        ("unshakeable", "steady"),
    ],
    "en/personalization.json": [
        ("highly visible and magnetic", "highly visible and compelling"),
        ("profound adaptability", "deep adaptability"),
        ("Your Magnetic Draw means", "Your natural draw means"),
    ],
    "en/sinsal.json": [
        ('"Magnetic Draw"', '"Natural Draw"'),
    ],
    "en/year.json": [
        ("sacred rest", "quiet rest"),
        ("sacred foundation", "quiet foundation"),
        ("sacred", "quiet"),
    ],
}

# ============================================================
# C. ko (버팀목/유기적/고결한 10건)
# ============================================================
KO_PATCHES = {
    "ko/compatibility.json": [
        ("가장 단단한 버팀목", "가장 든든한 기반"),
        ("든든한 버팀목", "든든한 의지처"),
        ("유기적인 역할 분담", "자연스러운 역할 분담"),
    ],
    "ko/core_pillars/乙酉.json": [
        ("고결한 꽃", "기품 있는 꽃"),
    ],
    "ko/core_pillars/壬寅.json": [
        ("든든한 버팀목", "든든한 토양"),
    ],
    "ko/core_pillars/己酉.json": [
        ("고결한 미적 감각", "단아한 미적 감각"),
    ],
    "ko/core_pillars/庚辰.json": [
        ("든든한 버팀목", "든든한 중심"),
    ],
    "ko/personalization.json": [
        ("든든한 버팀목", "든든한 의지처"),
    ],
    "ko/year.json": [
        ("든든한 버팀목", "든든한 지주"),
    ],
}

# ============================================================
# D. ko/core.json — 문장 시작 '당신' 제거 (정규식)
# ============================================================
DANGSIN_RE = re.compile(r"(^|[.!?]\s+|(?<=\n))당신(은|이|의|을|를|에게|에게는|도|만)?\s+")


def fix_ko_core_dangsin() -> int:
    p = DATA / "ko" / "core.json"
    if not p.exists():
        print("  ❌ ko/core.json 없음")
        return 0
    data = json.loads(p.read_text(encoding="utf-8"))
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)

    def fixer(val, _path):
        if not isinstance(val, str):
            return val
        return DANGSIN_RE.sub(r"\1", val)

    data = walk(data, fixer)
    after = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if before == after:
        print("  ➖ ko/core 당신 제거: 변경 없음")
        return 0
    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_before = json.loads(before).__str__().count("당신")
    n_after = json.dumps(data, ensure_ascii=False).count("당신")
    print(f"  {'✅' if APPLY else '🔍'} ko/core 당신 제거: {n_before} → {n_after}")
    return 1


# ============================================================
def main() -> int:
    print("=" * 66)
    print(f"  fix_tone_p1 ({'APPLY' if APPLY else 'DRY-RUN'})")
    print("=" * 66)

    # A. en/compatibility.json
    apply_patches("en/compatibility.json", EN_COMPAT_PATCHES, "en/compatibility")

    # B. en 기타
    for rel, patches in EN_MISC.items():
        apply_patches(rel, patches, rel)

    # C. ko
    for rel, patches in KO_PATCHES.items():
        apply_patches(rel, patches, rel)

    # D. ko/core 당신
    fix_ko_core_dangsin()

    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    else:
        print(f"  백업: *. {TS} .bak")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
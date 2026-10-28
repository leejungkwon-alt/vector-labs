#!/usr/bin/env python3
"""scripts/migrations/fix_ko_tone_p1.py

안전한 KO 톤 정비 (판단 불필요):
  1. ko/core.json  '당신' 문장 시작 제거 (해요체 자연화)
  2. ko/compatibility.json  '애정 전선' → '관계', '유기적인 조화' → '자연스러운 조화'
  3. ko 전체 '버팀목' → '의지할 곳' (문맥 안전한 케이스만)

실행:
  python scripts/migrations/fix_ko_tone_p1.py
  python scripts/migrations/fix_ko_tone_p1.py --apply
"""
from __future__ import annotations
import json, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# 문장 시작에서만 '당신+조사 ' 제거 (중간은 건드리지 않음)
DANGSIN_START = re.compile(
    r'(^|[.!?]\s+|(?<=\n))당신(은|이|의|을|를|에게|에게는|도|만)\s+',
)

SAFE_KO_SUBS = [
    ("애정 전선", "관계"),
    ("유기적인 조화", "자연스러운 조화"),
    ("유기적인 시너지", "자연스러운 시너지"),
    ("가장 단단한 버팀목", "가장 든든한 의지처"),
    ("버팀목이 되어", "의지처가 되어"),
]


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def strip_start_dangsin(s: str) -> str:
    return DANGSIN_START.sub(r'\1', s)


def walk_fix(obj, fixer):
    if isinstance(obj, dict):
        return {k: walk_fix(v, fixer) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk_fix(v, fixer) for v in obj]
    if isinstance(obj, str):
        return fixer(obj)
    return obj


def apply_ko(path: Path, fixer, label: str) -> None:
    if not path.exists():
        print(f"  ❌ 없음: {path.relative_to(DATA)}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ❌ 파싱 실패: {path.relative_to(DATA)} ({e})")
        return

    before = json.dumps(data, ensure_ascii=False)
    fixed = walk_fix(data, fixer)
    after = json.dumps(fixed, ensure_ascii=False)

    if before == after:
        print(f"  ➖ {label}: 변경 없음")
        return

    if APPLY:
        backup(path)
        path.write_text(json.dumps(fixed, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        print(f"  ✅ {label}")
    else:
        print(f"  🔍 {label} (dry-run)")


def main() -> int:
    print("=" * 66); print(f"  fix_ko_tone_p1 ({'APPLY' if APPLY else 'DRY-RUN'})"); print("=" * 66)

    # 1. ko/core.json — 당신 제거
    apply_ko(DATA / "ko" / "core.json",
             lambda s: strip_start_dangsin(s), "ko/core 당신 제거")

    # 2. ko 전체 파일 — 안전 치환
    def ko_fixer(s: str) -> str:
        s = strip_start_dangsin(s)
        for old, new in SAFE_KO_SUBS:
            s = s.replace(old, new)
        return s

    ko_dir = DATA / "ko"
    for fp in sorted(ko_dir.rglob("*.json")):
        rel = fp.relative_to(DATA)
        if "core_pillars" in fp.parts:  # 이미 톤 좋음, 스킵
            continue
        apply_ko(fp, ko_fixer, f"{rel}")

    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    else:
        print(f"  백업: *. {TS} .bak")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
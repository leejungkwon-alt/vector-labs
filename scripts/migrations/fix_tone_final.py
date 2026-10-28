#!/usr/bin/env python3
"""scripts/migrations/fix_tone_final.py

Tone Audit 최종 정리 (8건 + KO 당신 제거):
  A. en/compatibility.json — 'profound connection' → 'deep connection'
  B. en/core_pillars/丙午.json — 'magnetic presence' → 'warm presence'
  C. en/core_pillars/庚申.json — 'unshakeable' → 'steady'
  D. en/sinsal.json — 'Magnetic Draw' → 'Natural Draw'
  E. ko/compatibility.json — '버팀목' → '의지처'
  F. ko/year.json — '버팀목' → '기둥'
  G. ko/core.json — 문장 중간 포함 '당신' 일괄 제거 (84건 → 0건)

실행:
  python scripts/migrations/fix_tone_final.py            # dry-run
  python scripts/migrations/fix_tone_final.py --apply
"""
from __future__ import annotations
import json, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# '당신은', '당신의', '당신이' 등을 빈 문자열로 (뒤따르는 공백 포함 제거)
DANGSIN_RE = re.compile(r"당신(은|이|의|을|를|에게|에게는|도|만)?\s*")


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def walk(obj, fn):
    if isinstance(obj, dict):
        return {k: walk(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, fn) for v in obj]
    return fn(obj)


def apply_patches(rel: str, patches: list[tuple[str, str]], label: str) -> None:
    p = DATA / rel
    if not p.exists():
        print(f"  ❌ 없음: {rel}")
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)

    def fixer(val):
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
        return
    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {'✅' if APPLY else '🔍'} {label}")


def fix_ko_core_dangsin() -> None:
    p = DATA / "ko" / "core.json"
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    before = json.dumps(data, ensure_ascii=False)
    n_before = before.count("당신")

    def fixer(val):
        if not isinstance(val, str):
            return val
        return DANGSIN_RE.sub("", val)

    data = walk(data, fixer)
    after = json.dumps(data, ensure_ascii=False)
    n_after = after.count("당신")

    if n_before == n_after:
        print("  ➖ ko/core 당신 제거: 변경 없음")
        return

    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {'✅' if APPLY else '🔍'} ko/core 당신 완전 제거: {n_before} → {n_after}")


def main() -> int:
    print("=" * 66)
    print(f"  fix_tone_final ({'APPLY' if APPLY else 'DRY-RUN'})")
    print("=" * 66)

    # A. en/compatibility.json
    apply_patches("en/compatibility.json", [
        ("profound connection", "deep connection")
    ], "en/compatibility (profound)")

    # B. en/core_pillars/丙午.json
    apply_patches("en/core_pillars/丙午.json", [
        ('"magnetic presence"', '"warm presence"')
    ], "en/core_pillars/丙午 (magnetic)")

    # C. en/core_pillars/庚申.json
    apply_patches("en/core_pillars/庚申.json", [
        ('"unshakeable"', '"steady"')
    ], "en/core_pillars/庚申 (unshakeable)")

    # D. en/sinsal.json
    apply_patches("en/sinsal.json", [
        ('"Magnetic Draw"', '"Natural Draw"')
    ], "en/sinsal (Magnetic Draw)")

    # E. ko/compatibility.json
    apply_patches("ko/compatibility.json", [
        ("버팀목", "의지처")
    ], "ko/compatibility (버팀목)")

    # F. ko/year.json
    apply_patches("ko/year.json", [
        ("버팀목", "기둥")
    ], "ko/year (버팀목)")

    # G. ko/core.json (당신)
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIX-25: 멀티라인 console.log("[Boot]") -> if (__DEV__) 가드. + FIX-22 컨텍스트 덤프."""
from __future__ import annotations
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path("frontend")
APPLY = False


def P(s: str) -> None:
    try: print(s)
    except UnicodeEncodeError: print(s.encode("ascii", "replace").decode("ascii"))


def read(p: Path) -> str: return p.read_text(encoding="utf-8")


def backup_write(p: Path, s: str) -> None:
    if not APPLY: return
    bak = p.with_suffix(p.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(p, bak)
    p.write_text(s, encoding="utf-8")


# ------------------------------------------------------------------ FIX-25
def fix_25() -> str:
    p = ROOT / "app/index.tsx"
    if not p.exists():
        return f"[SKIP] FIX-25 {p.name} 없음"
    src = read(p)
    # 이미 가드된 경우
    if re.search(r"if\s*\(\s*__DEV__\s*\)\s*console\.log\s*\(\s*\n?\s*[\"']\[Boot\]", src):
        return "[SKIP] FIX-25 이미 __DEV__ 가드됨"

    # console.log(  + (줄바꿈 + 공백) + "[Boot]
    pat = re.compile(
        r"^(?P<indent>[ \t]*)console\.log\(\s*\n(?P<next>[ \t]*)(?P<q>[\"'])\[Boot\]",
        re.MULTILINE,
    )
    m = pat.search(src)
    if not m:
        return "[SKIP] FIX-25 [Boot] console.log 패턴 없음"

    def _repl(mm: re.Match) -> str:
        ind = mm.group("indent")
        nxt = mm.group("next")
        q = mm.group("q")
        return f"{ind}if (__DEV__) console.log(\n{nxt}{q}[Boot]"

    new = pat.sub(_repl, src, count=1)
    if new == src:
        return "[SKIP] FIX-25 치환 실패"
    backup_write(p, new)
    return f"[{'OK' if APPLY else 'DRY'}] FIX-25 {p.name}: if(__DEV__) console.log('[Boot]...')"


# ------------------------------------------------------------------ dump helpers
def dump_file(p: Path, head: int = 40, tail: int = 0) -> None:
    if not p.exists():
        P(f"  (없음) {p}"); return
    lines = read(p).splitlines()
    end = head if not tail else len(lines) - tail
    for i, ln in enumerate(lines[:end], 1):
        P(f"  {i:>3}| {ln}")
    if tail and end < len(lines):
        P("  ...")
        for i, ln in enumerate(lines[-tail:], len(lines) - tail + 1):
            P(f"  {i:>3}| {ln}")


def dump_ctx(p: Path, needles: list[str], before: int = 2, after: int = 6) -> None:
    if not p.exists():
        P(f"  (없음) {p}"); return
    lines = read(p).splitlines()
    for i, ln in enumerate(lines):
        if any(n in ln for n in needles):
            lo, hi = max(0, i - before), min(len(lines), i + after + 1)
            P(f"  --- {p.name} L{i+1} ---")
            for j in range(lo, hi):
                mark = ">>" if j == i else "  "
                P(f"  {mark}{j+1:>4}| {lines[j]}")


# ------------------------------------------------------------------ main
def main() -> int:
    global APPLY
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dump", action="store_true", help="client.ts / FIX-22 컨텍스트 덤프")
    args = ap.parse_args()
    APPLY = args.apply

    P("=" * 68)
    P(f"ROOT = {ROOT.resolve()}   MODE = {'APPLY' if APPLY else 'DRY'}")
    P("=" * 68)

    P(fix_25())

    if args.dump:
        P("\n--- client.ts (앞 50줄) ---")
        dump_file(ROOT / "src/api/client.ts", head=50)

        P("\n--- client.ts  BASE_URL  컨텍스트 ---")
        dump_ctx(ROOT / "src/api/client.ts",
                 ["BASE_URL", "run.app", "https://", "API_URL"], before=2, after=4)

        P("\n--- compatibility.tsx  offsetHours  컨텍스트 ---")
        dump_ctx(ROOT / "app/(tabs)/compatibility.tsx", ["offsetHours", "longitude"], before=2, after=4)

        P("\n--- birth-input.tsx  offsetHours  컨텍스트 ---")
        dump_ctx(ROOT / "app/birth-input.tsx", ["offsetHours", "longitude"], before=2, after=4)

    if not APPLY:
        P("\n>> 적용: python fix_frontend_v3.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
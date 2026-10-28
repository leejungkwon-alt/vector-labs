#!/usr/bin/env python3
"""
scripts/apply_handoff_step4.py

Handoff Step 4 — CrisisBanner 안전 마진 (선택 적용).

  [M1] styles.title      += flexShrink: 1
  [M2] styles.linkText   += textAlign: "center", flexShrink: 1

Usage:
  python scripts/apply_handoff_step4.py           # dry-run
  python scripts/apply_handoff_step4.py --apply
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNER = ROOT / "frontend" / "src" / "components" / "CrisisBanner.tsx"

OLD_TITLE = """  title: {
    fontSize: 14,
    fontWeight: "700",
    color: "#8B1E1E",
    marginLeft: 6,
  },"""

NEW_TITLE = """  title: {
    fontSize: 14,
    fontWeight: "700",
    color: "#8B1E1E",
    marginLeft: 6,
    flexShrink: 1,
  },"""

OLD_LINK = """  linkText: {
    fontSize: 12,
    color: "#8B1E1E",
    textDecorationLine: "underline",
  },"""

NEW_LINK = """  linkText: {
    fontSize: 12,
    color: "#8B1E1E",
    textDecorationLine: "underline",
    textAlign: "center",
    flexShrink: 1,
  },"""


def plan() -> None:
    print("=" * 72)
    print("  apply_handoff_step4  (DRY-RUN/APPLY)")
    print("=" * 72)
    text = BANNER.read_text(encoding="utf-8")
    print(f"  [M1] title.flexShrink    : {'already' if 'flexShrink: 1' in text.split('title:')[1].split('},')[0] else 'PATCH'}")
    print(f"  [M2] linkText.textAlign  : {'already' if 'textAlign: \"center\"' in text.split('linkText:')[1].split('},')[0] else 'PATCH'}")
    print(f"  [M2] linkText.flexShrink : {'already' if 'flexShrink: 1' in text.split('linkText:')[1].split('},')[0] else 'PATCH'}")


def apply() -> None:
    text = BANNER.read_text(encoding="utf-8")
    changed = 0
    if OLD_TITLE in text:
        text = text.replace(OLD_TITLE, NEW_TITLE, 1)
        print("  [M1] patched title.flexShrink")
        changed += 1
    else:
        print("  [M1] skip (already / not found)")
    if OLD_LINK in text:
        text = text.replace(OLD_LINK, NEW_LINK, 1)
        print("  [M2] patched linkText.textAlign + flexShrink")
        changed += 1
    else:
        print("  [M2] skip (already / not found)")
    if changed:
        with BANNER.open("w", encoding="utf-8", newline="\n") as f:
            f.write(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    plan()
    print("-" * 72)
    if not args.apply:
        print("  dry-run 완료 → --apply 로 적용")
        print("=" * 72)
        return 0
    apply()
    print("-" * 72)
    print("  apply 완료")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
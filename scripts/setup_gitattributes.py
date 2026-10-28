#!/usr/bin/env python3
"""Create/update .gitattributes for LF normalization.

Usage:
  python scripts/setup_gitattributes.py           # dry-run
  python scripts/setup_gitattributes.py --apply   # write file
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".gitattributes"

CONTENT = """\
# Normalize to LF on commit and checkout
* text=auto eol=lf

# Windows-native scripts keep CRLF
*.bat  text eol=crlf
*.cmd  text eol=crlf
*.ps1  text eol=crlf

# Binary — do not touch
*.png  binary
*.jpg  binary
*.jpeg binary
*.gif  binary
*.ico  binary
*.pdf  binary
"""

def main() -> int:
    apply = "--apply" in sys.argv
    existing = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""

    if existing == CONTENT:
        print("[skip] .gitattributes already up to date")
        return 0

    if existing and "* text=auto eol=lf" in existing:
        print("[skip] .gitattributes already contains eol=lf rule — review manually")
        print("       current content:")
        print(existing)
        return 0

    if not apply:
        print("[dry-run] would write .gitattributes with LF normalization rules")
        if existing:
            print("[warn] .gitattributes exists with different content — diff manually")
        return 0

    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(CONTENT)
    print(f"[applied] wrote {TARGET.name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
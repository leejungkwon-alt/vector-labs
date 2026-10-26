#!/usr/bin/env python3
"""P2: awkward phrase 문맥 덤프 (read-only)."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app/services/content/data/en"

PATTERNS = [
    "such as in",
    "no aversion to",
    "the power to open the way",
    "big life flow",
    "pushing your grain",
    "the protagonist of the stage",
]

def iter_strings(node, path="root"):
    """JSON을 순회하며 (path, string) 스트림."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from iter_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_strings(v, f"{path}[{i}]")

def main() -> int:
    found = 0
    for f in sorted(DATA.rglob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        for jsonpath, text in iter_strings(data):
            for pat in PATTERNS:
                if pat in text:
                    found += 1
                    print(f"\n📄 {f.name}  ::  {jsonpath}")
                    print(f"   [{pat}]")
                    print(f"   {text}")
    print(f"\n총 {found}건")
    return 0

if __name__ == "__main__":
    sys.exit(main())
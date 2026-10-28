#!/usr/bin/env python3
"""루트 ./app.json 참조 스캔 후 .legacy 로 rename.

Usage:
  python scripts/cleanup_root_app_json.py           # dry-run
  python scripts/cleanup_root_app_json.py --apply   # 실제 rename
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "app.json"
LEGACY = ROOT / "app.json.legacy"

SKIP_DIRS = {".git", "node_modules", ".expo", "__pycache__",
             ".pytest_cache", "dist", "build", ".venv"}
SCAN_EXTS = {".js", ".ts", ".tsx", ".jsx", ".json", ".py",
             ".yml", ".yaml", ".toml", ".md"}

PATTERNS = [
    re.compile(r'\.\.\s*/\s*app\.json'),
    re.compile(r'require\(\s*[\'"]\./app\.json[\'"]\s*\)'),
    re.compile(r'from\s+[\'"]\./app\.json[\'"]'),
    re.compile(r'path\.join\([^)]*[\'"]app\.json[\'"]\s*\)'),
    re.compile(r'["\']\.\/app\.json["\']'),
]

def scan_refs() -> list[Path]:
    hits: list[Path] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p == TARGET or p.suffix not in SCAN_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if any(pat.search(text) for pat in PATTERNS):
            hits.append(p)
    return hits

def main() -> int:
    apply = "--apply" in sys.argv
    if not TARGET.exists():
        print(f"[skip] {TARGET.name} not found (already clean)")
        return 0

    refs = scan_refs()
    if refs:
        print(f"[BLOCK] {len(refs)} possible reference(s) to root app.json:")
        for r in refs:
            print(f"   - {r.relative_to(ROOT)}")
        print("       resolve these first, then re-run.")
        return 1

    fe = ROOT / "frontend" / "app.json"
    if fe.exists() and "privacyManifests" in fe.read_text(encoding="utf-8", errors="ignore"):
        print("[info] frontend/app.json has privacyManifests ✓")
    else:
        print("[warn] frontend/app.json missing or no privacyManifests — verify G1 fix still in place")

    if not apply:
        print(f"[dry-run] would rename {TARGET.name} -> {LEGACY.name}")
        return 0

    if LEGACY.exists():
        print(f"[error] {LEGACY.name} already exists, refusing to overwrite")
        return 1

    TARGET.rename(LEGACY)
    print(f"[applied] {TARGET.name} -> {LEGACY.name}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
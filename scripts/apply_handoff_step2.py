#!/usr/bin/env python3
"""
scripts/apply_handoff_step2.py

Handoff Step 2 — script folder cleanup + CI wiring.

  1) scripts/migrations/  (one-off migrations, 12 files)        → delete
  2) scripts/preview_report.py.bak.*                            → delete
  3) scripts/_todo_english_narratives.{json,txt} (orphaned)     → delete
  4) scripts/fix_es_post.py, scripts/verify_es.py (legacy)      → delete
  5) .github/workflows/ci.yml                                   → create
     (verify_i18n → verify_i18n_tone → pytest)

Usage:
  python scripts/apply_handoff_step2.py           # dry-run (default)
  python scripts/apply_handoff_step2.py --apply   # apply
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

GROUPS: list[tuple[str, list[Path]]] = [
    ("migrations (one-off)",      [SCRIPTS / "migrations"]),
    ("backup",                    [SCRIPTS / "preview_report.py.bak.20261025_235347"]),
    ("orphaned todo data",        [SCRIPTS / "_todo_english_narratives.json",
                                   SCRIPTS / "_todo_english_narratives_readable.txt"]),
    ("legacy one-off es scripts", [SCRIPTS / "fix_es_post.py",
                                   SCRIPTS / "verify_es.py"]),
]

CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"

CI_CONTENT = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: i18n keys guardrail
        run: python scripts/verify_i18n.py

      - name: i18n tone guardrail
        run: python scripts/verify_i18n_tone.py

      - name: Tests
        run: python -m pytest -q
"""


def show_plan(apply: bool) -> None:
    print("=" * 72)
    print(f"  apply_handoff_step2  ({'APPLY' if apply else 'DRY-RUN'})")
    print("=" * 72)
    for label, paths in GROUPS:
        print(f"  [{label}]")
        for p in paths:
            if not p.exists():
                print(f"    SKIP    {p.relative_to(ROOT)}  (not found)")
                continue
            if p.is_dir():
                files = [f for f in sorted(p.rglob("*")) if f.is_file()]
                print(f"    DELETE  {p.relative_to(ROOT)}/  ({len(files)} files)")
                for f in files:
                    print(f"              - {f.relative_to(ROOT)}")
            else:
                print(f"    DELETE  {p.relative_to(ROOT)}  ({p.stat().st_size} bytes)")
    if CI_PATH.exists():
        print(f"  [CI]  SKIP    {CI_PATH.relative_to(ROOT)}  (already exists)")
    else:
        print(f"  [CI]  CREATE  {CI_PATH.relative_to(ROOT)}")


def execute() -> None:
    for _, paths in GROUPS:
        for p in paths:
            if not p.exists():
                continue
            if p.is_dir():
                shutil.rmtree(p)
                print(f"  deleted dir : {p.relative_to(ROOT)}")
            else:
                p.unlink()
                print(f"  deleted file: {p.relative_to(ROOT)}")
    if CI_PATH.exists():
        print(f"  skipped CI  : {CI_PATH.relative_to(ROOT)} (already exists)")
    else:
        CI_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CI_PATH.open("w", encoding="utf-8", newline="\n") as f:
            f.write(CI_CONTENT)
        print(f"  created CI  : {CI_PATH.relative_to(ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="실제로 삭제/생성 수행 (기본은 dry-run)")
    args = ap.parse_args()

    show_plan(args.apply)
    print("-" * 72)
    if not args.apply:
        print("  dry-run 완료 → --apply 로 적용")
        print("=" * 72)
        return 0

    execute()
    print("-" * 72)
    print("  apply 완료")
    print("  다음: git add -A && git status && git diff --cached --stat")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
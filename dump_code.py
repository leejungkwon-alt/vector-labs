#!/usr/bin/env python3
"""
프로젝트 코드를 리뷰용 단일 텍스트 파일로 덤프합니다.

사용법 (프로젝트 루트에서):
    python dump_code.py                      # 기본: saju_complete_code.txt
    python dump_code.py -o review.txt
    python dump_code.py --include-scripts    # _add_*.py 패치 스크립트도 포함
    python dump_code.py --frontend           # frontend 소스(.ts/.tsx/.js/.json 설정)도 포함

기본 동작
- node_modules, venv, .git, __pycache__ 등은 가지치기(탐색 자체를 안 함)
- 콘텐츠 JSON(app/services/content/data/**)을 포함 (로더가 JSON 우선이므로 필수)
- _add_*.py / _fix_*.py / _test_*.py 같은 일회성 패치 스크립트는 제외 (코드가 중복되어 덤프가 부풀어짐)
- .env, *.db, 키/인증서 파일은 항상 제외 (비밀 유출 방지)
- 파일 순서는 경로순으로 고정, 끝에 요약(파일 수/크기) 출력
"""
import argparse
import os
import sys

PRUNE_DIRS = {
    "node_modules", "venv", ".venv", "env", "__pycache__", ".git", ".idea",
    ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build",
    ".expo", "android", "ios", "coverage", ".next",
}
NEVER_FILES = {".env", ".env.local", ".env.production"}
NEVER_SUFFIX = (".db", ".sqlite", ".sqlite3", ".pem", ".key", ".p12", ".keystore", ".jks")
SCRIPT_PREFIXES = ("_add_", "_fix_", "_test_", "_patch_")

BACKEND_SUFFIX = (".py",)
BACKEND_NAMES = {"pytest.ini", "pyproject.toml", "Dockerfile", ".env.example", "setup.cfg"}
FRONTEND_SUFFIX = (".ts", ".tsx", ".js", ".jsx")
FRONTEND_NAMES = {"package.json", "app.json", "tsconfig.json"}


def is_requirements(name: str) -> bool:
    return name.startswith("requirements") and name.endswith(".txt")


def wanted(rel: str, name: str, args) -> bool:
    low = name.lower()
    if name in NEVER_FILES or low.endswith(NEVER_SUFFIX):
        return False
    if name in (os.path.basename(args.output), "dump_code.py"):
        return False
    in_frontend = rel.replace("\\", "/").startswith("frontend/")
    if in_frontend:
        return args.frontend and (low.endswith(FRONTEND_SUFFIX) or name in FRONTEND_NAMES)
    if not args.include_scripts and name.startswith(SCRIPT_PREFIXES):
        return False
    if low.endswith(BACKEND_SUFFIX) or name in BACKEND_NAMES or is_requirements(name):
        return True
    if low.endswith(".json") and "/content/data/" in "/" + rel.replace("\\", "/"):
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="saju_complete_code.txt")
    ap.add_argument("--root", default=".")
    ap.add_argument("--include-scripts", action="store_true")
    ap.add_argument("--frontend", action="store_true")
    ap.add_argument("--max-file-kb", type=int, default=400,
                    help="이 크기를 넘는 개별 파일은 앞부분만 덤프")
    args = ap.parse_args()

    collected = []
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = sorted(d for d in dirnames if d not in PRUNE_DIRS)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, args.root)
            if wanted(rel, fn, args):
                collected.append((rel.replace("\\", "/"), full))
    collected.sort()

    total = 0
    with open(args.output, "w", encoding="utf-8", newline="\n") as out:
        out.write("=== TREE ===\n" + "\n".join(r for r, _ in collected) + "\n\n")
        for rel, full in collected:
            try:
                with open(full, encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                print(f"[skip: not utf-8] {rel}", file=sys.stderr)
                continue
            limit = args.max_file_kb * 1024
            if len(text.encode("utf-8")) > limit:
                text = text[:limit] + f"\n... [TRUNCATED at {args.max_file_kb}KB] ...\n"
            out.write(f"=== FILE: {rel} ===\n{text}\n\n")
            total += len(text)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"{len(collected)} files -> {args.output} ({size_kb:,.0f} KB, {total:,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
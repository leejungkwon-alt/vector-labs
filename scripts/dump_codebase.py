#!/usr/bin/env python3
"""
scripts/dump_codebase.py

프로젝트 전체 코드를 단일 텍스트 파일로 덤프합니다.
LLM 컨텍스트 주입 / 코드 리뷰 / 백업용.

특징:
  - git ls-files 기반 → .gitignore 자동 존중 (.git 없으면 os.walk 폴백)
  - .env, *.db, 바이너리(널바이트/비율 sniff), 대용량 파일 자동 제외
  - 프로젝트별 preset (all / frontend / tma / backend / minimal)
  - 트리 + 파일 내용을 === FILE: path === 구분자로 출력

사용 예:
  python scripts/dump_codebase.py
  python scripts/dump_codebase.py -o saju_dump.txt
  python scripts/dump_codebase.py --preset frontend
  python scripts/dump_codebase.py --preset tma -o tma_dump.txt
  python scripts/dump_codebase.py --include "app/**" "tests/**" -o api_dump.txt
  python scripts/dump_codebase.py --no-content         # 트리만
  python scripts/dump_codebase.py --max-file-size 200000
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# 기본 제외 규칙
# ---------------------------------------------------------------------------

EXCLUDE_DIRS = {
    ".git", ".github", ".vscode", ".idea", ".vs",
    "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".nox", ".ipynb_checkpoints",
    "dist", "build", ".next", "out", ".nuxt", ".output", "coverage",
    ".vercel", ".turbo", ".cache", ".parcel-cache",
    "venv", ".venv", "env", "site-packages",
    "data",                    # data/auth.db 등 런타임 데이터
}

EXCLUDE_GLOBS = {
    # 파이썬 캐시/바이너리
    "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dylib", "*.dll", "*.exe",
    # 로그/임시
    "*.log", "*.tmp", "*.swp", "*.swo", "*.bak", "*.bak_*", "*.orig", "*.rej",
    # 이미지/미디어
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp", "*.ico", "*.bmp", "*.tiff",
    "*.svg",  # 소스로 쓰는 svg가 있으면 --include ".svg"로 override
    "*.mp4", "*.mov", "*.avi", "*.mkv", "*.mp3", "*.wav", "*.ogg", "*.flac",
    "*.pdf", "*.docx", "*.xlsx", "*.pptx",
    # 압축
    "*.zip", "*.tar", "*.tar.gz", "*.tgz", "*.gz", "*.bz2", "*.xz", "*.7z", "*.rar",
    # 폰트
    "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot",
    # 시크릿 / DB
    ".env", ".env.local", ".env.production", ".env.development",
    "*.pem", "*.key", "*.crt", "*.p12",
    "*.db", "*.sqlite", "*.sqlite3", "*.db-journal",
    # 락파일 (너무 길어서 컨텍스트만 잡아먹음)
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", "uv.lock", "Pipfile.lock",
    # OS
    ".DS_Store", "Thumbs.db", "desktop.ini",
}

# 명시적으로 포함할 override (glob 매칭 전에 체크)
INCLUDE_OVERRIDES = {
    ".env.example",
    ".gitignore",
    ".dockerignore",
}

# ---------------------------------------------------------------------------
# 프로젝트 preset
# ---------------------------------------------------------------------------

PRESETS: dict[str, list[str]] = {
    # 살아있는 것만 (죽은 frontend/, _archive 제외) — 기본
    "all": [],
    # 메인 웹 프론트만
    "frontend": ["frontend/*", "frontend/**/*"],
    # 텔레그램 미니앱만
    "tma": ["tma/*", "tma/**/*"],
    # 백엔드 API + 엔진 + 스키마
    "backend": [
        "app/*", "app/**/*",
        "tests/*", "tests/**/*",
        "conftest.py",
        "requirements.txt", "Dockerfile", ".env.example",
    ],
    # 최소 컨텍스트 (README + 엔트리포인트 + 스키마)
    "minimal": [
        "app/main.py",
        "app/api/v1/endpoints/*.py",
        "app/schemas/*.py",
        "README*",
        "requirements.txt", "Dockerfile",
        ".env.example",
    ],
}

# ---------------------------------------------------------------------------
# 필터 헬퍼
# ---------------------------------------------------------------------------

def is_excluded_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS


def is_excluded_file(rel: str, name: str) -> bool:
    # override 우선
    if rel in INCLUDE_OVERRIDES or name in INCLUDE_OVERRIDES:
        return False
    for pat in EXCLUDE_GLOBS:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel, pat):
            return True
    return False


def is_binary(path: Path, sniff: int = 8192) -> bool:
    """
    바이너리 판정.
    한국어/일본어/중국어 UTF-8은 글자당 3바이트가 0x80 이상이라
    기존 ASCII 비율 검사로는 정상 텍스트가 바이너리로 오판됐다.
    """
    try:
        with path.open("rb") as f:
            chunk = f.read(sniff)
    except OSError:
        return True

    if not chunk:
        return False

    # 1) 널 바이트 = 바이너리 확정
    if b"\x00" in chunk:
        return True

    # 2) UTF-8로 디코딩되면 텍스트 (한/중/일 포함)
    try:
        chunk.decode("utf-8")
        return False
    except UnicodeDecodeError:
        pass

    # 3) UTF-8이 아니면, printable 비율로 최종 판정
    text_ok = set(range(32, 127)) | {9, 10, 13}
    nontext = sum(1 for b in chunk if b not in text_ok)
    return (nontext / len(chunk)) > 0.30

# ---------------------------------------------------------------------------
# 파일 수집
# ---------------------------------------------------------------------------

def collect_via_git(root: Path) -> list[Path] | None:
    """git ls-files 기반 수집. git이 없거나 실패하면 None."""
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root, stderr=subprocess.DEVNULL, timeout=20,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None

    paths: list[Path] = []
    for raw in out.split(b"\x00"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        p = root / rel
        if p.is_file():
            paths.append(p)
    return paths


def collect_via_walk(root: Path) -> list[Path]:
    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not is_excluded_dir(d))
        for fname in sorted(filenames):
            paths.append(Path(dirpath) / fname)
    return paths


def apply_filters(
    root: Path,
    paths: list[Path],
    includes: list[str],
    excludes: list[str],
) -> list[Path]:
    result: list[Path] = []
    for p in paths:
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            continue
        name = p.name
        if is_excluded_file(rel, name):
            continue
        if includes and not any(
            fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat)
            for pat in includes
        ):
            continue
        if excludes and any(
            fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat)
            for pat in excludes
        ):
            continue
        result.append(p)
    return sorted(set(result))

# ---------------------------------------------------------------------------
# 트리 렌더
# ---------------------------------------------------------------------------

def build_tree(root: Path, files: list[Path]) -> str:
    rels = sorted(f.relative_to(root).as_posix() for f in files)
    tree: dict = {}
    for rel in rels:
        parts = rel.split("/")
        cur = tree
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = None

    lines: list[str] = []

    def render(node: dict, prefix: str = "") -> None:
        # dict(디렉터리) 먼저, 파일 나중
        entries = sorted(node.keys(), key=lambda k: (node[k] is None, k))
        for i, name in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            child = node[name]
            if isinstance(child, dict):
                ext = "    " if is_last else "│   "
                render(child, prefix + ext)

    render(tree)
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# 메인 덤프
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[!] not a directory: {root}", file=sys.stderr)
        return 2

    out_path = Path(args.output).resolve()

    # preset ↔ include 병합
    includes = list(args.include or [])
    if args.preset and args.preset in PRESETS:
        includes = PRESETS[args.preset] + includes

    print(f"[*] root: {root}", file=sys.stderr)
    print(f"[*] preset: {args.preset or '(none)'}", file=sys.stderr)

    # 수집
    if args.use_git:
        paths = collect_via_git(root)
        if paths is not None:
            print(f"[*] git ls-files: {len(paths)} files", file=sys.stderr)
        else:
            print("[*] git unavailable → os.walk fallback", file=sys.stderr)
            paths = collect_via_walk(root)
    else:
        paths = collect_via_walk(root)
        print(f"[*] os.walk: {len(paths)} files", file=sys.stderr)

    files = apply_filters(root, paths, includes, args.exclude or [])
    total = len(files)
    print(f"[*] after filters: {total} files", file=sys.stderr)

    if total == 0:
        print("[!] no files matched", file=sys.stderr)
        return 1

    # 조립
    chunks: list[str] = []

    if not args.no_tree:
        chunks.append("=== TREE ===")
        chunks.append(build_tree(root, files))

    if not args.no_content:
        kept = skipped_bin = skipped_big = skipped_err = 0
        for i, f in enumerate(files, 1):
            rel = f.relative_to(root).as_posix()

            try:
                size = f.stat().st_size
            except OSError:
                skipped_err += 1
                continue

            if size > args.max_file_size:
                chunks.append(f"=== FILE: {rel} ===")
                chunks.append(f"[skipped: {size:,} bytes > {args.max_file_size:,}]")
                skipped_big += 1
                continue

            if is_binary(f):
                chunks.append(f"=== FILE: {rel} ===")
                chunks.append("[skipped: binary]")
                skipped_bin += 1
                continue

            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                chunks.append(f"=== FILE: {rel} ===")
                chunks.append(f"[skipped: {e}]")
                skipped_err += 1
                continue

            chunks.append(f"=== FILE: {rel} ===")
            chunks.append(content.rstrip("\n"))
            kept += 1

            if i % 50 == 0:
                print(f"    ... {i}/{total}", file=sys.stderr)

        print(
            f"[*] content: kept={kept} "
            f"skipped_bin={skipped_bin} skipped_big={skipped_big} err={skipped_err}",
            file=sys.stderr,
        )

    chunks.append("=== END ===")

    body = "\n".join(chunks) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")

    size_bytes = len(body.encode("utf-8"))
    print(
        f"[✓] wrote {out_path}  "
        f"({len(body):,} chars, {size_bytes:,} bytes, {now_str()})",
        file=sys.stderr,
    )
    return 0


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Dump entire codebase to a single text file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "예시:\n"
            "  python scripts/dump_codebase.py\n"
            "  python scripts/dump_codebase.py --preset frontend -o frontend_dump.txt\n"
            "  python scripts/dump_codebase.py --preset backend --no-tree -o api.txt\n"
            "  python scripts/dump_codebase.py --include 'app/**' 'tests/**'\n"
            "  python scripts/dump_codebase.py --exclude 'tests/**' --max-file-size 200000\n"
        ),
    )
    p.add_argument("root", nargs="?", default=".",
                   help="root directory (default: current dir)")
    p.add_argument("-o", "--output", default="saju_dump.txt",
                   help="output file path (default: saju_dump.txt)")
    p.add_argument("--preset", choices=sorted(PRESETS.keys()), default=None,
                   help="프로젝트 preset (all / frontend / tma / backend / minimal)")
    p.add_argument("--include", nargs="*", default=[],
                   help="glob whitelist (rel path). 지정 시 이 패턴에 매칭되는 파일만 포함")
    p.add_argument("--exclude", nargs="*", default=[],
                   help="glob blacklist (rel path)")
    p.add_argument("--max-file-size", type=int, default=500_000,
                   help="개별 파일 최대 크기 (bytes, default 500KB)")
    p.add_argument("--no-tree", action="store_true",
                   help="트리 섹션 생략")
    p.add_argument("--no-content", action="store_true",
                   help="파일 내용 생략 (트리만)")
    p.add_argument("--no-git", dest="use_git", action="store_false",
                   help="git ls-files 사용 안 함 (os.walk 강제)")
    p.set_defaults(use_git=True)

    args = p.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
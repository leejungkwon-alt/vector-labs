#!/usr/bin/env python3
"""
dump_all_code.py — Dump entire repo (backend + frontend) as a single text blob.

Default output: saju_complete_code.txt (project root)

Output format (matches project convention):
    === TREE ===
    <file list>

    === FILE: <path> ===
    <content>

Handles:
- Keeps frontend/ explicitly; sanity check at end warns if missing
- Skips only noise: node_modules, .git, __pycache__, .expo, .next,
  build artifacts, iOS Pods, Android .gradle, dist, coverage
- Skips root-level data/ (SQLite) but KEEPS app/services/content/data/ (JSON packs)
- Skips .env / .env.local / .env.production etc. (secrets), keeps .env.example
- Skips lock files (package-lock.json, yarn.lock, pnpm-lock.yaml, poetry.lock)
- Skips binary files (images, fonts, DB) via content sniffing
- Skips files > --max-file-size (default 2MB)
- Decodes UTF-8 with errors='replace' fallback

Usage:
    python scripts/dump_all_code.py                        # → saju_complete_code.txt
    python scripts/dump_all_code.py --out custom.txt        # → custom.txt
    python scripts/dump_all_code.py --stdout                # → stdout (pipe)
    python scripts/dump_all_code.py -v                      # verbose logs
    python scripts/dump_all_code.py --extra-exclude "frontend/legacy,firmware"
    python scripts/dump_all_code.py --max-file-size 5000000
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

DEFAULT_OUTPUT_FILENAME = "saju_complete_code.txt"

# --- directory names to prune anywhere in the tree ---
STD_EXCLUDED_DIR_NAMES = {
    # VCS
    ".git", ".github", ".gitlab",
    # Python
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox", ".venv", "venv", "env",
    # JS/Node/build
    "node_modules",
    ".next", ".nuxt", ".svelte-kit", ".turbo", ".parcel-cache",
    "dist", "build", "coverage", ".nyc_output",
    # Expo / RN
    ".expo", ".expo-shared",
    # Native
    "Pods", ".gradle", ".cxx",
    # IDE
    ".idea", ".vscode",
}

STD_EXCLUDED_DIR_PATTERNS = (
    ".egg-info",
    ".dist-info",
)

# --- specific file names to skip (secrets, locks) ---
STD_EXCLUDED_FILE_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "poetry.lock",
    "Pipfile.lock",
    "tsconfig.tsbuildinfo",
    "Thumbs.db",
    ".DS_Store",
    # avoid dumping our own previous output recursively
    DEFAULT_OUTPUT_FILENAME,
}

# --- file extensions to skip (binary-ish, never useful as text) ---
STD_EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".dll", ".exe",
    ".log",
    ".db", ".sqlite", ".sqlite3",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".svgz",
    ".mp4", ".mov", ".webm", ".mp3", ".wav", ".flac",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".pdf",
    ".map",
}

DEFAULT_MAX_FILE_SIZE = 2_000_000  # 2 MB


def _is_env_secret(name: str) -> bool:
    """`.env`, `.env.local`, `.env.production` … but NOT `.env.example`."""
    if not name.startswith(".env"):
        return False
    return name not in (".env.example", ".env.sample", ".env.template")


def _dir_should_prune(dir_path: Path, root: Path) -> bool:
    """Return True to prune this dir entirely."""
    name = dir_path.name
    try:
        rel = dir_path.relative_to(root)
    except ValueError:
        return True

    # Root-level data/ (SQLite DB path) — but KEEP nested content/data/*
    if rel == Path("data"):
        return True

    if name in STD_EXCLUDED_DIR_NAMES:
        return True

    for pat in STD_EXCLUDED_DIR_PATTERNS:
        if name.endswith(pat):
            return True

    # Any path segment equals Pods/.gradle/.cxx (belt + braces)
    if any(part in ("Pods", ".gradle", ".cxx") for part in rel.parts):
        return True

    return False


def _file_should_skip(path: Path) -> bool:
    name = path.name
    if name in STD_EXCLUDED_FILE_NAMES:
        return True
    if _is_env_secret(name):
        return True
    if path.suffix.lower() in STD_EXCLUDED_EXTENSIONS:
        return True
    return False


def _is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
    except Exception:
        return True
    if not chunk:
        return False
    if b"\x00" in chunk:
        return True
    non_text = sum(1 for b in chunk if b < 9 or (13 < b < 32))
    return (non_text / len(chunk)) > 0.30


def _read_file(path: Path, max_size: int) -> tuple[str, str | None]:
    try:
        size = path.stat().st_size
    except Exception as e:
        return "", f"stat error: {e}"
    if size > max_size:
        return "", f"skipped (too large: {size:,} > {max_size:,} bytes)"
    if _is_binary(path):
        return "", f"skipped (binary, {size:,} bytes)"
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace"), None
        except Exception as e:
            return "", f"decode error: {e}"
    except Exception as e:
        return "", f"read error: {e}"


def _collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dp = Path(dirpath)
        # Prune in-place — critical: this must NOT eat frontend/
        dirnames[:] = sorted(
            d for d in dirnames
            if not _dir_should_prune(dp / d, root)
        )
        for fn in sorted(filenames):
            fp = dp / fn
            if _file_should_skip(fp):
                continue
            files.append(fp.relative_to(root))
    files.sort(key=lambda p: str(p).replace("\\", "/"))
    return files


def _sanity_check(files: list[Path], root: Path, verbose: bool) -> int:
    """Return 1 if suspicious, else 0. Prints warnings to stderr."""
    names = [str(p).replace("\\", "/") for p in files]
    joined = "\n".join(names)
    problems = 0

    if "frontend/" not in joined:
        print("WARNING: 'frontend/' directory NOT present in output.",
              file=sys.stderr)
        print(f"         root = {root}", file=sys.stderr)
        print("         Check --root, .gitignore, and exclusion rules.",
              file=sys.stderr)
        problems += 1

    if "app/services/content/data/" not in joined:
        print("WARNING: 'app/services/content/data/' (JSON content packs) "
              "NOT present in output.", file=sys.stderr)
        problems += 1

    frontend_markers = ("package.json", "tsconfig.json", "app.json",
                        "App.tsx", "app/_layout.tsx")
    if "frontend/" in joined:
        found = [m for m in frontend_markers if f"frontend/{m}" in joined]
        if verbose:
            print(f"[frontend markers] found: {found or 'none'}", file=sys.stderr)

    return 1 if problems else 0


def _print_summary(files: list[Path], skipped: list[tuple[str, str]],
                   total_bytes: int, verbose: bool) -> None:
    print(f"\n[summary] files included: {len(files):,}", file=sys.stderr)
    print(f"[summary] total content:  {total_bytes:,} bytes "
          f"({total_bytes / 1024 / 1024:.2f} MB)", file=sys.stderr)
    print(f"[summary] files skipped:  {len(skipped):,}", file=sys.stderr)
    if verbose and skipped:
        print("[summary] skipped detail:", file=sys.stderr)
        for name, reason in skipped[:50]:
            print(f"  - {name}: {reason}", file=sys.stderr)
        if len(skipped) > 50:
            print(f"  ... and {len(skipped) - 50} more", file=sys.stderr)

    # Top-level directory histogram
    hist: dict[str, int] = {}
    for p in files:
        top = p.parts[0] if len(p.parts) > 1 else "(root)"
        hist[top] = hist.get(top, 0) + 1
    print("[summary] top-level:", file=sys.stderr)
    for top, n in sorted(hist.items(), key=lambda x: -x[1])[:10]:
        print(f"  {top}/  → {n} files", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Dump entire repo (backend + frontend) as a single text blob.",
    )
    ap.add_argument("--root", default=".",
                    help="Project root (default: current dir)")
    ap.add_argument("--out", default=DEFAULT_OUTPUT_FILENAME,
                    help=f"Output file path "
                         f"(default: ./{DEFAULT_OUTPUT_FILENAME})")
    ap.add_argument("--stdout", action="store_true",
                    help="Print to stdout instead of writing a file "
                         "(overrides --out)")
    ap.add_argument("--max-file-size", type=int, default=DEFAULT_MAX_FILE_SIZE,
                    help=f"Max bytes per file (default: {DEFAULT_MAX_FILE_SIZE:,})")
    ap.add_argument("--extra-exclude", default="",
                    help="Comma-separated additional path substrings to exclude")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="Verbose logs to stderr (does not pollute stdout)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 2

    extras = [x.strip() for x in args.extra_exclude.split(",") if x.strip()]

    if args.verbose:
        print(f"[info] root = {root}", file=sys.stderr)
        print(f"[info] max_file_size = {args.max_file_size:,} bytes",
              file=sys.stderr)
        print(f"[info] output mode = "
              f"{'stdout' if args.stdout else args.out}", file=sys.stderr)
        if extras:
            print(f"[info] extra excludes = {extras}", file=sys.stderr)

    files = _collect_files(root)
    if extras:
        files = [
            p for p in files
            if not any(ex in str(p).replace("\\", "/") for ex in extras)
        ]

    # Read + serialize
    out_lines: list[str] = []
    skipped: list[tuple[str, str]] = []
    total_bytes = 0

    out_lines.append("=== TREE ===")
    for p in files:
        out_lines.append(str(p).replace("\\", "/"))
    out_lines.append("")

    for p in files:
        fp = root / p
        content, err = _read_file(fp, args.max_file_size)
        rel = str(p).replace("\\", "/")

        out_lines.append(f"=== FILE: {rel} ===")
        if err:
            out_lines.append(f"# [{err}]")
            skipped.append((rel, err))
        else:
            total_bytes += len(content.encode("utf-8"))
            out_lines.append(content.rstrip("\n"))
        out_lines.append("")

    text = "\n".join(out_lines)

    # Sanity check (warn, don't fail)
    _sanity_check(files, root, args.verbose)

    # Write or print
    if args.stdout:
        sys.stdout.write(text)
    else:
        # If --out is relative, anchor it at the project root
        out_arg = Path(args.out)
        out_path = out_arg if out_arg.is_absolute() else (root / out_arg)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"\n[out] wrote {out_path} "
              f"({len(files):,} files, "
              f"{len(text.encode('utf-8')):,} bytes)", file=sys.stderr)

    _print_summary(files, skipped, total_bytes, args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
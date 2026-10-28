"""
dump_all_code.py
SAJU 프로젝트의 소스 코드를 단일 텍스트 파일(saju_complete_code.txt)로 덤프합니다.

사용법:
    python dump_all_code.py

특징:
    - .gitignore와 무관하게 명시적 화이트리스트 확장자만 포함
    - .env 계열(API 키) 및 바이너리/대용량 파일은 절대 포함하지 않음
    - 파일 크기/개수/총 바이트 요약을 헤더/푸터에 기록
"""
import os
from pathlib import Path
from datetime import datetime

OUTPUT_FILE = "saju_complete_code.txt"
ROOT = Path(__file__).resolve().parent
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB per file

# 제외 디렉토리 (정확히 일치 또는 '.'으로 시작)
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build",
    ".idea", ".vscode", ".next", ".cache", "coverage", "htmlcov",
    ".tox", "site-packages", "logs", "tmp", "temp", "backups",
}

# 제외 파일 (보안/용량)
EXCLUDE_FILES = {
    "saju_complete_code.txt",
    "dump_all_code.py",
    ".DS_Store", "Thumbs.db",
    # ★ API 키 보호: .env 계열 절대 덤프 금지
    ".env", ".env.local", ".env.development", ".env.production",
    ".env.test", ".env.staging", ".env.example",
    # 락 파일
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
}

# 제외 확장자 (바이너리/미디어)
EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".mp3", ".mp4", ".wav", ".ogg", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".lock", ".log", ".db", ".sqlite", ".sqlite3",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".map",
}

# 포함 확장자 (화이트리스트)
INCLUDE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".md", ".rst", ".txt",
    ".sh", ".bat", ".ps1",
    ".sql",
}

# 확장자 없이 포함할 특수 파일
INCLUDE_NAMES = {
    "Dockerfile", "Makefile", "Procfile", "LICENSE", "README",
    ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
}


def should_skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS or name.startswith(".")


def should_include(p: Path) -> bool:
    if p.name in EXCLUDE_FILES:
        return False
    if p.name in INCLUDE_NAMES:
        return True
    ext = p.suffix.lower()
    if ext in EXCLUDE_EXTS:
        return False
    return ext in INCLUDE_EXTS


def main() -> None:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]
        for fn in filenames:
            p = Path(dirpath) / fn
            if should_include(p):
                files.append(p)

    files.sort(key=lambda x: str(x.relative_to(ROOT)).lower())

    total_files = 0
    total_bytes = 0
    skipped: list[tuple[str, str]] = []

    with open(OUTPUT_FILE, "w", encoding="utf-8", errors="replace") as out:
        out.write("=" * 80 + "\n")
        out.write("SAJU PROJECT — COMPLETE CODE DUMP\n")
        out.write(f"Generated : {datetime.now().isoformat(timespec='seconds')}\n")
        out.write(f"Root      : {ROOT}\n")
        out.write(f"Candidates: {len(files)}\n")
        out.write("=" * 80 + "\n\n")

        for p in files:
            rel = p.relative_to(ROOT)
            try:
                size = p.stat().st_size
            except OSError as e:
                skipped.append((str(rel), f"stat failed: {e}"))
                continue

            if size > MAX_FILE_SIZE:
                skipped.append((str(rel), f"too large: {size:,} bytes"))
                continue

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                skipped.append((str(rel), f"read failed: {e}"))
                continue

            total_files += 1
            total_bytes += len(content.encode("utf-8", errors="replace"))

            out.write("\n" + "=" * 80 + "\n")
            out.write(f"FILE: {rel}\n")
            out.write("=" * 80 + "\n")
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")

        if skipped:
            out.write("\n" + "=" * 80 + "\n")
            out.write("SKIPPED FILES\n")
            out.write("=" * 80 + "\n")
            for rel, reason in skipped:
                out.write(f"  - {rel}  ({reason})\n")

        out.write("\n" + "=" * 80 + "\n")
        out.write(f"END OF DUMP — {total_files} files, ~{total_bytes:,} bytes\n")
        out.write("=" * 80 + "\n")

    print(f"[OK] Dump written: {OUTPUT_FILE}")
    print(f"     Files      : {total_files}")
    print(f"     Size       : ~{total_bytes:,} bytes")
    if skipped:
        print(f"     Skipped    : {len(skipped)}")


if __name__ == "__main__":
    main()p
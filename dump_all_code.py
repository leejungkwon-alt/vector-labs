"""
dump_all_code.py
SAJU 프로젝트의 소스 코드를 단일 텍스트 파일(saju_complete_code.txt)로 덤프합니다.

사용법:
    python dump_all_code.py           # 덤프 생성
    python dump_all_code.py --list    # 파일 쓰지 않고 포함/제외 목록만 확인 (dry-run)

특징:
    - 명시적 화이트리스트 확장자만 포함
    - .env 계열 / 키·인증서·서비스계정 파일은 이름 패턴으로 제외
    - 본문에 하드코딩된 API 키는 정규식으로 찾아 ***REDACTED*** 처리
    - 파일당 / 전체 용량 상한, 바이너리(NUL 포함) 및 심볼릭 링크 제외
    - 출력 파일은 스크립트 위치(ROOT) 기준으로 항상 같은 곳에 생성
"""
import fnmatch
import os
import re
import sys
from datetime import datetime
from pathlib import Path

OUTPUT_FILE = "saju_complete_code.txt"
ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / OUTPUT_FILE

MAX_FILE_SIZE = 300 * 1024          # 파일당 300 KB
MAX_TOTAL_BYTES = 6 * 1024 * 1024   # 전체 6 MB (초과분은 SKIPPED 기록)

# 제외 디렉토리 (정확히 일치 또는 '.'으로 시작)
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build",
    ".idea", ".vscode", ".next", ".cache", "coverage", "htmlcov",
    ".tox", "site-packages", "logs", "tmp", "temp", "backups",
}

# 제외 파일 (정확히 일치)
EXCLUDE_FILES = {
    OUTPUT_FILE,
    Path(__file__).name,
    ".DS_Store", "Thumbs.db",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
}

# 제외 파일명 패턴 (소문자 fnmatch) — 시크릿/키/인증서 계열
EXCLUDE_GLOBS = [
    "*secret*", "*credential*", "*serviceaccount*", "*service-account*",
    "*service_account*", "firebase-adminsdk*", "google-services.json",
    "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore",
    "id_rsa*", "id_ed25519*", ".npmrc", ".pypirc", ".netrc",
    # 생성 산출물(리포트 데이터) — 필요하면 이 줄을 지우세요
    "report_*.json",
]

# 제외 확장자 (바이너리/미디어/백업)
EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp", ".svg",
    ".mp3", ".mp4", ".wav", ".ogg", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".lock", ".log", ".db", ".sqlite", ".sqlite3",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".map", ".bak",
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

# 본문 내 시크릿 마스킹 규칙
REDACT = "***REDACTED***"
SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),                 # Anthropic
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{32,}"),           # OpenAI 계열
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),                     # Google API key
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),                 # GitHub token
    re.compile(r"github_pat_[A-Za-z0-9_]{50,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),                           # AWS access key id
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),              # Slack
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
]
# KEY = "값" 형태의 일반 할당 (값 부분만 치환)
ASSIGN_PATTERN = re.compile(
    r"""(?ix)
    ((?:api[_-]?key|secret(?:[_-]?key)?|access[_-]?token|auth[_-]?token|token|passwd|password)
     ["']?\s*[:=]\s*["'])
    ([^"'\s]{8,})
    (["'])
    """
)


def is_env_file(name: str) -> bool:
    n = name.lower()
    return n.startswith(".env") or n.endswith(".env") or ".env." in n or n == ".envrc"


def should_skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS or name.startswith(".")


def exclusion_reason(p: Path) -> str | None:
    """포함 대상이면 None, 아니면 제외 사유."""
    name = p.name
    if name in EXCLUDE_FILES:
        return "excluded file"
    if is_env_file(name):
        return "env file"
    lower = name.lower()
    if any(fnmatch.fnmatch(lower, g) for g in EXCLUDE_GLOBS):
        return "excluded pattern"
    if name in INCLUDE_NAMES:
        return None
    ext = p.suffix.lower()
    if ext in EXCLUDE_EXTS or ext not in INCLUDE_EXTS:
        return "extension"
    return None


def redact_secrets(text: str) -> tuple[str, int]:
    count = 0
    for pat in SECRET_PATTERNS:
        text, n = pat.subn(REDACT, text)
        count += n
    text, n = ASSIGN_PATTERN.subn(lambda m: f"{m.group(1)}{REDACT}{m.group(3)}", text)
    count += n
    return text, count


def collect_files() -> tuple[list[Path], list[tuple[str, str]]]:
    files: list[Path] = []
    skipped: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):  # followlinks=False
        kept = []
        for d in dirnames:
            if should_skip_dir(d):
                continue
            kept.append(d)
        dirnames[:] = kept
        for fn in filenames:
            p = Path(dirpath) / fn
            reason = exclusion_reason(p)
            if reason is None:
                if p.is_symlink():
                    skipped.append((str(p.relative_to(ROOT)), "symlink"))
                else:
                    files.append(p)
            elif reason in ("env file", "excluded pattern"):
                # 조용히 빠지면 헷갈리므로 보안/패턴 제외는 기록
                skipped.append((str(p.relative_to(ROOT)), reason))
    files.sort(key=lambda x: str(x.relative_to(ROOT)).lower())
    return files, skipped


def main() -> None:
    dry_run = "--list" in sys.argv
    files, skipped = collect_files()

    included: list[tuple[Path, str]] = []  # (path, content)
    total_bytes = 0
    total_redactions = 0
    redacted_files: list[tuple[str, int]] = []

    for p in files:
        rel = str(p.relative_to(ROOT))
        try:
            size = p.stat().st_size
        except OSError as e:
            skipped.append((rel, f"stat failed: {e}"))
            continue

        if size > MAX_FILE_SIZE:
            skipped.append((rel, f"too large: {size:,} bytes"))
            continue

        try:
            raw = p.read_bytes()
        except Exception as e:
            skipped.append((rel, f"read failed: {e}"))
            continue

        if b"\x00" in raw:
            skipped.append((rel, "binary (NUL byte)"))
            continue

        content = raw.decode("utf-8", errors="replace")
        content, n = redact_secrets(content)
        if n:
            total_redactions += n
            redacted_files.append((rel, n))

        encoded_len = len(content.encode("utf-8", errors="replace"))
        if total_bytes + encoded_len > MAX_TOTAL_BYTES:
            skipped.append((rel, f"total limit reached ({MAX_TOTAL_BYTES:,} bytes)"))
            continue

        total_bytes += encoded_len
        included.append((p, content))

    # ---- 목록 출력 (검증용) ----
    print(f"[INFO] Root: {ROOT}")
    print(f"[INFO] Included files ({len(included)}):")
    for p, content in included:
        print(f"   {len(content.encode('utf-8', errors='replace')):>9,}  {p.relative_to(ROOT)}")

    if dry_run:
        print(f"\n[DRY-RUN] 파일은 쓰지 않았습니다. 예상 크기 ~{total_bytes:,} bytes")
        if skipped:
            print(f"[DRY-RUN] Skipped {len(skipped)}:")
            for rel, reason in skipped:
                print(f"   - {rel}  ({reason})")
        if redacted_files:
            print("[DRY-RUN] Redacted:")
            for rel, n in redacted_files:
                print(f"   - {rel}: {n}")
        return

    with open(OUT_PATH, "w", encoding="utf-8", errors="replace") as out:
        out.write("=" * 80 + "\n")
        out.write("SAJU PROJECT — COMPLETE CODE DUMP\n")
        out.write(f"Generated : {datetime.now().isoformat(timespec='seconds')}\n")
        out.write(f"Root      : {ROOT}\n")
        out.write(f"Files     : {len(included)}\n")
        out.write("=" * 80 + "\n\n")

        out.write("FILE LIST\n")
        for p, _ in included:
            out.write(f"  - {p.relative_to(ROOT)}\n")

        for p, content in included:
            rel = p.relative_to(ROOT)
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

        if redacted_files:
            out.write("\n" + "=" * 80 + "\n")
            out.write("REDACTED SECRETS\n")
            out.write("=" * 80 + "\n")
            for rel, n in redacted_files:
                out.write(f"  - {rel}: {n}\n")

        out.write("\n" + "=" * 80 + "\n")
        out.write(f"END OF DUMP — {len(included)} files, ~{total_bytes:,} bytes\n")
        out.write("=" * 80 + "\n")

    print(f"\n[OK] Dump written: {OUT_PATH}")
    print(f"     Files      : {len(included)}")
    print(f"     Size       : ~{total_bytes:,} bytes")
    if skipped:
        print(f"     Skipped    : {len(skipped)}")
    if total_redactions:
        print(f"     Redacted   : {total_redactions} secret(s) in {len(redacted_files)} file(s)")
        print("     ※ 덤프를 외부에 공유하기 전에 REDACTED SECRETS 섹션을 확인하세요.")


if __name__ == "__main__":
    main()
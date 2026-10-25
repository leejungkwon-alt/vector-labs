"""
하드코딩 다국어 문자열 / 언어 분기 스캐너
- app/ 하위 .py 전체 스캔
- app/services/content/{ko,en}/ 은 콘텐츠 팩이라 기본 제외
- 결과를 UTF-8 텍스트 파일로 저장 (터미널 잘림 없음)

분류(kind):
  HARDCODED_KO        → 유저에게 노출되는 하드코딩 한글 문자열  ★ 리팩터링 대상
  HARDCODED_KO_FSTRING→ f-string 안에 박힌 한글                 ★ 리팩터링 대상
  LANG_BRANCH         → if lang == "ko"/"en" 같은 언어 분기     ★ 리팩터링 대상
  LANG_IN             → lang in [...] 같은 분기                 ★ 리팩터링 대상
  DOCSTRING_KO        → 모듈/함수/클래스 docstring (개발자용, 무시 가능)
  COMMENT_KO          → # 주석 안의 한글 (개발자용, 무시 가능)
"""
import re
import ast
import io
import tokenize
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"C:\Users\lenovo\Desktop\SAJU")
SCAN_BASE = ROOT / "app"
OUTPUT = ROOT / "hardcoded_scan_full.txt"

KOREAN_RE = re.compile(r'[\uac00-\ud7a3]')
LANG_EQ_PAT = re.compile(
    r'\b\w*(?:lang|language|locale)\w*\s*(?:==|!=)\s*[\'"](?:ko|en|kr|ja|zh)[\'"]',
    re.IGNORECASE,
)
LANG_IN_PAT = re.compile(
    r'\b\w*(?:lang|language|locale)\w*\s+(?:in|not\s+in)\s+[\[\(\{]',
    re.IGNORECASE,
)

# 콘텐츠 팩(정상 JSON-등가 데이터)은 스킵
SKIP_DIRS = (
    ROOT / "app" / "services" / "content" / "ko",
    ROOT / "app" / "services" / "content" / "en",
)

def should_skip(path: Path) -> bool:
    for skip in SKIP_DIRS:
        try:
            path.relative_to(skip)
            return True
        except ValueError:
            continue
    return False

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def collect_docstring_lines(tree: ast.AST) -> set:
    lines = set()
    def mark(node):
        body = getattr(node, "body", None)
        if body and isinstance(body[0], ast.Expr):
            v = body[0].value
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                start = getattr(v, "lineno", None)
                end = getattr(v, "end_lineno", start)
                if start:
                    lines.update(range(start, (end or start) + 1))
    mark(tree)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            mark(n)
    return lines

def collect_comment_lines(src: str) -> set:
    lines = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT and KOREAN_RE.search(tok.string):
                lines.add(tok.start[0])
    except Exception:
        pass
    return lines

def scan(path: Path):
    findings = []  # (kind, line, text)
    try:
        src = path.read_text(encoding="utf-8")
    except Exception as e:
        return [("READ_ERROR", -1, str(e))]
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [("SYNTAX_ERROR", e.lineno or -1, str(e))]

    doc_lines = collect_docstring_lines(tree)
    comment_lines = collect_comment_lines(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if not KOREAN_RE.search(val):
                continue
            ln = getattr(node, "lineno", -1)
            if ln in doc_lines:
                findings.append(("DOCSTRING_KO", ln, val.split("\n")[0][:120]))
            else:
                preview = val.replace("\n", "\\n")
                if len(preview) > 300:
                    preview = preview[:300] + "...(trunc)"
                findings.append(("HARDCODED_KO", ln, preview))
        elif isinstance(node, ast.JoinedStr):
            try:
                s = ast.unparse(node)
            except Exception:
                s = ""
            if KOREAN_RE.search(s):
                ln = getattr(node, "lineno", -1)
                if len(s) > 300:
                    s = s[:300] + "...(trunc)"
                findings.append(("HARDCODED_KO_FSTRING", ln, s))

    for i, line in enumerate(src.splitlines(), 1):
        if LANG_EQ_PAT.search(line):
            findings.append(("LANG_BRANCH", i, line.strip()))
        elif LANG_IN_PAT.search(line):
            findings.append(("LANG_IN", i, line.strip()))

    for ln in sorted(comment_lines):
        if ln not in doc_lines:
            src_lines = src.splitlines()
            line_text = src_lines[ln - 1] if ln - 1 < len(src_lines) else ""
            findings.append(("COMMENT_KO", ln, line_text.strip()[:200]))

    return findings

def main():
    if not SCAN_BASE.exists():
        print(f"[!] not found: {SCAN_BASE}")
        return

    all_findings = defaultdict(list)
    scanned = 0
    for path in sorted(SCAN_BASE.rglob("*.py")):
        if should_skip(path):
            continue
        scanned += 1
        f = scan(path)
        if f:
            all_findings[rel(path)] = f

    total = sum(len(v) for v in all_findings.values())
    kind_count = defaultdict(int)
    for v in all_findings.values():
        for k, _, _ in v:
            kind_count[k] += 1

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("# Hardcoded-string / lang-branch scan\n")
        f.write(f"# Root    : {ROOT}\n")
        f.write(f"# Scanned : {scanned} .py files (content packs skipped)\n")
        f.write(f"# Findings: {total}\n\n")
        f.write("## By kind\n")
        for k, c in sorted(kind_count.items(), key=lambda x: -x[1]):
            f.write(f"  {k:24s} {c}\n")
        f.write("\n## Top files\n")
        for r, fs in sorted(all_findings.items(), key=lambda x: -len(x[1]))[:40]:
            f.write(f"  {len(fs):4d}  {r}\n")
        f.write("\n\n## Full findings\n")
        for r in sorted(all_findings):
            fs = all_findings[r]
            f.write("\n" + "=" * 90 + "\n")
            f.write(f"FILE: {r}   ({len(fs)})\n")
            f.write("=" * 90 + "\n")
            for kind, ln, text in sorted(fs, key=lambda x: (x[1], x[0])):
                f.write(f"[{kind}] L{ln}\n    {text}\n")

    print(f"[OK] report -> {OUTPUT}")
    print(f"     scanned {scanned} files, {total} findings in {len(all_findings)} files")
    print("     by kind:")
    for k, c in sorted(kind_count.items(), key=lambda x: -x[1]):
        print(f"       {k:24s} {c}")
    print()
    print("Top 15 files:")
    for r, fs in sorted(all_findings.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  {len(fs):4d}  {r}")
    print()
    print(f"전체 내용은 이 파일에서 확인: {OUTPUT}")

if __name__ == "__main__":
    main()
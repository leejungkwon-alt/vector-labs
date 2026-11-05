"""1-F-fix: add raise_for_status() to FakeResp mock classes in OIDC tests."""
from pathlib import Path
import re
import sys

TEST_FILE = Path("tests/test_oidc_verification.py")

# Match `class FakeResp:` then (possibly blank lines) then `<indent>status_code = 200`
PATTERN = re.compile(
    r"class FakeResp:[^\n]*\n"
    r"(?:[ \t]*\n)*"
    r"(?P<indent>[ \t]+)status_code = 200\n",
)


def repl(m: re.Match) -> str:
    indent = m.group("indent")
    return (
        m.group(0)
        + f"{indent}def raise_for_status(self):\n"
        + f"{indent}    return None\n"
    )


def main() -> int:
    if not TEST_FILE.is_file():
        print(f"[fail] not found: {TEST_FILE}", file=sys.stderr)
        return 1
    src = TEST_FILE.read_text(encoding="utf-8")
    if "def raise_for_status" in src:
        print("[skip] already patched")
        return 0
    new_src, n = PATTERN.subn(repl, src)
    if n == 0:
        print("[fail] no 'class FakeResp: ... status_code = 200' block found", file=sys.stderr)
        for i, line in enumerate(src.splitlines(), 1):
            if "FakeResp" in line or "status_code" in line:
                print(f"  L{i}: {line!r}", file=sys.stderr)
        return 1
    TEST_FILE.write_text(new_src, encoding="utf-8")
    print(f"[ok] patched {n} FakeResp class(es) in {TEST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
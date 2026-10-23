#!/usr/bin/env python3
"""generate_full_report()에 today 파라미터 추가 (report.py의 호출과 일치시킴)."""
import ast, re, shutil, sys
from datetime import datetime
from pathlib import Path

TARGET = Path("app/services/content_writer.py")

def die(msg: str, code: int = 1) -> None:
    print(msg); sys.exit(code)

if not TARGET.exists():
    die(f"❌ {TARGET} 없음")

src = TARGET.read_text(encoding="utf-8")

# def generate_full_report(...) : 캡처 (괄호 중첩 허용)
pat = re.compile(
    r"(def\s+generate_full_report\s*\()([^()]*?)(\)\s*(?:->\s*[^:\n]+)?\s*:)",
    re.DOTALL,
)
m = pat.search(src)
if not m:
    die("❌ def generate_full_report() 시그니처를 찾지 못함. 수동 확인 필요.")

params = m.group(2).strip()

# 파라미터 이름만 추출 (기본값·타입힌트 제거)
names: set[str] = set()
for chunk in params.split(","):
    head = chunk.split("=")[0].split(":")[0].strip()
    if head.startswith("**"):
        print(f"ℹ️ 이미 **{head[2:]} 로 kwarg 수용 중 → 수정 불필요"); sys.exit(0)
    if head.startswith("*"):
        continue
    if head:
        names.add(head)

if "today" in names:
    print("✅ 'today' 이미 존재 — 수정 불필요"); sys.exit(0)

new_params = (params + ", today=None") if params else "today=None"
new_src = src[:m.start(2)] + new_params + src[m.end(2):]

# 사전 검증
try:
    ast.parse(new_src)
except SyntaxError as e:
    die(f"❌ 생성 코드 문법 오류 → 저장 중단: {e.msg} (line {e.lineno})")

bak = TARGET.with_suffix(TARGET.suffix + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
shutil.copy2(TARGET, bak)
TARGET.write_text(new_src, encoding="utf-8")
print(f"✅ generate_full_report({new_params}) 로 수정")
print(f"📦 백업: {bak.name}")
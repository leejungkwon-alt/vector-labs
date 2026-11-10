# scripts/fix_logout_v2.py
"""
signOut 함수를 라인 기반으로 찾아서 익명 세션 재생성 추가.
- 들여쓰기/줄바꿈 무관
- ast 검증 (TS지만 괄호 균형만 체크)
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/authStore.ts")

if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

txt = STORE.read_text(encoding="utf-8")
lines = txt.splitlines(keepends=True)

# ─── signOut 함수 찾기 ───
start_idx = None
for i, line in enumerate(lines):
    if "signOut:" in line and ("async" in line or "() =>" in line):
        start_idx = i
        break

if start_idx is None:
    print("❌ signOut 함수를 찾지 못했습니다.")
    for i, line in enumerate(lines):
        if "signOut" in line:
            print(f"  L{i+1}: {repr(line)}")
    sys.exit(1)

print(f"✅ signOut 발견: L{start_idx + 1}")

# ─── 함수 끝 찾기 (중괄호 카운팅) ───
depth = 0
end_idx = None
started = False
for i in range(start_idx, len(lines)):
    line = lines[i]
    for ch in line:
        if ch == "{":
            depth += 1
            started = True
        elif ch == "}":
            depth -= 1
    if started and depth == 0:
        # `},` 또는 `}`로 끝나는 라인 다음이 함수 끝
        end_idx = i
        break

if end_idx is None:
    print("❌ 함수 끝을 찾지 못했습니다.")
    sys.exit(1)

print(f"✅ 함수 끝: L{end_idx + 1}")
print(f"\n[현재 함수]")
for i in range(start_idx, end_idx + 1):
    print(f"  {i+1:3d}: {lines[i].rstrip()}")

# ─── 들여쓰기 감지 ───
first_line = lines[start_idx]
base_indent = first_line[:len(first_line) - len(first_line.lstrip())]
body_indent = base_indent + "  "

print(f"\n✅ 들여쓰기: {len(base_indent)}칸")

# ─── 새 함수 본문 생성 ───
# 기존 함수 안의 마지막 `},` 위치 유지하면서 내부만 확장
new_body = [
    f"{base_indent}signOut: async () => {{\n",
    f"{body_indent}await storage.deleteItem(TOKEN_KEY);\n",
    f"{body_indent}setAuthToken(null);\n",
    f"{body_indent}set({{ user: null }});\n",
    f"{body_indent}// 🆕 로그아웃 후 새 익명 세션 자동 생성\n",
    f"{body_indent}try {{\n",
    f"{body_indent}  const res = await api.anonymous();\n",
    f"{body_indent}  await storage.setItem(TOKEN_KEY, res.access_token);\n",
    f"{body_indent}  setAuthToken(res.access_token);\n",
    f"{body_indent}  set({{ user: res.user, ready: true, authError: null }});\n",
    f"{body_indent}}} catch (e) {{\n",
    f"{body_indent}  console.warn('[signOut] anonymous re-issue failed:', e);\n",
    f"{body_indent}}}\n",
    f"{base_indent}}},\n",
]

# 이미 패치됐는지 확인
if "anonymous re-issue" in txt:
    print("\nℹ️ 이미 패치됨")
    sys.exit(0)

# ─── 교체 ───
new_lines = lines[:start_idx] + new_body + lines[end_idx + 1:]
new_txt = "".join(new_lines)

# 괄호 균형 검증
if new_txt.count("{") != new_txt.count("}"):
    print(f"\n❌ 중괄호 불균형: {{ {new_txt.count('{')} vs }} {new_txt.count('}')}")
    sys.exit(1)
if new_txt.count("(") != new_txt.count(")"):
    print(f"\n❌ 소괄호 불균형")
    sys.exit(1)

print("\n✅ 문법 검증 통과")

# 미리보기
print("\n[새 함수]")
for i in range(start_idx, start_idx + len(new_body)):
    print(f"  {i+1:3d}: {new_body[i - start_idx].rstrip()}")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_logout_v2.py --apply")
    sys.exit(0)

STORE.write_text(new_txt, encoding="utf-8")
print(f"\n🎉 저장 완료: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/authStore.ts"')
print('   git commit -m "fix(auth): auto-reissue anonymous session after signOut"')
print("   git push origin main")
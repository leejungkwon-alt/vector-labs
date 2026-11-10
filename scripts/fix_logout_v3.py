# scripts/fix_logout_v3.py
"""
signOut 구현부(interface 아님)만 정확히 찾아서 패치
- `signOut: async () => {` 패턴만 매칭 (인터페이스 `signOut: () => Promise<void>;` 제외)
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/authStore.ts")

txt = STORE.read_text(encoding="utf-8")
lines = txt.splitlines(keepends=True)

# 이미 패치됐는지 확인
if "anonymous re-issue" in txt:
    print("ℹ️ 이미 패치됨")
    sys.exit(0)

# ─── signOut 구현부 찾기 (async + { 필수) ───
start_idx = None
for i, line in enumerate(lines):
    stripped = line.strip()
    # interface 제외: `signOut: () => Promise<void>;` (세미콜론으로 끝남)
    if stripped.startswith("signOut:") and "async" in stripped and "{" in stripped:
        start_idx = i
        break

if start_idx is None:
    print("❌ signOut 구현부(async)를 찾지 못했습니다.")
    for i, line in enumerate(lines):
        if "signOut" in line:
            print(f"  L{i+1}: {line.rstrip()}")
    sys.exit(1)

print(f"✅ signOut 구현부 발견: L{start_idx + 1}")

# ─── 함수 끝 찾기 (중괄호 카운팅) ───
depth = 0
started = False
end_idx = None
for i in range(start_idx, len(lines)):
    for ch in lines[i]:
        if ch == "{":
            depth += 1
            started = True
        elif ch == "}":
            depth -= 1
    if started and depth == 0:
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

# ─── 새 본문 ───
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

# ─── 교체 ───
new_lines = lines[:start_idx] + new_body + lines[end_idx + 1:]
new_txt = "".join(new_lines)

# 괄호 균형 (전체 파일이 아닌 패치 후 diff로 판단 어려우니, 패치 전후 비교)
orig_open = txt.count("(") - txt.count(")")
new_open = new_txt.count("(") - new_txt.count(")")
if orig_open != new_open:
    print(f"\n❌ 소괄호 균형 변화: {orig_open} → {new_open}")
    sys.exit(1)

orig_curl = txt.count("{") - txt.count("}")
new_curl = new_txt.count("{") - new_txt.count("}")
if orig_curl != new_curl:
    print(f"\n❌ 중괄호 균형 변화: {orig_curl} → {new_curl}")
    sys.exit(1)

print("\n✅ 문법 검증 통과 (괄호 균형 변화 없음)")

# 미리보기
print("\n[새 함수]")
for i, line in enumerate(new_body):
    print(f"  {start_idx + i + 1:3d}: {line.rstrip()}")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_logout_v3.py --apply")
    sys.exit(0)

STORE.write_text(new_txt, encoding="utf-8")
print(f"\n🎉 저장 완료: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/authStore.ts"')
print('   git commit -m "fix(auth): auto-reissue anonymous session after signOut"')
print("   git push origin main")
# scripts/fix_profile_refresh.py
"""
1) signInWithProvider 후 loadProfile 호출
2) linkAccount 후 loadProfile 호출
3) signOut (익명 재생성) 후 loadProfile 호출
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

# ─── 1) import 확인 ───
if "useProfileStore" not in txt:
    # authStore 상단에 import 추가
    for i, line in enumerate(lines):
        if line.startswith("import"):
            continue
        # 첫 import 아래에 추가
        lines.insert(i, 'import { useProfileStore } from "./profileStore";\n')
        print("✅ useProfileStore import 추가")
        break

# ─── 2) signOut에 loadProfile 추가 ───
# signOut 함수 찾기
sidx = None
for i, line in enumerate(lines):
    if "signOut:" in line and "async" in line and "{" in line:
        sidx = i
        break

if sidx is not None:
    # 함수 끝 찾기
    depth = 0
    started = False
    eidx = None
    for i in range(sidx, len(lines)):
        for ch in lines[i]:
            if ch == "{": depth += 1; started = True
            elif ch == "}": depth -= 1
        if started and depth == 0:
            eidx = i
            break
    
    if eidx is not None:
        # 익명 세션 생성 후 loadProfile 호출 (이미 있으면 스킵)
        block = "".join(lines[sidx:eidx+1])
        if "loadProfile" not in block:
            # `set({ user: res.user, ready: true, authError: null });` 다음에 추가
            for i in range(sidx, eidx+1):
                if "set({ user: res.user, ready: true, authError: null })" in lines[i]:
                    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                    new_line = f"{indent}try {{ await useProfileStore.getState().loadProfile(); }} catch {{}}\n"
                    lines.insert(i + 1, new_line)
                    eidx += 1
                    print("✅ signOut 후 loadProfile 추가")
                    break

# ─── 3) signInWithProvider에 loadProfile 추가 ───
sidx = None
for i, line in enumerate(lines):
    if "signInWithProvider:" in line and "async" in line and "{" in line:
        sidx = i
        break

if sidx is not None:
    depth = 0
    started = False
    eidx = None
    for i in range(sidx, len(lines)):
        for ch in lines[i]:
            if ch == "{": depth += 1; started = True
            elif ch == "}": depth -= 1
        if started and depth == 0:
            eidx = i
            break
    
    if eidx is not None:
        block = "".join(lines[sidx:eidx+1])
        if "loadProfile" not in block:
            # `set({ user: res.user });` 다음에 추가
            for i in range(sidx, eidx+1):
                if "set({ user: res.user })" in lines[i]:
                    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                    new_line = f"{indent}try {{ await useProfileStore.getState().loadProfile(); }} catch {{}}\n"
                    lines.insert(i + 1, new_line)
                    eidx += 1
                    print("✅ signInWithProvider 후 loadProfile 추가")
                    break

# ─── 4) linkAccount에 loadProfile 추가 ───
sidx = None
for i, line in enumerate(lines):
    if "linkAccount:" in line and "async" in line and "{" in line:
        sidx = i
        break

if sidx is not None:
    depth = 0
    started = False
    eidx = None
    for i in range(sidx, len(lines)):
        for ch in lines[i]:
            if ch == "{": depth += 1; started = True
            elif ch == "}": depth -= 1
        if started and depth == 0:
            eidx = i
            break
    
    if eidx is not None:
        block = "".join(lines[sidx:eidx+1])
        if "loadProfile" not in block:
            for i in range(sidx, eidx+1):
                if "set({ user: res.user });" in lines[i]:
                    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                    new_line = f"{indent}try {{ await useProfileStore.getState().loadProfile(); }} catch {{}}\n"
                    lines.insert(i + 1, new_line)
                    eidx += 1
                    print("✅ linkAccount 후 loadProfile 추가")
                    break

new_txt = "".join(lines)

# 괄호 검증
if new_txt.count("{") != new_txt.count("}"):
    print(f"❌ 중괄호 불균형")
    sys.exit(1)

print("✅ 문법 검증 통과")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_profile_refresh.py --apply")
    sys.exit(0)

STORE.write_text(new_txt, encoding="utf-8")
print(f"\n🎉 저장 완료: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/authStore.ts"')
print('   git commit -m "fix(auth): refresh profile after login/logout"')
print("   git push origin main")
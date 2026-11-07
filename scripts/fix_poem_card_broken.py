# scripts/fix_poem_card_broken.py
"""
1) git checkout으로 깨진 파일 복구
2) 중괄호 카운팅 방식으로 getPoetName 함수 안전 제거
3) poet 렌더링 JSX 안전 제거
"""
import re
import subprocess
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/src/components/poem/PoemFlipCard.tsx")

# ═══════════════════════════════════════════════
# STEP 1: git checkout으로 복구
# ═══════════════════════════════════════════════
print("=" * 55)
print("STEP 1: git checkout으로 파일 복구")
print("=" * 55)

result = subprocess.run(
    ["git", "checkout", str(TSX)],
    capture_output=True, text=True,
)
if result.returncode == 0:
    print(f"  ✅ 복구 완료: {TSX}")
    if result.stderr.strip():
        print(f"  {result.stderr.strip()}")
else:
    print(f"  ❌ git checkout 실패: {result.stderr}")
    sys.exit(1)

# ═══════════════════════════════════════════════
# STEP 2: 안전하게 getPoetName 함수 제거 (중괄호 카운팅)
# ═══════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 2: getPoetName 함수 안전 제거")
print("=" * 55)

txt = TSX.read_text(encoding="utf-8")

def remove_function_safe(text: str, name: str) -> tuple[str, int]:
    """중괄호 카운팅으로 함수 전체(헤더 + 본문) 안전 제거."""
    removed = 0
    while True:
        # 함수 시작 위치 찾기 (여러 형태)
        patterns = [
            rf'(?:const|let|var)\s+{name}\s*=\s*\([^)]*\)\s*(?::\s*\w+)?\s*=>\s*\{{',
            rf'(?:const|let|var)\s+{name}\s*=\s*\([^)]*\)\s*(?::\s*\w+)?\s*=>',
            rf'function\s+{name}\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{{',
        ]
        
        found = False
        for pat in patterns:
            m = re.search(pat, text)
            if not m:
                continue
            start = m.start()
            
            # 화살표 함수인데 `{` 없으면 세미콜론까지
            if not m.group(0).rstrip().endswith("{"):
                # 한 줄 화살표 함수
                semi = text.find(";", m.end())
                if semi == -1:
                    semi = text.find("\n", m.end())
                if semi == -1:
                    break
                text = text[:start] + text[semi+1:]
                removed += 1
                found = True
                break
            
            # `{` 위치
            brace_start = m.end() - 1
            depth = 0
            end_pos = -1
            for i in range(brace_start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end_pos = i
                        break
            
            if end_pos == -1:
                break
            
            # `};` 또는 `}` + 선택적 세미콜론까지
            after = end_pos + 1
            while after < len(text) and text[after] in " \t":
                after += 1
            if after < len(text) and text[after] == ";":
                after += 1
            # 후행 개행 1개까지 포함
            if after < len(text) and text[after] == "\n":
                after += 1
            
            text = text[:start] + text[after:]
            removed += 1
            found = True
            break
        
        if not found:
            break
    
    return text, removed

txt, n = remove_function_safe(txt, "getPoetName")
print(f"  ✅ getPoetName 함수 {n}개 제거")

# ═══════════════════════════════════════════════
# STEP 3: poet 렌더링 JSX 제거 (중괄호 카운팅)
# ═══════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 3: poet 렌더링 JSX 제거")
print("=" * 55)

def remove_jsx_block(text: str, marker: str) -> tuple[str, int]:
    """marker가 포함된 { ... } JSX 블록을 안전하게 제거 (중괄호 카운팅)."""
    removed = 0
    pos = 0
    while True:
        idx = text.find(marker, pos)
        if idx == -1:
            break
        
        # marker 이전의 가장 가까운 `{` 찾기
        brace_start = text.rfind("{", 0, idx)
        if brace_start == -1 or brace_start < pos:
            pos = idx + len(marker)
            continue
        
        # 중괄호 매칭
        depth = 0
        end_pos = -1
        for i in range(brace_start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end_pos = i
                    break
        
        if end_pos == -1:
            pos = idx + len(marker)
            continue
        
        # 후행 공백/개행 1개까지
        after = end_pos + 1
        if after < len(text) and text[after] == "\n":
            after += 1
        
        text = text[:brace_start] + text[after:]
        removed += 1
        pos = brace_start
    
    return text, removed

txt, n = remove_jsx_block(txt, "poem.poet")
print(f"  ✅ poet 렌더링 블록 {n}개 제거")

# ═══════════════════════════════════════════════
# STEP 4: poet 스타일 제거
# ═══════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 4: poet 스타일 제거")
print("=" * 55)

# `poet: { ... },` — 중괄호 카운팅
def remove_style_safe(text: str, style_name: str) -> tuple[str, int]:
    pattern = re.compile(rf'\b{style_name}\s*:\s*\{{')
    m = pattern.search(text)
    if not m:
        return text, 0
    brace_start = m.end() - 1
    depth = 0
    end_pos = -1
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end_pos = i
                break
    if end_pos == -1:
        return text, 0
    # 후행 `,` 까지
    after = end_pos + 1
    while after < len(text) and text[after] in " \t":
        after += 1
    if after < len(text) and text[after] == ",":
        after += 1
    # 후행 개행
    if after < len(text) and text[after] == "\n":
        after += 1
    return text[:m.start()] + text[after:], 1

txt, n = remove_style_safe(txt, "poet")
print(f"  ✅ poet 스타일 {n}개 제거")

# ═══════════════════════════════════════════════
# 결과 확인 + 저장
# ═══════════════════════════════════════════════
print("\n" + "=" * 55)
print("검증")
print("=" * 55)

# 잔여 체크
leftovers = []
if "getPoetName" in txt:
    leftovers.append("getPoetName")
if "poem.poet" in txt:
    leftovers.append("poem.poet")
if "작자 미상" in txt:
    leftovers.append("작자 미상")
# 대괄호/중괄호 균형 확인
if txt.count("{") != txt.count("}"):
    leftovers.append(f"중괄호 불균형 ({{={txt.count('{')}, }}={txt.count('}')})")

if leftovers:
    print(f"  ⚠️ 잔여: {leftovers}")
else:
    print("  ✅ 모든 잔여 제거 완료")

# 미리보기: 함수 주변 라인
print("\n🩺 [파일 앞부분 60줄]")
for i, line in enumerate(txt.splitlines()[:60], 1):
    print(f"  {i:3d}: {line}")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_poem_card_broken.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장 완료: {TSX}")
print("\n다음 명령:")
print("   git add frontend/src/components/poem/PoemFlipCard.tsx")
print('   git commit -m "fix(poem): safe removal of poet rendering"')
print("   git push origin main")
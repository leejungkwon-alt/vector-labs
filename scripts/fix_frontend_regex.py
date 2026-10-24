import re
from pathlib import Path

FRONTEND = Path("frontend/src/components/sections")

def clean_file(filename, patterns):
    path = FRONTEND / filename
    if not path.exists():
        print(f"❌ {filename}: 파일 없음")
        return
    src = path.read_text(encoding="utf-8")
    orig = src
    for pattern, repl in patterns:
        src = re.sub(pattern, repl, src, flags=re.DOTALL)
    
    if src != orig:
        path.write_text(src, encoding="utf-8")
        print(f"✅ {filename}: 한자 노출 코드 제거 완료!")
    else:
        print(f"⚠️ {filename}: 이미 한자 코드가 없습니다. (정상)")

print("=== 정규식 기반 한자 노출 코드 완벽 제거 ===")

# 1. CoreSection: section.pillar_name_traditional 삭제
clean_file("CoreSection.tsx", [
    (r"\{section\.pillar_name_traditional\s*&&\s*\(.*?</Text>\s*\)\}", "")
])

# 2. Year/Monthly/Timeline: || section.pillar 또는 || item.pillar 삭제
clean_file("YearSection.tsx", [
    (r"\s*\|\|\s*section\.pillar\b", "")
])
clean_file("MonthlySection.tsx", [
    (r"\s*\|\|\s*item\.pillar\b", "")
])
clean_file("TimelineSection.tsx", [
    (r"\s*\|\|\s*item\.pillar\b", "")
])

# 3. PremiumSection: {item.pillar} · 삭제
clean_file("PremiumSection.tsx", [
    (r"\{item\.pillar\}\s*·\s*", "")
])

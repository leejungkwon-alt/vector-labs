from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "sections" / "shared.tsx"

t = p.read_text(encoding="utf-8")

# 정확히 이 한 줄만 제거
target = '<Ionicons name="sparkles" size={20} color={colors.primary} />'

if target in t:
    # 줄 전체를 지우기 (앞 공백 포함, 뒤 개행 포함)
    import re
    t = re.sub(r'\n\s*' + re.escape(target) + r'\s*\n', '\n', t, count=1)
    p.write_text(t, encoding="utf-8")
    print("[OK] shared.tsx: Ionicons sparkles 아이콘 제거 완료")
else:
    print("[SKIP] 아이콘 라인이 이미 제거되었거나 찾지 못했습니다.")

# Ionicons import도 사용 안 하면 남겨두기 (다른 곳에서 쓸 수 있음)

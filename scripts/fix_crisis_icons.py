import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "CrisisBanner.tsx"

if not p.exists():
    print("[ERR] CrisisBanner.tsx 파일을 찾을 수 없습니다.")
else:
    t = p.read_text(encoding="utf-8")
    
    # Ionicons, MaterialIcons 등 모든 벡터 아이콘 태그 제거
    t = re.sub(r'<Ionicons\s+[^>]*?/?>', '', t)
    t = re.sub(r'<MaterialIcons\s+[^>]*?/?>', '', t)
    t = re.sub(r'<FontAwesome\s+[^>]*?/?>', '', t)
    t = re.sub(r'<Feather\s+[^>]*?/?>', '', t)
    
    p.write_text(t, encoding="utf-8")
    print("[OK] CrisisBanner.tsx: 모든 벡터 아이콘(Ionicons 등) 제거 완료")

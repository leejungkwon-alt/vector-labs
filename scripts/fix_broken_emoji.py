import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "sections" / "shared.tsx"

if p.exists():
    t = p.read_text(encoding="utf-8")
    # LockedHint 내부의 이모지들을 안전한 기호로 교체
    t = t.replace("🔒", "🔐") # 표준 자물쇠로 교체 (보통 잘 보임)
    t = t.replace("✨", "✦")
    t = t.replace("💡", "💡")
    # 만약 'x' 박스가 특정 이모지라면 싹 지우고 텍스트로 대체
    # LockedHint 내부에 있는 이모지 패턴을 모두 찾아 제거하는 로직 추가
    t = re.sub(r'[\U00010000-\U0010ffff]', '', t) # 모든 이모지 제거 (안전빵)
    
    p.write_text(t, encoding="utf-8")
    print("[OK] shared.tsx 이모지 깨짐 방지 패치 완료 (안전한 텍스트로 대체)")
else:
    print("[ERR] shared.tsx 파일을 찾을 수 없습니다.")

# scripts/fix_variant_collision.py
"""
hash 기반 variant 선택 → index 기반으로 변경
- 인접 대운은 index가 1씩 증가하므로 자동으로 다른 variant
- 같은 pillar → 항상 같은 variant (일관성 유지)
"""
import ast
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
CW = Path("app/services/content_writer.py")

txt = CW.read_text(encoding="utf-8")

OLD = '''    # 3-variant list면 hash로 선택, dict면 그대로 (하위 호환)
    if isinstance(raw, list):
        import hashlib
        seed = str(d.get("pillar", "")) + ":" + str(d.get("index", 0))
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        t = raw[h % len(raw)]'''

NEW = '''    # 3-variant list면 index 기반 선택 (인접 대운 자동 다름)
    if isinstance(raw, list):
        idx = int(d.get("index", 0))
        t = raw[idx % len(raw)]'''

if OLD not in txt:
    print("❌ hash 기반 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'app/services/content_writer.py' | Select-String 'hashlib' -Context 2,2")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ index 기반 variant 선택")

# hash import도 제거 (더 이상 안 씀)
if "import hashlib\n        h = int" not in txt and "hashlib.md5" not in txt:
    print("ℹ️ hashlib import는 이미 정리됨")

# ast 검증
try:
    ast.parse(txt)
    print("✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_variant_collision.py --apply")
    sys.exit(0)

CW.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료. 다음: .\\deploy.ps1")
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "types.ts"
t = p.read_text(encoding="utf-8")

old = '  sijo_ko: string;'
new = '  sijo_ko: string;\n  sijo?: string;'

if old in t and 'sijo?: string;' not in t:
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("[OK] types.ts 수정 완료 (sijo 필드 추가)")
else:
    print("[SKIP] 이미 수정되었거나 찾을 수 없음")

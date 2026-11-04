from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "frontend" / "src" / "components" / "poem" / "PoemFlipCard.tsx"
t = p.read_text(encoding="utf-8")

old = '<Text style={styles.sijoText}>{poem.sijo_ko}</Text>'
new = '<Text style={styles.sijoText}>{poem.sijo || poem.sijo_ko}</Text>'

if old in t:
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("[OK] PoemFlipCard.tsx 수정 완료 (sijo 필드 표시)")
else:
    print("[SKIP] 이미 수정되었거나 찾을 수 없음")

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "app" / "services" / "content_writer.py"
t = p.read_text(encoding="utf-8")

old = '        "sijo_ko": match.get("sijo_ko", ""),'
new = '        "sijo_ko": match.get("sijo_ko", ""),\n        "sijo": tr.get("sijo", match.get("sijo_ko", "")),'

if old in t and '"sijo": tr.get("sijo"' not in t:
    t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8")
    print("[OK] content_writer.py 수정 완료 (sijo 필드 추가)")
else:
    print("[SKIP] 이미 수정되었거나 찾을 수 없음")

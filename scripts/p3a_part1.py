import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app/services/content/data"

# 1. year.json notes
for lang, note in [
    ("en", "The year above follows the solar-term calendar (Lichun to Lichun). In January, the previous solar year is still active."),
    ("ko", "위의 연도는 절기년(입춘~입춘) 기준입니다. 1월에는 아직 전년도 절기년이 적용됩니다."),
]:
    p = DATA / lang / "year.json"
    raw = p.read_text(encoding="utf-8")
    d = json.loads(raw)
    if d.get("SOLAR_CALENDAR_NOTE") == note:
        print(f"  skip {lang}/year.json"); continue
    d["SOLAR_CALENDAR_NOTE"] = note
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  ok {lang}/year.json")

# 2. content_writer.py
p = ROOT / "app/services/content_writer.py"
s = p.read_text(encoding="utf-8")
a = '    default_theme = pack.get("DEFAULT_YEAR_THEME", {})\n'
b = a + '    solar_calendar_note = pack.get("SOLAR_CALENDAR_NOTE", "")\n'
if "solar_calendar_note = pack.get" not in s:
    s = s.replace(a, b, 1); p.write_text(s, encoding="utf-8"); print("  ok cw line1")
else:
    print("  skip cw line1")

s = p.read_text(encoding="utf-8")
c = '        "life_stage_context": life_stage_context,\n    }'
dd = '        "life_stage_context": life_stage_context,\n        "solar_calendar_note": solar_calendar_note,\n    }'
if '"solar_calendar_note": solar_calendar_note' not in s:
    s = s.replace(c, dd, 1); p.write_text(s, encoding="utf-8"); print("  ok cw line2")
else:
    print("  skip cw line2")

# 3. entitlements.py
p = ROOT / "app/services/entitlements.py"
s = p.read_text(encoding="utf-8")
a = '"name", "headline", "watch_for",'
b = '"name", "headline", "watch_for",\n            "solar_calendar_note",'
if '"solar_calendar_note"' not in s:
    s = s.replace(a, b, 1); p.write_text(s, encoding="utf-8"); print("  ok entitlements")
else:
    print("  skip entitlements")
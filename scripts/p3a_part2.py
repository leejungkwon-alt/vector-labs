from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

# 1. types.ts
p = ROOT / "frontend/types.ts"
s = p.read_text(encoding="utf-8")
a = "  lean_into?: string;\n  life_stage_context"
b = "  lean_into?: string;\n  solar_calendar_note?: string;\n  life_stage_context"
if "solar_calendar_note?" not in s:
    s = s.replace(a, b, 1); p.write_text(s, encoding="utf-8"); print("  ok types.ts")
else:
    print("  skip types.ts")

# 2. YearSection.tsx
p = ROOT / "frontend/src/components/sections/YearSection.tsx"
s = p.read_text(encoding="utf-8")
a = '      <Text style={ss.coreHero}>{section.name}</Text>'
b = '''      {section.solar_calendar_note && (
        <Text style={[ss.metaText, { fontStyle: "italic", marginBottom: 8 }]}>
          {section.solar_calendar_note}
        </Text>
      )}
      <Text style={ss.coreHero}>{section.name}</Text>'''
if "solar_calendar_note &&" not in s:
    s = s.replace(a, b, 1); p.write_text(s, encoding="utf-8"); print("  ok YearSection")
else:
    print("  skip YearSection")
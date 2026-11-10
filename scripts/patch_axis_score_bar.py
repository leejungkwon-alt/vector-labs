# scripts/patch_axis_score_bar.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/compatibility.tsx")
if not PATH.exists():
    print("❌ compatibility.tsx 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. axisScore 계산을 위한 로직 삽입
old_map = 'const isExpanded = !!expandedAxes[key];'
new_map = 'const isExpanded = !!expandedAxes[key];\n          const axisScore = Math.round((axis.score + 1) * 50);'

if new_map not in src:
    if old_map in src:
        src = src.replace(old_map, new_map, 1)
    else:
        print("❌ .map 내부 로직 찾을 수 없음"); sys.exit(1)

# 2. 점수 바(Progress Bar) UI 추가
old_ui = '''<Text style={{ fontWeight: "700", color: gradeColors[axis.grade] }}>{axis.grade}</Text>
              </View>'''
new_ui = '''<Text style={{ fontWeight: "700", color: gradeColors[axis.grade] }}>{axis.grade}</Text>
              </View>
              <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 8 }}>
                <View style={{ flex: 1, height: 6, backgroundColor: colors.border, borderRadius: 3, overflow: "hidden", marginRight: 8 }}>
                  <View style={{ height: "100%", width: `${axisScore}%`, backgroundColor: gradeColors[axis.grade] }} />
                </View>
                <Text style={{ fontSize: 12, fontWeight: "600", color: colors.textMuted }}>{axisScore}</Text>
              </View>'''

if new_ui not in src:
    if old_ui in src:
        src = src.replace(old_ui, new_ui, 1)
    else:
        print("❌ UI 렌더링 부분 찾을 수 없음"); sys.exit(1)

PATH.write_text(src, encoding="utf-8")
print("✅ compatibility.tsx 점수 바 패치 완료")
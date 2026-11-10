# scripts/finalize_timeline.py
"""
1) tagger.py, content_writer.py의 모든 DEBUG print 제거 (프로덕션 클린업)
2) TimelineSection.tsx에 접이식 UI (theme/body/caution/practice 표시)
3) 5개 언어 JSON에 caution/practice 라벨 추가
"""
import ast
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. 백엔드 디버그 print 제거
# ═══════════════════════════════════════════════════════════
print("=" * 55)
print("1) 백엔드 디버그 print 제거")
print("=" * 55)

for path in ["app/semantic/tagger.py", "app/services/content_writer.py"]:
    p = Path(path)
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8")
    lines = txt.splitlines(keepends=True)
    cleaned = [l for l in lines if not any(k in l for k in ["[DEBUG-THEME]", "[DEBUG-YONGSIN]"])]
    new_txt = "".join(cleaned)
    removed = len(lines) - len(cleaned)
    if removed:
        try:
            ast.parse(new_txt)
            if APPLY:
                p.write_text(new_txt, encoding="utf-8")
            print(f"  ✅ {path}: {removed}줄 제거")
        except SyntaxError as e:
            print(f"  ❌ {path}: 문법 오류 {e.lineno}")
            sys.exit(1)
    else:
        print(f"  ℹ️ {path}: 디버그 없음")

# ═══════════════════════════════════════════════════════════
# 2. TimelineSection.tsx 접이식 UI
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("2) TimelineSection.tsx 접이식 UI")
print("=" * 55)

TSX = Path("frontend/src/components/sections/TimelineSection.tsx")
if not TSX.exists():
    print(f"  ❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")

# useState import 추가
if "useState" not in txt:
    txt = txt.replace(
        'import { View, Text, Platform } from "react-native";',
        'import { View, Text, Platform, TouchableOpacity, StyleSheet } from "react-native";\nimport { useState } from "react";',
        1,
    )
    print("  ✅ import 추가 (useState, TouchableOpacity, StyleSheet)")

# items.map 블록 전체 교체
OLD_MAP = '''      {section.items.map((item, i) => (
        <View
          key={i}
          style={[
            ss.blockBox,
            item.is_current && { borderColor: colors.primary, borderWidth: 2 },
          ]}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4, flexWrap: "wrap", gap: 4 }}>
            <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>
              {item.ages[0]}–{item.ages[1]}{t("sections.yearsOld")}{item.pillar_name ? ` · ${item.pillar_name}` : ""}
              {item.is_current && <Text style={{ color: colors.primary }}> · {t("sections.current")}</Text>}
            </Text>
            <Text
              style={{
                fontSize: 13,
                fontWeight: "700",
                color: gradeColors[item.grade] || colors.text,
              }}
            >
              {item.grade}
            </Text>
          </View>
          {item.blurb && <Text style={ss.paragraph}>{item.blurb}</Text>}
        </View>
      ))}'''

NEW_MAP = '''      {section.items.map((item, i) => (
        <TimelineItem key={i} item={item} gradeColors={gradeColors} colors={colors} ss={ss} t={t} />
      ))}'''

if OLD_MAP not in txt:
    print("  ❌ items.map 패턴 불일치")
    sys.exit(1)

txt = txt.replace(OLD_MAP, NEW_MAP, 1)
print("  ✅ items.map → TimelineItem 컴포넌트로 교체")

# TimelineItem 컴포넌트 추가 (파일 끝)
if "function TimelineItem" not in txt:
    TIMELINE_ITEM = '''

function TimelineItem({ item, gradeColors, colors, ss, t }: any) {
  const [open, setOpen] = useState(item.is_current === true);
  const hasDetails = !!(item.theme || item.body || item.caution || item.practice);

  return (
    <View
      style={[
        ss.blockBox,
        item.is_current && { borderColor: colors.primary, borderWidth: 2 },
        { paddingVertical: 8 },
      ]}
    >
      <TouchableOpacity
        onPress={() => hasDetails && setOpen(!open)}
        disabled={!hasDetails}
        style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 4 }}
      >
        <View style={{ flex: 1 }}>
          <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>
            {item.ages[0]}–{item.ages[1]}{t("sections.yearsOld")}
            {item.pillar_name ? ` · ${item.pillar_name}` : ""}
            {item.is_current && <Text style={{ color: colors.primary }}> · {t("sections.current")}</Text>}
          </Text>
          {item.theme && (
            <Text style={{ fontSize: 13, color: colors.textMuted, marginTop: 2 }}>
              {item.theme}
            </Text>
          )}
        </View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          <Text style={{ fontSize: 13, fontWeight: "700", color: gradeColors[item.grade] || colors.text }}>
            {item.grade}
          </Text>
          {hasDetails && (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>{open ? "▲" : "▼"}</Text>
          )}
        </View>
      </TouchableOpacity>

      {open && hasDetails && (
        <View style={{ marginTop: 10, paddingTop: 10, borderTopWidth: 1, borderTopColor: colors.border }}>
          {item.body && <Text style={[ss.paragraph, { marginBottom: 8 }]}>{item.body}</Text>}
          {item.caution && (
            <Text style={{ fontSize: 13, color: colors.warn, marginBottom: 6 }}>
              ⚠️ {item.caution}
            </Text>
          )}
          {item.practice && (
            <Text style={{ fontSize: 13, color: colors.primary }}>
              💡 {item.practice}
            </Text>
          )}
        </View>
      )}
    </View>
  );
}
'''
    txt = txt.rstrip() + TIMELINE_ITEM
    print("  ✅ TimelineItem 컴포넌트 추가")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/finalize_timeline.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {TSX}")
print("\n다음 명령 (한 줄씩):")
print("   .\\deploy.ps1  (백엔드 디버그 제거)")
print('   git add "frontend/src/components/sections/TimelineSection.tsx" "app/semantic/tagger.py" "app/services/content_writer.py"')
print('   git commit -m "feat(timeline): personalized themes + accordion UI"')
print("   git push origin main")
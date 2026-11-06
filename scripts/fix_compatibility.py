# scripts/fix_compatibility.py
"""
compatibility.tsx 통합 패치:
1) 관계 선택 버튼 UI (ScrollView→View, flex 균등, numberOfLines=1, 폰트 축소)
2) person_a: myProfile → 명시적 필드만 추출 (422 해결)
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/app/(tabs)/compatibility.tsx")

if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# ============ 1) UI 패치: ScrollView → View, numberOfLines ============
old_ui = '''      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 24 }}>
        <View style={[styles.segmentWrap, { paddingRight: 0 }]}>
          {[
            { key: "romance", label: t("compatibility.typeRomance") },
            { key: "business", label: t("compatibility.typeBusiness") },
            { key: "friend", label: t("compatibility.typeFriend") },
            { key: "family", label: t("compatibility.typeFamily") },
          ].map((tab) => (
            <TouchableOpacity 
              key={tab.key}
              style={[styles.segmentBtn, relationshipType === tab.key && styles.segmentBtnActive, { paddingHorizontal: 16 }]} 
              onPress={() => setRelationshipType(tab.key as any)}
            >
              <Text style={[styles.segmentText, relationshipType === tab.key && styles.segmentTextActive]}>{tab.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>'''

new_ui = '''      <View style={styles.segmentWrap}>
        {[
          { key: "romance", label: t("compatibility.typeRomance") },
          { key: "business", label: t("compatibility.typeBusiness") },
          { key: "friend", label: t("compatibility.typeFriend") },
          { key: "family", label: t("compatibility.typeFamily") },
        ].map((tab) => (
          <TouchableOpacity 
            key={tab.key}
            style={[styles.segmentBtn, relationshipType === tab.key && styles.segmentBtnActive]} 
            onPress={() => setRelationshipType(tab.key as any)}
          >
            <Text 
              style={[styles.segmentText, relationshipType === tab.key && styles.segmentTextActive]}
              numberOfLines={1}
              adjustsFontSizeToFit
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>'''

if old_ui in txt:
    txt = txt.replace(old_ui, new_ui, 1)
    print("✅ UI 패치 완료 (ScrollView→View, numberOfLines=1)")
else:
    print("❌ UI 패턴 불일치 — 수동 확인 필요")
    sys.exit(1)

# ============ 2) UI 스타일 조정 ============
old_style = '''  segmentBtn: { flex: 1, paddingVertical: 12, alignItems: "center", borderRadius: radius.pill },
  segmentText: { fontSize: 15, fontWeight: "600", color: colors.textMuted },'''
new_style = '''  segmentBtn: { flex: 1, paddingVertical: 10, paddingHorizontal: 4, alignItems: "center", justifyContent: "center", borderRadius: radius.pill },
  segmentText: { fontSize: 13, fontWeight: "600", color: colors.textMuted },'''
if old_style in txt:
    txt = txt.replace(old_style, new_style, 1)
    print("✅ 스타일 조정 완료 (폰트 15→13, padding 12→10)")

# ============ 3) 422 해결: person_a 명시적 필드 추출 ============
old_person = '''        person_a: myProfile,
        person_b: {'''
new_person = '''        person_a: {
          birth_date: myProfile.birth_date,
          birth_time: myProfile.birth_time,
          birth_time_mode: myProfile.birth_time_mode,
          birth_location: myProfile.birth_location,
          timezone_str: myProfile.timezone_str,
          longitude: myProfile.longitude,
          gender: myProfile.gender,
        },
        person_b: {'''

if old_person in txt:
    txt = txt.replace(old_person, new_person, 1)
    print("✅ 422 패치 완료 (person_a 명시적 필드)")
else:
    print("⚠️ person_a 패턴 불일치")

# ============ 결과 ============
if txt == orig:
    print("\nℹ️ 변경 없음")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_compatibility.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료")
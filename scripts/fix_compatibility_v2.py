# scripts/fix_compatibility_v2.py
"""
compatibility.tsx 통합 패치 v2:
1) UI: ScrollView→View, numberOfLines=1, flex 균등분배
2) person_a: 명시적 필드만 추출 (user_id/updated_at 제거) + jasi_boundary/correction_mode 포함
3) birth_time_mode: birth_time 유무로 판단 (exact vs noon)
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

# ========== 1) UI: ScrollView → View, numberOfLines ==========
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
    print("✅ UI 패치 (ScrollView → View, numberOfLines=1)")
else:
    print("⚠️ UI 패턴 불일치 — 이미 패치됐거나 코드 변경됨")

# 스타일 조정
old_style = 'segmentBtn: { flex: 1, paddingVertical: 12, alignItems: "center", borderRadius: radius.pill },'
new_style = 'segmentBtn: { flex: 1, paddingVertical: 10, paddingHorizontal: 4, alignItems: "center", justifyContent: "center", borderRadius: radius.pill },'
if old_style in txt:
    txt = txt.replace(old_style, new_style, 1)
    print("✅ 스타일 조정 (paddingVertical 12→10)")

old_text_style = 'segmentText: { fontSize: 15, fontWeight: "600", color: colors.textMuted },'
new_text_style = 'segmentText: { fontSize: 13, fontWeight: "600", color: colors.textMuted },'
if old_text_style in txt:
    txt = txt.replace(old_text_style, new_text_style, 1)
    print("✅ 스타일 조정 (fontSize 15→13)")

# ========== 2) person_a: 명시적 필드만 ==========
old_person = '''        person_a: myProfile,
        person_b: {'''

new_person = '''        person_a: {
          birth_date: myProfile.birth_date,
          birth_time: myProfile.birth_time || undefined,
          birth_time_mode: myProfile.birth_time ? "exact" : "noon",
          birth_location: myProfile.birth_location || undefined,
          timezone_str: myProfile.timezone_str,
          longitude: myProfile.longitude,
          gender: myProfile.gender,
          jasi_boundary: myProfile.jasi_boundary,
          correction_mode: myProfile.correction_mode,
          lang: lang,
        },
        person_b: {'''

if old_person in txt:
    txt = txt.replace(old_person, new_person, 1)
    print("✅ person_a 명시적 필드 (user_id/updated_at 제거 → 422 해결)")
    print("   birth_time_mode: birth_time 있으면 'exact', 없으면 'noon'")
    print("   jasi_boundary, correction_mode, lang 포함")
else:
    print("⚠️ person_a 패턴 불일치 — 이미 패치됐을 수 있음")

# ========== 결과 ==========
if txt == orig:
    print("\nℹ️ 변경 사항 없음 (이미 패치된 상태?)")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_compatibility_v2.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료. 다음:")
print("   git add frontend/app/(tabs)/compatibility.tsx")
print('   git commit -m "fix(compatibility): explicit person_a fields (422) + UI fix"')
print("   git push origin main")
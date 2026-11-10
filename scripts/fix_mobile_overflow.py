# scripts/fix_mobile_overflow.py
"""
1) compatibility.tsx: numberOfLines 제한 → 더보기/접기 토글
2) 5개 언어 JSON: readMore/readLess 키 추가
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. TSX 패치
# ═══════════════════════════════════════════════════════════
TSX = Path("frontend/app/(tabs)/compatibility.tsx")
if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# ① expandedAxes state 추가
if "expandedAxes" not in txt:
    # useEffect나 useState import 확인
    old_state = 'const [isCalculated, setIsCalculated] = useState(false);'
    new_state = 'const [isCalculated, setIsCalculated] = useState(false);\n  const [expandedAxes, setExpandedAxes] = useState<Record<string, boolean>>({});'
    if old_state in txt:
        txt = txt.replace(old_state, new_state, 1)
        print("✅ expandedAxes state 추가")
    else:
        # fallback: 아무 useState 근처에 추가
        print("⚠️ isCalculated state 못 찾음 — 수동 확인 필요")
        print("   다음 명령으로 확인:")
        print("   Get-Content 'frontend/app/(tabs)/compatibility.tsx' | Select-String 'useState' -Context 0,2")
        sys.exit(1)

# ② 축 카드 렌더링 부분 교체
OLD_AXES = '''        {Object.entries(compat.axes).map(([key, axis]) => (
          <View key={key} style={styles.axisCard}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
              <Text style={styles.axisTitle}>
                {key === "elements" ? t("compatibility.axisElements") : key === "day_master" ? t("compatibility.axisDayMaster") : key === "ten_gods" ? t("compatibility.axisTenGods") : t("compatibility.axisSinsal")}
              </Text>
              <Text style={{ fontWeight: "700", color: gradeColors[axis.grade] }}>{axis.grade}</Text>
            </View>
            <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 }}>{axis.headline}</Text>
            <Text style={{ fontSize: 14, color: colors.textMuted, lineHeight: 20 }} numberOfLines={4}>{axis.body}</Text>
          </View>
        ))}'''

NEW_AXES = '''        {Object.entries(compat.axes).map(([key, axis]) => {
          const isExpanded = !!expandedAxes[key];
          return (
            <View key={key} style={styles.axisCard}>
              <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
                <Text style={styles.axisTitle}>
                  {key === "elements" ? t("compatibility.axisElements") : key === "day_master" ? t("compatibility.axisDayMaster") : key === "ten_gods" ? t("compatibility.axisTenGods") : t("compatibility.axisSinsal")}
                </Text>
                <Text style={{ fontWeight: "700", color: gradeColors[axis.grade] }}>{axis.grade}</Text>
              </View>
              <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 }}>{axis.headline}</Text>
              <Text style={{ fontSize: 14, color: colors.textMuted, lineHeight: 20 }} numberOfLines={isExpanded ? undefined : 4}>{axis.body}</Text>
              {axis.body && axis.body.length > 100 && (
                <TouchableOpacity
                  onPress={() => setExpandedAxes(prev => ({ ...prev, [key]: !prev[key] }))}
                  style={{ paddingVertical: 6, marginTop: 4 }}
                >
                  <Text style={{ fontSize: 13, color: colors.primary, fontWeight: "600" }}>
                    {isExpanded ? t("compatibility.readLess") : t("compatibility.readMore")}
                  </Text>
                </TouchableOpacity>
              )}
            </View>
          );
        })}'''

if OLD_AXES not in txt:
    print("❌ 축 카드 렌더링 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'frontend/app/(tabs)/compatibility.tsx' | Select-String 'compat.axes' -Context 0,15")
    sys.exit(1)

txt = txt.replace(OLD_AXES, NEW_AXES, 1)
print("✅ 축 카드 → 더보기/접기 토글")

# ═══════════════════════════════════════════════════════════
# 2. 5개 언어 JSON 번역 키 추가
# ═══════════════════════════════════════════════════════════
TRANS = {
    "ko": {"readMore": "더보기 ▾", "readLess": "접기 ▴"},
    "en": {"readMore": "Read more ▾", "readLess": "Show less ▴"},
    "ja": {"readMore": "もっと見る ▾", "readLess": "閉じる ▴"},
    "zh_cn": {"readMore": "展开 ▾", "readLess": "收起 ▴"},
    "es": {"readMore": "Ver más ▾", "readLess": "Ver menos ▴"},
}

def lang_key(p):
    s = p.stem.lower()
    return "zh_cn" if s.startswith("zh") else s if s in ("ko", "en", "ja", "es") else None

print("\n" + "=" * 55)
print("2) 5개 언어 JSON: readMore/readLess")
print("=" * 55)

for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if lang not in TRANS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if "compatibility" not in data:
        data["compatibility"] = {}
    changed = False
    for k, v in TRANS[lang].items():
        if data["compatibility"].get(k) != v:
            data["compatibility"][k] = v
            changed = True
    if changed:
        print(f"  ✅ {f.name}")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_mobile_overflow.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {TSX}")
print("\n다음:")
print('   git add "frontend/app/(tabs)/compatibility.tsx" frontend/src/locales/')
print('   git commit -m "fix(compat): collapsible axis body for mobile"')
print("   git push origin main")
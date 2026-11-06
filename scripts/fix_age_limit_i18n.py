# scripts/fix_age_limit_i18n.py
"""
1) 5개 언어 JSON에 만 14세 미만 에러 문구 추가
2) compatibility.tsx에서 400 에러(14세) 감지 시 다국어(t) 적용된 UI 노출
"""
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ==========================================
# 1) JSON 번역 키 추가 (5개 언어)
# ==========================================
TRANS = {
    "ko": {
        "ageLimitTitle": "🔞 만 14세 미만은 이용할 수 없습니다",
        "ageLimitDesc": "Gyeol은 만 14세 이상만 이용 가능한 서비스입니다.\n상대방의 생년월일을 다시 확인해 주세요.",
        "ageLimitRetry": "다시 입력하기",
    },
    "en": {
        "ageLimitTitle": "🔞 Users under 14 cannot use this service",
        "ageLimitDesc": "Gyeol is available only to users aged 14 and over.\nPlease check the birthdate again.",
        "ageLimitRetry": "Try again",
    },
    "ja": {
        "ageLimitTitle": "🔞 14歳未満の方はご利用いただけません",
        "ageLimitDesc": "Gyeolは14歳以上の方のみご利用いただけます。\nお相手の生年月日をご確認ください。",
        "ageLimitRetry": "再入力する",
    },
    "zh_cn": {
        "ageLimitTitle": "🔞 14岁以下用户无法使用此服务",
        "ageLimitDesc": "Gyeol仅限14岁及以上用户使用。\n请重新确认对方的出生日期。",
        "ageLimitRetry": "重新输入",
    },
    "es": {
        "ageLimitTitle": "🔞 Los menores de 14 años no pueden usar este servicio",
        "ageLimitDesc": "Gyeol solo está disponible para usuarios de 14 años o más.\nVerifique la fecha de nacimiento nuevamente.",
        "ageLimitRetry": "Intentar de nuevo",
    },
}

def lang_key(p: Path) -> str:
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

print("=" * 55)
print("1) 프론트엔드 JSON: ageLimit 번역 키 추가")
print("=" * 55)
for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if lang not in TRANS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    compat = data.setdefault("compatibility", {})
    changed = False
    for k, v in TRANS[lang].items():
        if compat.get(k) != v:
            compat[k] = v
            changed = True
    if changed:
        print(f"  ✅ {f.name}: ageLimit 키 업데이트")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)

# ==========================================
# 2) compatibility.tsx: 400 에러(14세) 감지 및 다국어 UI
# ==========================================
print("\n" + "=" * 55)
print("2) 프론트엔드: 14세 에러 다국어 UI 적용")
print("=" * 55)

TSX = Path("frontend/app/(tabs)/compatibility.tsx")
if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# 기존 하드코딩된 만 14세 UI를 찾아서 교체 (이전 패치가 적용된 경우)
old_block = '''      // 🚨 400 에러 중 '14세' 관련 메시지 처리
      if (status === 400 && msg.includes("14")) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.dangerSoft, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.danger }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>🔞</Text>
            <Text style={{ fontSize: 18, fontWeight: "800", color: colors.danger, marginBottom: 8, textAlign: "center" }}>
              만 14세 미만은 이용할 수 없습니다
            </Text>
            <Text style={{ fontSize: 15, color: colors.text, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
              Gyeol은 만 14세 이상만 이용 가능한 서비스입니다.{"\\n"}상대방의 생년월일을 다시 확인해 주세요.
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => setIsCalculated(false)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>다시 입력하기</Text>
            </TouchableOpacity>
          </View>
        );
      }'''

new_block = '''      // 🚨 400 에러 중 '14세' 관련 메시지 처리 (다국어)
      const lowerMsg = msg.toLowerCase();
      if (status === 400 && (lowerMsg.includes("14") || lowerMsg.includes("years old"))) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.dangerSoft, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.danger }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>🔞</Text>
            <Text style={{ fontSize: 18, fontWeight: "800", color: colors.danger, marginBottom: 8, textAlign: "center" }}>
              {t("compatibility.ageLimitTitle")}
            </Text>
            <Text style={{ fontSize: 15, color: colors.text, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
              {t("compatibility.ageLimitDesc")}
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => setIsCalculated(false)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
                {t("compatibility.ageLimitRetry")}
              </Text>
            </TouchableOpacity>
          </View>
        );
      }'''

if old_block in txt:
    txt = txt.replace(old_block, new_block, 1)
    print("  ✅ 기존 하드코딩 UI → t() 다국어 UI로 교체")
elif 't("compatibility.ageLimitTitle")' in txt:
    print("  ℹ️ 이미 다국어 UI 적용됨")
else:
    # 이전 패치가 아예 안 된 상태 (에러 처리 블록이 없는 경우)
    # renderResult 내 error 처리 부분에 삽입
    insert_marker = 'if (status === 401 || status === 403) {'
    if insert_marker in txt:
        age_block = '''      const lowerMsg = msg.toLowerCase();
      if (status === 400 && (lowerMsg.includes("14") || lowerMsg.includes("years old"))) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.dangerSoft, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.danger }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>🔞</Text>
            <Text style={{ fontSize: 18, fontWeight: "800", color: colors.danger, marginBottom: 8, textAlign: "center" }}>
              {t("compatibility.ageLimitTitle")}
            </Text>
            <Text style={{ fontSize: 15, color: colors.text, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
              {t("compatibility.ageLimitDesc")}
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => setIsCalculated(false)}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
                {t("compatibility.ageLimitRetry")}
              </Text>
            </TouchableOpacity>
          </View>
        );
      }

      // 401(세션 만료) 또는 403(구독/결제 필요) 에러 핸들링
      if (status === 401 || status === 403) {'''
        txt = txt.replace(insert_marker, age_block, 1)
        print("  ✅ 신규 다국어 UI 삽입 (기존 하드코딩 없음)")
    else:
        print("  ❌ 에러 처리 블록을 찾지 못했습니다. 수동 확인 필요")
        sys.exit(1)

if txt != orig and APPLY:
    TSX.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_age_limit_i18n.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   git add frontend/")
    print('   git commit -m "fix(compat): age limit error i18n (5 languages)"')
    print("   git push origin main")
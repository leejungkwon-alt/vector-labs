#!/usr/bin/env python3
"""Step 4: compatibility.tsx — useT 적용 + en.json compatibility 자연어 재작성."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, apply_patches, print_footer

EN_JSON = ROOT / "frontend/src/locales/en.json"
KO_JSON = ROOT / "frontend/src/locales/ko.json"
TSX = "frontend/app/(tabs)/compatibility.tsx"

# ---------------------------------------------------------
# 1) en.json compatibility 섹션 — 자연어 재작성
# ---------------------------------------------------------
EN_COMPAT = {
    "noProfile": "Add your birth details first so we can read your side of the chart.",
    "title": "See your chemistry with someone",
    "typeRomance": "💖 Romance",
    "typeBusiness": "💼 Business",
    "typeFriend": "🤝 Friend",
    "typeFamily": "🏠 Family",
    "partnerDate": "Their birthday",
    "partnerTime": "Their birth time",
    "unknownTime": "Time unknown",
    "timeUnknown": "Time unknown (assuming noon)",
    "partnerCity": "Their birthplace",
    "partnerTimezone": "Birthplace timezone",
    "partnerGender": "Their gender",
    "male": "Male",
    "female": "Female",
    "calculate": "Read the chemistry",
    "paywallTitle": "Chemistry is a Premium feature",
    "paywallBody": "Unlock your 4-axis chemistry — elements, day master, values, and special traits — with the Compatibility add-on, or upgrade to Premium.",
    "paywallCta": "See plans",
    "resultRomance": "Romance chemistry",
    "resultBusiness": "Business chemistry",
    "resultFriend": "Friendship chemistry",
    "resultFamily": "Family chemistry",
    "scoreUnit": "pts",
    "adviceTitle": "💡 Advice tuned to this relationship",
    "axisElements": "Five Elements",
    "axisDayMaster": "Day master",
    "axisTenGods": "Values & mode",
    "axisSinsal": "Special traits",
}

KO_ADD = {"partnerTimezone": "출생지 타임존 (Timezone)"}


def patch_json(path: Path, section: str, payload: dict, *, replace: bool) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if replace:
        data[section] = payload
    else:
        data.setdefault(section, {}).update(payload)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    action = "재작성" if replace else "키 추가"
    print(f"✅ {path.name}: compatibility {action} ({len(payload)}개)")


# ---------------------------------------------------------
# 2) compatibility.tsx 패치 (모두 안전한 substring 치환)
# ---------------------------------------------------------
PATCHES = [
    # --- import + 훅 ---
    (
        'import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang\n',
        'import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang\n'
        'import { useT } from "@/i18n";\n',
        "import useT",
    ),
    (
        '  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl\n',
        '  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl\n'
        '  const t = useT();\n',
        "const t = useT()",
    ),
    # --- cityLabel: '직접 입력'만 치환 ---
    (
        'isCustomCity ? "직접 입력" : ',
        'isCustomCity ? t("birthInput.customCity") : ',
        "cityLabel → t(birthInput.customCity)",
    ),
    # --- 화면 상단 ---
    (
        '<Text style={{ color: colors.textMuted }}>내 사주 정보를 먼저 입력해 주세요.</Text>',
        '<Text style={{ color: colors.textMuted }}>{t("compatibility.noProfile")}</Text>',
        "noProfile",
    ),
    (
        '<Text style={styles.title}>누구와의 케미를 확인해 볼까요?</Text>',
        '<Text style={styles.title}>{t("compatibility.title")}</Text>',
        "title",
    ),
    # --- 타입 셀렉터: map param t → tab (shadowing 회피) ---
    (
        '''          {[
            { key: "romance", label: "💖 연애" },
            { key: "business", label: "💼 비즈니스" },
            { key: "friend", label: "🤝 친구" },
            { key: "family", label: "🏠 가족" },
          ].map((t) => (
            <TouchableOpacity 
              key={t.key}
              style={[styles.segmentBtn, relationshipType === t.key && styles.segmentBtnActive, { paddingHorizontal: 16 }]} 
              onPress={() => setRelationshipType(t.key as any)}
            >
              <Text style={[styles.segmentText, relationshipType === t.key && styles.segmentTextActive]}>{t.label}</Text>
            </TouchableOpacity>
          ))}''',
        '''          {[
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
          ))}''',
        "type selector (map param t → tab)",
    ),
    # --- 라벨들 ---
    (
        '<Text style={styles.label}>상대방 생년월일</Text>',
        '<Text style={styles.label}>{t("compatibility.partnerDate")}</Text>',
        "partnerDate",
    ),
    (
        '<Text style={styles.label}>상대방 출생 시간</Text>',
        '<Text style={styles.label}>{t("compatibility.partnerTime")}</Text>',
        "partnerTime",
    ),
    (
        '<Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>시간을 몰라요</Text>',
        '<Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>{t("compatibility.unknownTime")}</Text>',
        "unknownTime",
    ),
    # --- 시간 표기: HH시 MM분 → HH:MM (영어권 자연 표기) ---
    (
        '          {unknownTime ? "시간 모름 (정오 기준)" : `${String(partnerTime.getHours()).padStart(2, "0")}시 ${String(partnerTime.getMinutes()).padStart(2, "0")}분`}',
        '          {unknownTime ? t("compatibility.timeUnknown") : `${String(partnerTime.getHours()).padStart(2, "0")}:${String(partnerTime.getMinutes()).padStart(2, "0")}`}',
        "time display → HH:MM",
    ),
    (
        '<Text style={styles.label}>상대방 출생지</Text>',
        '<Text style={styles.label}>{t("compatibility.partnerCity")}</Text>',
        "partnerCity",
    ),
    (
        '<Text style={styles.label}>출생지 타임존 (Timezone)</Text>',
        '<Text style={styles.label}>{t("compatibility.partnerTimezone")}</Text>',
        "partnerTimezone",
    ),
    (
        '<Text style={styles.label}>상대방 성별</Text>',
        '<Text style={styles.label}>{t("compatibility.partnerGender")}</Text>',
        "partnerGender",
    ),
    (
        '<Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>남성</Text>',
        '<Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>{t("compatibility.male")}</Text>',
        "gender M",
    ),
    (
        '<Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>여성</Text>',
        '<Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>{t("compatibility.female")}</Text>',
        "gender F",
    ),
    (
        '<Text style={styles.nextBtnText}>케미 보기</Text>',
        '<Text style={styles.nextBtnText}>{t("compatibility.calculate")}</Text>',
        "calculate button",
    ),
    # --- Paywall ---
    (
        '<Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>궁합 분석은 유료 기능입니다</Text>',
        '<Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>{t("compatibility.paywallTitle")}</Text>',
        "paywallTitle",
    ),
    (
        '              상대방과의 4가지 케미(오행, 일간, 가치관, 신살)를 확인하려면{"\\n"}\n              궁합 애드온을 구매하거나 프리미엄으로 업그레이드하세요.',
        '              {t("compatibility.paywallBody")}',
        "paywallBody",
    ),
    (
        '<Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 / 애드온 구매하러 가기</Text>',
        '<Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>{t("compatibility.paywallCta")}</Text>',
        "paywallCta",
    ),
    # --- 결과 라벨 (substring — 문법 그대로 유지) ---
    ('"연애 케미"', 't("compatibility.resultRomance")', "resultRomance"),
    ('"비즈니스 케미"', 't("compatibility.resultBusiness")', "resultBusiness"),
    ('"친구 케미"', 't("compatibility.resultFriend")', "resultFriend"),
    ('"가족 케미"', 't("compatibility.resultFamily")', "resultFamily"),
    # --- 점수 단위 ---
    (
        '<Text style={{ fontSize: 20, fontWeight: "700", color: colors.textMuted, marginBottom: 10 }}> / 100점</Text>',
        '<Text style={{ fontSize: 20, fontWeight: "700", color: colors.textMuted, marginBottom: 10 }}> / 100 {t("compatibility.scoreUnit")}</Text>',
        "score unit",
    ),
    # --- 조언 타이틀 ---
    (
        '<Text style={styles.tipTitle}>💡 관계 맞춤 조언</Text>',
        '<Text style={styles.tipTitle}>{t("compatibility.adviceTitle")}</Text>',
        "advice title",
    ),
    # --- 축 라벨 (substring — 문법 그대로 유지) ---
    ('"오행 상생"', 't("compatibility.axisElements")', "axisElements"),
    ('"일간 관계"', 't("compatibility.axisDayMaster")', "axisDayMaster"),
    ('"가치관/모드"', 't("compatibility.axisTenGods")', "axisTenGods"),
    ('"신살 공명"', 't("compatibility.axisSinsal")', "axisSinsal"),
]


def main() -> int:
    print("[step4] compatibility.tsx + en.json 자연어 재작성")
    print("=" * 62)
    patch_json(EN_JSON, "compatibility", EN_COMPAT, replace=True)
    patch_json(KO_JSON, "compatibility", KO_ADD, replace=False)
    print("-" * 62)
    print(f"[step4] {TSX}")
    applied, skipped = apply_patches(TSX, PATCHES)
    print(f"\n결과: 적용 {applied} / 건너뜀 {skipped}")
    print_footer("step4", "i18n(step4): compatibility.tsx useT + en 자연어 재작성")
    return 0 if applied > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
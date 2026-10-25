#!/usr/bin/env python3
"""Step 5: 용어 사전 생성 + en.json 통일 + settings.tsx i18n 적용."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, apply_patches, print_footer

EN_JSON   = ROOT / "frontend/src/locales/en.json"
KO_JSON   = ROOT / "frontend/src/locales/ko.json"
GLOSSARY  = ROOT / "docs/i18n-glossary.md"
TSX       = "frontend/app/(tabs)/settings.tsx"

# ============================================================
# 1) Glossary 문서 생성 (이후 모든 Step이 이 표를 따름)
# ============================================================
GLOSSARY_MD = """# SAJU i18n Glossary (canonical)

같은 개념엔 같은 단어. 새 문자열을 추가할 때 이 표를 먼저 확인.

## 원칙
1. **직역 금지** — 영어는 그 기능을 처음 보는 사람이 자연스럽게 읽는 문장.
2. **용어 통일** — 아래 표를 앱 전체에서 동일하게 사용.
3. **숫자·단위** — 통화는 `$2.99`(locale-independent), 시간은 24h `14:30`.
4. **날짜** — `YYYY-MM-DD` (백엔드 표준).

## Section titles (백엔드 `sec.title`)

| id | KO | EN |
|---|---|---|
| core | 당신의 본질 | Your Core |
| energy | 당신의 에너지 지도 | Your Energy Signature |
| lucky_code | 당신에게 필요한 기운 | Your Lucky Code |
| health | 몸과 마음 | Body & Wellness |
| money | 재물과 돈 | Money & Wealth |
| work | 일과 재능 | Work & Craft |
| bonds | 친구와 동료 | Bonds & Belonging |
| year | 올해의 흐름 | This Year |
| timeline | 인생의 궤적 | Your Timeline |
| monthly | 월별 흐름 | Your Monthly Calendar |
| chart | 당신의 네 가지 얼굴 | Your Four Faces |
| sinsal | 특별한 재능 | Special Traits |

## UI 크롬 (프론트)

| Concept | KO | EN |
|---|---|---|
| Shadow | 그림자 | Shadows |
| Advice | 조언 | Advice |
| Personalized insights | 맞춤 인사이트 | Personalized insights |
| Patterns | 패턴 | Patterns |
| More actions | 추가 실천 | More actions |
| Practices | 실천 | Practices |
| Focus | 집중 | Focus |
| Watch out | 주의 | Watch out |
| Locked content | 잠긴 콘텐츠 | Locked content |
| Current | 현재 | Current |
| Life stage | 생애 단계 | Life stage |
| (Core) tag | (본질) | (Core) |

## Compatibility (궁합)

| Concept | KO | EN |
|---|---|---|
| Chemistry | 케미 | Chemistry |
| Romance / Business / Friend / Family | 연애 / 비즈니스 / 친구 / 가족 | Romance / Business / Friend / Family |
| Best match | 최고의 케미 | Best match |
| Challenging match | 주의할 케미 | Challenging match |
| Five Elements axis | 오행 상생 | Five Elements |
| Day master axis | 일간 관계 | Day master |
| Values & mode axis | 가치관/모드 | Values & mode |
| Special traits axis | 신살 공명 | Special traits |

## Auth & Plan

| Concept | KO | EN |
|---|---|---|
| Free tier | 무료 회원 | Free |
| Subscription | 구독자 | Subscription |
| Premium | 프리미엄 회원 | Premium |
| Guest | 게스트 | Guest |
| Plan (settings row) | 이용 등급 | Plan |
| Not signed in | 로그인 안 됨 | Not signed in |
| Receipts | 결제 내역 | Receipts |

## Sub-brand words (번역 금지)
- `Gyeol` — 브랜드명, 영어 그대로
- `Premium` — 브랜드 톤
- 아키타입 이름(`The Radiator`, `The Blade`, ...)은 백엔드 `core.json`이 유일 소스.

## 백로그 (아직 처리 안 됨)
- [ ] `birth_location` raw key(`seoul`, `new_york`) 표시 → 도시 display name 매핑
- [ ] `frontend/app/index.tsx` 스플래시 — "결" 브랜드 표기 정책
- [ ] 백엔드 `en/cross_insight.json`, `en/free_gating.json`, `en/premium_insights.json` 누락
"""

def ensure_glossary() -> None:
    GLOSSARY.parent.mkdir(parents=True, exist_ok=True)
    GLOSSARY.write_text(GLOSSARY_MD, encoding="utf-8")
    print(f"✅ {GLOSSARY.relative_to(ROOT)} 생성")

# ============================================================
# 2) en.json 용어 통일 (glossary 일치화)
# ============================================================
EN_FIXES = {
    ("settings", "tier"): "Plan",
    ("settings", "loginAnonymous"): "Guest",
    ("settings", "paymentHistory"): "Receipts",
    ("sections", "shadow"): "Shadows",
    ("common", "notice"): "Notice",
}

KO_ADD = {
    ("common", "notice"): "알림",
}

def apply_json_fixes(path: Path, fixes: dict) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    n = 0
    for (section, key), val in fixes.items():
        data.setdefault(section, {})[key] = val
        n += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ {path.name}: {n}개 키 통일")

# ============================================================
# 3) settings.tsx 패치
# ============================================================
PATCHES = [
    # --- import & hook ---
    (
        'import { useLanguageStore, SupportedLang } from "@/store/languageStore";\n',
        'import { useLanguageStore, SupportedLang } from "@/store/languageStore";\n'
        'import { useT } from "@/i18n";\n',
        "import useT",
    ),
    (
        '  const user = useAuthStore((s) => s.user);\n',
        '  const user = useAuthStore((s) => s.user);\n'
        '  const t = useT();\n',
        "const t = useT()",
    ),
    # --- formatBirthInfo() ---
    (
        'if (!profile?.birth_date) return "미등록 (입력 필요)";',
        'if (!profile?.birth_date) return t("settings.birthNotSet");',
        "birthNotSet",
    ),
    (
        'info += " (시간 모름 - 정오 기준)";',
        'info += t("settings.timeUnknownNoon");',
        "timeUnknownNoon",
    ),
    (
        'info += " (시간 모름 - 일주만)";',
        'info += t("settings.timeUnknownDayOnly");',
        "timeUnknownDayOnly",
    ),
    # --- getLoginProvider() ---
    (
        'if (!user) return "로그인 안 됨";',
        'if (!user) return t("settings.loginNotSet");',
        "loginNotSet",
    ),
    (
        'if (user.is_anonymous) return "게스트 (익명 로그인)";',
        'if (user.is_anonymous) return t("settings.loginAnonymous");',
        "loginAnonymous",
    ),
    (
        '    return `${user.social_provider?.toUpperCase() || "소셜"} 연동됨`;',
        '    const provider = user.social_provider\n'
        '      ? user.social_provider.charAt(0).toUpperCase() + user.social_provider.slice(1)\n'
        '      : "Social";\n'
        '    return t("settings.loginSocial", { provider });',
        "loginSocial (capitalized provider)",
    ),
    # --- 삭제 다이얼로그 ---
    (
        '        const msg = e?.detail || "계정 삭제에 실패했습니다.";\n'
        '        if (Platform.OS === "web") alert(msg);\n'
        '        else Alert.alert("오류", msg);',
        '        const msg = e?.detail || t("settings.deleteAccountFail");\n'
        '        if (Platform.OS === "web") alert(msg);\n'
        '        else Alert.alert(t("common.notice"), msg);',
        "delete error alert",
    ),
    (
        'if (confirm("정말로 계정을 삭제하시겠습니까? 모든 데이터가 사라집니다.")) performDelete();',
        'if (confirm(t("settings.deleteAccountConfirmWeb"))) performDelete();',
        "delete confirm (web)",
    ),
    (
        '      Alert.alert("계정 삭제", "정말로 계정을 영구 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.", [\n'
        '        { text: "취소", style: "cancel" },\n'
        '        { text: "영구 삭제", style: "destructive", onPress: performDelete },\n'
        '      ]);',
        '      Alert.alert(t("settings.deleteAccountOk"), t("settings.deleteAccountConfirm"), [\n'
        '        { text: t("settings.deleteAccountCancel"), style: "cancel" },\n'
        '        { text: t("settings.deleteAccountDelete"), style: "destructive", onPress: performDelete },\n'
        '      ]);',
        "delete confirm (native)",
    ),
    # --- 구독 관리 (web) ---
    (
        '      alert("모바일 앱에서 구독을 관리하실 수 있습니다.");',
        '      alert(t("settings.manageSubscriptionWeb"));',
        "manageSubscriptionWeb",
    ),
    # --- 계정 정보 박스 ---
    (
        '<Text style={styles.sectionTitle}>내 계정 정보</Text>',
        '<Text style={styles.sectionTitle}>{t("settings.accountInfo")}</Text>',
        "accountInfo",
    ),
    (
        '<Text style={styles.label}>로그인 계정</Text>',
        '<Text style={styles.label}>{t("settings.loginAccount")}</Text>',
        "loginAccount",
    ),
    (
        '<Text style={styles.label}>출생 정보 (생년월일시)</Text>',
        '<Text style={styles.label}>{t("settings.birthInfo")}</Text>',
        "birthInfo",
    ),
    (
        '<Text style={styles.label}>이용 등급</Text>',
        '<Text style={styles.label}>{t("settings.tier")}</Text>',
        "tier label",
    ),
    (
        '              user?.tier === "free" ? "무료 회원 (Free)" :\n'
        '              user?.tier === "subscription" ? "구독자 (Subscription)" :\n'
        '              user?.tier === "premium" ? "프리미엄 회원 (Premium)" : user?.tier',
        '              user?.tier === "free" ? t("settings.tierFree") :\n'
        '              user?.tier === "subscription" ? t("settings.tierSubscription") :\n'
        '              user?.tier === "premium" ? t("settings.tierPremium") : user?.tier',
        "tier values",
    ),
    # --- 구독 관리 카드 ---
    (
        '<Text style={[styles.sectionTitle, { color: colors.primary }]}>💎 구독 관리</Text>',
        '<Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.subscriptionManageTitle")}</Text>',
        "subscriptionManageTitle",
    ),
    (
        '            현재 모든 프리미엄 혜택을 이용 중이십니다.',
        '            {t("settings.subscriptionActive")}',
        "subscriptionActive",
    ),
    (
        '<Text style={styles.manageBtnText}>구독 변경 및 취소하기</Text>',
        '<Text style={styles.manageBtnText}>{t("settings.manageSubscription")}</Text>',
        "manageSubscription",
    ),
    # --- 업그레이드 카드 ---
    (
        '<Text style={[styles.sectionTitle, { color: colors.primary }]}>✨ 프리미엄 업그레이드</Text>',
        '<Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.upgradeTitle")}</Text>',
        "upgradeTitle",
    ),
    (
        '            구독하면 7일치 데일리 에너지와 궁합 분석을 모두 이용할 수 있습니다.',
        '            {t("settings.upgradeBody")}',
        "upgradeBody",
    ),
    (
        '<Text style={styles.upgradeBtnText}>프리미엄 구독하기</Text>',
        '<Text style={styles.upgradeBtnText}>{t("settings.upgradeCta")}</Text>',
        "upgradeCta",
    ),
    # --- 결제 내역 ---
    (
        '<Text style={styles.sectionTitle}>결제 내역 (Payment History)</Text>',
        '<Text style={styles.sectionTitle}>{t("settings.paymentHistory")}</Text>',
        "paymentHistory",
    ),
    (
        '                  {p.product_id === "sub_monthly_299" ? "월간 구독권" : \n'
        '                   p.product_id === "addon_compat_199" ? "궁합 애드온" :\n'
        '                   p.product_id === "addon_deep_099" ? "심화 리포트" : p.product_id}',
        '                  {p.product_id === "sub_monthly_299" ? t("settings.productSubMonthly") : \n'
        '                   p.product_id === "addon_compat_199" ? t("settings.productCompatAddon") :\n'
        '                   p.product_id === "addon_deep_099" ? t("settings.productDeepReport") : p.product_id}',
        "product names",
    ),
    # --- 계정 액션 ---
    (
        '<Text style={styles.btnText}>출생 정보 수정하기</Text>',
        '<Text style={styles.btnText}>{t("settings.editBirthInfo")}</Text>',
        "editBirthInfo",
    ),
    (
        '<Text style={styles.dangerText}>계정 영구 삭제</Text>',
        '<Text style={styles.dangerText}>{t("settings.deleteAccount")}</Text>',
        "deleteAccount button",
    ),
    # --- 언어 설정 ---
    (
        '<Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 12 }}>언어 설정 (Language)</Text>',
        '<Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 12 }}>{t("settings.language")}</Text>',
        "language section",
    ),
]

# ============================================================
# main
# ============================================================
def main() -> int:
    print("[step5] glossary + en 통일 + settings.tsx")
    print("=" * 62)
    ensure_glossary()
    apply_json_fixes(EN_JSON, EN_FIXES)
    apply_json_fixes(KO_JSON, KO_ADD)
    print("-" * 62)
    print(f"[step5] {TSX}")
    applied, skipped = apply_patches(TSX, PATCHES)
    print(f"\n결과: 적용 {applied} / 건너뜀 {skipped}")
    print_footer("step5", "i18n(step5): glossary + settings.tsx useT + en 통일")
    return 0 if skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
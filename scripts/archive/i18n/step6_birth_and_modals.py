#!/usr/bin/env python3
"""Step 6: birth-input.tsx + CityPickerModal + TimezonePickerModal + i18n date/time helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, apply_patches, print_footer

I18N_TS = ROOT / "frontend/src/i18n.ts"

I18N_APPEND = '''
// ---------------------------------------------------------------
// Date/Time helpers (locale-aware display for pickers)
// ---------------------------------------------------------------
export function formatPickerDate(d: Date, lang: string): string {
  if (lang === "ko") {
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
  }
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

export function formatPickerTime(d: Date): string {
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
'''


def append_i18n_helpers() -> None:
    src = I18N_TS.read_text(encoding="utf-8")
    if "formatPickerDate" in src:
        print("ℹ️  i18n.ts: formatPickerDate 이미 존재 — 건너뜀")
        return
    I18N_TS.write_text(src + I18N_APPEND, encoding="utf-8")
    print("✅ i18n.ts: formatPickerDate / formatPickerTime 추가")


# ============================================================
# birth-input.tsx
# ============================================================
BIRTH_PATCHES = [
    (
        'import { useProfileStore } from "@/store/profileStore";\n',
        'import { useProfileStore } from "@/store/profileStore";\n'
        'import { useLanguageStore } from "@/store/languageStore";\n'
        'import { useT, formatPickerDate, formatPickerTime } from "@/i18n";\n',
        "birth: imports",
    ),
    (
        '  const saveProfile = useProfileStore((s) => s.saveProfile);\n',
        '  const saveProfile = useProfileStore((s) => s.saveProfile);\n'
        '  const lang = useLanguageStore((s) => s.lang);\n'
        '  const t = useT();\n',
        "birth: hooks",
    ),
    (
        'const cityLabel = isCustomCity ? "직접 입력" : ',
        'const cityLabel = isCustomCity ? t("birthInput.customCity") : ',
        "birth: cityLabel",
    ),
    (
        '<Text style={styles.title}>출생 정보 입력</Text>',
        '<Text style={styles.title}>{t("birthInput.title")}</Text>',
        "birth: title",
    ),
    (
        '<Text style={styles.label}>생년월일</Text>',
        '<Text style={styles.label}>{t("birthInput.birthDate")}</Text>',
        "birth: date label",
    ),
    (
        '<Text style={styles.inputText}>{birthDate.getFullYear()}년 {birthDate.getMonth() + 1}월 {birthDate.getDate()}일</Text>',
        '<Text style={styles.inputText}>{formatPickerDate(birthDate, lang)}</Text>',
        "birth: date display",
    ),
    (
        '<Text style={styles.label}>출생 시간</Text>',
        '<Text style={styles.label}>{t("birthInput.birthTime")}</Text>',
        "birth: time label",
    ),
    (
        '<Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>시간을 몰라요</Text>',
        '<Text style={{ fontSize: 13, color: colors.textMuted, marginRight: 6 }}>{t("birthInput.unknownTime")}</Text>',
        "birth: unknown toggle",
    ),
    (
        '          {unknownTime ? "시간 모름 (정오 기준)" : `${String(birthTime.getHours()).padStart(2, "0")}시 ${String(birthTime.getMinutes()).padStart(2, "0")}분`}',
        '          {unknownTime ? t("birthInput.timeUnknown") : formatPickerTime(birthTime)}',
        "birth: time display",
    ),
    (
        '<Text style={styles.label}>출생지</Text>',
        '<Text style={styles.label}>{t("birthInput.birthCity")}</Text>',
        "birth: city label",
    ),
    (
        '<Text style={styles.label}>출생지 타임존 (Timezone)</Text>',
        '<Text style={styles.label}>{t("birthInput.birthTimezone")}</Text>',
        "birth: timezone label",
    ),
    (
        '            * 정확한 경도는 시스템이 타임존을 기준으로 자동 계산합니다.\n',
        '            {t("birthInput.timezoneHint")}\n',
        "birth: timezone hint",
    ),
    (
        '<Text style={styles.label}>성별</Text>',
        '<Text style={styles.label}>{t("birthInput.gender")}</Text>',
        "birth: gender label",
    ),
    (
        '<Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>남성</Text>',
        '<Text style={[styles.genderText, gender === "M" && styles.genderTextActive]}>{t("birthInput.male")}</Text>',
        "birth: male",
    ),
    (
        '<Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>여성</Text>',
        '<Text style={[styles.genderText, gender === "F" && styles.genderTextActive]}>{t("birthInput.female")}</Text>',
        "birth: female",
    ),
    (
        '<Text style={styles.nextBtnText}>결과 보기</Text>',
        '<Text style={styles.nextBtnText}>{t("birthInput.submit")}</Text>',
        "birth: submit",
    ),
    (
        '      Alert.alert("오류", "저장에 실패했습니다. 입력값을 확인해주세요.");',
        '      Alert.alert(t("common.notice"), t("birthInput.saveFailed"));',
        "birth: alert",
    ),
]


# ============================================================
# CityPickerModal.tsx
# ============================================================
CITY_PATCHES = [
    (
        'import { CITY_LIST } from "@/constants/cities";\n',
        'import { CITY_LIST } from "@/constants/cities";\n'
        'import { useT } from "@/i18n";\n',
        "city: import useT",
    ),
    (
        'export function CityPickerModal({ visible, onClose, onSelect, currentCityKey }: Props) {\n'
        '  const [search, setSearch] = useState("");\n',
        'export function CityPickerModal({ visible, onClose, onSelect, currentCityKey }: Props) {\n'
        '  const [search, setSearch] = useState("");\n'
        '  const t = useT();\n',
        "city: hook",
    ),
    (
        '<Text style={styles.title}>출생지 선택</Text>',
        '<Text style={styles.title}>{t("cityModal.title")}</Text>',
        "city: title",
    ),
    (
        '<Text style={styles.closeText}>닫기</Text>',
        '<Text style={styles.closeText}>{t("common.close")}</Text>',
        "city: close",
    ),
    (
        'placeholder="도시 이름 검색 (예: 서울, New York)"',
        'placeholder={t("cityModal.placeholder")}',
        "city: placeholder",
    ),
    (
        '+ 내 도시가 없나요? (직접 입력)',
        '{t("cityModal.customCta")}',
        "city: customCta",
    ),
    (
        'ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>검색 결과가 없습니다.</Text>}',
        'ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>{t("cityModal.noResults")}</Text>}',
        "city: noResults",
    ),
]


# ============================================================
# TimezonePickerModal.tsx
# ============================================================
TZ_PATCHES = [
    (
        'import { TIMEZONE_LIST } from "@/constants/timezones";\n',
        'import { TIMEZONE_LIST } from "@/constants/timezones";\n'
        'import { useT } from "@/i18n";\n',
        "tz: import useT",
    ),
    (
        'export function TimezonePickerModal({ visible, onClose, onSelect, currentTz }: Props) {\n'
        '  const [search, setSearch] = useState("");\n',
        'export function TimezonePickerModal({ visible, onClose, onSelect, currentTz }: Props) {\n'
        '  const [search, setSearch] = useState("");\n'
        '  const t = useT();\n',
        "tz: hook",
    ),
    (
        '<Text style={styles.title}>타임존 선택</Text>',
        '<Text style={styles.title}>{t("timezoneModal.title")}</Text>',
        "tz: title",
    ),
    (
        '<Text style={styles.closeText}>닫기</Text>',
        '<Text style={styles.closeText}>{t("common.close")}</Text>',
        "tz: close",
    ),
    (
        'placeholder="도시 또는 타임존 검색 (예: 모스크바)"',
        'placeholder={t("timezoneModal.placeholder")}',
        "tz: placeholder",
    ),
    (
        'ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>검색 결과가 없습니다.</Text>}',
        'ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>{t("timezoneModal.noResults")}</Text>}',
        "tz: noResults",
    ),
]


def main() -> int:
    print("[step6] birth-input + city modal + timezone modal + i18n helpers")
    print("=" * 62)
    append_i18n_helpers()
    print("-" * 62)
    for label, target, patches in [
        ("birth-input", "frontend/app/birth-input.tsx", BIRTH_PATCHES),
        ("city modal", "frontend/src/components/CityPickerModal.tsx", CITY_PATCHES),
        ("timezone modal", "frontend/src/components/TimezonePickerModal.tsx", TZ_PATCHES),
    ]:
        print(f"[{label}] {target}")
        a, s = apply_patches(target, patches)
        print(f"  결과: 적용 {a} / 건너뜀 {s}")
    print_footer("step6", "i18n(step6): birth-input + 모달 + date/time helpers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
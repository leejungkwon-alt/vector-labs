// frontend/src/components/sections/MbtiContrastCard.tsx
//
// 사주 × MBTI 대조 카드 (결과 상단 1장).
// ⚠️ 서버가 MBTI 유형을 추정하지 않는다. 사용자가 입력한 값과 사주 결을
//    대조해 outward|inward|balanced 중 하나만 보여준다.
// ⚠️ '재미로 보는 대조' 고지는 항상 표시한다(입력 전 CTA 에서도).
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { useT } from "@/i18n";
import type { MbtiContrastSection } from "../../../types";

type Props = {
  section?: MbtiContrastSection | null;
  onPressInput: () => void;
  onPressUpgrade: () => void;
};

function labelEmoji(label?: string) {
  if (label === "outward") return "↗";
  if (label === "inward") return "↘";
  return "≈";
}

export function MbtiContrastCard({ section, onPressInput, onPressUpgrade }: Props) {
  const t = useT();

  // ---- MBTI 미입력: 입력 CTA (고지는 그대로 상시 표시) ----
  if (!section) {
    return (
      <View style={styles.card}>
        <Text style={styles.kicker}>{t("mbtiContrast.kicker")}</Text>
        <Text style={styles.ctaTitle}>{t("mbtiContrast.ctaTitle")}</Text>
        <Text style={styles.ctaBody}>{t("mbtiContrast.ctaBody")}</Text>
        <TouchableOpacity style={styles.ctaButton} onPress={onPressInput} accessibilityRole="button">
          <Text style={styles.ctaButtonText}>{t("mbtiContrast.ctaButton")}</Text>
        </TouchableOpacity>
        <Text style={styles.disclaimer}>{t("mbtiContrast.disclaimer")}</Text>
      </View>
    );
  }

  const isLocked = !!(section.locked_fields && section.locked_fields.length > 0);

  return (
    <View style={styles.card}>
      <Text style={styles.kicker}>{t("mbtiContrast.kicker")}</Text>

      <View style={styles.badgeRow}>
        <View style={styles.typeBadge}>
          <Text style={styles.typeBadgeText}>{section.mbti}</Text>
        </View>
        {/* 공식 검사 오해 금지 표기 */}
        <Text style={styles.styleNote}>{section.mbti_style_note || t("mbtiContrast.styleNote")}</Text>
      </View>

      <Text style={styles.linkHeadline}>
        {labelEmoji(section.label)} {section.link_headline || section.label_title || ""}
      </Text>
      {!!section.summary && <Text style={styles.summary}>{section.summary}</Text>}
      {!!section.day_stem_overlay && <Text style={styles.overlay}>{section.day_stem_overlay}</Text>}
      {/* 시각 미상(정오 가정) — 시간 의존 신호를 뺐다는 한 줄 안내 */}
      {section.hour_signals_excluded && (
        <Text style={styles.hourHint}>{t("mbtiContrast.hourUnknown")}</Text>
      )}
      {!!section.hourly_notice && <Text style={styles.hourly}>{section.hourly_notice}</Text>}

      {/* 상세 슬롯(프리미엄) — 무료는 잠금 안내 */}
      {isLocked && (
        <TouchableOpacity style={styles.lockBox} onPress={onPressUpgrade} accessibilityRole="button">
          <Text style={styles.lockText}>{t("mbtiContrast.unlockDetail")}</Text>
        </TouchableOpacity>
      )}
      {!isLocked && (section.detail_slots || []).length > 0 && (
        <View style={{ marginTop: spacing.sm }}>
          {section.detail_slots!.map((slot) => (
            <View key={slot.key} style={{ marginBottom: spacing.sm }}>
              <Text style={styles.slotTitle}>{slot.title}</Text>
              <Text style={styles.slotBody}>{slot.body}</Text>
            </View>
          ))}
        </View>
      )}

      {/* '재미로 보는 대조' 고지 상시 표시 */}
      <Text style={styles.disclaimer}>{section.disclaimer || t("mbtiContrast.disclaimer")}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    margin: spacing.lg, marginBottom: 0, padding: spacing.md,
    backgroundColor: colors.surface, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border,
  },
  kicker: { fontSize: 12, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  badgeRow: { flexDirection: "row", alignItems: "center", marginBottom: 8, flexWrap: "wrap" },
  typeBadge: {
    backgroundColor: colors.primarySoft, paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: radius.pill, marginRight: 8,
  },
  typeBadgeText: { fontWeight: "800", color: colors.primary, fontSize: 14 },
  styleNote: { fontSize: 11, color: colors.textMuted, flexShrink: 1 },
  linkHeadline: { fontSize: 17, fontWeight: "800", color: colors.text, marginBottom: 6 },
  summary: { fontSize: 14, color: colors.text, lineHeight: 21, marginBottom: 6 },
  overlay: { fontSize: 13, color: colors.textMuted, lineHeight: 19, marginBottom: 6 },
  hourly: { fontSize: 12, color: colors.textMuted, marginBottom: 6 },
  hourHint: { fontSize: 12, color: colors.textMuted, lineHeight: 18, marginBottom: 6 },
  lockBox: {
    marginTop: spacing.sm, padding: spacing.sm, backgroundColor: colors.bgElevated,
    borderRadius: radius.md, borderWidth: 1, borderColor: colors.border,
  },
  lockText: { fontSize: 13, color: colors.primary, fontWeight: "700" },
  slotTitle: { fontSize: 14, fontWeight: "700", color: colors.text, marginBottom: 2 },
  slotBody: { fontSize: 13, color: colors.text, lineHeight: 20 },
  ctaTitle: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: 4 },
  ctaBody: { fontSize: 13, color: colors.textMuted, lineHeight: 19, marginBottom: spacing.sm },
  ctaButton: { backgroundColor: colors.primary, paddingVertical: 10, borderRadius: radius.md, alignItems: "center" },
  ctaButtonText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  disclaimer: { fontSize: 11, color: colors.textMuted, marginTop: spacing.sm, lineHeight: 16 },
});

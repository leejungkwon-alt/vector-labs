// frontend/src/components/sections/shared.tsx
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "@/theme";
import { useLanguageStore } from "@/store/languageStore";
import { useT } from "@/i18n";
import type { CompatibilityAdvice } from "../../../types";

// 섹션 공통 스타일 — 각 렌더러가 import 해서 사용
export const ss = StyleSheet.create({
  paragraph: { fontSize: 15, color: colors.text, lineHeight: 24, marginBottom: 12, flexShrink: 1, width: "100%" },
  blockBox: {
    backgroundColor: colors.bg,
    padding: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  blockTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 6, flexShrink: 1 },
  coreHero: { fontSize: 18, fontWeight: "700", color: colors.text, lineHeight: 26, marginVertical: 10 },
  adviceText: { fontSize: 14, color: colors.primary, fontWeight: "600", marginTop: 8 },
  metaText: { fontSize: 13, color: colors.textMuted, marginBottom: 4 },
  tagRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 6, marginBottom: 8 },
  tag: {
    backgroundColor: colors.primarySoft,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radius.pill,
    fontSize: 12,
    color: colors.primary,
    fontWeight: "600",
    overflow: "hidden",
  },
});

// ============================================================
// LockedHint — 유료 잠금 안내 카드 (기존 home.tsx 에서 이동)
// ============================================================
export function LockedHint({ onPress }: { onPress: () => void }) {
  const t = useT();
  return (
    <View style={sharedStyles.lockedCard}>
      <BlurView intensity={30} tint="light" style={StyleSheet.absoluteFill} />
      <View style={sharedStyles.lockedContent}>
        <Ionicons name="sparkles" size={20} color={colors.primary} />
        <Text style={sharedStyles.lockedText}>
          {t("home.unlockHint")}
        </Text>
        <TouchableOpacity style={sharedStyles.upgradeBtn} onPress={onPress}>
          <Text style={sharedStyles.upgradeBtnText}>{t("home.viewFullReport")}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// ============================================================
// CompatBox — Mode/Premium 섹션 공용 케미 상자
// ============================================================

const useFormatMode = () => {
  const lang = useLanguageStore((s) => s.lang);
  return (m: string) => {
    if (!m || !m.startsWith("THE_")) return m;
    const entry = MODE_LABELS[m];
    if (!entry) return m;
    return lang === "ko" ? entry.ko : entry.en;
  };
};


const MODE_LABELS: Record<string, { ko: string, en: string }> = {
  THE_PIONEER: { ko: "거목 (Pioneer)", en: "Pioneer" },
  THE_ADAPTER: { ko: "덩굴 (Adapter)", en: "Adapter" },
  THE_RADIATOR: { ko: "태양 (Radiator)", en: "Radiator" },
  THE_KEEPER: { ko: "등불 (Keeper)", en: "Keeper" },
  THE_ANCHOR: { ko: "산 (Anchor)", en: "Anchor" },
  THE_CULTIVATOR: { ko: "정원 (Cultivator)", en: "Cultivator" },
  THE_BLADE: { ko: "칼날 (Blade)", en: "Blade" },
  THE_GEM: { ko: "보석 (Gem)", en: "Gem" },
  THE_DEEP: { ko: "바다 (Deep)", en: "Deep" },
  THE_SPRING: { ko: "샘 (Spring)", en: "Spring" },
  THE_STEWARD: { ko: "관리자 (Steward)", en: "Steward" },
  THE_OPERATOR: { ko: "운영자 (Operator)", en: "Operator" },
  THE_FLOW: { ko: "흐름 (Flow)", en: "Flow" },
  THE_CREATOR: { ko: "창작자 (Creator)", en: "Creator" },
  THE_CHALLENGER: { ko: "도전자 (Challenger)", en: "Challenger" },
  THE_OFFICER: { ko: "원칙주의자 (Officer)", en: "Officer" },
  THE_SURVIVOR: { ko: "생존자 (Survivor)", en: "Survivor" },
  THE_MYSTIC: { ko: "탐구자 (Mystic)", en: "Mystic" },
  THE_MENTOR: { ko: "멘토 (Mentor)", en: "Mentor" },
  THE_GENERALIST: { ko: "올라운더 (Generalist)", en: "Generalist" },
  THE_TWIN: { ko: "동반자 (Twin)", en: "Twin" },
  THE_RIVAL: { ko: "경쟁자 (Rival)", en: "Rival" },
  THE_ALLY: { ko: "조력자 (Ally)", en: "Ally" },
  THE_EMPATH: { ko: "공감자 (Empath)", en: "Empath" },
};

export function CompatBox({ compat }: { compat?: CompatibilityAdvice }) {
  const t = useT();
  const formatMode = useFormatMode();
  if (!compat) return null;
  return (
    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.bg, borderRadius: radius.md }}>
      <Text style={ss.blockTitle}>{t("sections.compatibility")}</Text>
      <Text style={ss.paragraph}>{t("sections.bestMatch")}: {(compat.best_match || []).map(formatMode).join(", ")}</Text>
      <Text style={ss.metaText}>{compat.best_reason}</Text>
      <Text style={[ss.paragraph, { marginTop: 6 }]}>
        {t("sections.challengingMatch")}: {(compat.challenging_match || []).map(formatMode).join(", ")}
      </Text>
      <Text style={ss.metaText}>{compat.challenging_reason}</Text>
    </View>
  );
}

// ============================================================
// RedFlagsBox — Mode/Premium 섹션 공용 주의사항 상자
// ============================================================
export function RedFlagsBox({ flags }: { flags?: string[] }) {
  const t = useT();
  if (!flags || flags.length === 0) return null;
  return (
    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.dangerSoft, borderRadius: radius.md }}>
      <Text style={[ss.blockTitle, { color: colors.danger }]}>{t("sections.redFlags")}</Text>
      {flags.map((r, i) => (
        <Text key={i} style={ss.paragraph}>⚠ {r}</Text>
      ))}
    </View>
  );
}

const sharedStyles = StyleSheet.create({
  lockedCard: {
    marginTop: 16,
    borderRadius: radius.md,
    overflow: "hidden",
    borderWidth: 1,
    borderStyle: "dashed",
    borderColor: colors.primarySoft,
    backgroundColor: colors.primarySoft,
  },
  lockedContent: { padding: 16, alignItems: "center", gap: 8 },
  lockedText: { fontSize: 14, color: colors.text, fontWeight: "600", textAlign: "center" },
  upgradeBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: radius.sm,
    marginTop: 4,
  },
  upgradeBtnText: { color: colors.onPrimary, fontSize: 14, fontWeight: "700" },
});

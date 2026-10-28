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
    return entry[lang as keyof typeof entry] || entry.en;
  };
};

const MODE_LABELS: Record<string, { ko: string, en: string, ja: string, zh_cn: string, es: string }> = {
  THE_PIONEER:    { ko: "거목",       en: "Pioneer",    ja: "大木",         zh_cn: "先锋",     es: "Pionero" },
  THE_ADAPTER:    { ko: "덩굴",       en: "Adapter",    ja: "蔦",           zh_cn: "适应者",   es: "Adaptador" },
  THE_RADIATOR:   { ko: "태양",       en: "Radiator",   ja: "太陽",         zh_cn: "太阳",     es: "Radiador" },
  THE_KEEPER:     { ko: "등불",       en: "Keeper",     ja: "灯火",         zh_cn: "守灯人",   es: "Linterna" },
  THE_ANCHOR:     { ko: "산",         en: "Anchor",     ja: "山",           zh_cn: "锚",       es: "Ancla" },
  THE_CULTIVATOR: { ko: "정원",       en: "Cultivator", ja: "庭",           zh_cn: "耕耘者",   es: "Cultivador" },
  THE_BLADE:      { ko: "칼날",       en: "Blade",      ja: "刃",           zh_cn: "刀刃",     es: "Filo" },
  THE_GEM:        { ko: "보석",       en: "Gem",        ja: "宝石",         zh_cn: "宝石",     es: "Gema" },
  THE_DEEP:       { ko: "바다",       en: "Deep",       ja: "海",           zh_cn: "深海",     es: "Profundo" },
  THE_SPRING:     { ko: "샘",         en: "Spring",     ja: "泉",           zh_cn: "泉水",     es: "Manantial" },
  THE_STEWARD:    { ko: "관리자",     en: "Steward",    ja: "管理人",       zh_cn: "管家",     es: "Administrador" },
  THE_OPERATOR:   { ko: "운영자",     en: "Operator",   ja: "運営者",       zh_cn: "运营者",   es: "Operador" },
  THE_FLOW:       { ko: "흐름",       en: "Flow",       ja: "流れ",         zh_cn: "流动型",   es: "Flujo" },
  THE_CREATOR:    { ko: "창작자",     en: "Creator",    ja: "創造者",       zh_cn: "创作者",   es: "Creador" },
  THE_CHALLENGER: { ko: "도전자",     en: "Challenger", ja: "挑戦者",       zh_cn: "挑战者",   es: "Desafiante" },
  THE_OFFICER:    { ko: "원칙주의자", en: "Officer",    ja: "原理主義者",   zh_cn: "管理者",   es: "Guardián" },
  THE_SURVIVOR:   { ko: "생존자",     en: "Survivor",   ja: "生存者",       zh_cn: "幸存者",   es: "Superviviente" },
  THE_MYSTIC:     { ko: "탐구자",     en: "Mystic",     ja: "探究者",       zh_cn: "神秘主义者", es: "Místico" },
  THE_MENTOR:     { ko: "멘토",       en: "Mentor",     ja: "メンター",     zh_cn: "导师",     es: "Mentor" },
  THE_GENERALIST: { ko: "올라운더",   en: "Generalist", ja: "オールラウンダー", zh_cn: "通才",   es: "Generalista" },
  THE_TWIN:       { ko: "동반자",     en: "Twin",       ja: "相棒",         zh_cn: "同伴者",   es: "Compañero" },
  THE_RIVAL:      { ko: "경쟁자",     en: "Rival",      ja: "ライバル",     zh_cn: "竞争对手", es: "Rival" },
  THE_ALLY:       { ko: "조력자",     en: "Ally",       ja: "味方",         zh_cn: "盟友",     es: "Aliado" },
  THE_EMPATH:     { ko: "공감자",     en: "Empath",     ja: "共感者",       zh_cn: "共情者",   es: "Empático" },
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

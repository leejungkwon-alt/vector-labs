import { useLanguageStore } from "@/store/languageStore"; // SAJU-PATCH:api-lang
import { useT } from "@/i18n";
// frontend/app/(tabs)/home.tsx
import { useQuery } from "@tanstack/react-query";
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useEffect, useState } from "react";

import { api, ApiError } from "@/api/client";
import { colors, spacing, radius } from "@/theme";
import { useProfileStore } from "@/store/profileStore";
import type { ReportResponse } from "../../types";
import {
  ChartSectionView,
  CoreSectionView,
  EnergySectionView,
  LuckyCodeSectionView,
  HealthSectionView,
  ModeSectionView,
  PremiumSectionView,
  TimelineSectionView,
  MonthlySectionView,
  SinsalSectionView,
  AgeBandSectionView,
  YearSectionView,
  LockedHint,
} from "@/components/sections";

function renderSection(key: string, sec: any) {
  switch (key) {
    case "chart":      return <ChartSectionView section={sec} />;
    case "core":       return <CoreSectionView section={sec} />;
    case "energy":     return <EnergySectionView section={sec} />;
    case "lucky_code": return <LuckyCodeSectionView section={sec} />;
    case "health":     return <HealthSectionView section={sec} />;
    case "money":
    case "work":
    case "bonds":      return <ModeSectionView section={sec} />;
    case "love":
    case "career":
    case "wealth":     return <PremiumSectionView section={sec} />;
    case "timeline":   return <TimelineSectionView section={sec} />;
    case "monthly":    return <MonthlySectionView section={sec} />;
    case "sinsal":     return <SinsalSectionView section={sec} />;
    case "age_band":   return <AgeBandSectionView section={sec} />;
    case "year":       return <YearSectionView section={sec} />;
    default:           return null;
  }
}

export default function HomeScreen() {
  const lang = useLanguageStore((s) => s.lang); // SAJU-PATCH:lang-decl
  const t = useT();
  const profile = useProfileStore((s) => s.profile);
  const profileReady = useProfileStore((s) => s.ready);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ core: true });

  useEffect(() => {
    if (profileReady && !profile) {
      router.replace("/birth-input");
    }
  }, [profileReady, profile]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["report", profile, lang],
    queryFn: () =>
      api.report({ ...profile, target_year: new Date().getFullYear(), lang }),
    enabled: !!profile,
    retry: false,
  });

  const toggleSection = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const goToUpgrade = () => {
    router.push("/(tabs)/settings");
  };

  if (!profileReady || !profile) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }
  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>{t("home.loading")}</Text>
      </View>
    );
  }
  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>
          {error instanceof ApiError ? error.detail : (error as Error).message}
        </Text>
      </View>
    );
  }

  const report = data?.report as ReportResponse["report"];
  if (!report) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      {/* Cover */}
      <View style={styles.cover}>
        <Text style={styles.coverSymbol}>{report.cover.archetype.symbol}</Text>
        <Text style={styles.coverTitle}>{report.cover.archetype.name}</Text>
        <Text style={styles.coverTagline}>{report.cover.archetype.tagline}</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{report.cover.intensity_label}</Text>
        </View>
      </View>

      {/* Summary Cards */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t("home.summary")}</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
          {report.summary_cards.map((card: any, idx: number) => (
            <View key={idx} style={[styles.summaryCard, card.locked && styles.summaryCardLocked]}>
              <Text style={styles.cardLabel}>{card.label}</Text>
              <Text style={styles.cardHeadline}>{card.headline}</Text>
              {card.locked && (
                <View style={styles.miniLock}>
                  <Ionicons name="lock-closed" size={12} color={colors.textMuted} />
                </View>
              )}
            </View>
          ))}
        </ScrollView>
      </View>

      {/* Dynamic Sections (Accordion + Dispatch) */}
      <View style={{ paddingHorizontal: spacing.lg }}>
        {Object.entries(report.sections).map(([key, sec]) => {
          if (!sec || !sec.title) return null;
          const isOpen = expanded[key] || false;
          const isLocked = !!sec.locked_fields && sec.locked_fields.length > 0;

          return (
            <View key={key} style={styles.accordion}>
              <TouchableOpacity
                style={styles.accordionHeader}
                onPress={() => toggleSection(key)}
              >
                <Text style={styles.accordionTitle}>{sec.title}</Text>
                <Ionicons
                  name={isOpen ? "chevron-up" : "chevron-down"}
                  size={20}
                  color={colors.textMuted}
                />
              </TouchableOpacity>

              {isOpen && (
                <View style={styles.accordionContent}>
                  {renderSection(key, sec)}
                  {isLocked && <LockedHint onPress={goToUpgrade} />}
                </View>
              )}
            </View>
          );
        })}
      </View>

      <View style={styles.disclaimerBox}>
        <Text style={styles.disclaimerText}>{report.disclaimer}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg, padding: spacing.lg },
  loadingText: { marginTop: spacing.md, fontSize: 16, color: colors.textMuted },
  errorText: { fontSize: 16, color: colors.danger, textAlign: "center" },
  container: { flex: 1, backgroundColor: colors.bg },

  cover: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  coverSymbol: { fontSize: 48, marginBottom: spacing.sm },
  coverTitle: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: spacing.xs },
  coverTagline: { fontSize: 16, color: colors.textMuted, textAlign: "center", marginBottom: spacing.md },
  badge: {
    backgroundColor: colors.primarySoft,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: radius.pill,
  },
  badgeText: { color: colors.primary, fontWeight: "700", fontSize: 14 },

  section: { padding: spacing.lg },
  sectionTitle: { fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: spacing.md },

  summaryCard: {
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: radius.md,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
    width: 160,
    position: "relative",
  },
  summaryCardLocked: { backgroundColor: colors.bgElevated, borderColor: colors.border },
  miniLock: { position: "absolute", top: 8, right: 8 },
  cardLabel: { fontSize: 12, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  cardHeadline: { fontSize: 16, fontWeight: "700", color: colors.text },

  accordion: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: "hidden",
  },
  accordionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: spacing.md,
  },
  accordionTitle: { fontSize: 18, fontWeight: "700", color: colors.text, flexShrink: 1, marginRight: 10 },
  accordionContent: {
    padding: spacing.md,
    paddingTop: 0,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },

  disclaimerBox: {
    margin: spacing.lg,
    padding: spacing.md,
    backgroundColor: colors.bgMuted,
    borderRadius: radius.md,
  },
  disclaimerText: { fontSize: 12, color: colors.textMuted, lineHeight: 18 },
});

import { useLanguageStore } from "@/store/languageStore";
import { useT } from "@/i18n";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { router, useFocusEffect } from "expo-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { View, Text, ScrollView, ActivityIndicator, StyleSheet, TouchableOpacity } from "react-native";
import { api, ApiError } from "@/api/client";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore, refreshUser } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { usePoemStore } from "@/store/poemStore";
import { CrisisBanner } from "@/components/CrisisBanner";
import type { ReportResponse } from "../../types";
import {
  ChartSectionView, CoreSectionView, EnergySectionView, LuckyCodeSectionView,
  HealthSectionView, ModeSectionView, PremiumSectionView, TimelineSectionView,
  MonthlySectionView, SinsalSectionView, AgeBandSectionView, YearSectionView, LockedHint,
  MbtiContrastCard,
} from "@/components/sections";

function renderSection(key: string, sec: any) {
  switch (key) {
    case "chart": return <ChartSectionView section={sec} />;
    case "core": return <CoreSectionView section={sec} />;
    case "energy": return <EnergySectionView section={sec} />;
    case "lucky_code": return <LuckyCodeSectionView section={sec} />;
    case "health": return <HealthSectionView section={sec} />;
    case "money": case "work": case "bonds": return <ModeSectionView section={sec} />;
    case "love": case "career": case "wealth": return <PremiumSectionView section={sec} />;
    case "timeline": return <TimelineSectionView section={sec} />;
    case "monthly": return <MonthlySectionView section={sec} />;
    case "sinsal": return <SinsalSectionView section={sec} />;
    case "age_band": return <AgeBandSectionView section={sec} />;
    case "year": return <YearSectionView section={sec} />;
    default: return null;
  }
}

export default function HomeScreen() {
  const lang = useLanguageStore((s) => s.lang);
  const t = useT();
  const profile = useProfileStore((s) => s.profile);
  const profileReady = useProfileStore((s) => s.ready);
  const ready = useAuthStore((s) => s.ready);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ core: true });
  // 1회권(크레딧)을 이번 세션에서 이미 리포트 생성에 사용했는지 (재요청 방지)
  const [creditUsed, setCreditUsed] = useState(false);
  const showingCreditRef = useRef(false);
  const setCurrentPoem = usePoemStore((s) => s.setCurrentPoem);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (profileReady && !profile) {
      router.replace("/birth-input");
    }
  }, [profileReady, profile]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["report", profile, lang, ready, creditUsed],
    queryFn: () => api.report({ ...{
          birth_date: profile.birth_date,
          birth_time: profile.birth_time || undefined,
          birth_time_mode: profile.birth_time_mode || "exact",
          timezone_str: profile.timezone_str || "Asia/Seoul",
          longitude: profile.longitude ?? 126.978,
          correction_mode: profile.correction_mode || "lmt",
          jasi_boundary: profile.jasi_boundary ?? 23,
          gender: profile.gender || "M",
          birth_location: profile.birth_location || undefined,
        }, use_current_solar_year: true, lang }),
    enabled: !!profile && profileReady && ready,
    retry: false,
  });

  // 🆕 리포트 데이터 로드 완료 후 크레딧(이용권) 잔액 갱신
  //    - 화면에 1회권으로 열린 리포트가 떠 있으면 이미 차감된 상태이므로,
  //      위처럼 재요청(재차감)하지 않고 유저 정보만 새로고침한다.
  useEffect(() => {
    if (!data?.report) return;
    const creditUsedNow = (data.report as any).meta?.credit_used === true;

    if (creditUsedNow && !showingCreditRef.current) {
      // 쿼리 키를 바꿔 캐시를 고정 → 같은 리포트가 자동으로 재요청/재차감되는 것을 방지
      showingCreditRef.current = true;
      setCreditUsed(true);
    }
    refreshUser();
  }, [data]);

  // 💳 결제/복귀 등으로 홈 탭에 다시 들어오면 새로 결제했을 수 있으므로
  //    유저 정보(보유 크레딧)를 새로 받아오고, 상태가 바뀌었으면 리포트를 다시 불러와
  //    잠겨 있던 콘텐츠가 열리도록 한다.
  useFocusEffect(
    useCallback(() => {
      let cancelled = false;
      (async () => {
        const before = useAuthStore.getState().user;
        const after = await refreshUser();
        if (cancelled || !after || !before) return;
        // 이미 1회권 리포트를 보여준 뒤라면 재요청하지 않는다 (크레딧 재차감 방지)
        if (showingCreditRef.current) return;
        const changed =
          before.tier !== after.tier ||
          (before.onetime_credits ?? 0) !== (after.onetime_credits ?? 0);
        if (changed) await queryClient.invalidateQueries({ queryKey: ["report"] });
      })();
      return () => { cancelled = true; };
    }, [queryClient])
  );

  useEffect(() => {
    if (data?.report?.sections?.lucky_code?.poem) {
      const poem = data.report.sections.lucky_code.poem;
      const collection = (poem as any).collection && (poem as any).collection.length > 0 ? (poem as any).collection : [poem];
      setCurrentPoem(poem, collection);
    }
  }, [data, setCurrentPoem]);

  const toggleSection = (id: string) => setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  const goToUpgrade = () => router.push("/(tabs)/settings");

  if (!profileReady || !profile || !ready) return <View style={styles.center}><ActivityIndicator color={colors.primary} /></View>;
  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /><Text style={styles.loadingText}>{t("home.loading")}</Text></View>;
  if (error) {
    // 422(모순된 생년월일/시각 조합 등)나 기타 오류에서 프로필을 고칠 길이 없으면
    // 화면이 막힌다. 최소한 '생년월일 다시 입력' 경로를 항상 제공한다.
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error instanceof ApiError ? error.detail : (error as Error).message}</Text>
        <TouchableOpacity style={styles.recoverButton} onPress={() => router.replace("/birth-input")} accessibilityRole="button">
          <Text style={styles.recoverButtonText}>{t("home.reenterBirth")}</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const report = data?.report as ReportResponse["report"];
  if (!report) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 150 }}>
      <View style={styles.cover}>
        <Text style={styles.coverSymbol}>{report.cover.archetype.symbol}</Text>
        <Text style={styles.coverTitle}>{report.cover.archetype.name}</Text>
        <Text style={styles.coverTagline}>{report.cover.archetype.tagline}</Text>
        <View style={styles.badge}><Text style={styles.badgeText}>{report.cover.intensity_label}</Text></View>
      </View>

      {/* 사주 × MBTI 대조 카드 — 결과 상단 1장. 미입력이면 입력 CTA. */}
      <MbtiContrastCard
        section={(report.sections as any)?.mbti_contrast ?? null}
        onPressInput={() => router.push("/birth-input")}
        onPressUpgrade={goToUpgrade}
      />

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t("home.summary")}</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
          {report.summary_cards.map((card: any, idx: number) => (
            <View key={idx} style={[styles.summaryCard, card.locked && styles.summaryCardLocked]}>
              <Text style={styles.cardLabel}>{card.label}</Text>
              <Text style={styles.cardHeadline}>{card.headline}</Text>
              {card.locked && <View style={styles.miniLock}><Text style={{ fontSize: 12 }}></Text></View>}
            </View>
          ))}
        </ScrollView>
      </View>

      <View style={{ paddingHorizontal: spacing.lg }}>
        {Object.entries(report.sections).map(([key, sec]) => {
          if (!sec || !sec.title) return null;
          const isOpen = expanded[key] || false;
          const isLocked = !!sec.locked_fields && sec.locked_fields.length > 0;
          return (
            <View key={key} style={styles.accordion}>
              <TouchableOpacity style={styles.accordionHeader} onPress={() => toggleSection(key)}>
                <Text style={styles.accordionTitle}>{sec.title}</Text>
                <Text style={{ fontSize: 16, color: colors.textMuted }}>{isOpen ? "▲" : "▼"}</Text>
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
      <CrisisBanner crisis={(report as any).crisis_resources} />
      <View style={styles.disclaimerBox}><Text style={styles.disclaimerText}>{report.disclaimer}</Text></View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg, padding: spacing.lg },
  loadingText: { marginTop: spacing.md, fontSize: 16, color: colors.textMuted },
  errorText: { fontSize: 16, color: colors.danger, textAlign: "center" },
  recoverButton: { marginTop: spacing.lg, backgroundColor: colors.primary, paddingVertical: 12, paddingHorizontal: 20, borderRadius: radius.md },
  recoverButtonText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  container: { flex: 1, backgroundColor: colors.bg },
  cover: { backgroundColor: colors.surface, padding: spacing.xl, alignItems: "center", borderBottomWidth: 1, borderBottomColor: colors.border },
  coverSymbol: { fontSize: 48, marginBottom: spacing.sm },
  coverTitle: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: spacing.xs },
  coverTagline: { fontSize: 16, color: colors.textMuted, textAlign: "center", marginBottom: spacing.md },
  badge: { backgroundColor: colors.primarySoft, paddingHorizontal: 12, paddingVertical: 6, borderRadius: radius.pill },
  badgeText: { color: colors.primary, fontWeight: "700", fontSize: 14 },
  section: { padding: spacing.lg },
  sectionTitle: { fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  summaryCard: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, marginRight: spacing.sm, borderWidth: 1, borderColor: colors.border, width: 160, position: "relative" },
  summaryCardLocked: { backgroundColor: colors.bgElevated, borderColor: colors.border },
  miniLock: { position: "absolute", top: 8, right: 8 },
  cardLabel: { fontSize: 12, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  cardHeadline: { fontSize: 16, fontWeight: "700", color: colors.text },
  accordion: { backgroundColor: colors.surface, borderRadius: radius.md, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  accordionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: spacing.md },
  accordionTitle: { fontSize: 18, fontWeight: "700", color: colors.text, flexShrink: 1, marginRight: 10 },
  accordionContent: { padding: spacing.md, paddingTop: 0, borderTopWidth: 1, borderTopColor: colors.border },
  disclaimerBox: { margin: spacing.lg, padding: spacing.md, backgroundColor: colors.bgMuted, borderRadius: radius.md },
  disclaimerText: { fontSize: 12, color: colors.textMuted, lineHeight: 18 },
});

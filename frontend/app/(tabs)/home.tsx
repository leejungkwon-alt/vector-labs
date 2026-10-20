import { useQuery } from "@tanstack/react-query";
import { View, Text, ScrollView, ActivityIndicator, StyleSheet, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import { api, ApiError } from "@/api/client";
import { colors, spacing, radius } from "@/theme";
import { useProfileStore } from "@/store/profileStore";
import type { ReportResponse } from "../../types";
import { useEffect, useState } from "react";
import { Ionicons } from "@expo/vector-icons";
import { BlurView } from "expo-blur";

function LockedHint({ onPress }: { onPress: () => void }) {
  return (
    <View style={styles.lockedCard}>
      <BlurView intensity={30} tint="light" style={StyleSheet.absoluteFill} />
      <View style={styles.lockedContent}>
        <Ionicons name="sparkles" size={20} color={colors.primary} />
        <Text style={styles.lockedText}>
          더 깊은 분석과 맞춤 인사이트가 준비되어 있어요.
        </Text>
        <TouchableOpacity style={styles.upgradeBtn} onPress={onPress}>
          <Text style={styles.upgradeBtnText}>전체 리포트 보기</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function HomeScreen() {
  const profile = useProfileStore((s) => s.profile);
  const profileReady = useProfileStore((s) => s.ready);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ core: true });

  useEffect(() => {
    if (profileReady && !profile) {
      router.replace("/birth-input");
    }
  }, [profileReady, profile]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["report", profile],
    queryFn: () => api.report({ ...profile, target_year: new Date().getFullYear(), lang: "ko" }),
    enabled: !!profile,
    retry: false,
  });

  const toggleSection = (id: string) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const goToUpgrade = () => {
    router.push("/(tabs)/settings");
  };

  if (!profileReady || !profile) return <View style={styles.center}><ActivityIndicator color={colors.primary} /></View>;
  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /><Text style={styles.loadingText}>인생 설계도를 분석 중입니다...</Text></View>;
  if (error) return <View style={styles.center}><Text style={styles.errorText}>{error instanceof ApiError ? error.detail : (error as Error).message}</Text></View>;

  const report = data?.report as ReportResponse["report"];
  if (!report) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      {/* Cover */}
      <View style={styles.cover}>
        <Text style={styles.coverSymbol}>{report.cover.archetype.symbol}</Text>
        <Text style={styles.coverTitle}>{report.cover.archetype.name}</Text>
        <Text style={styles.coverTagline}>{report.cover.archetype.tagline}</Text>
        <View style={styles.badge}><Text style={styles.badgeText}>{report.cover.intensity_label}</Text></View>
      </View>

      {/* Summary Cards */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>요약</Text>
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

      {/* Dynamic Sections (Accordion) */}
      <View style={{ paddingHorizontal: spacing.lg }}>
        {Object.entries(report.sections).map(([key, sec]: [string, any]) => {
          if (!sec || !sec.title) return null;
          const isOpen = expanded[key] || false;
          const isLocked = sec.locked_fields && sec.locked_fields.length > 0;

          return (
            <View key={key} style={styles.accordion}>
              <TouchableOpacity style={styles.accordionHeader} onPress={() => toggleSection(key)}>
                <Text style={styles.accordionTitle}>{sec.title}</Text>
                <Ionicons name={isOpen ? "chevron-up" : "chevron-down"} size={20} color={colors.textMuted} />
              </TouchableOpacity>
              
              {isOpen && (
                <View style={styles.accordionContent}>
                  
                  {/* Chart */}
                  {key === "chart" && sec.layers && (
                    <View>
                      {sec.hero && <Text style={[styles.paragraph, { fontStyle: "italic", color: colors.primary, marginBottom: 16 }]}>{sec.hero}</Text>}
                      {sec.layers.map((layer: any, i: number) => (
                        <View key={i} style={[styles.blockBox, layer.is_self && { borderColor: colors.primary, borderWidth: 2 }]}>
                          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                            <Text style={styles.blockTitle}>{layer.label} {layer.is_self && "(본질)"}</Text>
                            <Text style={{ fontSize: 14, fontWeight: "700", color: colors.primary }}>{layer.archetype} · {layer.element}</Text>
                          </View>
                          <Text style={{ fontSize: 13, color: colors.textMuted, marginBottom: 6 }}>{layer.role}</Text>
                          <Text style={styles.paragraph}>{layer.narrative}</Text>
                        </View>
                      ))}
                    </View>
                  )}

                  {/* Core (복구된 렌더링) */}
                  {key === "core" && (
                    <View>
                      {sec.hero && <Text style={styles.coreHero}>{sec.hero}</Text>}
                      {sec.narrative && sec.narrative.map((p: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>{p}</Text>
                      ))}
                      {sec.shadows && sec.shadows.map((s: string, i: number) => (
                        <Text key={i} style={[styles.paragraph, { color: colors.danger }]}>그림자: {s}</Text>
                      ))}
                      {sec.advice && sec.advice.map((a: string, i: number) => (
                        <Text key={i} style={[styles.paragraph, { fontWeight: "600" }]}>💡 {a}</Text>
                      ))}
                    </View>
                  )}
                  
                  {/* Energy / Health (blocks) */}
                  {sec.blocks && sec.blocks.map((b: any, i: number) => (
                    <View key={i} style={styles.blockBox}>
                      <Text style={styles.blockTitle}>{b.name}</Text>
                      <Text style={styles.paragraph}>{b.body}</Text>
                    </View>
                  ))}

                  {/* Money / Work / Bonds */}
                  {sec.headline && <Text style={styles.coreHero}>{sec.headline}</Text>}
                  {sec.body && <Text style={styles.paragraph}>{sec.body}</Text>}
                  {sec.advice && <Text style={styles.adviceText}>💡 {sec.advice}</Text>}
                  
                  {/* Lucky Code */}
                  {sec.power && (
                    <View>
                      <Text style={styles.paragraph}>• 핵심 에너지: {sec.power.element}</Text>
                      {sec.power.colors && <Text style={styles.paragraph}>• 추천 색상: {sec.power.colors?.join(", ")}</Text>}
                      {sec.power.numbers && <Text style={styles.paragraph}>• 행운의 숫자: {sec.power.numbers?.join(", ")}</Text>}
                    </View>
                  )}

                  {/* Timeline */}
                  {key === "timeline" && sec.items && sec.items.map((item: any, i: number) => (
                    <View key={i} style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
                      <Text style={{ fontSize: 14, color: colors.text }}>{item.ages[0]}세 ~ {item.ages[1]}세 ({item.pillar})</Text>
                      <Text style={{ fontSize: 14, fontWeight: "700", color: item.grade === "PEAK" ? "#2F7A3F" : colors.text }}>{item.grade}</Text>
                    </View>
                  ))}

                  {/* Sinsal */}
                  {key === "sinsal" && sec.items && sec.items.map((item: any, i: number) => (
                    <View key={i} style={styles.blockBox}>
                      <Text style={styles.blockTitle}>{item.name} ({item.name_traditional})</Text>
                      <Text style={styles.paragraph}>{item.body}</Text>
                      <Text style={{ fontSize: 13, color: colors.primary, marginTop: 4 }}>👉 {item.advice}</Text>
                    </View>
                  ))}

                  {/* Monthly */}
                  {key === "monthly" && sec.items && sec.items.map((item: any, i: number) => (
                    <View key={i} style={styles.blockBox}>
                      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
                        <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>{item.approx_solar_month} ({item.pillar})</Text>
                        <Text style={{ fontSize: 13, fontWeight: "700", color: colors.primary }}>{item.grade_label}</Text>
                      </View>
                      <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 }}>{item.name}</Text>
                      <Text style={styles.paragraph}>{item.headline}</Text>
                    </View>
                  ))}

                                    {/* Dynamic Sections (Love, Career, Wealth, Money, Work, Bonds) */}
                  {sec.patterns && sec.patterns.length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={styles.blockTitle}>관계 패턴</Text>
                      {sec.patterns.map((p: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>• {p}</Text>
                      ))}
                    </View>
                  )}
                  {sec.compatibility && (
                    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.surface, borderRadius: radius.md }}>
                      <Text style={styles.blockTitle}>궁합</Text>
                      <Text style={styles.paragraph}>최고의 궁합: {(sec.compatibility.best_match || []).join(", ")}</Text>
                      <Text style={{ fontSize: 14, color: colors.textMuted, marginBottom: 8 }}>{sec.compatibility.best_reason}</Text>
                      <Text style={styles.paragraph}>주의할 궁합: {(sec.compatibility.challenging_match || []).join(", ")}</Text>
                      <Text style={{ fontSize: 14, color: colors.textMuted }}>{sec.compatibility.challenging_reason}</Text>
                    </View>
                  )}
                  {sec.actions && sec.actions.length > 0 && (
                    <View style={{ marginTop: 12 }}>
                      <Text style={styles.blockTitle}>실천 가이드</Text>
                      {sec.actions.map((a: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>→ {a}</Text>
                      ))}
                    </View>
                  )}
                  {sec.red_flags && sec.red_flags.length > 0 && (
                    <View style={{ marginTop: 12, padding: 12, backgroundColor: "#FFF5F0", borderRadius: radius.md }}>
                      <Text style={[styles.blockTitle, { color: "#C2461F" }]}>주의할 점</Text>
                      {sec.red_flags.map((r: string, i: number) => (
                        <Text key={i} style={styles.paragraph}>⚠ {r}</Text>
                      ))}
                    </View>
                  )}
                  {!sec.patterns && isLocked && (
                    <View style={{ marginTop: 12, padding: 16, backgroundColor: colors.bg, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border }}>
                      <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22 }}>
                        프리미엄 결제 후 상세 분석을 확인하실 수 있습니다.
                      </Text>
                    </View>
                  )}

                  {/* 공통 잠금 힌트 */}
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
  cover: { backgroundColor: colors.surface, padding: spacing.xl, alignItems: "center", borderBottomWidth: 1, borderBottomColor: colors.border },
  coverSymbol: { fontSize: 48, marginBottom: spacing.sm },
  coverTitle: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: spacing.xs },
  coverTagline: { fontSize: 16, color: colors.textMuted, textAlign: "center", marginBottom: spacing.md },
  badge: { backgroundColor: colors.primary + "20", paddingHorizontal: 12, paddingVertical: 6, borderRadius: radius.pill },
  badgeText: { color: colors.primary, fontWeight: "700", fontSize: 14 },
  section: { padding: spacing.lg },
  sectionTitle: { fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  
  summaryCard: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, marginRight: spacing.sm, borderWidth: 1, borderColor: colors.border, width: 160, position: "relative" },
  summaryCardLocked: { backgroundColor: "#F9F6F0", borderColor: colors.border },
  miniLock: { position: "absolute", top: 8, right: 8 },
  cardLabel: { fontSize: 12, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  cardHeadline: { fontSize: 16, fontWeight: "700", color: colors.text },
  
  accordion: { backgroundColor: colors.surface, borderRadius: radius.md, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border, overflow: "hidden" },
  accordionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: spacing.md },
  accordionTitle: { fontSize: 18, fontWeight: "700", color: colors.text },
  accordionContent: { padding: spacing.md, paddingTop: 0, borderTopWidth: 1, borderTopColor: colors.border },
  coreHero: { fontSize: 18, fontWeight: "700", color: colors.text, lineHeight: 26, marginVertical: 10 },
  paragraph: { fontSize: 15, color: colors.text, lineHeight: 24, marginBottom: 12 },
  blockBox: { backgroundColor: colors.bg, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.sm, borderWidth: 1, borderColor: colors.border },
  blockTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  adviceText: { fontSize: 14, color: colors.primary, fontWeight: "600", marginTop: 8 },
  
  lockedCard: { marginTop: 16, borderRadius: radius.md, overflow: "hidden", borderWidth: 1, borderStyle: "dashed", borderColor: colors.primary + "40", backgroundColor: colors.primary + "05" },
  lockedContent: { padding: 16, alignItems: "center", gap: 8 },
  lockedText: { fontSize: 14, color: colors.text, fontWeight: "600", textAlign: "center" },
  upgradeBtn: { backgroundColor: colors.primary, paddingHorizontal: 16, paddingVertical: 8, borderRadius: radius.sm, marginTop: 4 },
  upgradeBtnText: { color: "#FFF", fontSize: 14, fontWeight: "700" },

  disclaimerBox: { margin: spacing.lg, padding: spacing.md, backgroundColor: "#F0EAE1", borderRadius: radius.md },
  disclaimerText: { fontSize: 12, color: colors.textMuted, lineHeight: 18 },
});

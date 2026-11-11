import { useLocalSearchParams, router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { View, Text, ActivityIndicator, TouchableOpacity, ScrollView, StyleSheet } from "react-native";
import { api } from "@/api/client";
import { colors, spacing, radius } from "@/theme";

export default function SharedCompatibilityScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["shared-compat", id],
    queryFn: () => api.getSharedCompatibility(id as string),
    enabled: !!id,
  });

  const handleGoToApp = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg && tg.initData) {
      tg.openTelegramLink("https://t.me/my_vector_labs_bot?startapp=share");
    } else {
      router.push("/");
    }
  };

  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  if (error || !data) return <View style={styles.center}><Text style={styles.errorText}>결과를 찾을 수 없습니다.</Text></View>;

  // 이중 래핑 해제
  let compat = data.compatibility || data;
  if (compat && compat.compatibility) compat = compat.compatibility;

  if (!compat) return <View style={styles.center}><Text style={styles.errorText}>데이터가 없습니다.</Text></View>;

  const score = compat.overall_score || 0;
  const gradeLabel = compat.grade_label || "중립";
  
  return (
    <ScrollView style={styles.container}>
      <View style={styles.resultCard}>
        <Text style={styles.resultLabel}>궁합 결과</Text>
        <Text style={styles.overallScore}>{score}</Text>
        <View style={styles.gaugeBg}>
          <View style={[styles.gaugeFill, { width: `${score}%`, backgroundColor: colors.primary }]} />
        </View>
        <Text style={styles.overallGrade}>{gradeLabel}</Text>
        <Text style={styles.resultHeadline}>{compat.headline}</Text>
        <Text style={styles.resultBody}>{compat.body}</Text>
      </View>

      {compat.pair && (
        <View style={styles.pairBox}>
          <Text style={styles.pairTitle}>상대방은 이런 사람일까요?</Text>
          <Text style={styles.pairText}>A: {compat.pair.a?.archetype_label || compat.pair.a?.archetype || "?"}</Text>
          <Text style={styles.pairText}>B: {compat.pair.b?.archetype_label || compat.pair.b?.archetype || "?"}</Text>
        </View>
      )}

      {Array.isArray(compat.axes) && compat.axes.map((axis: any, idx: number) => (
        <View key={idx} style={styles.axisBox}>
          <View style={styles.axisHeader}>
            <Text style={styles.axisTitle}>{axis.title}</Text>
            {axis.score !== undefined && <Text style={styles.axisScore}>{axis.score}</Text>}
          </View>
          <Text style={styles.axisDesc}>{axis.description}</Text>
        </View>
      ))}

      {compat.relationship_advice && (
        <View style={styles.adviceBox}>
          <Text style={styles.adviceTitle}>관계 맞춤 조언</Text>
          <Text style={styles.adviceText}>{compat.relationship_advice}</Text>
        </View>
      )}

      <TouchableOpacity style={styles.ctaBtn} onPress={handleGoToApp}>
        <Text style={styles.ctaText}>나도 내 궁합 확인하러 가기</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg, padding: 20 },
  errorText: { fontSize: 16, color: colors.textMuted, textAlign: "center" },
  resultCard: { backgroundColor: colors.surface, padding: spacing.xl, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, alignItems: "center", marginBottom: spacing.md },
  resultLabel: { fontSize: 14, fontWeight: "700", color: colors.textMuted, marginBottom: 8 },
  overallScore: { fontSize: 56, fontWeight: "800", color: colors.primary, marginBottom: 8 },
  gaugeBg: { width: "100%", height: 8, backgroundColor: colors.bgMuted, borderRadius: 4, marginBottom: 16, overflow: "hidden" },
  gaugeFill: { height: "100%", borderRadius: 4 },
  overallGrade: { fontSize: 20, fontWeight: "700", marginBottom: 16, color: colors.text },
  resultHeadline: { fontSize: 18, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 8 },
  resultBody: { fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22 },
  pairBox: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md },
  pairTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 8 },
  pairText: { fontSize: 14, color: colors.text, marginBottom: 4 },
  axisBox: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: spacing.md },
  axisHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  axisTitle: { fontSize: 16, fontWeight: "700", color: colors.primary },
  axisScore: { fontSize: 16, fontWeight: "700", color: colors.text },
  axisDesc: { fontSize: 14, color: colors.text, lineHeight: 20 },
  adviceBox: { backgroundColor: colors.primary + "10", padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.primary + "30", marginBottom: spacing.md },
  adviceTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  adviceText: { fontSize: 15, color: colors.text, lineHeight: 22 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40, marginTop: 8 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});

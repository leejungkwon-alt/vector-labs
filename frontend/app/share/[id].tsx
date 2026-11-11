import { useLocalSearchParams, router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { View, Text, ActivityIndicator, TouchableOpacity, ScrollView, StyleSheet, Platform } from "react-native";
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

  // 이중 래핑 대응: data.compatibility.compatibility 또는 data.compatibility
  let compat = data.compatibility;
  if (compat && compat.compatibility) {
    compat = compat.compatibility;
  }

  if (!compat) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>데이터 형식이 올바르지 않습니다.</Text>
      </View>
    );
  }

  const safeBody = typeof compat.body === 'string' 
    ? compat.body 
    : JSON.stringify(compat.body, null, 2);

  const pair = compat.pair;
  const score = compat.overall_score || compat.total_score || null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
        {score !== null && <Text style={styles.score}>{score}점</Text>}
        {compat.grade_label && <Text style={styles.grade}>{compat.grade_label}</Text>}
        {compat.headline && <Text style={styles.headline}>{compat.headline}</Text>}
        {safeBody && <Text style={styles.body}>{safeBody}</Text>}
        
        {compat.relationship_advice && (
          <View style={styles.adviceBox}>
            <Text style={styles.adviceTitle}>관계 조언</Text>
            <Text style={styles.adviceText}>{compat.relationship_advice}</Text>
          </View>
        )}

        {pair && (
          <View style={styles.pairBox}>
            <Text style={styles.pairTitle}>두 사람의 에너지</Text>
            <Text style={styles.pairText}>A: {pair.a?.archetype_label || pair.a?.archetype || ""}</Text>
            <Text style={styles.pairText}>B: {pair.b?.archetype_label || pair.b?.archetype || ""}</Text>
          </View>
        )}
      </View>
      
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
  card: { backgroundColor: colors.surface, padding: 24, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, marginBottom: 24 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 16 },
  score: { fontSize: 56, fontWeight: "800", color: colors.primary, textAlign: "center", marginBottom: 8 },
  grade: { fontSize: 22, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 16 },
  headline: { fontSize: 18, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 8 },
  body: { fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 },
  adviceBox: { backgroundColor: colors.primary + "10", padding: 16, borderRadius: radius.md, marginBottom: 12 },
  adviceTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  adviceText: { fontSize: 15, color: colors.text, lineHeight: 22 },
  pairBox: { backgroundColor: colors.bg, padding: 16, borderRadius: radius.md, marginBottom: 12 },
  pairTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 8 },
  pairText: { fontSize: 14, color: colors.text, marginBottom: 4 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});

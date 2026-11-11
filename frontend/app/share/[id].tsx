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

  // 디버그: 실제 데이터 구조 콘솔 출력
  if (data) {
    console.log("=== SHARED COMPAT DATA ===", JSON.stringify(data, null, 2));
  }

  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  if (error || !data) return <View style={styles.center}><Text style={styles.errorText}>결과를 찾을 수 없습니다.</Text></View>;

  // 여러 가능한 구조를 모두 시도해서 최종 데이터 추출
  let compat = data.compatibility || data;
  // 이중 래핑 해제: compat.compatibility가 있고, compat에 직접 grade/headline이 없으면 안쪽 사용
  if (compat && compat.compatibility && !compat.grade_label && !compat.headline) {
    compat = compat.compatibility;
  }
  // 또 한 번 더 확인 (삼중 래핑 가능성)
  if (compat && compat.compatibility && !compat.grade_label && !compat.headline) {
    compat = compat.compatibility;
  }

  if (!compat || typeof compat !== 'object') {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>데이터 형식이 올바르지 않습니다.</Text>
      </View>
    );
  }

  // 각 필드를 안전하게 추출
  const score = compat.overall_score ?? compat.total_score ?? compat.score ?? null;
  const gradeLabel = compat.grade_label ?? compat.grade ?? null;
  const headline = compat.headline ?? compat.title ?? null;
  const body = typeof compat.body === 'string' ? compat.body : (compat.body ? JSON.stringify(compat.body) : null);
  const advice = compat.relationship_advice ?? compat.advice ?? null;
  const pair = compat.pair ?? null;
  const axes = Array.isArray(compat.axes) ? compat.axes : [];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
        
        {score !== null && <Text style={styles.score}>{score}점</Text>}
        {gradeLabel && <Text style={styles.grade}>{gradeLabel}</Text>}
        {headline && <Text style={styles.headline}>{headline}</Text>}
        {body && <Text style={styles.body}>{body}</Text>}

        {axes.map((axis: any, idx: number) => (
          <View key={idx} style={styles.axisBox}>
            <View style={styles.axisHeader}>
              <Text style={styles.axisTitle}>{axis.title || axis.name || `축 ${idx + 1}`}</Text>
              {axis.score !== undefined && <Text style={styles.axisScore}>{axis.score}</Text>}
            </View>
            {axis.description && <Text style={styles.axisDesc}>{axis.description}</Text>}
          </View>
        ))}

        {advice && (
          <View style={styles.adviceBox}>
            <Text style={styles.adviceTitle}>관계 조언</Text>
            <Text style={styles.adviceText}>{typeof advice === 'string' ? advice : JSON.stringify(advice)}</Text>
          </View>
        )}

        {pair && (
          <View style={styles.pairBox}>
            <Text style={styles.pairTitle}>두 사람의 에너지</Text>
            <Text style={styles.pairText}>A: {pair.a?.archetype_label || pair.a?.archetype || "?"}</Text>
            <Text style={styles.pairText}>B: {pair.b?.archetype_label || pair.b?.archetype || "?"}</Text>
          </View>
        )}

        {/* 디버그용 raw 데이터 (개발 모드에서만 보이게 하려면 조건 추가) */}
        {__DEV__ && (
          <View style={{ marginTop: 20, padding: 10, backgroundColor: "#f0f0f0" }}>
            <Text style={{ fontSize: 10, color: "#666" }}>DEBUG: {JSON.stringify(compat).slice(0, 200)}</Text>
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
  axisBox: { backgroundColor: colors.bg, padding: 16, borderRadius: radius.md, marginBottom: 12 },
  axisHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  axisTitle: { fontSize: 16, fontWeight: "700", color: colors.primary },
  axisScore: { fontSize: 16, fontWeight: "700", color: colors.text },
  axisDesc: { fontSize: 14, color: colors.text, lineHeight: 20 },
  adviceBox: { backgroundColor: colors.primary + "10", padding: 16, borderRadius: radius.md, marginBottom: 12 },
  adviceTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  adviceText: { fontSize: 15, color: colors.text, lineHeight: 22 },
  pairBox: { backgroundColor: colors.bg, padding: 16, borderRadius: radius.md, marginBottom: 12 },
  pairTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 8 },
  pairText: { fontSize: 14, color: colors.text, marginBottom: 4 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});

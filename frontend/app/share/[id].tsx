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

  // 데이터 구조 안전성 검사
  const compat = data.compatibility;
  if (!compat) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>데이터 형식이 올바르지 않습니다.</Text>
      </View>
    );
  }

  // body가 배열이거나 객체일 수 있으므로 문자열로 안전하게 변환
  const safeBody = typeof compat.body === 'string' 
    ? compat.body 
    : JSON.stringify(compat.body, null, 2);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
        <Text style={styles.score}>{compat.overall_score || 0}점</Text>
        <Text style={styles.headline}>{compat.headline || ""}</Text>
        <Text style={styles.body}>{safeBody}</Text>
        
        {/* axes가 배열일 때만 렌더링 */}
        {Array.isArray(compat.axes) && compat.axes.map((axis: any, idx: number) => (
          <View key={idx} style={styles.axisBox}>
            <Text style={styles.axisTitle}>{axis.title || ""}</Text>
            <Text style={styles.axisDesc}>{axis.description || ""}</Text>
          </View>
        ))}
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
  headline: { fontSize: 18, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 8 },
  body: { fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 },
  axisBox: { backgroundColor: colors.bg, padding: 16, borderRadius: radius.md, marginBottom: 12 },
  axisTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  axisDesc: { fontSize: 14, color: colors.text, lineHeight: 20 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});

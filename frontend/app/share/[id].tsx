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
      // 텔레그램 환경이면 봇 딥링크로 이동
      tg.openTelegramLink("https://t.me/my_vector_labs_bot?startapp=share");
    } else {
      // 웹 환경이면 메인으로 이동
      router.push("/");
    }
  };

  if (isLoading) return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  if (error || !data) return <View style={styles.center}><Text style={styles.errorText}>결과를 찾을 수 없습니다.</Text></View>;

  const compat = data.compatibility;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
        <Text style={styles.score}>{compat.overall_score || 0}점</Text>
        <Text style={styles.headline}>{compat.headline}</Text>
        <Text style={styles.body}>{compat.body}</Text>
        
        {compat.axes?.map((axis: any, idx: number) => (
          <View key={idx} style={styles.axisBox}>
            <Text style={styles.axisTitle}>{axis.title}</Text>
            <Text style={styles.axisDesc}>{axis.description}</Text>
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
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg },
  errorText: { fontSize: 16, color: colors.textMuted },
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

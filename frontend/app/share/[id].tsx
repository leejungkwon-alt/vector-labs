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

  if (!compat || typeof compat !== 'object') {
    return <View style={styles.center}><Text style={styles.errorText}>데이터 형식이 올바르지 않습니다.</Text></View>;
  }

  // 동적으로 섹션(axes) 추출: headline + body를 가진 객체들
  const sections: { key: string; data: any }[] = [];
  const skipKeys = ["meta", "axes", "pair", "relationship_advice", "disclaimer"];
  
  Object.keys(compat).forEach((key) => {
    if (skipKeys.includes(key)) return;
    const val = compat[key];
    if (val && typeof val === 'object' && (val.headline || val.body)) {
      sections.push({ key, data: val });
    }
  });

  const pair = compat.pair;
  const advice = compat.relationship_advice;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>궁합 결과</Text>
      </View>
      
      {sections.map(({ key, data: sec }) => {
        const rawScore = sec.score;
        const displayScore = rawScore !== undefined 
          ? (rawScore <= 1 ? Math.round(rawScore * 100) : Math.round(rawScore))
          : null;
        return (
          <View key={key} style={styles.card}>
            <View style={styles.headerRow}>
              <Text style={styles.axisTitle}>{sec.headline || key}</Text>
              {displayScore !== null && <Text style={styles.axisScore}>{displayScore}</Text>}
            </View>
            {sec.body && <Text style={styles.axisBody}>{sec.body}</Text>}
            {sec.day_master && typeof sec.day_master === 'object' && (
              <View style={styles.subBox}>
                <Text style={styles.subTitle}>{sec.day_master.headline || "세부 분석"}</Text>
                {sec.day_master.body && <Text style={styles.subBody}>{sec.day_master.body}</Text>}
              </View>
            )}
          </View>
        );
      })}
      
      {pair && (
        <View style={styles.card}>
          <Text style={styles.pairTitle}>두 사람의 에너지</Text>
          <Text style={styles.pairText}>A: {pair.a?.archetype_label || pair.a?.archetype || "?"}</Text>
          <Text style={styles.pairText}>B: {pair.b?.archetype_label || pair.b?.archetype || "?"}</Text>
        </View>
      )}
      
      {advice && (
        <View style={styles.card}>
          <Text style={styles.adviceTitle}>관계 조언</Text>
          <Text style={styles.adviceText}>{typeof advice === 'string' ? advice : JSON.stringify(advice)}</Text>
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
  card: { backgroundColor: colors.surface, padding: 20, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border, marginBottom: 16 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text, textAlign: "center" },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  axisTitle: { flex: 1, fontSize: 16, fontWeight: "700", color: colors.text },
  axisScore: { fontSize: 20, fontWeight: "800", color: colors.primary, marginLeft: 12 },
  axisBody: { fontSize: 14, color: colors.textMuted, lineHeight: 22 },
  subBox: { marginTop: 12, padding: 12, backgroundColor: colors.bg, borderRadius: radius.md },
  subTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  subBody: { fontSize: 13, color: colors.text, lineHeight: 20 },
  pairTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 8 },
  pairText: { fontSize: 14, color: colors.text, marginBottom: 4 },
  adviceTitle: { fontSize: 14, fontWeight: "700", color: colors.primary, marginBottom: 6 },
  adviceText: { fontSize: 15, color: colors.text, lineHeight: 22 },
  ctaBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginBottom: 40, marginTop: 8 },
  ctaText: { color: colors.onPrimary, fontSize: 17, fontWeight: "700" },
});

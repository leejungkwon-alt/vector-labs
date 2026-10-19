import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api, ApiError } from "@/api/client";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import type { DailyResponse } from "../../types";

export default function DailyScreen() {
  const [profile, setProfile] = useState<any>(null);
  const [profileLoaded, setProfileLoaded] = useState(false);
  
  // 👇 유저 정보(토큰 상태)를 가져옵니다.
  const user = useAuthStore((s) => s.user);
  const ready = useAuthStore((s) => s.ready);

  useEffect(() => {
    AsyncStorage.getItem("saju_profile").then((data) => {
      if (data) setProfile(JSON.parse(data));
      setProfileLoaded(true);
    });
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: ["daily", profile, user?.id], // 👈 user.id를 키에 추가하여 로그인 상태 변경 시 재호출
    // user와 ready 상태가 확실할 때만 API 호출
    queryFn: () => api.daily({ ...profile, days: 7, lang: "ko" }),
    enabled: !!profile && profileLoaded && !!user && ready, 
    retry: false,
  });

  if (!profileLoaded || !ready) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>사용자 정보를 불러오는 중...</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>사주 정보가 없습니다.</Text>
        <Text style={styles.errorDetail}>홈 탭에서 사주 정보를 먼저 입력해 주세요.</Text>
      </View>
    );
  }

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>7일간의 기운을 읽어오고 있습니다...</Text>
      </View>
    );
  }

  if (error) {
    const isForbidden = error instanceof ApiError && error.status === 403;
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>
          {isForbidden ? "구독자 전용 기능입니다" : "오류가 발생했습니다"}
        </Text>
        <Text style={styles.errorDetail}>
          {isForbidden 
            ? `데일리 에너지 서비스는 구독권 또는 프리미엄 회원만 이용하실 수 있습니다.\n\n(현재 내 등급: ${user?.tier?.toUpperCase()})`
            : (error instanceof ApiError ? (error as ApiError).detail : (error as Error).message)}
        </Text>
      </View>
    );
  }

  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) return null;

  const gradeColors: Record<string, string> = {
    PEAK: "#2F7A3F",
    FAVORABLE: "#5FAF7A",
    NEUTRAL: "#7A6A5C",
    CAUTION: "#D4A017",
    CHALLENGING: "#C2461F",
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
      <View style={styles.heroBox}>
        <Text style={styles.heroTitle}>{dailyData.hero}</Text>
        <Text style={styles.heroSub}>앞으로 7일간의 일운입니다.</Text>
      </View>

      <View style={styles.list}>
        {dailyData.items.map((item, idx) => (
          <View key={idx} style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.dateText}>{item.date}</Text>
              <View style={[styles.badge, { backgroundColor: gradeColors[item.grade] + "20" }]}>
                <Text style={[styles.badgeText, { color: gradeColors[item.grade] }]}>
                  {item.grade_label}
                </Text>
              </View>
            </View>
            
            <Text style={styles.dayName}>{item.name}</Text>
            <Text style={styles.headline}>{item.headline}</Text>
            <Text style={styles.body}>{item.body}</Text>
            
            <View style={styles.tipBox}>
              <Text style={styles.tipText}>💡 <Text style={{fontWeight: "700"}}>집중:</Text> {item.lean_into}</Text>
              <Text style={styles.tipText}>⚠️ <Text style={{fontWeight: "700"}}>주의:</Text> {item.watch_for}</Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg, padding: spacing.lg },
  loadingText: { marginTop: spacing.md, fontSize: 16, color: colors.textMuted },
  errorText: { fontSize: 20, fontWeight: "700", color: colors.danger, marginBottom: spacing.sm },
  errorDetail: { fontSize: 15, color: colors.text, textAlign: "center", lineHeight: 22 },
  
  container: { flex: 1, backgroundColor: colors.bg },
  
  heroBox: { padding: spacing.lg, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  heroTitle: { fontSize: 20, fontWeight: "800", color: colors.primary, marginBottom: spacing.xs },
  heroSub: { fontSize: 15, color: colors.textMuted },
  
  list: { padding: spacing.md },
  card: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border },
  
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
  dateText: { fontSize: 14, fontWeight: "600", color: colors.textMuted },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: radius.pill },
  badgeText: { fontSize: 12, fontWeight: "700" },
  
  dayName: { fontSize: 13, fontWeight: "700", color: colors.primary, marginBottom: 4 },
  headline: { fontSize: 18, fontWeight: "700", color: colors.text, marginBottom: 8 },
  body: { fontSize: 15, color: colors.text, lineHeight: 22, marginBottom: spacing.md },
  
  tipBox: { backgroundColor: "#FDF6EE", padding: spacing.sm, borderRadius: radius.sm, gap: 4 },
  tipText: { fontSize: 13, color: colors.textMuted },
});

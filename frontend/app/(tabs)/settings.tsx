import { useLanguageStore, SupportedLang } from "@/store/languageStore";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, Linking } from "react-native";
import { router } from "expo-router";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { api } from "@/api/client";
import { SocialLoginModal } from "@/components/SocialLoginModal";
import { PaymentModal } from "@/components/PaymentModal";

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const signOut = useAuthStore((s) => s.signOut);
  const profile = useProfileStore((s) => s.profile); // 생년월일 가져오기
  const clearProfile = useProfileStore((s) => s.clearProfile);

  const { data: purchaseData } = useQuery({
    queryKey: ["purchases", user?.id],
    queryFn: () => api.getPurchases(),
    enabled: !!user,
  });

  const [showLogin, setShowLogin] = useState(false);
  const [showPayment, setShowPayment] = useState(false);

  const handleUpgrade = () => {
    if (!user) return;
    if (user.is_anonymous) {
      setShowLogin(true);
    } else {
      setShowPayment(true);
    }
  };

  const handleReset = async () => {
    await clearProfile();
    router.replace("/birth-input");
  };

  const handleDeleteAccount = () => {
    const performDelete = async () => {
      try {
        await api.deleteAccount();
        await clearProfile();
        await signOut();
        router.replace("/");
      } catch (e: any) {
        const msg = e?.detail || "계정 삭제에 실패했습니다.";
        if (Platform.OS === "web") alert(msg);
        else Alert.alert("오류", msg);
      }
    };

    if (Platform.OS === "web") {
      if (confirm("정말로 계정을 삭제하시겠습니까? 모든 데이터가 사라집니다.")) performDelete();
    } else {
      Alert.alert("계정 삭제", "정말로 계정을 영구 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.", [
        { text: "취소", style: "cancel" },
        { text: "영구 삭제", style: "destructive", onPress: performDelete },
      ]);
    }
  };

  const handleManageSubscription = () => {
    // 실제 앱스토어/플레이스토어 구독 관리 페이지로 이동 (임시 링크)
    if (Platform.OS === "ios") {
      Linking.openURL("https://apps.apple.com/account/subscriptions");
    } else if (Platform.OS === "android") {
      Linking.openURL("https://play.google.com/store/account/subscriptions");
    } else {
      alert("모바일 앱에서 구독을 관리하실 수 있습니다.");
    }
  };

  const lang = useLanguageStore((s) => s.lang);
  const setLang = useLanguageStore((s) => s.setLang);


  const formatBirthInfo = () => {
    if (!profile?.birth_date) return "미등록 (입력 필요)";
    let info = profile.birth_date;
    
    if (profile.birth_time_mode === "exact" && profile.birth_time) {
      // HH:MM:SS 중 앞의 5자리(HH:MM)만 표시
      info += ` ${profile.birth_time.substring(0, 5)}`;
    } else if (profile.birth_time_mode === "noon") {
      info += " (시간 모름 - 정오 기준)";
    } else if (profile.birth_time_mode === "day_only") {
      info += " (시간 모름 - 일주만)";
    }
    
    if (profile.birth_location) {
      // 도시 키값(seoul, new_york)을 보기 좋게 표시
      info += ` · ${profile.birth_location}`;
    }
    return info;
  };

  const getLoginProvider = () => {
    if (!user) return "로그인 안 됨";
    if (user.is_anonymous) return "게스트 (익명 로그인)";
    return `${user.social_provider?.toUpperCase() || "소셜"} 연동됨`;
  };

  return (
    <View style={styles.container}>
      {/* 1. 내 계정 정보 (이메일/생년월일/등급) */}
      <View style={styles.profileBox}>
        <Text style={styles.sectionTitle}>내 계정 정보</Text>
        
        <View style={styles.row}>
          <Text style={styles.label}>로그인 계정</Text>
          <Text style={styles.value}>{getLoginProvider()}</Text>
        </View>
        
        <View style={styles.row}>
          <Text style={styles.label}>출생 정보 (생년월일시)</Text>
          <Text style={[styles.value, { flexShrink: 1, textAlign: "right" }]}>
            {formatBirthInfo()}
          </Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.label}>이용 등급</Text>
          <Text style={[styles.value, { fontWeight: "bold", color: user?.tier === "free" ? colors.text : colors.primary }]}>
            {
              user?.tier === "free" ? "무료 회원 (Free)" :
              user?.tier === "subscription" ? "구독자 (Subscription)" :
              user?.tier === "premium" ? "프리미엄 회원 (Premium)" : user?.tier
            }
          </Text>
        </View>
      </View>

      {/* 2. 프리미엄 구독 관리 (유료 유저 전용) */}
      {user?.tier !== "free" && (
        <View style={[styles.profileBox, { backgroundColor: colors.primary + "10", borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>💎 구독 관리</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            현재 모든 프리미엄 혜택을 이용 중이십니다.
          </Text>
          <TouchableOpacity style={styles.manageBtn} onPress={handleManageSubscription}>
            <Text style={styles.manageBtnText}>구독 변경 및 취소하기</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 3. 무료 유저 업그레이드 유도 */}
      {user?.tier === "free" && (
        <View style={[styles.profileBox, { backgroundColor: colors.primary + "10", borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>✨ 프리미엄 업그레이드</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            구독하면 7일치 데일리 에너지와 궁합 분석을 모두 이용할 수 있습니다.
          </Text>
          <TouchableOpacity style={styles.upgradeBtn} onPress={handleUpgrade}>
            <Text style={styles.upgradeBtnText}>프리미엄 구독하기</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 3.5 결제 내역 (영수증) */}
      {purchaseData?.purchases && purchaseData.purchases.length > 0 && (
        <View style={styles.profileBox}>
          <Text style={styles.sectionTitle}>결제 내역 (Payment History)</Text>
          {purchaseData.purchases.map((p: any, i: number) => (
            <View key={i} style={[styles.row, { borderBottomWidth: i === purchaseData.purchases.length - 1 ? 0 : 1, borderBottomColor: colors.border, paddingBottom: 10, marginBottom: 10 }]}>
              <View>
                <Text style={{ fontSize: 14, fontWeight: "600", color: colors.text }}>
                  {p.product_id === "sub_monthly_299" ? "월간 구독권" : 
                   p.product_id === "addon_compat_199" ? "궁합 애드온" :
                   p.product_id === "addon_deep_099" ? "심화 리포트" : p.product_id}
                </Text>
                <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4 }}>
                  {new Date(p.purchased_at).toLocaleString()} · {p.platform.toUpperCase()}
                </Text>
              </View>
              <Text style={{ fontSize: 15, fontWeight: "700", color: colors.primary }}>
                {p.product_id === "sub_monthly_299" ? "$2.99" : 
                 p.product_id === "addon_compat_199" ? "$1.99" :
                 p.product_id === "addon_deep_099" ? "$0.99" : "-"}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* 4. 계정 액션 */}
      <View style={styles.list}>
        <TouchableOpacity style={styles.btn} onPress={handleReset}>
          <Text style={styles.btnText}>출생 정보 수정하기</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={handleDeleteAccount}>
          <Text style={styles.dangerText}>계정 영구 삭제</Text>
        </TouchableOpacity>
      </View>

      {/* 5. 언어 설정 */}
      <View style={{ marginTop: 24, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: colors.border }}>
        <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 12 }}>언어 설정 (Language)</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
          {([
            { key: "ko", label: "한국어" },
            { key: "en", label: "English" },
            { key: "ja", label: "日本語" },
            { key: "zh_cn", label: "简体中文" },
            { key: "zh_tw", label: "繁體中文" },
          ] as { key: SupportedLang; label: string }[]).map((item) => (
            <TouchableOpacity
              key={item.key}
              onPress={() => setLang(item.key)}
              style={{ paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8, borderWidth: 1,
                borderColor: lang === item.key ? colors.primary : colors.border }}
            >
              <Text style={{ color: lang === item.key ? colors.primary : colors.textMuted }}>{item.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <SocialLoginModal
        visible={showLogin}
        onClose={() => setShowLogin(false)}
        onSuccess={() => {
          setShowLogin(false);
          setShowPayment(true);
        }}
      />
      <PaymentModal
        visible={showPayment}
        onClose={() => setShowPayment(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  profileBox: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.md, borderWidth: 1, borderColor: colors.border },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  row: { flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.sm, alignItems: "center" },
  label: { fontSize: 15, color: colors.textMuted },
  value: { fontSize: 15, fontWeight: "500", color: colors.text },
  list: { gap: spacing.sm },
  btn: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  btnText: { color: colors.text, fontSize: 16, fontWeight: "600" },
  dangerBtn: { borderColor: colors.danger },
  dangerText: { color: colors.danger, fontSize: 16, fontWeight: "600" },
  upgradeBtn: { backgroundColor: colors.primary, padding: 14, borderRadius: radius.md, alignItems: "center" },
  upgradeBtnText: { color: colors.onPrimary, fontSize: 16, fontWeight: "700" },
  manageBtn: { backgroundColor: colors.surface, padding: 14, borderRadius: radius.md, alignItems: "center", borderWidth: 1, borderColor: colors.primary },
  manageBtnText: { color: colors.primary, fontSize: 15, fontWeight: "600" },
});

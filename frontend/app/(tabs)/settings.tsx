import { useLanguageStore, SupportedLang } from "@/store/languageStore";
import { useT } from "@/i18n";
import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, Linking, ScrollView } from "react-native";
import { router } from "expo-router";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { api } from "@/api/client";
import { SocialLoginModal } from "@/components/SocialLoginModal";
import { PaymentModal } from "@/components/PaymentModal";

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const t = useT();
  const signOut = useAuthStore((s) => s.signOut);
  const profile = useProfileStore((s) => s.profile);
  const clearProfile = useProfileStore((s) => s.clearProfile);

  const [showLogin, setShowLogin] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [upgradeAfterLogin, setUpgradeAfterLogin] = useState(false); // 로그인 후 결제창 띄울지 여부

  const handleUpgrade = () => {
    if (!user) return;
    if (user.is_anonymous) {
      setUpgradeAfterLogin(true); // 업그레이드 목적으로 로그인 시도
      setShowLogin(true);
    } else {
      setShowPayment(true);
    }
  };

  // 단순히 계정만 연결하고 싶을 때
  const handleLinkAccount = () => {
    setUpgradeAfterLogin(false); // 단순 연동 목적
    setShowLogin(true);
  };

  const handleReset = () => {
    router.push("/birth-input");
  };

  const handleDeleteAccount = () => {
    const performDelete = async () => {
      try {
        await api.deleteAccount();
        await clearProfile();
        await signOut();
        router.replace("/");
      } catch (e: any) {
        const msg = e?.detail || t("settings.deleteAccountFail");
        if (Platform.OS === "web") alert(msg);
        else Alert.alert(t("common.notice"), msg);
      }
    };

    if (Platform.OS === "web") {
      if (confirm(t("settings.deleteAccountConfirmWeb"))) performDelete();
    } else {
      Alert.alert(t("settings.deleteAccountOk"), t("settings.deleteAccountConfirm"), [
        { text: t("settings.deleteAccountCancel"), style: "cancel" },
        { text: t("settings.deleteAccountDelete"), style: "destructive", onPress: performDelete },
      ]);
    }
  };

  const handleManageSubscription = () => {
    // Lemon Squeezy 고객 포털 (구독 관리·카드 변경·영수증 다운로드)
    // TODO: 백엔드에서 signed URL을 받아 자동 로그인으로 전환 예정
    Linking.openURL("https://gyeol.lemonsqueezy.com/billing");
  };

  const lang = useLanguageStore((s) => s.lang);
  const setLang = useLanguageStore((s) => s.setLang);

  const formatBirthInfo = () => {
    if (!profile?.birth_date) return t("settings.birthNotSet");
    let info = profile.birth_date;
    if (profile.birth_time_mode === "exact" && profile.birth_time) {
      info += ` ${profile.birth_time.substring(0, 5)}`;
    } else if (profile.birth_time_mode === "noon") {
      info += t("settings.timeUnknownNoon");
    } else if (profile.birth_time_mode === "day_only") {
      info += t("settings.timeUnknownDayOnly");
    }
    if (profile.birth_location) {
      info += ` · ${profile.birth_location}`;
    }
    return info;
  };

  const getLoginProvider = () => {
    if (!user) return t("settings.loginNotSet");
    if (user.is_anonymous) return t("settings.loginAnonymous");
    const provider = user.social_provider
      ? user.social_provider.charAt(0).toUpperCase() + user.social_provider.slice(1)
      : "Social";
    return t("settings.loginSocial", { provider });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
      {/* 1. 내 계정 정보 */}
      <View style={styles.profileBox}>
        <Text style={styles.sectionTitle}>{t("settings.accountInfo")}</Text>
        
        <View style={styles.row}>
          <Text style={styles.label}>{t("settings.loginAccount")}</Text>
          <Text style={styles.value}>{getLoginProvider()}</Text>
        </View>
        
        <View style={styles.row}>
          <Text style={styles.label}>{t("settings.birthInfo")}</Text>
          <Text style={[styles.value, { flexShrink: 1, textAlign: "right" }]}>
            {formatBirthInfo()}
          </Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.label}>{t("settings.tier")}</Text>
          <Text style={[styles.value, { fontWeight: "bold", color: user?.tier === "free" ? colors.text : colors.primary }]}>
            {user?.tier === "free" ? t("settings.tierFree") :
             user?.tier === "subscription" ? t("settings.tierSubscription") :
             user?.tier === "premium" ? t("settings.tierPremium") : user?.tier}
          </Text>
        </View>
      </View>

      {/* ⭐️ 추가된 부분: 익명 로그인 상태일 때 계정 연결 유도 */}
      {user?.is_anonymous && (
        <View style={[styles.profileBox, { backgroundColor: colors.surface, borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>t("settings.linkAccountTitle")</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            t("settings.linkAccountDesc")
          </Text>
          <TouchableOpacity style={styles.upgradeBtn} onPress={handleLinkAccount}>
            <Text style={styles.upgradeBtnText}>t("settings.linkAccountCta")</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 2. 프리미엄 구독 관리 */}
      {!!user && user.tier !== "free" && (
        <View style={[styles.profileBox, { backgroundColor: colors.primary + "10", borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.subscriptionManageTitle")}</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            {t("settings.subscriptionActive")}
          </Text>
          <TouchableOpacity style={styles.manageBtn} onPress={handleManageSubscription}>
            <Text style={styles.manageBtnText}>{t("settings.manageSubscription")}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 3. 무료 유저 업그레이드 유도 */}
      {user?.tier === "free" && (
        <View style={[styles.profileBox, { backgroundColor: colors.primary + "10", borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.upgradeTitle")}</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            {t("settings.upgradeBody")}
          </Text>
          <TouchableOpacity style={styles.upgradeBtn} onPress={handleUpgrade}>
            <Text style={styles.upgradeBtnText}>{t("settings.upgradeCta")}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* 4. 계정 액션 */}
      <View style={styles.list}>
        <TouchableOpacity style={styles.btn} onPress={handleReset}>
          <Text style={styles.btnText}>{t("settings.editBirthInfo")}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={handleDeleteAccount}>
          <Text style={styles.dangerText}>{t("settings.deleteAccount")}</Text>
        </TouchableOpacity>
      </View>

      {/* 5. 언어 설정 */}
      <View style={{ marginTop: 24, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: colors.border }}>
        <Text style={{ fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 12 }}>{t("settings.language")}</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 10 }}>
          {([
            { key: "ko", label: "한국어" },
            { key: "en", label: "English" },
            { key: "ja", label: "日本語" },
            { key: "zh_cn", label: "简体中文" },
            { key: "es", label: "Español" },
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
          if (upgradeAfterLogin) {
            // 업그레이드 버튼을 눌러서 들어온 경우 -> 성공 시 결제창으로 연결
            setShowPayment(true);
          } else {
            // 단순히 계정 연동 버튼을 눌러서 들어온 경우 -> 성공 t("common.notice")만 띄우고 종료
            const msg = "t("settings.linkAccountSuccess")";
            if (Platform.OS === "web") alert(msg);
            else Alert.alert("t("common.notice")", msg);
          }
        }}
      />
      <PaymentModal
        visible={showPayment}
        onClose={() => setShowPayment(false)}
      />
    </ScrollView>
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
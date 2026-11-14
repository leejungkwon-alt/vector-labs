import { useLanguageStore, SupportedLang } from "@/store/languageStore";
import { useT } from "@/i18n";
import { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform, Linking, ScrollView } from "react-native";
import { Switch } from "react-native";
import { router } from "expo-router";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { usePoemStore } from "@/store/poemStore";
import { api } from "@/api/client";
import type { Purchase } from "../../types";
import { SocialLoginModal } from "@/components/SocialLoginModal";
import { PaymentModal } from "@/components/PaymentModal";

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const t = useT();
  const signOut = useAuthStore((s) => s.signOut);
  const profile = useProfileStore((s) => s.profile);
  const clearProfile = useProfileStore((s) => s.clearProfile);
  const setCurrentPoem = usePoemStore((s) => s.setCurrentPoem);

  const [showLogin, setShowLogin] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [upgradeAfterLogin, setUpgradeAfterLogin] = useState(false); // 로그인 후 결제창 띄울지 여부

  // ---- 구매 내역 ----
  // 처음에는 최신 N개만 보여주고 나머지는 "더보기"로 펼칩니다.
  const [showAllPurchases, setShowAllPurchases] = useState(false);

  // 구매 내역 한 줄의 표시 문구를 만든다: "상품명(결제 채널)"
  // - 상품 종류: item.kind 우선, 없으면 product_id로 추정 (예전 데이터의 google_sub, lemon_onetime 포함)
  // - 결제 채널: platform 기준 (google_play/android → 앱, telegram → 텔레그램, 그 외 → 웹)
  const productDetails = (item: Purchase) => {
    const pid = (item.product_id || "").toLowerCase();
    const plat = (item.platform || "").toLowerCase();

    let channelKey = "settings.purchaseChannelWeb";
    if (/google|android|play/.test(plat)) channelKey = "settings.purchaseChannelApp";
    else if (/telegram|stars/.test(plat)) channelKey = "settings.purchaseChannelTelegram";

    let nameKey: string | null = null;
    if (pid === "deep_report") nameKey = "settings.productDeepReport";
    else if (pid === "compatibility_addon") nameKey = "settings.productCompatAddon";
    else if (item.kind === "subscription" || /sub|premium|monthly/.test(pid)) nameKey = "settings.purchaseSub";
    else if (item.kind === "onetime" || /onetime|credit|once/.test(pid)) nameKey = "settings.purchaseOnetime";

    const name = nameKey ? t(nameKey) : item.product_id; // 알 수 없는 상품은 ID 그대로
    let status = "";
    if (nameKey === "settings.purchaseSub" && item.expires_date) {
      const expires = new Date(item.expires_date);
      status = expires > new Date()
        ? ` (${t("settings.subscriptionStatusActive")} ~${expires.toLocaleDateString()})`
        : ` (${t("settings.subscriptionStatusExpired")})`;
    }

    return {
      name: `${t("settings.purchaseLabel", { name, channel: t(channelKey) })}${status}`,
      purchasedAt: new Date(item.purchased_at).toLocaleDateString(),
    };
  };

  const PURCHASE_PREVIEW_COUNT = 4;
  const visiblePurchases = showAllPurchases ? purchases : purchases.slice(0, PURCHASE_PREVIEW_COUNT);
  const hiddenPurchaseCount = Math.max(0, purchases.length - PURCHASE_PREVIEW_COUNT);

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
  const [isTgSubscribed, setIsTgSubscribed] = useState(false);
  const [isTgLoading, setIsTgLoading] = useState(false);
  const [isTgEnv, setIsTgEnv] = useState(false);

  // 화면이 그려진 후 텔레그램 SDK가 로드되었는지 확인
  
  useEffect(() => {
    if (user) {
      api.getPurchases().then((res) => {
        if (res && res.purchases) setPurchases(res.purchases);
      }).catch((e) => console.warn("Failed to load purchases", e));
    }
  }, [user]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      // 텔레그램 SDK는 웹에서도 객체를 만들기 때문에, initData가 실제로 있는지 확인해야 함
      const tg = (window as any).Telegram?.WebApp;
      setIsTgEnv(!!tg?.initData && tg.initData.length > 0);
    }
  }, []);

  const handleTelegramToggle = async () => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg || !tg.initData) return;
    setIsTgLoading(true);
    try {
      const { storage } = await import("@/store/secureStore");
      const token = await storage.getItem("saju.access_token");
      const endpoint = isTgSubscribed ? "unregister" : "register";
      const res = await fetch(`https://saju-backend-787049663118.asia-northeast3.run.app/api/v1/telegram/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token || ""}`,
        },
        body: JSON.stringify({ init_data: tg.initData, lang }),
      });
      if (!res.ok) {
        if (res.status === 409) throw new Error(t("settings.telegramPushNoProfile"));
        if (res.status === 403) throw new Error(t("settings.telegramPushAgeLimit"));
        throw new Error(t("settings.telegramPushError"));
      }
      setIsTgSubscribed(!isTgSubscribed);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setIsTgLoading(false);
    }
  };

  const handleLinkAccount = () => {
    setUpgradeAfterLogin(false); // 단순 연동 목적
    setShowLogin(true);
  };

  const handleReset = () => {
    router.push("/birth-input");
  };

  const handleSignOut = async () => {
    const performSignOut = async () => {
      try {
        await signOut();
        // 🆕 프로필/시조 상태 완전 초기화 (이전 계정 데이터 제거)
        try { await clearProfile(); } catch {}
        try { setCurrentPoem(null as any, []); } catch {}
        // 🆕 웹은 풀 리로드 (모든 캐시 초기화, 확실한 로그아웃)
        if (Platform.OS === "web") {
          window.location.href = "/";
        } else {
          router.replace("/");
        }
      } catch (e: any) {
        const msg = e?.message || t("settings.logoutFail");
        if (Platform.OS === "web") alert(msg);
        else Alert.alert(t("common.notice"), msg);
      }
    };

    if (Platform.OS === "web") {
      if (confirm(t("settings.logoutConfirm"))) await performSignOut();
    } else {
      Alert.alert(
        t("settings.logout"),
        t("settings.logoutConfirm"),
        [
          { text: t("common.cancel"), style: "cancel" },
          { text: t("settings.logout"), style: "destructive", onPress: performSignOut },
        ]
      );
    }
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

  const handleManageSubscription = async () => {
    try {
      const res = await api.getPortalUrl();
      if (!res?.url) {
        alert(t("settings.subscriptionNotFound"));
        return;
      }
      if (Platform.OS === "web") {
        window.location.href = res.url;
      } else {
        await Linking.openURL(res.url);
      }
    } catch (e: any) {
      alert(e?.detail || t("settings.subscriptionPortalFail"));
    }
  };

  const lang = useLanguageStore((s) => s.lang);
  const setLang = useLanguageStore((s) => s.setLang);

  const productLabel = (id: string) => {
    const keys: Record<string, string> = {
      stars_onetime: "settings.productStarsOnetime",
      stars_sub: "settings.productStarsSub",
      lemon_sub: "settings.productWebSub",
      lemon_onetime: "settings.productWebOnetime",
      gyeol_onetime_credit: "settings.productPlayOnetime",
      gyeol_premium_monthly: "settings.productPlaySub",
    };
    return keys[id] ? t(keys[id] as any) : id;
  };

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
    
    // 💡 텔레그램 환경에서는 무조건 텔레그램으로 표시
    if (isTgEnv) {
      return t("settings.telegramLinked");
    }
    
    // 웹 환경에서는 기존 소셜 로그인 정보 표시
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
          <Text style={[styles.value, { fontWeight: "bold", color: (user?.tier === "free" && (user?.onetime_credits ?? 0) === 0) ? colors.text : colors.primary }]}>
            {user?.tier === "premium" ? t("settings.tierPremium") :
             user?.tier === "subscription" ? t("settings.tierSubscription") :
             (user?.onetime_credits ?? 0) > 0 ? t("settings.creditsHeld", { count: user?.onetime_credits ?? 0 }) :
             t("settings.tierFree")}
          </Text>
        </View>
      </View>

      {/* ⭐️ 게스트 상태: 텔레그램 환경이면 텔레그램 로그인 카드, 아니면 SNS 연동 카드 */}
      {user?.is_anonymous && (
        isTgEnv ? (
          <View style={[styles.profileBox, { backgroundColor: "#f0f8ff", borderColor: "#0088cc" }]}>
            <Text style={[styles.sectionTitle, { color: "#0088cc" }]}>{t("settings.telegramLoginTitle")}</Text>
            <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
              {t("settings.telegramLoginDesc")}
            </Text>
            <TouchableOpacity 
              style={[styles.upgradeBtn, { backgroundColor: "#0088cc" }]} 
              onPress={() => {
                useAuthStore.getState().loginWithTelegram().then(() => {
                  useAuthStore.getState().bootstrap();
                }).catch((e: any) => alert(e.message));
              }}
            >
              <Text style={styles.upgradeBtnText}>{t("settings.telegramLoginCta")}</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={[styles.profileBox, { backgroundColor: colors.surface, borderColor: colors.primary }]}>
            <Text style={[styles.sectionTitle, { color: colors.primary }]}>{t("settings.linkAccountTitle")}</Text>
            <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
              {t("settings.linkAccountDesc")}
            </Text>
            <TouchableOpacity style={styles.upgradeBtn} onPress={handleLinkAccount}>
              <Text style={styles.upgradeBtnText}>{t("settings.linkAccountCta")}</Text>
            </TouchableOpacity>
          </View>
        )
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
      {user?.tier === "free" && (user?.onetime_credits ?? 0) === 0 && (
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

      {/* 구매 내역 */}
      {purchases.length > 0 && (
        <View style={styles.profileBox}>
          <Text style={styles.sectionTitle}>{t("settings.purchaseHistory")}</Text>
          {visiblePurchases.map((item) => {
            const details = productDetails(item);
            return (
              <View key={item.id} style={styles.row}>
                <Text style={[styles.label, styles.purchaseName]}>{details.name}</Text>
                <Text style={styles.value}>{details.purchasedAt}</Text>
              </View>
            );
          })}
          {hiddenPurchaseCount > 0 && (
            <TouchableOpacity style={styles.moreBtn} onPress={() => setShowAllPurchases((v) => !v)}>
              <Text style={styles.moreBtnText}>
                {showAllPurchases
                  ? t("settings.purchaseCollapse")
                  : t("settings.purchaseViewMore", { count: hiddenPurchaseCount })}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      {/* 4. 계정 액션 */}
      <View style={styles.list}>
        <TouchableOpacity style={styles.btn} onPress={handleReset}>
          <Text style={styles.btnText}>{t("settings.editBirthInfo")}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.btn} onPress={handleSignOut}>
          <Text style={styles.btnText}>{t("settings.logout")}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={handleDeleteAccount}>
          <Text style={styles.dangerText}>{t("settings.deleteAccount")}</Text>
        </TouchableOpacity>
      </View>

      {/* 텔레그램 알림 스위치 */}
      {isTgEnv && (
        <View style={{ marginTop: 24, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: "#0088cc", backgroundColor: "#f0f8ff" }}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <Text style={{ fontSize: 16, fontWeight: "600", color: "#0088cc" }}>{t("settings.telegramPushTitle")}</Text>
              <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, lineHeight: 18 }}>
                {t("settings.telegramPushDesc")}
              </Text>
            </View>
            <Switch 
              value={isTgSubscribed} 
              onValueChange={handleTelegramToggle} 
              disabled={isTgLoading} 
            />
          </View>
        </View>
      )}

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
        onSuccess={async () => {
          await useAuthStore.getState().bootstrap(); // 유저 정보 강제 갱신
          setShowLogin(false);
          if (upgradeAfterLogin) {
            setShowPayment(true);
          } else {
            const msg = t("settings.linkAccountSuccess");
            if (Platform.OS === "web") alert(msg);
            else Alert.alert(t("common.notice"), msg);
          }
        }}
      />
      <PaymentModal
        visible={showPayment}
        onClose={() => setShowPayment(false)}
        onRequireLogin={() => {
          setShowPayment(false);
          setUpgradeAfterLogin(true);
          setShowLogin(true);
        }}
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
  purchaseName: { flexShrink: 1, marginRight: spacing.sm },
  moreBtn: { alignItems: "center", paddingVertical: spacing.sm },
  moreBtnText: { fontSize: 14, fontWeight: "600", color: colors.primary },
});
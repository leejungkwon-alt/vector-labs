import React, { useState, useEffect } from "react";
import { ActivityIndicator, Alert, Modal, Platform, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { ApiError } from "@/api/client";
import { useT } from "@/i18n";

interface Props {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function SocialLoginModal({ visible, onClose, onSuccess }: Props) {
  const linkAccount = useAuthStore((s) => s.linkAccount);
  const signInWithProvider = useAuthStore((s) => s.signInWithProvider);
  const t = useT();
  const [loading, setLoading] = useState<string | null>(null);
  const [mode, setMode] = useState<"link" | "login">("login");
  const [isTelegram, setIsTelegram] = useState(false);
  useEffect(() => { setIsTelegram(!!(window as any).Telegram?.WebApp?.initData); }, []);

  const handleTelegramLogin = async () => {
    setLoading("telegram");
    try {
      await useAuthStore.getState().loginWithTelegram();
      onSuccess();
    } catch (e: any) {
      alert(e.message || t("socialLogin.loginFailed"));
    } finally {
      setLoading(null);
    }
  };

  const handleLogin = async (provider: "apple" | "google" | "kakao") => {
    setLoading(provider);
    try {
      if (mode === "login") {
        await signInWithProvider(provider);
      } else {
        await linkAccount(provider);
      }
      onSuccess();
    } catch (e: any) {
      if (mode === "login" && e instanceof ApiError && e.status === 404) {
        setMode("link");
        const msg = t("socialLogin.noAccountPrompt");
        if (typeof Platform !== "undefined" && Platform.OS === "web") window.alert(msg);
        else Alert.alert(t("common.notice"), msg);
      } else {
        const msg = e?.message || t("socialLogin.loginFailed");
        if (typeof Platform !== "undefined" && Platform.OS === "web") window.alert(msg);
        else Alert.alert(t("common.notice"), msg);
      }
    } finally {
      setLoading(null);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.overlay}>
        {/* 🎨 모드에 따라 배경색과 미세한 테두리 톤을 다르게 적용 */}
        <View style={[
          styles.card, 
          mode === "link" ? styles.linkCard : styles.loginCard
        ]}>
          <Text style={styles.title}>
            {mode === "login" ? t("socialLogin.loginTitle") : t("socialLogin.title")}
          </Text>
          <Text style={styles.desc}>
            {mode === "login" ? t("socialLogin.loginDesc") : t("socialLogin.desc")}
          </Text>

          {!isTelegram && (
            <TouchableOpacity style={[styles.btn, styles.googleBtn]} onPress={() => handleLogin("google")} disabled={!!loading}>
              {loading === "google" ? <ActivityIndicator color="#000" /> : (
                <Text style={styles.btnTextBlack}>
                  {mode === "login" ? t("socialLogin.googleLoginCta") : t("socialLogin.googleCta")}
                </Text>
              )}
            </TouchableOpacity>
          )}

          {!isTelegram && (
            <TouchableOpacity style={[styles.btn, styles.kakaoBtn]} onPress={() => handleLogin("kakao")} disabled={!!loading}>
              {loading === "kakao" ? <ActivityIndicator color="#000" /> : (
                <Text style={styles.btnTextBlack}>
                  {mode === "login" ? t("socialLogin.kakaoLoginCta") : t("socialLogin.kakaoCta")}
                </Text>
              )}
            </TouchableOpacity>
          )}

          {isTelegram && (
            <TouchableOpacity style={[styles.btn, { backgroundColor: "#0088cc" }]} onPress={handleTelegramLogin} disabled={!!loading}>
              {loading === "telegram" ? <ActivityIndicator color="#FFF" /> : (
                <Text style={styles.btnTextWhite}>{t("socialLogin.telegramCta")}</Text>
              )}
            </TouchableOpacity>
          )}

          {!isTelegram && (
            <View style={styles.divider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>{t("socialLogin.or")}</Text>
              <View style={styles.dividerLine} />
            </View>
          )}

          {!isTelegram && (
            <TouchableOpacity
              style={styles.modeToggle}
              onPress={() => setMode(mode === "login" ? "link" : "login")}
              disabled={!!loading}
            >
              <Text style={styles.modeToggleText}>
                {mode === "login" ? t("socialLogin.switchToLink") : t("socialLogin.switchToLogin")}
              </Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity style={styles.closeBtn} onPress={onClose} disabled={!!loading}>
            <Text style={styles.closeText}>{t("socialLogin.later")}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center", padding: 20 },
  
  // 기본 공통 카드 스타일
  card: { width: "100%", maxWidth: 340, borderRadius: radius.lg, padding: 24, alignItems: "center", shadowColor: "#000", shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.15, shadowRadius: 12, elevation: 5 },
  
  // 🔑 로그인 모드 배경 (깔끔한 기본 서피스 톤)
  loginCard: { backgroundColor: colors.surface },
  
  // 🔗 계정 연동 모드 배경 (눈에 띄게 구분되도록 따뜻한 미세 베이지/오렌지빛 또는 테두리 강조)
  linkCard: { backgroundColor: "#FFF8F3", borderWidth: 1.5, borderColor: "#FEE2D5" },

  title: { fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 8, textAlign: "center" },
  desc: { fontSize: 14, color: colors.textMuted, textAlign: "center", lineHeight: 20, marginBottom: 24 },
  btn: { flexDirection: "row", alignItems: "center", justifyContent: "center", width: "100%", padding: 14, borderRadius: radius.md, marginBottom: 12, gap: 8 },
  googleBtn: { backgroundColor: "#FFF", borderWidth: 1, borderColor: "#CCC" },
  kakaoBtn: { backgroundColor: "#FEE500" },
  btnTextWhite: { color: colors.onPrimary, fontSize: 16, fontWeight: "600" },
  btnTextBlack: { color: "#000", fontSize: 16, fontWeight: "600" },
  closeBtn: { marginTop: 12, padding: 8 },
  closeText: { color: colors.textMuted, fontSize: 14 },
  divider: { flexDirection: "row", alignItems: "center", width: "100%", marginVertical: 12 },
  dividerLine: { flex: 1, height: 1, backgroundColor: colors.border },
  dividerText: { marginHorizontal: 12, color: colors.textMuted, fontSize: 12 },
  modeToggle: { paddingVertical: 10, paddingHorizontal: 16 },
  modeToggleText: { color: colors.primary, fontSize: 14, fontWeight: "600" },
});
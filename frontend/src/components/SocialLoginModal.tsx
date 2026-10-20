import React, { useState } from "react";
import { Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { useAuthStore } from "@/store/authStore";

interface Props {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function SocialLoginModal({ visible, onClose, onSuccess }: Props) {
  const linkAccount = useAuthStore((s) => s.linkAccount);
  const [loading, setLoading] = useState<string | null>(null);

  const handleLogin = async (provider: "apple" | "google" | "kakao") => {
    setLoading(provider);
    try {
      await linkAccount(provider);
      onSuccess();
    } catch (e: any) {
      alert(e.message || "로그인에 실패했습니다.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.card}>
          <Text style={styles.title}>계정 연결</Text>
          <Text style={styles.desc}>
            기기를 변경하거나 앱을 삭제해도{"\n"}내 사주 데이터와 결제 정보를 안전하게 보관합니다.
          </Text>

          <TouchableOpacity style={[styles.btn, styles.appleBtn]} onPress={() => handleLogin("apple")} disabled={!!loading}>
            {loading === "apple" ? <ActivityIndicator color="#FFF" /> : (
              <>
                <Ionicons name="logo-apple" size={20} color="#FFF" />
                <Text style={styles.btnTextWhite}>Apple로 계속하기</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={[styles.btn, styles.googleBtn]} onPress={() => handleLogin("google")} disabled={!!loading}>
            {loading === "google" ? <ActivityIndicator color="#000" /> : (
              <>
                <Ionicons name="logo-google" size={20} color="#000" />
                <Text style={styles.btnTextBlack}>Google로 계속하기</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={[styles.btn, styles.kakaoBtn]} onPress={() => handleLogin("kakao")} disabled={!!loading}>
            {loading === "kakao" ? <ActivityIndicator color="#000" /> : (
              <>
                <Ionicons name="chatbubble" size={20} color="#000" />
                <Text style={styles.btnTextBlack}>카카오로 계속하기</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={styles.closeBtn} onPress={onClose} disabled={!!loading}>
            <Text style={styles.closeText}>나중에 하기</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", alignItems: "center", padding: 20 },
  card: { backgroundColor: colors.surface, width: "100%", maxWidth: 340, borderRadius: radius.lg, padding: 24, alignItems: "center" },
  title: { fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 8 },
  desc: { fontSize: 14, color: colors.textMuted, textAlign: "center", lineHeight: 20, marginBottom: 24 },
  btn: { flexDirection: "row", alignItems: "center", justifyContent: "center", width: "100%", padding: 14, borderRadius: radius.md, marginBottom: 12, gap: 8 },
  appleBtn: { backgroundColor: "#000" },
  googleBtn: { backgroundColor: "#FFF", borderWidth: 1, borderColor: "#CCC" },
  kakaoBtn: { backgroundColor: "#FEE500" },
  btnTextWhite: { color: "#FFF", fontSize: 16, fontWeight: "600" },
  btnTextBlack: { color: "#000", fontSize: 16, fontWeight: "600" },
  closeBtn: { marginTop: 12, padding: 8 },
  closeText: { color: colors.textMuted, fontSize: 14 },
});

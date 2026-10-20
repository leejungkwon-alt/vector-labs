import React, { useState } from "react";
import { Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { api } from "@/api/client";
import { useAuthStore } from "@/store/authStore";

interface Props {
  visible: boolean;
  onClose: () => void;
}

export function PaymentModal({ visible, onClose }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const bootstrap = useAuthStore((s) => s.bootstrap);

  const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      await api.purchase(productId);
      await bootstrap(); // 유저 정보(티어/애드온) 갱신
      Alert.alert("결제 완료", "잠금이 해제되었습니다! 리포트를 새로고침합니다.");
      onClose();
      // 브라우저 강제 새로고침 (새로운 데이터 반영)
      if (typeof window !== "undefined") {
        window.location.reload();
      }
    } catch (e: any) {
      Alert.alert("결제 실패", e.message || "다시 시도해주세요.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>Gyeol 프리미엄</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeIcon}>
              <Ionicons name="close" size={24} color={colors.textMuted} />
            </TouchableOpacity>
          </View>
          <Text style={styles.desc}>나에게 꼭 필요한 맞춤형 결제를 선택하세요.</Text>

          {/* 1. 구독 */}
          <TouchableOpacity style={[styles.planBox, { borderColor: colors.primary, backgroundColor: colors.primary + "05" }]} onPress={() => handlePay("sub_monthly_3900")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <Text style={styles.planName}>월간 구독</Text>
                <View style={{ backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}><Text style={{ color: "#FFF", fontSize: 10, fontWeight: "700" }}>추천</Text></View>
              </View>
              <Text style={styles.planDetail}>데일리 운세, 월운, 모든 심층 리포트 무제한</Text>
              <Text style={styles.planPrice}>₩3,900 / 월</Text>
            </View>
            {loading === "sub_monthly_3900" ? <ActivityIndicator color={colors.primary} /> : <Ionicons name="chevron-forward" size={24} color={colors.primary} />}
          </TouchableOpacity>

          {/* 2. 심화 리포트 단건 */}
          <TouchableOpacity style={styles.planBox} onPress={() => handlePay("addon_deep_990")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>심화 리포트 (연애/커리어/재물)</Text>
              <Text style={styles.planDetail}>내 사주의 숨겨진 패턴과 궁합, 액션 플랜</Text>
              <Text style={styles.planPrice}>₩990 (단건)</Text>
            </View>
            {loading === "addon_deep_990" ? <ActivityIndicator color={colors.textMuted} /> : <Ionicons name="chevron-forward" size={24} color={colors.textMuted} />}
          </TouchableOpacity>

          {/* 3. 궁합 단건 */}
          <TouchableOpacity style={styles.planBox} onPress={() => handlePay("addon_compat_1900")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>프리미엄 궁합</Text>
              <Text style={styles.planDetail}>상대방과의 4축 케미 및 맞춤 조언</Text>
              <Text style={styles.planPrice}>₩1,900 (단건)</Text>
            </View>
            {loading === "addon_compat_1900" ? <ActivityIndicator color={colors.textMuted} /> : <Ionicons name="chevron-forward" size={24} color={colors.textMuted} />}
          </TouchableOpacity>

          <Text style={styles.terms}>언제든지 해지할 수 있으며, 결제는 모의(시뮬레이션)로 처리됩니다.</Text>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  card: { backgroundColor: colors.surface, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: 24, paddingBottom: 40 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text },
  closeIcon: { padding: 4 },
  desc: { fontSize: 14, color: colors.textMuted, marginBottom: 20 },
  planBox: { flexDirection: "row", alignItems: "center", borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: 16, marginBottom: 12 },
  planName: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: 2 },
  planDetail: { fontSize: 13, color: colors.textMuted, marginBottom: 6 },
  planPrice: { fontSize: 15, fontWeight: "600", color: colors.primary },
  terms: { textAlign: "center", fontSize: 11, color: colors.textMuted, marginTop: 12 },
});

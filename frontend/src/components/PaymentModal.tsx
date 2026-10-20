import React, { useState } from "react";
import { Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";

interface Props {
  visible: boolean;
  onClose: () => void;
}

export function PaymentModal({ visible, onClose }: Props) {
  const [plan, setPlan] = useState<"monthly" | "yearly">("yearly");
  const [loading, setLoading] = useState(false);

  const handlePay = () => {
    setLoading(true);
    // TODO: 실제 IAP (react-native-iap) 연동 필요
    setTimeout(() => {
      setLoading(false);
      alert("결제 시뮬레이션 성공!\n(실제 앱에서는 Apple/Google 결제창이 뜹니다.)");
      onClose();
    }, 1500);
  };

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>프리미엄 업그레이드</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeIcon}>
              <Ionicons name="close" size={24} color={colors.textMuted} />
            </TouchableOpacity>
          </View>
          <Text style={styles.desc}>모든 데일리 에너지, 궁합, 심층 리포트를 무제한으로 확인하세요.</Text>

          <TouchableOpacity style={[styles.planBox, plan === "yearly" && styles.planBoxActive]} onPress={() => setPlan("yearly")}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>연간 구독 (40% 할인)</Text>
              <Text style={styles.planPrice}>₩39,000 / 년</Text>
            </View>
            <Ionicons name={plan === "yearly" ? "radio-button-on" : "radio-button-off"} size={24} color={colors.primary} />
          </TouchableOpacity>

          <TouchableOpacity style={[styles.planBox, plan === "monthly" && styles.planBoxActive]} onPress={() => setPlan("monthly")}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>월간 구독</Text>
              <Text style={styles.planPrice}>₩5,500 / 월</Text>
            </View>
            <Ionicons name={plan === "monthly" ? "radio-button-on" : "radio-button-off"} size={24} color={colors.primary} />
          </TouchableOpacity>

          <TouchableOpacity style={styles.payBtn} onPress={handlePay} disabled={loading}>
            {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.payBtnText}>결제하기</Text>}
          </TouchableOpacity>
          <Text style={styles.terms}>언제든지 해지할 수 있습니다.</Text>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "flex-end" },
  card: { backgroundColor: colors.surface, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg, padding: 24, paddingBottom: 40 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text },
  closeIcon: { padding: 4 },
  desc: { fontSize: 14, color: colors.textMuted, marginBottom: 24, lineHeight: 20 },
  planBox: { flexDirection: "row", alignItems: "center", borderWidth: 1, borderColor: colors.border, borderRadius: radius.md, padding: 16, marginBottom: 12 },
  planBoxActive: { borderColor: colors.primary, backgroundColor: colors.primary + "05" },
  planName: { fontSize: 16, fontWeight: "600", color: colors.text, marginBottom: 4 },
  planPrice: { fontSize: 15, color: colors.textMuted },
  payBtn: { backgroundColor: colors.primary, padding: 16, borderRadius: radius.md, alignItems: "center", marginTop: 12 },
  payBtnText: { color: "#FFF", fontSize: 17, fontWeight: "700" },
  terms: { textAlign: "center", fontSize: 12, color: colors.textMuted, marginTop: 16 },
});

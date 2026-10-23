import { useQueryClient } from '@tanstack/react-query';
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
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState<string | null>(null);
  const bootstrap = useAuthStore((s) => s.bootstrap);

  const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      await api.purchase(productId);
      try { await queryClient.invalidateQueries(); }
      catch (e) { console.warn('[FIX-21] cache invalidate failed', e); }
      await bootstrap();   // 한 번만
      Alert.alert("Payment Successful", "The locked content has been unlocked.");
      onClose();
    } catch (e: any) {
      Alert.alert("Payment Failed", e.message || "Please try again.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>Gyeol Premium</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeIcon}>
              <Ionicons name="close" size={24} color={colors.textMuted} />
            </TouchableOpacity>
          </View>
          <Text style={styles.desc}>Choose the plan that fits your journey.</Text>

          {/* 1. 구독 */}
          <TouchableOpacity style={[styles.planBox, { borderColor: colors.primary, backgroundColor: colors.primary + "05" }]} onPress={() => handlePay("sub_monthly_299")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <Text style={styles.planName}>Monthly Subscription</Text>
                <View style={{ backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}><Text style={{ color: colors.onPrimary, fontSize: 10, fontWeight: "700" }}>BEST</Text></View>
              </View>
              <Text style={styles.planDetail}>Daily, Monthly & All Deep Reports</Text>
              <Text style={styles.planPrice}>$2.99 / month</Text>
            </View>
            {loading === "sub_monthly_299" ? <ActivityIndicator color={colors.primary} /> : <Ionicons name="chevron-forward" size={24} color={colors.primary} />}
          </TouchableOpacity>

          {/* 2. 심화 리포트 단건 */}
          <TouchableOpacity style={styles.planBox} onPress={() => handlePay("addon_deep_099")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>Deep Report</Text>
              <Text style={styles.planDetail}>Love, Career & Wealth patterns</Text>
              <Text style={styles.planPrice}>$0.99 (one-time)</Text>
            </View>
            {loading === "addon_deep_099" ? <ActivityIndicator color={colors.textMuted} /> : <Ionicons name="chevron-forward" size={24} color={colors.textMuted} />}
          </TouchableOpacity>

          {/* 3. 궁합 단건 */}
          <TouchableOpacity style={styles.planBox} onPress={() => handlePay("addon_compat_199")} disabled={!!loading}>
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>Premium Compatibility</Text>
              <Text style={styles.planDetail}>4-axis chemistry with your partner</Text>
              <Text style={styles.planPrice}>$1.99 (one-time)</Text>
            </View>
            {loading === "addon_compat_199" ? <ActivityIndicator color={colors.textMuted} /> : <Ionicons name="chevron-forward" size={24} color={colors.textMuted} />}
          </TouchableOpacity>

          <Text style={styles.terms}>Cancel anytime. Simulated checkout for global testing.</Text>
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

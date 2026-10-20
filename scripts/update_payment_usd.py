#!/usr/bin/env python3
"""
scripts/update_payment_usd.py

수익화 모델 달러($)화 적용
  1. iap.py: 상품 ID 변경 (sub_monthly_299, addon_deep_099, addon_compat_199)
  2. PaymentModal.tsx: 글로벌 달러 가격 표기 및 영문/국문 병기 UI
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

def patch_iap():
    p = ROOT / "app" / "services" / "iap.py"
    if not p.exists(): return
    text = p.read_text(encoding="utf-8")
    
    text = text.replace('"premium_monthly"', '"sub_monthly_299"')
    text = text.replace('"addon_compatibility"', '"addon_compat_199"')
    text = text.replace('"addon_deep_990"', '"addon_deep_099"')
    
    # 기존 로직이 남아있을 경우를 대비해 확실하게 교체
    if '"sub_monthly_299"' not in text:
        text = text.replace(
            'if product_id == "sub_monthly_3900":',
            'if product_id == "sub_monthly_299":'
        ).replace(
            'if product_id == "addon_compat_1900":',
            'if product_id == "addon_compat_199":'
        )
        
    p.write_text(text, encoding="utf-8")
    print("  [OK] iap.py: 상품 ID 달러 기준으로 업데이트")

NEW_PAYMENT_MODAL = '''import React, { useState } from "react";
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
      Alert.alert("Payment Successful", "The locked content has been unlocked.");
      onClose();
      if (typeof window !== "undefined") {
        window.location.reload();
      }
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
                <View style={{ backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}><Text style={{ color: "#FFF", fontSize: 10, fontWeight: "700" }}>BEST</Text></View>
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
'''

def main():
    print("=" * 60)
    print("  결제 UI/상품 글로벌 달러($)화 적용")
    print("=" * 60)

    patch_iap()
    
    p_modal = FRONTEND / "src" / "components" / "PaymentModal.tsx"
    p_modal.write_text(NEW_PAYMENT_MODAL, encoding="utf-8")
    print("  [OK] PaymentModal.tsx: 글로벌 달러($) UI로 전면 개편")

    print("\n[git] add → commit → push")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "fix(payment): update pricing to USD ($2.99 / $1.99 / $0.99) for global launch"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
        print("\n[done] 커밋 + 푸시 완료")
    except subprocess.CalledProcessError:
        print("\n[!!] git 커밋 실패")

if __name__ == "__main__":
    main()
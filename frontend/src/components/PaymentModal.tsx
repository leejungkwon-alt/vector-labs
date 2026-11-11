import * as RNIap from 'react-native-iap';
import { useQueryClient } from '@tanstack/react-query';
import React, { useState } from "react";
import { Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert } from "react-native";
import { colors, radius, spacing } from "@/theme";
import { api } from "@/api/client";
import { useAuthStore } from "@/store/authStore";
import { Platform, Linking } from 'react-native';

interface Props {
  visible: boolean;
  onClose: () => void;
  onRequireLogin?: () => void;
}

export function PaymentModal({ visible, onClose, onRequireLogin }: Props) {
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState<string | null>(null);

  const [iapReady, setIapReady] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const initIAP = async () => {
      if (Platform.OS === 'android' && !isTelegramEnv) {
        try {
          await RNIap.initConnection();
          if (isMounted) setIapReady(true);
          console.log('IAP Connection initialized');
        } catch (err) {
          console.warn('IAP init error:', err);
        }
      }
    };
    initIAP();
    return () => {
      isMounted = false;
      if (Platform.OS === 'android' && !isTelegramEnv) {
        RNIap.endConnection();
      }
    };
  }, [isTelegramEnv]);

  const bootstrap = useAuthStore((s) => s.bootstrap);
  const user = useAuthStore((s) => s.user);
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;

  const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      const tg = (window as any).Telegram?.WebApp;
      const isTelegram = !!tg?.initData;

      // --- 1. 안드로이드 앱 (구글 플레이 결제) ---
      if (Platform.OS === 'android' && !isTelegram) {
        if (!iapReady) {
          alert("구글 플레이 결제 모듈을 불러오는 중입니다. 잠시 후 다시 시도해 주세요.");
          setLoading(null);
          return;
        }
        try {
          const sku = productId === "onetime" ? "gyeol_onetime_credit" : "gyeol_premium_monthly";
          const purchase = productId === "onetime"
            ? await RNIap.requestPurchase({ sku })
            : await RNIap.requestSubscription({ sku });

          if (purchase) {
            // TODO: 백엔드 영수증 검증 API 호출
            await RNIap.finishTransaction({ purchase: purchase as any, isConsumable: productId === "onetime" });
            alert("결제가 완료되었습니다! (서버 검증 연동 필요)");
            onClose();
            bootstrap();
          }
        } catch (err: any) {
          if (err.code !== 'E_USER_CANCELLED') {
            alert("결제 중 오류가 발생했습니다: " + err.message);
          }
        }
        setLoading(null);
        return;
      }

      // --- 2. 텔레그램 스타 결제 ---
      if (isTelegram) {
        try {
          const { invoice_link } = productId === "onetime"
            ? await api.createStarsInvoiceOnetime()
            : await api.createStarsInvoice();
          tg.openInvoice(invoice_link, (status: string) => {
            if (status === "paid") {
              alert("결제 완료! 프리미엄이 활성화되었습니다.");
              window.location.reload();
            }
          });
        } catch (e: any) {
          alert("결제 오류: " + (e.message || "텔레그램 결제를 시작할 수 없습니다."));
        }
        setLoading(null);
        return;
      }

      // --- 3. 일반 웹 (레몬 스퀴지) ---
      const { url } = await api.checkout(productId === 'onetime');
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      alert("Checkout Failed: " + (e.message || "Please try again."));
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
              <Text style={{ fontSize: 22, color: colors.textMuted, lineHeight: 24 }}>✕</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.desc}>Unlock all deep reports and daily insights.</Text>

          {/* 💎 프리미엄 구독 플랜 (단일화) */}
          <TouchableOpacity 
            style={[styles.planBox, { borderColor: colors.primary, backgroundColor: colors.primary + "05" }]} 
            onPress={() => handlePay("sub_monthly_699")} 
            disabled={!!loading}
          >
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <Text style={styles.planName}>Premium Subscription</Text>
                <View style={{ backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}>
                  <Text style={{ color: colors.onPrimary, fontSize: 10, fontWeight: "700" }}>BEST</Text>
                </View>
              </View>
              <Text style={styles.planDetail}>Daily, Monthly & All Deep Reports</Text>
              <Text style={styles.planPrice}>{isTelegramEnv ? "400 Stars / month (Auto-renews)" : "$6.99 / month (Auto-renews. Cancel anytime.)"}</Text>
            </View>
            {loading === "sub_monthly_699" ? (
              <ActivityIndicator color={colors.primary} />
            ) : (
              <Text style={{ fontSize: 26, color: colors.primary, lineHeight: 26 }}>›</Text>
            )}
          </TouchableOpacity>

          {/* 💳 일시불 단품 결제 (One-time) */}
          <TouchableOpacity 
            style={[styles.planBox, { borderColor: colors.border, backgroundColor: colors.surface, marginTop: 12 }]} 
            onPress={() => handlePay("onetime")} 
            disabled={!!loading}
          >
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>Deep Report (1-time)</Text>
              <Text style={styles.planDetail}>Unlock one deep report. No subscription.</Text>
              <Text style={styles.planPrice}>{isTelegramEnv ? "150 Stars" : "$2.99 (One-time)"}</Text>
            </View>
            {loading === "onetime" ? (
              <ActivityIndicator color={colors.textMuted} />
            ) : (
              <Text style={{ fontSize: 26, color: colors.textMuted, lineHeight: 26 }}>›</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.terms}>{isTelegramEnv ? "Secure checkout powered by Telegram Stars." : "Secure checkout powered by Lemon Squeezy."}</Text>
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
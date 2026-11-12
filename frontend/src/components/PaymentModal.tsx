import * as RNIap from "react-native-iap";
import React, { useState, useEffect, useRef } from "react";
import {
  Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert,
  Platform, Linking,
} from "react-native";
import { colors, radius, spacing } from "@/theme";
import { api } from "@/api/client";
import { useAuthStore } from "@/store/authStore";

// Play Console에 등록한 상품 ID와 정확히 같아야 합니다.
const SKU_ONETIME = "gyeol_onetime_credit"; // 관리형 상품(1회권)
const SKU_SUBS = "gyeol_premium_monthly"; // 구독

interface Props {
  visible: boolean;
  onClose: () => void;
  onRequireLogin?: () => void;
}

export function PaymentModal({ visible, onClose, onRequireLogin }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [iapReady, setIapReady] = useState(false);

  const bootstrap = useAuthStore((s) => s.bootstrap);
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;
  const isAndroidApp = Platform.OS === "android" && !isTelegramEnv;

  // 리스너 안에서 최신 함수를 쓰기 위한 ref
  const onCloseRef = useRef(onClose);
  const bootstrapRef = useRef(bootstrap);
  useEffect(() => { onCloseRef.current = onClose; }, [onClose]);
  useEffect(() => { bootstrapRef.current = bootstrap; }, [bootstrap]);

  // 같은 구매가 두 번 처리되지 않도록 기록
  const processedRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!isAndroidApp) return;
    let mounted = true;
    const IAP: any = RNIap;

    // 구매 결과는 requestPurchase의 반환값이 아니라 이 리스너로 옵니다.
    const updateSub = IAP.purchaseUpdatedListener(async (purchase: any) => {
      try {
        const token: string = purchase?.purchaseToken ?? "";
        const sku: string = purchase?.productId ?? purchase?.ids?.[0] ?? "";
        if (purchase?.purchaseState === "pending") return; // 결제 보류 중
        if (token && processedRef.current.has(token)) return;
        if (token) processedRef.current.add(token);

        // 서버 검증: api.verifyGooglePurchase 를 백엔드에 만든 뒤 연결하세요.
        // 검증이 성공한 뒤에만 finishTransaction 을 호출해야 안전합니다.
        const verify = (api as any).verifyGooglePurchase;
        if (typeof verify === "function") {
          await verify({ sku, purchaseToken: token, productId: sku });
        } else {
          console.warn("[IAP] 서버 검증 API가 아직 없습니다. 검증 없이 처리됩니다.");
        }

        await IAP.finishTransaction({ purchase, isConsumable: sku === SKU_ONETIME });

        if (mounted) {
          setLoading(null);
          Alert.alert("결제 완료", "결제가 완료되었습니다.");
          onCloseRef.current();
          bootstrapRef.current();
        }
      } catch (e: any) {
        if (mounted) setLoading(null);
        Alert.alert("결제 처리 오류", String(e?.message ?? e));
      }
    });

    const errorSub = IAP.purchaseErrorListener((err: any) => {
      const code = String(err?.code ?? "");
      const cancelled = code === "user-cancelled" || code === "E_USER_CANCELLED";
      if (mounted) setLoading(null);
      if (!cancelled) Alert.alert("결제 오류", String(err?.message ?? err));
    });

    (async () => {
      try {
        await RNIap.initConnection();
        if (mounted) setIapReady(true);
      } catch (err) {
        console.warn("IAP init error:", err);
      }
    })();

    return () => {
      mounted = false;
      updateSub?.remove?.();
      errorSub?.remove?.();
      RNIap.endConnection();
    };
  }, [isAndroidApp]);

  const handlePay = async (productId: string) => {
    setLoading(productId);
    let keepLoading = false; // 구글 결제 창이 떠 있는 동안 버튼 잠금 유지
    try {
      const tgNow = (window as any)?.Telegram?.WebApp;
      const isTelegram = !!tgNow?.initData;

      // --- 1. 안드로이드 앱 (구글 플레이 결제) ---
      if (Platform.OS === "android" && !isTelegram) {
        if (!iapReady) {
          Alert.alert("잠시만요", "구글 플레이 결제 모듈을 불러오는 중입니다. 잠시 후 다시 시도해 주세요.");
          return;
        }
        const IAP: any = RNIap;
        const isOnetime = productId === "onetime";
        const sku = isOnetime ? SKU_ONETIME : SKU_SUBS;
        const type = isOnetime ? "in-app" : "subs";

        try {
          // 안드로이드는 구매 전에 상품 정보를 먼저 조회해야 합니다.
          const fetched: any = await IAP.fetchProducts({ skus: [sku], type });
          const products: any[] = Array.isArray(fetched) ? fetched : [];
          const product = products.find((p) => (p?.id ?? p?.productId) === sku);
          if (!product) {
            throw new Error(
              "상품 정보를 불러오지 못했습니다. Play Console의 상품 ID와 활성 상태를 확인하세요. (" + sku + ")"
            );
          }

          if (isOnetime) {
            await IAP.requestPurchase({
              request: { google: { skus: [sku] } },
              type: "in-app",
            });
          } else {
            const offer = product.subscriptionOffers?.[0];
            const offerToken =
              offer?.offerTokenAndroid ??
              offer?.offerToken ??
              product.subscriptionOfferDetailsAndroid?.[0]?.offerToken;
            if (!offerToken) {
              throw new Error(
                "구독 오퍼를 찾지 못했습니다: " +
                  JSON.stringify(product.subscriptionOffers ?? null).slice(0, 300)
              );
            }
            await IAP.requestPurchase({
              request: { google: { skus: [sku], subscriptionOffers: [{ sku, offerToken }] } },
              type: "subs",
            });
          }
          // 결과는 purchaseUpdatedListener / purchaseErrorListener 로 옵니다.
          keepLoading = true;
        } catch (err: any) {
          const code = String(err?.code ?? "");
          if (code !== "user-cancelled" && code !== "E_USER_CANCELLED") {
            Alert.alert("결제 오류", String(err?.message ?? err));
          }
        }
        return;
      }

      // --- 2. 텔레그램 스타 결제 ---
      if (isTelegram) {
        try {
          const { invoice_link } =
            productId === "onetime"
              ? await api.createStarsInvoiceOnetime()
              : await api.createStarsInvoice();
          tgNow.openInvoice(invoice_link, (status: string) => {
            if (status === "paid") {
              alert("결제 완료! 프리미엄이 활성화되었습니다.");
              window.location.reload();
            }
          });
        } catch (e: any) {
          alert("결제 오류: " + (e.message || "텔레그램 결제를 시작할 수 없습니다."));
        }
        return;
      }

      // --- 3. 일반 웹 (레몬 스퀴지) ---
      const { url } = await api.checkout(productId === "onetime");
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      Alert.alert("Checkout Failed", String(e?.message || "Please try again."));
    } finally {
      if (!keepLoading) setLoading(null);
    }
  };

  const termsText = isTelegramEnv
    ? "Secure checkout powered by Telegram Stars."
    : Platform.OS === "android"
    ? "Secure checkout powered by Google Play."
    : "Secure checkout powered by Lemon Squeezy.";

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

          {/* 💎 프리미엄 구독 플랜 */}
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
              <Text style={styles.planPrice}>
                {isTelegramEnv ? "400 Stars / month (Auto-renews)" : "$6.99 / month (Auto-renews. Cancel anytime.)"}
              </Text>
            </View>
            {loading === "sub_monthly_699" ? (
              <ActivityIndicator color={colors.primary} />
            ) : (
              <Text style={{ fontSize: 26, color: colors.primary, lineHeight: 26 }}>›</Text>
            )}
          </TouchableOpacity>

          {/* 💳 일시불 단품 결제 */}
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

          <Text style={styles.terms}>{termsText}</Text>
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
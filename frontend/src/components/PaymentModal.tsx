import * as RNIap from "react-native-iap";
import React, { useState, useEffect, useRef } from "react";
import {
  Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert,
  Platform, Linking, ScrollView,
} from "react-native";
import { colors, radius, spacing } from "@/theme";
import { api } from "@/api/client";
import { useAuthStore } from "@/store/authStore";
import { useQueryClient } from "@tanstack/react-query";
import { useT } from "@/i18n";

// Play Console에 등록한 상품 ID와 정확히 일치해야 합니다.
const SKU_ONETIME = "gyeol_onetime_credit"; // 관리형 상품(1회권)
const SKU_SUBS = "gyeol_premium_monthly"; // 구독

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

// 구글 결제는 반영/응답이 느릴 수 있어서, 서버 확인을 바로 포기하지 않고 몇 번 기다렸다가 다시 시도한다.
// 재시도 대상: 네트워크 끊김/타임아웃(0, 408), 결제 보류(409), 서버 오류(5xx), 구글 반영 지연으로 인한 400.
// 로그인 만료(401), 다른 계정 구매(403) 같은 확정 오류는 바로 중단한다.
const VERIFY_RETRY_DELAYS_MS = [0, 3000, 5000, 8000, 12000];
async function verifyWithRetry(payload: { sku: string; purchaseToken: string; productId?: string }) {
  let lastErr: any;
  for (const delay of VERIFY_RETRY_DELAYS_MS) {
    if (delay) await sleep(delay);
    try {
      return await api.verifyGooglePurchase(payload);
    } catch (e: any) {
      lastErr = e;
      const s = Number(e?.status);
      const retryable = s === 0 || s === 408 || s === 409 || s === 400 || s >= 500;
      if (!retryable) throw e;
    }
  }
  throw lastErr;
}

interface Props {
  visible: boolean;
  onClose: () => void;
  onRequireLogin?: () => void;
}

export function PaymentModal({ visible, onClose, onRequireLogin }: Props) {
  const [loading, setLoading] = useState<string | null>(null);
  const [iapReady, setIapReady] = useState(false);
  const [verifying, setVerifying] = useState(false); // 결제 후 서버 확인 중
  const t = useT();

  const bootstrap = useAuthStore((s) => s.bootstrap);
  const queryClient = useQueryClient();
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;
  const isAndroidApp = Platform.OS === "android" && !isTelegramEnv;

  // 리스너 안에서 최신 함수를 쓰기 위한 ref
  const onCloseRef = useRef(onClose);
  const bootstrapRef = useRef(bootstrap);
  const queryClientRef = useRef(queryClient);
  useEffect(() => { onCloseRef.current = onClose; }, [onClose]);
  useEffect(() => { bootstrapRef.current = bootstrap; }, [bootstrap]);
  useEffect(() => { queryClientRef.current = queryClient; }, [queryClient]);

  // 같은 구매가 두 번 처리되지 않도록 기록
  const processedRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!isAndroidApp) return;
    let mounted = true;
    const IAP: any = RNIap;

    // 구매 결과 리스너
    const updateSub = IAP.purchaseUpdatedListener(async (purchase: any) => {
      try {
        const token: string = purchase?.purchaseToken ?? "";
        const sku: string = purchase?.productId ?? purchase?.ids?.[0] ?? "";
        if (purchase?.purchaseState === "pending") {
          // 결제 승인 대기: 스피너가 영원히 돌지 않게 풀고 안내한다.
          if (mounted) {
            setLoading(null);
            Alert.alert(t("common.notice"), t("payment.pendingNotice"));
          }
          return;
        }
        if (token && processedRef.current.has(token)) return;
        if (token) processedRef.current.add(token);

        if (!token) throw new Error("Missing purchase token.");
        if (mounted) setVerifying(true);
        try {
          await verifyWithRetry({ sku, purchaseToken: token, productId: sku });
        } catch (e) {
          processedRef.current.delete(token); // allow retry
          throw e; // do not finish the purchase when server verification fails
        }

        await IAP.finishTransaction({ purchase, isConsumable: sku === SKU_ONETIME });

        if (mounted) {
          setLoading(null);
          Alert.alert(t("common.notice"), t("payment.successTitle"));
          onCloseRef.current();
          bootstrapRef.current();
          queryClientRef.current.invalidateQueries(); // refetch report/daily/etc. so locked content opens
        }
      } catch (e: any) {
        if (mounted) setLoading(null);
        const s = Number(e?.status);
        const delayed = s === 0 || s === 408 || s === 409 || s >= 500;
        Alert.alert(t("payment.failTitle"), delayed ? t("payment.verifyDelayed") : String(e?.message ?? e));
      } finally {
        if (mounted) setVerifying(false);
      }
    });

    const errorSub = IAP.purchaseErrorListener((err: any) => {
      const code = String(err?.code ?? "");
      const cancelled = code === "user-cancelled" || code === "E_USER_CANCELLED";
      if (mounted) setLoading(null);
      if (!cancelled) Alert.alert(t("payment.failTitle"), String(err?.message ?? err));
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
    let keepLoading = false; 
    try {
      const tgNow = (window as any)?.Telegram?.WebApp;
      const isTelegram = !!tgNow?.initData;

      // --- 1. 안드로이드 앱 (구글 플레이 결제) ---
      if (Platform.OS === "android" && !isTelegram) {
        if (!iapReady) {
          Alert.alert(t("common.notice"), t("payment.iapLoading"));
          setLoading(null);
          return;
        }
        const IAP: any = RNIap;
        const isOnetime = productId === "onetime";
        const sku = isOnetime ? SKU_ONETIME : SKU_SUBS;
        const type = isOnetime ? "in-app" : "subs";

        try {
          const fetched: any = await IAP.fetchProducts({ skus: [sku], type });
          const products: any[] = Array.isArray(fetched) ? fetched : [];
          const product = products.find((p) => (p?.id ?? p?.productId) === sku);
          if (!product) {
            throw new Error(t("payment.productFetchError") + " (" + sku + ")");
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
              throw new Error(t("payment.offerNotFoundError"));
            }
            await IAP.requestPurchase({
              request: { google: { skus: [sku], subscriptionOffers: [{ sku, offerToken }] } },
              type: "subs",
            });
          }
          keepLoading = true;
        } catch (err: any) {
          const code = String(err?.code ?? "");
          if (code !== "user-cancelled" && code !== "E_USER_CANCELLED") {
            Alert.alert(t("payment.failTitle"), String(err?.message ?? err));
          }
          setLoading(null);
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
              alert(t("payment.successTitle"));
              window.location.reload();
            }
          });
        } catch (e: any) {
          alert(t("payment.failTitle") + ": " + (e.message || "error"));
        } finally {
          setLoading(null);
        }
        return;
      }

      // --- 3. 일반 웹 (레몬 스퀴지 등) ---
      const { url } = await api.checkout(productId === "onetime");
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      Alert.alert(t("payment.failTitle"), String(e?.message || t("payment.failRetry")));
      setLoading(null);
    }
  };

  const termsText = isTelegramEnv
    ? t("payment.termsTelegram")
    : Platform.OS === "android"
    ? t("payment.termsGoogle")
    : t("payment.termsWeb");

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.title}>{t("payment.title")}</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeIcon}>
              <Text style={{ fontSize: 22, color: colors.textMuted, lineHeight: 24 }}>✕</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.desc}>{t("payment.description")}</Text>

          {verifying && (
            <View style={styles.verifyBox}>
              <ActivityIndicator color={colors.primary} />
              <Text style={styles.verifyText}>{t("payment.verifying")}</Text>
            </View>
          )}

          {/* 💎 프리미엄 구독 플랜 */}
          <TouchableOpacity
            style={[styles.planBox, { borderColor: colors.primary, backgroundColor: colors.primary + "05" }]}
            onPress={() => handlePay("sub_monthly_699")}
            disabled={!!loading}
          >
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 }}>
                <Text style={styles.planName}>{t("payment.subMonthlyTitle")}</Text>
                <View style={{ backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 }}>
                  <Text style={{ color: colors.onPrimary, fontSize: 10, fontWeight: "700" }}>{t("payment.best")}</Text>
                </View>
              </View>
              <Text style={styles.planDetail}>{t("payment.subMonthlyDetail")}</Text>
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
              <Text style={styles.planName}>{t("payment.deepReportTitle")}</Text>
              <Text style={styles.planDetail}>{t("payment.deepReportDetail")}</Text>
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
  verifyBox: { flexDirection: "row", alignItems: "center", gap: 10, padding: 12, marginBottom: 12, borderRadius: radius.md, backgroundColor: colors.primary + "10" },
  verifyText: { flex: 1, fontSize: 13, color: colors.text },
  terms: { textAlign: "center", fontSize: 11, color: colors.textMuted, marginTop: 12 },
});
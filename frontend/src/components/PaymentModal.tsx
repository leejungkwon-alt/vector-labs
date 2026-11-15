import * as RNIap from "react-native-iap";
import React, { useState, useEffect, useRef } from "react";
import {
  Modal, View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Alert,
  Platform, Linking, ScrollView,
} from "react-native";
import { colors, radius, spacing } from "@/theme";
import { api } from "@/api/client";
import { useAuthStore, refreshUser, applyWalletSnapshot } from "@/store/authStore";
import { useQueryClient } from "@tanstack/react-query";
import { useT } from "@/i18n";

// Play Console에 등록한 상품 ID와 정확히 일치해야 합니다.
const SKU_ONETIME = "gyeol_onetime_credit"; // 관리형 상품(1회권)
const SKU_SUBS = "gyeol_premium_monthly"; // 구독

// 💡 결제 종류는 반드시 이 두 값 중 하나로만 넘긴다.
//    (예전의 "sub_monthly_699" 같은 가격별 ID는 실제로 쓰이지 않고, onetime이 아니면 전부
//     구독으로 결제되는 구조라 오타 ID도 조용히 구독 결제가 되었다. 그래서 타입으로 막는다.)
type PayKind = "subs" | "onetime";

// 💡 표시 금액은 하드코딩하지 않고 결제 채널이 알려준 값을 우선 사용한다.
//    (화면 문구와 실제 청구 금액이 어긋나면 스토어 심사/환불 분쟁 사유가 된다.)
//    실제 금액을 못 얻은 경우에만 i18n 문구로 폴백한다.
const priceFromStore = (product: any): string | null => {
  if (!product) return null;
  const raw =
    product.displayPrice ??          // react-native-iap: 사람이 읽는 가격 문자열 (예: "$6.99")
    product.localizedPrice ??
    product.priceString ??
    product.oneTimePurchaseOfferDetailsAndroid?.formattedPrice ??
    null;
  const value = typeof raw === "string" ? raw.trim() : "";
  return value || null;
};

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

// 💡 결제 창(PaymentModal)은 홈/설정 등 여러 화면에 각각 마운트되어 있어서, 구글 결제 결과 리스너가 화면 수만큼 동시에 등록된다.
//    같은 구매를 화면마다 따로 처리하면 한 쪽은 성공, 다른 쪽은 이미 소비된 구매의 finishTransaction 실패("결제 실패")가 뜬다.
//    그래서 처리 기록과 "지금 열려 있는 결제 창 수"는 컴포넌트가 아니라 모듈 전체에서 공유한다.
const processedTokens = new Set<string>();
let visibleModalCount = 0;

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
  // 스토어(Play Console)가 실제로 청구하는 금액. 못 받으면 i18n 문구로 폴백한다.
  const [storePrices, setStorePrices] = useState<{ subs?: string; onetime?: string }>({});
  const t = useT();

  const queryClient = useQueryClient();
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;
  const isAndroidApp = Platform.OS === "android" && !isTelegramEnv;

  // 리스너 안에서 최신 함수를 쓰기 위한 ref
  const onCloseRef = useRef(onClose);
  const queryClientRef = useRef(queryClient);
  const visibleRef = useRef(visible);
  useEffect(() => { onCloseRef.current = onClose; }, [onClose]);
  useEffect(() => { queryClientRef.current = queryClient; }, [queryClient]);
  useEffect(() => {
    visibleRef.current = visible;
    if (!visible) return;
    visibleModalCount += 1;
    return () => { visibleModalCount -= 1; };
  }, [visible]);

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
        // 다른 결제 창이 열려 있으면 그 창이 처리한다 (이 창이 닫혀 있을 때만 양보)
        if (!visibleRef.current && visibleModalCount > 0) return;
        // 같은 구매는 앱 전체에서 한 번만 처리
        if (token && processedTokens.has(token)) return;
        if (token) processedTokens.add(token);

        if (!token) throw new Error("Missing purchase token.");
        if (mounted) setVerifying(true);
        let verified: { tier?: string; is_premium?: boolean; onetime_credits?: number } | null = null;
        try {
          verified = await verifyWithRetry({ sku, purchaseToken: token, productId: sku });
        } catch (e) {
          processedTokens.delete(token); // allow retry
          throw e; // do not finish the purchase when server verification fails
        }

        // 서버 지급은 이미 끝났다. 구매 마무리(소비/승인)가 실패해도 결제 실패로 보여주지 않는다.
        try {
          await IAP.finishTransaction({ purchase, isConsumable: sku === SKU_ONETIME });
        } catch (finishErr) {
          console.warn("finishTransaction failed (ignored, already granted):", finishErr);
        }

        // 💡 서버가 돌려준 티어/크레딧으로 유저 상태를 먼저 갱신한 뒤,
        //    화면(홈 리포트/daily 등)을 다시 불러온다. (닫기 전에 실행해야 반영이 보장됨)
        if (verified) applyWalletSnapshot(verified);
        await refreshUser();
        await queryClientRef.current.invalidateQueries();

        if (mounted) {
          setLoading(null);
          Alert.alert(t("common.notice"), t("payment.successTitle"));
          onCloseRef.current();
        }
      } catch (e: any) {
        if (mounted) setLoading(null);
        const s = Number(e?.status);
        const delayed = s === 0 || s === 408 || s === 409 || s >= 500;
        Alert.alert(delayed ? t("common.notice") : t("payment.failTitle"), delayed ? t("payment.verifyDelayed") : String(e?.message ?? e));
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
        return;
      }
      // 💡 결제창에 보여줄 금액은 Play Console 상품 가격을 그대로 쓴다.
      //    (i18n 문구에 적힌 금액과 실제 청구 금액이 다르면 사용자 혼란/환불 요청이 생긴다.)
      for (const [kind, sku, type] of [
        ["subs", SKU_SUBS, "subs"],
        ["onetime", SKU_ONETIME, "in-app"],
      ] as const) {
        try {
          const fetched: any = await IAP.fetchProducts({ skus: [sku], type });
          const products: any[] = Array.isArray(fetched) ? fetched : [];
          const product = products.find((p) => (p?.id ?? p?.productId) === sku);
          const price = priceFromStore(product);
          if (price && mounted) {
            setStorePrices((prev) => ({ ...prev, [kind]: price }));
          }
        } catch (err) {
          console.warn(`Price fetch failed for ${sku}:`, err);
        }
      }
    })();

    return () => {
      mounted = false;
      updateSub?.remove?.();
      errorSub?.remove?.();
      RNIap.endConnection();
    };
  }, [isAndroidApp]);

  const handlePay = async (kind: PayKind) => {
    setLoading(kind);
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
        const isOnetime = kind === "onetime";
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
            kind === "onetime"
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
      const { url } = await api.checkout(kind === "onetime");
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

  // 💡 금액 표시: 스토어(Play) 실제 가격 → i18n 문구 순으로 결정한다.
  //    Telegram은 서버 인보이스 금액(XTR)이 결제 금액과 같고, 웹은 Lemon Squeezy
  //    대시보드 variant 가격이 결제 금액이라 클라이언트에서 알 수 없다.
  //    그래서 웹은 i18n 문구를 쓰되, 대시보드 가격이 바뀌면 이 문구도 함께 맞춰야 한다.
  const subsPriceText = storePrices.subs || t("payment.subMonthlyPrice");
  const onetimePriceText = storePrices.onetime || t("payment.deepReportPrice");

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
            onPress={() => handlePay("subs")}
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
                {isTelegramEnv ? "400 Stars / month (Auto-renews)" : subsPriceText}
              </Text>
            </View>
            {loading === "subs" ? (
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
              <Text style={styles.planNote}>{t("payment.deepReportYearNote")}</Text>
              <Text style={styles.planPrice}>{isTelegramEnv ? "150 Stars" : onetimePriceText}</Text>
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
  planNote: { fontSize: 12, color: colors.primary, marginBottom: 6 },
  planPrice: { fontSize: 15, fontWeight: "600", color: colors.primary },
  verifyBox: { flexDirection: "row", alignItems: "center", gap: 10, padding: 12, marginBottom: 12, borderRadius: radius.md, backgroundColor: colors.primary + "10" },
  verifyText: { flex: 1, fontSize: 13, color: colors.text },
  terms: { textAlign: "center", fontSize: 11, color: colors.textMuted, marginTop: 12 },
});
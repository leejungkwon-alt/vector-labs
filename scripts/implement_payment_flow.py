#!/usr/bin/env python3
"""
scripts/implement_payment_flow.py

[수익화 모델 확정 적용]
1. 백엔드: 결제 API 엔드포인트 추가 및 IAP 상품 로직 업데이트
2. 백엔드: entitlements.py 수정 (단건 결제 시 특정 섹션만 락 해제)
3. 프론트엔드: PaymentModal 3개 상품 UI로 전면 개편
4. 프론트엔드: client.ts에 purchase API 추가
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

def patch_file(rel_path, old, new, label, is_frontend=True):
    base = FRONTEND if is_frontend else ROOT
    p = base / rel_path
    if not p.exists():
        print(f"  [!!] {p} 없음")
        return
    text = p.read_text(encoding="utf-8")
    if new in text:
        print(f"  [--] {label}: 이미 적용됨")
        return
    if old not in text:
        print(f"  [!!] {label}: 대상 문자열 불일치")
        return
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  [OK] {label}")

def main():
    print("=" * 60)
    print("  수익화 모델(결제 연동) 구현")
    print("=" * 60)

    # ---------------------------------------------------------
    # [백엔드] 1. iap.py 상품 로직 업데이트
    # ---------------------------------------------------------
    patch_file(
        "app/services/iap.py",
        '''    if receipt == "mock_valid_receipt":
        repo = get_repository()
        if product_id == "premium_monthly":
            repo.set_tier(user_id, "premium")
            return {"status": "success", "tier": "premium"}
        elif product_id == "addon_compatibility":
            repo.grant_addon(user_id, "compatibility")
            return {"status": "success", "addon": "compatibility"}
        else:
            raise IAPVerificationError(f"Unknown product_id: {product_id}")''',
        '''    if receipt == "mock_valid_receipt":
        repo = get_repository()
        if product_id == "sub_monthly_3900":
            repo.set_tier(user_id, "subscription")
            return {"status": "success", "tier": "subscription"}
        elif product_id == "addon_compat_1900":
            repo.grant_addon(user_id, "compatibility")
            return {"status": "success", "addon": "compatibility"}
        elif product_id == "addon_deep_990":
            repo.grant_addon(user_id, "deep_report")
            return {"status": "success", "addon": "deep_report"}
        else:
            raise IAPVerificationError(f"Unknown product_id: {product_id}")''',
        "iap.py 상품 로직 업데이트",
        is_frontend=False
    )

    # ---------------------------------------------------------
    # [백엔드] 2. auth/router.py 결제 엔드포인트 추가
    # ---------------------------------------------------------
    # 2-1. Import 추가
    patch_file(
        "app/auth/router.py",
        "from app.schemas.auth import (",
        "from pydantic import BaseModel\nfrom app.schemas.auth import (",
        "router.py Pydantic import",
        is_frontend=False
    )
    # 2-2. 엔드포인트 추가
    patch_file(
        "app/auth/router.py",
        '@router.get("/me/push-tokens")',
        '''class PurchaseRequest(BaseModel):
    product_id: str
    receipt: str = "mock_valid_receipt"

@router.post("/me/purchase")
def purchase(body: PurchaseRequest, user: dict = Depends(get_current_user)):
    from app.services.iap import verify_and_grant, IAPVerificationError
    try:
        return verify_and_grant(user["id"], "ios", body.receipt, body.product_id)
    except IAPVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/push-tokens")''',
        "router.py 결제 엔드포인트 추가",
        is_frontend=False
    )

    # ---------------------------------------------------------
    # [백엔드] 3. entitlements.py 게이팅 로직 확장 (애드온 지원)
    # ---------------------------------------------------------
    # 3-1. 함수 시그니처 변경
    patch_file(
        "app/services/entitlements.py",
        "def apply_entitlement_gate(report: dict, tier: str) -> dict:",
        "def apply_entitlement_gate(report: dict, tier: str, addons: list[str] = None) -> dict:",
        "entitlements.py 시그니처 변경",
        is_frontend=False
    )
    # 3-2. 애드온 확인 로직 추가
    patch_file(
        "app/services/entitlements.py",
        '''    meta = report.setdefault("meta", {})
    meta["tier"] = tier

    if tier in UNGATED_TIERS:''',
        '''    addons = addons or []
    meta = report.setdefault("meta", {})
    meta["tier"] = tier

    if tier in UNGATED_TIERS:''',
        "entitlements.py 애드온 변수",
        is_frontend=False
    )
    # 3-3. love, career, wealth 락 해제 조건 추가
    patch_file(
        "app/services/entitlements.py",
        '''    for sid, section in sections.items():
        rule = FREE_SECTION_RULES.get(sid)

        if rule is None:''',
        '''    for sid, section in sections.items():
        # [신규] 심화 리포트 애드온이 있으면 love, career, wealth는 잠금 해제
        if sid in ("love", "career", "wealth") and "deep_report" in addons:
            gated_sections[sid] = section
            continue

        rule = FREE_SECTION_RULES.get(sid)

        if rule is None:''',
        "entitlements.py 심화 리포트 락 해제",
        is_frontend=False
    )

    # ---------------------------------------------------------
    # [백엔드] 4. report.py 에서 유저 애드온을 entitlements로 전달
    # ---------------------------------------------------------
    patch_file(
        "app/api/v1/endpoints/report.py",
        '    tier = "free" if current_user is None else (current_user.get("tier") or "free")\n    report = apply_entitlement_gate(report, tier)',
        '''    tier = "free" if current_user is None else (current_user.get("tier") or "free")
    uid = current_user.get("id") if current_user else None
    from app.auth.repository import get_repository
    addons = get_repository().list_addons(uid) if uid else []
    report = apply_entitlement_gate(report, tier, addons)''',
        "report.py 애드온 전달",
        is_frontend=False
    )

    # ---------------------------------------------------------
    # [프론트엔드] 5. client.ts purchase API 추가
    # ---------------------------------------------------------
    patch_file(
        "src/api/client.ts",
        'linkProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/link/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),',
        'linkProvider: (provider: string, token: string) => request<AuthResponse>(`/auth/link/${provider}`, { method: "POST", body: JSON.stringify({ provider_token: token }) }),\n  purchase: (product_id: string) => request<any>("/auth/me/purchase", { method: "POST", body: JSON.stringify({ product_id, receipt: "mock_valid_receipt" }) }),',
        "client.ts purchase 추가"
    )

    # ---------------------------------------------------------
    # [프론트엔드] 6. PaymentModal.tsx 전면 개편 (3가지 상품)
    # ---------------------------------------------------------
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
'''
    (FRONTEND / "src" / "components" / "PaymentModal.tsx").write_text(NEW_PAYMENT_MODAL, encoding="utf-8")
    print("  [OK] PaymentModal.tsx 3가지 상품 UI로 전면 개편")

    print("\n[git] add → commit → push")
    try:
        subprocess.run(["git", "add", "."], cwd=ROOT, check=True)
        subprocess.run(["git", "commit", "-m", "feat(payment): implement 3-tier pricing (sub 3900, deep 990, compat 1900) and full payment cycle"], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
        print("\n[done] 커밋 + 푸시 완료")
    except subprocess.CalledProcessError:
        print("\n[!!] git 커밋 실패")

if __name__ == "__main__":
    main()
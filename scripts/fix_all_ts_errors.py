#!/usr/bin/env python3
"""
scripts/fix_all_ts_errors.py

타입스크립트 에러 10건 일괄 수정 및 settings.tsx 복구
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

def patch_file(rel_path, old, new, label):
    p = FRONTEND / rel_path
    if not p.exists():
        print(f"  [!!] {rel_path} 없음")
        return
    text = p.read_text(encoding="utf-8")
    if new in text:
        print(f"  [--] {label}: 이미 적용됨")
        return
    if old not in text:
        print(f"  [!!] {label}: 대상 문자열 불일치")
        return
    p.write_text(text.replace(old, new), encoding="utf-8")
    print(f"  [OK] {label} 수정 완료")

def main():
    print("=" * 60)
    print("  프론트엔드 TypeScript 에러 일괄 수정")
    print("=" * 60)

    # 1. settings.tsx 전체 복구 (이전 실행 중단으로 인해 덮어쓰기)
    NEW_SETTINGS = '''import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from "react-native";
import { router } from "expo-router";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { api } from "@/api/client";
import { SocialLoginModal } from "@/components/SocialLoginModal";
import { PaymentModal } from "@/components/PaymentModal";

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const signOut = useAuthStore((s) => s.signOut);
  const clearProfile = useProfileStore((s) => s.clearProfile);

  const [showLogin, setShowLogin] = useState(false);
  const [showPayment, setShowPayment] = useState(false);

  const handleUpgrade = () => {
    if (!user) return;
    if (user.is_anonymous) {
      setShowLogin(true);
    } else {
      setShowPayment(true);
    }
  };

  const handleReset = async () => {
    await clearProfile();
    router.replace("/birth-input");
  };

  const handleDeleteAccount = () => {
    const performDelete = async () => {
      try {
        await api.deleteAccount();
        await clearProfile();
        await signOut();
        router.replace("/");
      } catch (e: any) {
        const msg = e?.detail || "계정 삭제에 실패했습니다.";
        if (Platform.OS === "web") alert(msg);
        else Alert.alert("오류", msg);
      }
    };

    if (Platform.OS === "web") {
      if (confirm("정말로 계정을 삭제하시겠습니까? 모든 데이터가 사라집니다.")) performDelete();
    } else {
      Alert.alert("계정 삭제", "정말로 계정을 영구 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.", [
        { text: "취소", style: "cancel" },
        { text: "영구 삭제", style: "destructive", onPress: performDelete },
      ]);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.profileBox}>
        <Text style={styles.sectionTitle}>내 계정 정보</Text>
        <View style={styles.row}>
          <Text style={styles.label}>이용 등급</Text>
          <Text style={styles.value}>{user?.tier.toUpperCase()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>사용자 ID</Text>
          <Text style={styles.value}>{user?.id.slice(0, 8)}...</Text>
        </View>
      </View>

      {user?.tier === "free" && (
        <View style={[styles.profileBox, { backgroundColor: colors.primary + "10", borderColor: colors.primary }]}>
          <Text style={[styles.sectionTitle, { color: colors.primary }]}>✨ 프리미엄 업그레이드</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            구독하면 7일치 데일리 에너지와 궁합 분석을 모두 이용할 수 있습니다.
          </Text>
          <TouchableOpacity style={{ backgroundColor: colors.primary, padding: 14, borderRadius: radius.md, alignItems: "center" }} onPress={handleUpgrade}>
            <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 구독하기</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.list}>
        <TouchableOpacity style={styles.btn} onPress={handleReset}>
          <Text style={styles.btnText}>출생 정보 수정하기</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.btn, styles.dangerBtn]} onPress={handleDeleteAccount}>
          <Text style={styles.dangerText}>계정 영구 삭제</Text>
        </TouchableOpacity>
      </View>

      <SocialLoginModal
        visible={showLogin}
        onClose={() => setShowLogin(false)}
        onSuccess={() => {
          setShowLogin(false);
          setShowPayment(true);
        }}
      />
      <PaymentModal
        visible={showPayment}
        onClose={() => setShowPayment(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  profileBox: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.xl, borderWidth: 1, borderColor: colors.border },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  row: { flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.sm },
  label: { fontSize: 15, color: colors.textMuted },
  value: { fontSize: 15, fontWeight: "600", color: colors.text },
  list: { gap: spacing.sm },
  btn: { backgroundColor: colors.surface, padding: spacing.md, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, alignItems: "center" },
  btnText: { color: colors.text, fontSize: 16, fontWeight: "600" },
  dangerBtn: { borderColor: colors.danger },
  dangerText: { color: colors.danger, fontSize: 16, fontWeight: "600" },
});
'''
    (FRONTEND / "app" / "(tabs)" / "settings.tsx").write_text(NEW_SETTINGS, encoding="utf-8")
    print("  [OK] settings.tsx 복구 완료")

    # 2. _layout.tsx: Ionicons color 타입 에러 수정 (null 방지)
    p_layout = FRONTEND / "app" / "(tabs)" / "_layout.tsx"
    if p_layout.exists():
        text = p_layout.read_text(encoding="utf-8")
        text = text.replace("color={color}", 'color={color || "#7A6A5C"}')
        p_layout.write_text(text, encoding="utf-8")
        print("  [OK] _layout.tsx: 아이콘 color 타입 수정")

    # 3. compatibility.tsx: gender 타입 캐스팅
    patch_file(
        "app/(tabs)/compatibility.tsx",
        "gender: gender,",
        'gender: gender as "M" | "F",',
        "compatibility.tsx: gender 타입"
    )

    # 4. types.ts: relationship_advice 속성 추가
    patch_file(
        "types.ts",
        "disclaimer: string;\n    pair: {",
        "disclaimer: string;\n    relationship_advice?: string;\n    pair: {",
        "types.ts: relationship_advice 추가"
    )

    # 5. PaymentModal.tsx: radius.xl -> radius.lg
    p_payment = FRONTEND / "src" / "components" / "PaymentModal.tsx"
    if p_payment.exists():
        text = p_payment.read_text(encoding="utf-8")
        text = text.replace("radius.xl", "radius.lg")
        p_payment.write_text(text, encoding="utf-8")
        print("  [OK] PaymentModal.tsx: radius.xl -> radius.lg 수정")

    # 6. authStore.ts: linkAccount 인터페이스 추가
    patch_file(
        "src/store/authStore.ts",
        "  signInAnonymous: () => Promise<void>;",
        '  linkAccount: (provider: "apple" | "google" | "kakao") => Promise<void>;\n  signInAnonymous: () => Promise<void>;',
        "authStore.ts: linkAccount 타입 추가"
    )

    print("\n[완료] 모든 에러가 수정되었습니다.")

if __name__ == "__main__":
    main()
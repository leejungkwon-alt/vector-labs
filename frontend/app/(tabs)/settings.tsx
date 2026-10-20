import { View, Text, TouchableOpacity, StyleSheet, Alert, Platform } from "react-native";
import { router } from "expo-router";
import { colors, spacing, radius } from "@/theme";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { api } from "@/api/client";\nimport { SocialLoginModal } from "@/components/SocialLoginModal";\nimport { PaymentModal } from "@/components/PaymentModal";

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);\n  const [showLogin, setShowLogin] = useState(false);\n  const [showPayment, setShowPayment] = useState(false);
  const signOut = useAuthStore((s) => s.signOut);
  const clearProfile = useProfileStore((s) => s.clearProfile);

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

// frontend/app/billing/success.tsx
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";
import { colors, radius } from "@/theme";

export default function BillingSuccessScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>🎉</Text>
      <Text style={styles.title}>결제가 완료되었습니다!</Text>
      <Text style={styles.subtitle}>
        프리미엄 기능이 활성화되었습니다.{"\n"}
        잠시 후 설정 화면에서 확인해 주세요.
      </Text>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => router.replace("/settings")}
      >
        <Text style={styles.buttonText}>설정으로 돌아가기</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center", padding: 24 },
  emoji: { fontSize: 64, marginBottom: 16 },
  title: { fontSize: 24, fontWeight: "700", color: colors.text, marginBottom: 12 },
  subtitle: { fontSize: 16, color: colors.textMuted, textAlign: "center", lineHeight: 24, marginBottom: 32 },
  button: { backgroundColor: colors.primary, paddingVertical: 14, paddingHorizontal: 24, borderRadius: radius.md },
  buttonText: { color: colors.onPrimary, fontSize: 16, fontWeight: "700" },
});
// frontend/app/billing/success.tsx
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { router } from "expo-router";
import { useT } from "@/i18n";
import { colors, radius } from "@/theme";

export default function BillingSuccessScreen() {
  const t = useT();
  return (
    <View style={styles.container}>
      <Text style={styles.emoji}>🎉</Text>
      <Text style={styles.title}>{t("billing.successTitle")}</Text>
      <Text style={styles.subtitle}>
        {t("billing.successDesc1")}{"\n"}
        {t("billing.successDesc2")}
      </Text>
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={() => router.replace("/settings")}
      >
        <Text style={styles.buttonText}>{t("billing.backToSettings")}</Text>
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
import { router } from "expo-router";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { useT } from "@/i18n";

export default function BillingCancelScreen() {
  const t = useT();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t("billing.cancelTitle")}</Text>
      <Text style={styles.desc}>{t("billing.cancelDesc")}</Text>
      <TouchableOpacity style={styles.btn} onPress={() => router.replace("/settings")}>
        <Text style={styles.btnText}>{t("billing.backToSettings")}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center", padding: spacing.lg },
  title: { fontSize: 24, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  desc: { fontSize: 16, color: colors.textMuted, textAlign: "center", marginBottom: spacing.xl },
  btn: { backgroundColor: colors.primary, paddingVertical: 14, paddingHorizontal: 24, borderRadius: radius.md },
  btnText: { color: colors.onPrimary, fontSize: 16, fontWeight: "600" },
});

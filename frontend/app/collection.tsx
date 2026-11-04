import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { colors, spacing } from "@/theme";
import { router } from "expo-router";
import { usePoemStore } from "@/store/poemStore";
import { useAuthStore } from "@/store/authStore";

export default function CollectionScreen() {
  const user = useAuthStore((s) => s.user);
  const { collection, currentPoem } = usePoemStore();
  const isPremium = user?.tier === "premium" || user?.tier === "subscription";

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Poem Collection</Text>
        <Text style={styles.subtitle}>{collection[0]?.element || ""} x {collection.length}</Text>
      </View>
      <ScrollView contentContainerStyle={styles.grid}>
        {collection.map((poem, i) => {
          const isMyDailyPoem = poem.id === currentPoem?.id;
          const locked = !isPremium && !isMyDailyPoem;
          return (
            <View key={i} style={styles.card}>
              <View style={styles.cardImgBox}>
                <Text style={styles.cardElement}>{poem.element}</Text>
              </View>
              <Text style={styles.cardTitle}>{poem.title}</Text>
              <Text style={styles.cardRelation}>{poem.relation_kr}</Text>
              {locked && (
                <View style={styles.lockOverlay}>
                  <Text style={styles.lockText}>🔒 Premium</Text>
                </View>
              )}
            </View>
          );
        })}
      </ScrollView>
      {!isPremium && (
        <View style={styles.footer}>
          <Text style={styles.footerText}>Upgrade to see all 25 poems</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: { padding: spacing.lg, paddingTop: spacing.xl, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  backBtn: { marginBottom: spacing.md },
  backText: { color: colors.primary, fontSize: 16, fontWeight: "600" },
  title: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: colors.textMuted },
  grid: { padding: spacing.md, flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  card: { width: "48%", backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", position: "relative", marginBottom: spacing.md, overflow: "hidden" },
  cardImgBox: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.primarySoft, alignItems: "center", justifyContent: "center", marginBottom: 12 },
  cardElement: { fontSize: 36, color: colors.primary, fontWeight: "300" },
  cardTitle: { fontSize: 15, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.3)", alignItems: "center", justifyContent: "center", borderRadius: 16 },
  lockText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  footer: { padding: spacing.lg, backgroundColor: colors.primarySoft, alignItems: "center" },
  footerText: { color: colors.primary, fontWeight: "600" }
});

import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Image } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { router } from "expo-router";
import { useAuthStore } from "@/store/authStore";

const POEMS = [
  { id: "su_same", title: "같은 물결", relation: "同", tier: "free" },
  { id: "su_generates_me", title: "서리에서 온 물", relation: "生我", tier: "premium" },
  { id: "su_i_generate", title: "봄을 부르는 물", relation: "我生", tier: "premium" },
  { id: "su_i_control", title: "물의 손", relation: "我剋", tier: "premium" },
  { id: "su_controls_me", title: "둑 안의 물", relation: "剋我", tier: "premium" },
];

export default function CollectionScreen() {
  const user = useAuthStore((s) => s.user);
  const isPremium = user?.tier === "premium" || user?.tier === "subscription";

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>← 돌아가기</Text>
        </TouchableOpacity>
        <Text style={styles.title}>시조 컬렉션</Text>
        <Text style={styles.subtitle}>수(水) 기운의 5편</Text>
      </View>
      <ScrollView contentContainerStyle={styles.grid}>
        {POEMS.map((poem, i) => {
          const locked = poem.tier === "premium" && !isPremium;
          return (
            <View key={i} style={[styles.card, locked && { opacity: 0.7 }]}>
              <Image source={{ uri: `/assets/poems/${poem.id}_calligraphy.svg` }} style={styles.cardImg} />
              <Text style={styles.cardTitle}>{poem.title}</Text>
              <Text style={styles.cardRelation}>{poem.relation}</Text>
              {locked && (
                 <View style={styles.lockOverlay}>
                   <Text style={styles.lockText}>🔒 프리미엄</Text>
                 </View>
              )}
            </View>
          );
        })}
      </ScrollView>
      {!isPremium && (
        <View style={styles.footer}>
          <Text style={styles.footerText}>프리미엄으로 업그레이드하고 25편 전체를 감상하세요.</Text>
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
  grid: { padding: spacing.md, flexDirection: "row", flexWrap: "wrap", gap: spacing.md, justifyContent: "center" },
  card: { width: "45%", backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" },
  cardImg: { width: "100%", height: 80, borderRadius: 8, marginBottom: 8, backgroundColor: colors.bgMuted },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.4)", alignItems: "center", justifyContent: "center" },
  lockText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  footer: { padding: spacing.lg, backgroundColor: colors.primarySoft, alignItems: "center" },
  footerText: { color: colors.primary, fontWeight: "600" }
});

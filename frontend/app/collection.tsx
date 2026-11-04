import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { colors, spacing } from "@/theme";
import { router } from "expo-router";
import type { PoemCard } from "../types";

const MOCK_POEMS: Partial<PoemCard>[] = [
  { id: "su_same", title: "같은 물결", relation_kr: "同", tier: "free" },
  { id: "su_generates_me", title: "서리에서 온 물", relation_kr: "生我", tier: "premium" },
  { id: "su_i_generate", title: "봄을 부르는 물", relation_kr: "我生", tier: "premium" },
  { id: "su_i_control", title: "물의 손", relation_kr: "我剋", tier: "premium" },
  { id: "su_controls_me", title: "둑 안의 물", relation_kr: "剋我", tier: "premium" },
];

export default function CollectionScreen() {
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
        {MOCK_POEMS.map((poem, i) => (
          <View key={i} style={styles.card}>
            <Text style={styles.cardElement}>水</Text>
            <Text style={styles.cardTitle}>{poem.title}</Text>
            <Text style={styles.cardRelation}>{poem.relation_kr}</Text>
            {poem.tier === "premium" && (
               <View style={styles.lockBadge}><Text style={styles.lockText}>🔒 프리미엄</Text></View>
            )}
          </View>
        ))}
      </ScrollView>
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
  card: { width: "45%", aspectRatio: 0.8, backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center" },
  cardElement: { fontSize: 32, color: colors.primary, marginBottom: 8 },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockBadge: { position: "absolute", top: 8, right: 8, backgroundColor: colors.bgMuted, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 },
  lockText: { fontSize: 10, color: colors.textMuted, fontWeight: "700" },
});

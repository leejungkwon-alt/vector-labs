// frontend/src/components/sections/shared.tsx
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { BlurView } from "expo-blur";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "@/theme";
import type { CompatibilityAdvice } from "../../../types";

// 섹션 공통 스타일 — 각 렌더러가 import 해서 사용
export const ss = StyleSheet.create({
  paragraph: { fontSize: 15, color: colors.text, lineHeight: 24, marginBottom: 12, flexShrink: 1, width: "100%" },
  blockBox: {
    backgroundColor: colors.bg,
    padding: spacing.md,
    borderRadius: radius.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  blockTitle: { fontSize: 16, fontWeight: "700", color: colors.primary, marginBottom: 6, flexShrink: 1 },
  coreHero: { fontSize: 18, fontWeight: "700", color: colors.text, lineHeight: 26, marginVertical: 10 },
  adviceText: { fontSize: 14, color: colors.primary, fontWeight: "600", marginTop: 8 },
  metaText: { fontSize: 13, color: colors.textMuted, marginBottom: 4 },
  tagRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 6, marginBottom: 8 },
  tag: {
    backgroundColor: colors.primarySoft,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: radius.pill,
    fontSize: 12,
    color: colors.primary,
    fontWeight: "600",
    overflow: "hidden",
  },
});

// ============================================================
// LockedHint — 유료 잠금 안내 카드 (기존 home.tsx 에서 이동)
// ============================================================
export function LockedHint({ onPress }: { onPress: () => void }) {
  return (
    <View style={sharedStyles.lockedCard}>
      <BlurView intensity={30} tint="light" style={StyleSheet.absoluteFill} />
      <View style={sharedStyles.lockedContent}>
        <Ionicons name="sparkles" size={20} color={colors.primary} />
        <Text style={sharedStyles.lockedText}>
          더 깊은 분석과 맞춤 인사이트가 준비되어 있어요.
        </Text>
        <TouchableOpacity style={sharedStyles.upgradeBtn} onPress={onPress}>
          <Text style={sharedStyles.upgradeBtnText}>전체 리포트 보기</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// ============================================================
// CompatBox — Mode/Premium 섹션 공용 케미 상자
// ============================================================
export function CompatBox({ compat }: { compat?: CompatibilityAdvice }) {
  if (!compat) return null;
  return (
    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.bg, borderRadius: radius.md }}>
      <Text style={ss.blockTitle}>케미</Text>
      <Text style={ss.paragraph}>최고의 케미: {(compat.best_match || []).join(", ")}</Text>
      <Text style={ss.metaText}>{compat.best_reason}</Text>
      <Text style={[ss.paragraph, { marginTop: 6 }]}>
        주의할 케미: {(compat.challenging_match || []).join(", ")}
      </Text>
      <Text style={ss.metaText}>{compat.challenging_reason}</Text>
    </View>
  );
}

// ============================================================
// RedFlagsBox — Mode/Premium 섹션 공용 주의사항 상자
// ============================================================
export function RedFlagsBox({ flags }: { flags?: string[] }) {
  if (!flags || flags.length === 0) return null;
  return (
    <View style={{ marginTop: 12, padding: 12, backgroundColor: colors.dangerSoft, borderRadius: radius.md }}>
      <Text style={[ss.blockTitle, { color: colors.danger }]}>주의할 점</Text>
      {flags.map((r, i) => (
        <Text key={i} style={ss.paragraph}>⚠ {r}</Text>
      ))}
    </View>
  );
}

const sharedStyles = StyleSheet.create({
  lockedCard: {
    marginTop: 16,
    borderRadius: radius.md,
    overflow: "hidden",
    borderWidth: 1,
    borderStyle: "dashed",
    borderColor: colors.primarySoft,
    backgroundColor: colors.primarySoft,
  },
  lockedContent: { padding: 16, alignItems: "center", gap: 8 },
  lockedText: { fontSize: 14, color: colors.text, fontWeight: "600", textAlign: "center" },
  upgradeBtn: {
    backgroundColor: colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: radius.sm,
    marginTop: 4,
  },
  upgradeBtnText: { color: colors.onPrimary, fontSize: 14, fontWeight: "700" },
});

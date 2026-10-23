// frontend/src/components/sections/EnergySection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import { DonutChart, ELEMENT_COLORS } from "@/components/DonutChart";
import type { EnergySection } from "../../../types";

const ELEM_LABELS: Record<string, string> = {
  "木": "성장(Wood)", "火": "불꽃(Spark)", "土": "대지(Earth)", "金": "예리함(Metal)", "水": "흐름(Water)",
};

export function EnergySectionView({ section }: { section: EnergySection }) {
  const pct = section.percentages || {};
  const pctEntries = Object.entries(pct);

  return (
    <View>
      <Text style={ss.coreHero}>{section.hero}</Text>

      {pctEntries.length > 0 && (
        <View style={{ marginBottom: 16 }}>
          {/* 도넛 차트 */}
          <DonutChart data={pct} />

          {/* 하단 범례(Legend) */}
          <View style={{ flexDirection: "row", flexWrap: "wrap", justifyContent: "center", gap: 12, marginTop: 12 }}>
            {pctEntries.map(([elem, val]) => (
              <View key={elem} style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: ELEMENT_COLORS[elem] || colors.primary }} />
                <Text style={{ fontSize: 13, color: colors.text, fontWeight: "500" }}>
                  {ELEM_LABELS[elem] || elem} {val}%
                </Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {section.blocks.map((b, i) => (
        <View key={i} style={ss.blockBox}>
          <Text style={ss.blockTitle}>
            {b.name}{" "}
            <Text style={{ fontSize: 12, color: colors.textMuted }}>({b.role})</Text>
          </Text>
          <Text style={ss.paragraph}>{b.body}</Text>
          {b.keywords.length > 0 && (
            <View style={ss.tagRow}>
              {b.keywords.map((k, j) => (
                <Text key={j} style={ss.tag}>#{k}</Text>
              ))}
            </View>
          )}
        </View>
      ))}
    </View>
  );
}

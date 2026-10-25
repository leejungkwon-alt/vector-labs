// frontend/src/components/sections/EnergySection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import { DonutChart, ELEMENT_COLORS } from "@/components/DonutChart";
import { useT } from "@/i18n";
import type { EnergySection } from "../../../types";



export function EnergySectionView({ section }: { section: EnergySection }) {
  const t = useT();
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
                  {t(`sections.${({"木":"wood","火":"fire","土":"earth","金":"metal","水":"water"}[elem] || "unknown")}`)} {val}%
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

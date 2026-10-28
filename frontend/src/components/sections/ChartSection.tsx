import { useT } from "@/i18n";
// frontend/src/components/sections/ChartSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import type { ChartSection } from "../../../types";

export function ChartSectionView({ section }: { section: ChartSection }) {
  const t = useT();
  return (
    <View>
      {section.hero && (
        <Text style={[ss.paragraph, { fontStyle: "italic", color: colors.primary }]}>
          {section.hero}
        </Text>
      )}
      {section.layers.map((layer, i) => (
        <View
          key={i}
          style={[
            ss.blockBox,
            layer.is_self && { borderColor: colors.primary, borderWidth: 2 },
          ]}
        >
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 4,
            }}
          >
            <Text style={ss.blockTitle}>
              {layer.label} {layer.is_self && t("sections.coreEssence")}
            </Text>
            <Text style={{ fontSize: 14, fontWeight: "700", color: colors.primary }}>
              {layer.archetype} · {layer.element}
            </Text>
          </View>
          <Text style={ss.metaText}>{layer.role}</Text>
          <Text style={ss.paragraph}>{layer.narrative}</Text>
        </View>
      ))}
      {section.notes.map((n, i) => (
        <Text key={i} style={[ss.paragraph, { fontStyle: "italic" }]}>
          📌 {n}
        </Text>
      ))}
    </View>
  );
}

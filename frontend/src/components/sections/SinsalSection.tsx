// frontend/src/components/sections/SinsalSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import type { SinsalSection } from "../../../types";

export function SinsalSectionView({ section }: { section: SinsalSection }) {
  return (
    <View>
      {section.hero && <Text style={ss.coreHero}>{section.hero}</Text>}
      {section.items.map((item, i) => (
        <View key={i} style={ss.blockBox}>
          <Text style={ss.blockTitle}>
            {item.name}
            {item.name_traditional && (
              <Text style={{ fontSize: 13, color: colors.textMuted }}>
                {" "}({item.name_traditional})
              </Text>
            )}
          </Text>
          <Text style={ss.metaText}>
            {item.position_label} · {item.position}
          </Text>
          <Text style={{ fontSize: 15, fontWeight: "600", color: colors.text, marginBottom: 4 }}>
            {item.headline}
          </Text>
          <Text style={ss.paragraph}>{item.body}</Text>
          {item.position_note && (
            <Text style={[ss.metaText, { fontStyle: "italic" }]}>{item.position_note}</Text>
          )}
          <Text style={[ss.adviceText, { color: colors.primary }]}>👉 {item.advice}</Text>
        </View>
      ))}
    </View>
  );
}

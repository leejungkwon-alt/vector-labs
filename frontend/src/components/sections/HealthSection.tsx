// frontend/src/components/sections/HealthSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import type { HealthSection } from "../../../types";

export function HealthSectionView({ section }: { section: HealthSection }) {
  return (
    <View>
      <Text style={ss.coreHero}>{section.hero}</Text>

      {section.blocks.map((b, i) => (
        <View key={i} style={ss.blockBox}>
          <Text style={ss.blockTitle}>{b.name}</Text>
          
          <Text style={ss.paragraph}>{b.body}</Text>
        </View>
      ))}

      {section.practices.length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={ss.blockTitle}>실천</Text>
          {section.practices.map((p, i) => (
            <Text key={i} style={ss.paragraph}>• {p}</Text>
          ))}
        </View>
      )}

      {section.framework_note && (
        <Text style={[ss.metaText, { fontStyle: "italic", marginTop: 8 }]}>
          {section.framework_note}
        </Text>
      )}
      {section.disclaimer && (
        <Text style={[ss.metaText, { fontStyle: "italic", color: colors.danger }]}>
          {section.disclaimer}
        </Text>
      )}
    </View>
  );
}

// frontend/src/components/sections/CoreSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import type { CoreSection } from "../../../types";

export function CoreSectionView({ section }: { section: CoreSection }) {
  return (
    <View>
      {section.pillar_name && (
        <Text style={[ss.metaText, { marginBottom: 8 }]}>
          {section.pillar_name}
        </Text>
      )}
      <Text style={ss.coreHero}>{section.hero}</Text>

      {(section.narrative || []).map((p, i) => (
        <Text key={`n${i}`} style={ss.paragraph}>{p}</Text>
      ))}

      {(section.personalized_insights || []).length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={ss.blockTitle}>맞춤 인사이트</Text>
          {(section.personalized_insights || []).map((p, i) => (
            <Text key={`pi${i}`} style={ss.paragraph}>✦ {p}</Text>
          ))}
        </View>
      )}

      {(section.shadows || []).length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={[ss.blockTitle, { color: colors.danger }]}>그림자</Text>
          {(section.shadows || []).map((s, i) => (
            <Text key={`s${i}`} style={[ss.paragraph, { color: colors.danger }]}>{s}</Text>
          ))}
        </View>
      )}

      {(section.advice || []).length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={ss.blockTitle}>조언</Text>
          {(section.advice || []).map((a, i) => (
            <Text key={`a${i}`} style={[ss.paragraph, { fontWeight: "600" }]}>💡 {a}</Text>
          ))}
        </View>
      )}

      {(section.keywords || []).length > 0 && (
        <View style={ss.tagRow}>
          {(section.keywords || []).map((k, i) => (
            <Text key={`k${i}`} style={ss.tag}>#{k}</Text>
          ))}
        </View>
      )}
    </View>
  );
}

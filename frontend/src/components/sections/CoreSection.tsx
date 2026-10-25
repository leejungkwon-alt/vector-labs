// frontend/src/components/sections/CoreSection.tsx
import { View, Text } from "react-native";
import { colors } from "@/theme";
import { ss } from "./shared";
import { useT } from "@/i18n";
import type { CoreSection } from "../../../types";

export function CoreSectionView({ section }: { section: CoreSection }) {
  const t = useT();
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
          <Text style={ss.blockTitle}>{t("sections.personalizedInsights")}</Text>
          {(section.personalized_insights || []).map((p, i) => (
            <Text key={`pi${i}`} style={ss.paragraph}>✦ {p}</Text>
          ))}
        </View>
      )}

      {(section.shadows || []).length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={[ss.blockTitle, { color: colors.danger }]}>{t("sections.shadow")}</Text>
          {(section.shadows || []).map((s, i) => (
            <Text key={`s${i}`} style={[ss.paragraph, { color: colors.danger }]}>{s}</Text>
          ))}
        </View>
      )}

      {(section.advice || []).length > 0 && (
        <View style={{ marginTop: 8 }}>
          <Text style={ss.blockTitle}>{t("sections.advice")}</Text>
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

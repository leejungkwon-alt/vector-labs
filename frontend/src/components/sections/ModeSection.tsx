// frontend/src/components/sections/ModeSection.tsx
import { View, Text } from "react-native";
import { ss, CompatBox, RedFlagsBox } from "./shared";
import { useT } from "@/i18n";
import type { ModeSection } from "../../../types";

export function ModeSectionView({ section }: { section: ModeSection }) {
  const t = useT();
  const allActions = section.actions || [];
  const featured = section.action || allActions[0];
  const rest = allActions.filter(a => a !== featured);

  return (
    <View>
      <Text style={ss.coreHero}>{section.headline}</Text>
      <Text style={ss.paragraph}>{section.body}</Text>
      {featured && <Text style={ss.adviceText}>💡 {featured}</Text>}

      {section.patterns && section.patterns.length > 0 && (
        <View style={{ marginTop: 12 }}>
          <Text style={ss.blockTitle}>{t("sections.patterns")}</Text>
          {section.patterns.map((p, i) => (
            <Text key={i} style={ss.paragraph}>• {p}</Text>
          ))}
        </View>
      )}

      {rest.length > 0 && (
        <View style={{ marginTop: 12 }}>
          <Text style={ss.blockTitle}>{t("sections.additionalActions")}</Text>
          {rest.map((a, i) => (
            <Text key={i} style={ss.paragraph}>→ {a}</Text>
          ))}
        </View>
      )}

      <CompatBox compat={section.compatibility} />
      <RedFlagsBox flags={section.red_flags} />
    </View>
  );
}

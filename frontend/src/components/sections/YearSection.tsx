// frontend/src/components/sections/YearSection.tsx
import { View, Text } from "react-native";
import { ss } from "./shared";
import { useT } from "@/i18n";
import type { YearSection } from "../../../types";

export function YearSectionView({ section }: { section: YearSection }) {
  const t = useT();
  return (
    <View>
      <Text style={ss.metaText}>
        {section.target_year}{section.pillar_name ? ` · ${section.pillar_name}` : ""}
      </Text>
      {section.solar_calendar_note && (
        <Text style={[ss.metaText, { fontStyle: "italic", marginBottom: 8 }]}>
          {section.solar_calendar_note}
        </Text>
      )}
      <Text style={ss.coreHero}>{section.name}</Text>
      <Text style={[ss.paragraph, { fontWeight: "600" }]}>{section.headline}</Text>
      {section.body && <Text style={ss.paragraph}>{section.body}</Text>}
      {section.watch_for && <Text style={ss.metaText}>⚠️ {t("sections.watch")}: {section.watch_for}</Text>}
      {section.lean_into && <Text style={ss.metaText}>💡 {t("sections.focus")}: {section.lean_into}</Text>}
      {section.life_stage_context && (
        <View style={[ss.blockBox, { marginTop: 8 }]}>
          <Text style={ss.blockTitle}>{t("sections.lifeStage")}: {section.life_stage_context.label}</Text>
          <Text style={ss.paragraph}>{section.life_stage_context.headline}</Text>
        </View>
      )}
    </View>
  );
}

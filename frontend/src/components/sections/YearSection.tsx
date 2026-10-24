// frontend/src/components/sections/YearSection.tsx
import { View, Text } from "react-native";
import { ss } from "./shared";
import type { YearSection } from "../../../types";

export function YearSectionView({ section }: { section: YearSection }) {
  return (
    <View>
      <Text style={ss.metaText}>
        {section.target_year}년 · {section.pillar_name || section.pillar} · {section.ten_god}
      </Text>
      <Text style={ss.coreHero}>{section.name}</Text>
      <Text style={[ss.paragraph, { fontWeight: "600" }]}>{section.headline}</Text>
      {section.body && <Text style={ss.paragraph}>{section.body}</Text>}
      {section.watch_for && <Text style={ss.metaText}>⚠️ 주의: {section.watch_for}</Text>}
      {section.lean_into && <Text style={ss.metaText}>💡 집중: {section.lean_into}</Text>}
      {section.life_stage_context && (
        <View style={[ss.blockBox, { marginTop: 8 }]}>
          <Text style={ss.blockTitle}>생애 단계: {section.life_stage_context.label}</Text>
          <Text style={ss.paragraph}>{section.life_stage_context.headline}</Text>
        </View>
      )}
    </View>
  );
}

// frontend/src/components/sections/AgeBandSection.tsx
import { View, Text } from "react-native";
import { ss } from "./shared";
import type { AgeBandSection } from "../../../types";

export function AgeBandSectionView({ section }: { section: AgeBandSection }) {
  return (
    <View>
      <Text style={ss.metaText}>
        {section.label} · 만 {section.age}세 · 기준 {section.target_year}년
      </Text>
      <Text style={ss.coreHero}>{section.headline}</Text>
      <Text style={ss.paragraph}>{section.body}</Text>
      {section.advice.length > 0 && (
        <View style={{ marginTop: 8 }}>
          {section.advice.map((a, i) => (
            <Text key={i} style={ss.paragraph}>💡 {a}</Text>
          ))}
        </View>
      )}
    </View>
  );
}

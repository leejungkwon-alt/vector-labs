// frontend/src/components/sections/AgeBandSection.tsx
import { View, Text } from "react-native";
import { ss } from "./shared";
import { useT } from "@/i18n";
import type { AgeBandSection } from "../../../types";

export function AgeBandSectionView({ section }: { section: AgeBandSection }) {
  const t = useT();
  return (
    <View>
      <Text style={ss.metaText}>
        {t("sections.ageBandMeta", { label: section.label, age: section.age, year: section.target_year })}
      </Text>
      <Text style={ss.coreHero}>{section.headline}</Text>
      <Text style={ss.paragraph}>{section.body}</Text>
      {section.advice.length > 0 && (
        <View style={{ marginTop: 8 }}>
          {section.advice.map((a, i) => (
            <Text key={i} style={ss.paragraph}> {a}</Text>
          ))}
        </View>
      )}
    </View>
  );
}

// frontend/src/components/sections/TimelineSection.tsx
import { View, Text } from "react-native";
import { colors, gradeColors } from "@/theme";
import { ss } from "./shared";
import type { TimelineSection } from "../../../types";

export function TimelineSectionView({ section }: { section: TimelineSection }) {
  return (
    <View>
      {section.hero && <Text style={ss.coreHero}>{section.hero}</Text>}
      {section.items.map((item, i) => (
        <View
          key={i}
          style={[
            ss.blockBox,
            item.is_current && { borderColor: colors.primary, borderWidth: 2 },
          ]}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4, flexWrap: "wrap", gap: 4 }}>
            <Text style={{ fontSize: 15, fontWeight: "700", color: colors.text }}>
              {item.ages[0]}–{item.ages[1]}세 · {item.pillar_name || item.pillar}
              {item.is_current && <Text style={{ color: colors.primary }}> · 현재</Text>}
            </Text>
            <Text
              style={{
                fontSize: 13,
                fontWeight: "700",
                color: gradeColors[item.grade] || colors.text,
              }}
            >
              {item.grade}
            </Text>
          </View>
          {item.blurb && <Text style={ss.paragraph}>{item.blurb}</Text>}
        </View>
      ))}
    </View>
  );
}
